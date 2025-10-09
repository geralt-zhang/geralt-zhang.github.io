---
layout: lecture
title: "NVMe Virt"
details: PCIe & NVme detail
date: 2025-9-27
ready: true
sync: true
syncdate: 2025-09-27
---

# 虚拟盘是怎么出现在我的系统里的，一个identify发送到它发生了什么?

---

## 1) 这个虚拟盘是怎么出现在系统里的（从加载模块到驱动绑定）

1. **模块注册虚拟 PCI 设备**

   * `nvmev.ko` 在初始化时向内核的 PCI 层或 configfs/虚拟设备子系统注册自己为一个 PCI 设备（内核里会创建对应的 `struct pci_dev`/相应对象）。模块同时把自己要用的资源（PCI 配置空间、BAR 区大小、MSI-X 向量数）映射到之前你用 grub `memmap` 预留的那块物理内存里。
   * 结果：内核的 PCI 枚举/扫描会“看到”一个新的设备条目（虚拟的），并把它列入 `/sys/bus/pci/devices/0000:xx:xx.x`。

2. **内核 NVMe 驱动 probe 并绑定**

   * PCI 子系统在枚举到该设备后，会根据设备 class/ID 把它交给 NVMe 主机驱动（`nvme`）尝试 `probe`。
   * 驱动通过读取 PCI 配置空间和 BAR0（MMIO）来确认设备存在，并 ioremap(BAR0) 到内核虚拟地址，读出 NVMe 控制器寄存器（CAP, VS, etc.）。如果识别为 NVMe，驱动就把这个设备绑定为一个 `nvme` 控制器实例（`struct nvme_dev`）。

3. **驱动初始化 admin queue（主机端）**

   * NVMe 驱动在 host 端分配两块内存（host memory）：**Admin Submission Queue (ASQ)** 和 **Admin Completion Queue (ACQ)**，并把它们的物理地址（或 IOVA）写入控制器寄存器 `ASQ` 和 `ACQ`，并在 `AQA` 写入队列大小信息，然后把 `CC`[EN] 置 1 来启动控制器。
   * 在真实设备上，这些写操作是写到 BAR0 的寄存器；在虚拟设备上，写到 BAR0 会落在 `nvmevirt` 模块管理的那段 memmap 区，模块能立即看到这些寄存器变化。

---

# 2) PCI / NVMe 的关键寄存器与内存区域（快速清单）

* **PCI 配置空间**：Vendor ID, Device ID, BAR 数、MSI-X capability 等（虚拟设备在 config space 上呈现的值决定内核会加载哪个驱动）。
* **BAR0 (MMIO)**：映射 NVMe 控制器寄存器区，包含下面 NVMe 寄存器：

  * `CAP` (Controller Capabilities)
  * `VS` (Version)
  * `CC` (Controller Configuration)
  * `CSTS` (Controller Status)
  * `AQA` (Admin Queue Attributes)
  * `ASQ` (Admin Submission Queue Base Address)
  * `ACQ` (Admin Completion Queue Base Address)
  * Doorbell 区（每个队列有写 Doorbell 寄存器：写 Tail 值以通知设备）
* **Host Memory**：ASQ/ACQ 的实际缓冲区（driver 分配），以及后续 I/O 的 PRP/SGL 指向的数据缓冲区。
* **Reserved memmap 区（你预留的物理页）**：nvmevirt 把这块空间分成“寄存器空间 + 后端数据区 + 控制结构”，因此模块能在内存里直接访问或 memcpy 主机的缓冲区（实现模拟 DMA）。

---

# 3) 发送 `IDENTIFY`（Admin Identify）的完整流程 — 主机驱动层到虚拟设备再返回

我分成“主机（driver）动作” → “虚拟设备（nvmevirt）动作” → “主机处理完成”的阶段来描述。

## A. 主机（Linux nvme 驱动 / nvme-cli）准备并提交 Identify

1. **构造 Admin Identify 命令**

   * `IDENTIFY` 是一个 NVMe Admin opcode（Admin 命令集，opcode = 0x06）。驱动或 nvme-cli 通过内核 nvme 用户接口（ioctl / nvme-cli）构造一个 Admin command structure，里面会包含 opcode、nsid（0 for controller identify）、cdw10/cdw11 等，以及数据传输的描述（PRP1/PRP2 或 SGL）。
   * 驱动为数据缓冲区（要接收 Identify 返回的 4KB 信息）分配一个物理页面，并取得其物理地址（如果使用 IOMMU，就取得 IOVA）。

2. **把命令放到 Admin Submission Queue (ASQ)**

   * 驱动把命令填入 ASQ 中的下一个 slot（内存中的结构），并用 `wmb()` 等内存写屏障保证命令已写入主存。
   * 然后驱动写 **Submission Queue Tail Doorbell**（写入新的 tail 值）到 BAR0 的 doorbell 寄存器，**通知设备：有新命令**。这是主机到设备的通知关键动作。

## B. 设备（nvmevirt）看到命令并执行

3. **检测到 Doorbell 写入**

   * 在真实硬件中，设备会在收到 doorbell 后读取 host 的 ASQ 内存；在 `nvmevirt` 模块里，模块要么轮询 ASQ 的 tail（spin loop），要么通过写门铃（它可以 hook 到写门铃的 mmio-write）被告知。nvmevirt 实现中通常直接在 mmio write 回调里捕获 doorbell 写入。

4. **读取命令结构**

   * nvmevirt 从 ASQ 的 slot 中读取 NVMe Admin 命令数据结构，解析 opcode（看到是 Identify）、PRP1/PRP2（或 SGL）指向的物理地址、传输长度等。

5. **准备数据并“DMA”写入到 Host Buffer**

   * Identify 要返回 4096 字节（或 4096 * n）。在真实设备上，设备会根据 PRP 指向做 DMA，把 identify 数据写入 host physical pages。
   * 在你的虚拟实现中（nvmevirt），因为你已把一段 host 物理内存 `memmap` 给了模块，模块可以**直接把数据 memcpy 到 host 指定的物理地址**（不走真实 DMA）。如果 IOMMU 在作用，数据传输也要遵守 IOVA 映射。
   * NVMeIdentify 数据由虚拟控制器构造（填充制造商字符串、命名空间信息等）。

6. **写入 Completion Queue (ACQ)**

   * 模拟设备在 host 的 Completion Queue 中写入一个 completion entry（包括 command id、status 字段等），并通过写 Completion Doorbell 或设置 appropriate register 通知主机（或直接触发中断）。

7. **触发中断（MSI/MSI-X 或传统 INTx）**

   * 模拟设备会向内核“发起”一个 IRQ（虚拟设备调用内核 API 提交一个中断事件），结果内核会把这个中断分发给绑定此设备 IRQ 的 NVMe 驱动的中断处理程序（ISR）。

## C. 主机处理完成（从中断到上层返回）

8. **中断处理与读 Completion**

   * 内核的 NVMe 驱动的中断处理会读取 ACQ 中的 completion entry（通过 ioread / 或直接读内存），做必要的 memory barriers，确认 completion 是为哪条命令。
   * 驱动把 completion entry 的状态传回 NVMe core 层，NVMe core 根据 command id 找到等待该命令的上下文（blocking syscall、polling loop 或回调）。

9. **将结果返回给调用者**

   * 如果是同步 admin 请求（大多数 `nvme-cli id-ctrl` 的实现），驱动会把数据缓冲区地址返回给上层，ioctl 返回并把 identify buffer 的内容交给 nvme-cli，nvme-cli 打印/解析这些字段。

10. **清理与Doorbell更新**

    * 驱动会更新 Completion Queue head 或写 Completion Doorbell（通知设备可以复用该 CQ slot），并完成命令生命周期的清理。

---

# 4) 数据/同步细节（内存屏障、PRP/IOVA、CMB）

* **PRP (Physical Region Page)**：命令结构里的 PRP1/PRP2 指的是 Host 的物理页地址。虚拟设备要把数据写入这些地址。
* **内存屏障 (wmb/rmb)**：提交命令时主机要 `wmb()` 确保命令写入后再写 Doorbell；设备在读取命令时也要适当的读屏障确保读取一致。类似地，设备在写完 completion entry 后要发中断并保证内存可见性。
* **IOMMU**：如果系统启用了 IOMMU，主机 driver 通过 DMA API 做映射，虚拟设备若做 DMA 模拟需要使用 IOVA 地址或绕过 IOMMU（nvmevirt 的设计会考虑 IOMMU 情况）。
* **CMB (Controller Memory Buffer)**：一些实现支持 controller 的内存作为快速数据 path（你之前的 SPDK 例子里有用 CMB），nvmevirt 也可能支持在 memmap 区内直接把数据放到 CMB 区，从而免去 host memory 的两次拷贝。

---

# 5) 在你的系统上实际能观察/验证哪些点（命令）

下面这些命令/检查可以让你观察每一步是否按预期发生：

* **查看设备是否被内核识别并被 nvme 驱动绑定**

  ```bash
  lspci -v -s <device-bdf>
  ls /sys/bus/pci/devices/0000:xx:xx.x
  sudo nvme list
  ```

* **发 Identify 并看返回**

  ```bash
  sudo nvme id-ctrl /dev/nvme1
  sudo nvme id-ns /dev/nvme1n1
  ```

* **实时看内核日志（nvmevirt 模块打印）**

  ```bash
  sudo dmesg -w
  # 或在另一个终端运行命令，然后看 dmesg 输出是否出现 nvmevirt 对命令的日志
  ```

* **看中断与 completion 活动**

  ```bash
  cat /proc/interrupts | grep -i nvme
  sudo watch -n0.5 "cat /proc/interrupts | grep <your-irq>"
  ```

* **看 /proc/iomem 或 dmesg 的 memmap 信息，确认 memmap 区**

  ```bash
  cat /proc/iomem | grep -i 'Reserved\|System RAM'
  dmesg | grep -i memmap
  ```

---

# 6) 为什么虚拟设备看起来和真实设备几乎一样？

因为你把 **PCI 配置空间 + BAR/MMIO + doorbell + MSI-X + admin/IO queues** 都在内核层面完整地模拟／呈现给系统，系统的 NVMe 驱动照常按 NVMe 规范来做 probe、分配队列、提交命令、等待完成。虚拟模块只是在内部把“真实的物理 NAND / DMA”换成了“内存拷贝与软件处理”，其它路径一模一样，所以上层软件（nvme-cli、文件系统、IOBench）看不出差别（除了性能）。

---

# 7) 小结（一句话）

* **出现设备**：模块在 PCI 层“放置”了一个虚拟 PCI 设备（config space + BAR），内核 NVMe 驱动依据这些信息把它当成真实控制器来初始化。
* **发送 IDENTIFY**：驱动把 Identify 命令写入 Admin Submission Queue，写 doorbell；nvmevirt 捕获该 doorbell/读取命令，构造 identify 数据写到 host buffer（PRP 指向处），把 completion 写进 ACQ，并触发中断；驱动的 ISR 读取完成并把数据交回给用户态工具（nvme-cli）。

---

如果你想，我可以继续帮你做两件事（你选其一或两个都要）：

1. 把上面步骤和你当前 `nvmev` 的具体实现点对应起来（指出 `nvmev.ko` 里**哪个函数/回调**处理 doorbell、哪个结构是寄存器映射、哪个是数据后端），便于你阅读/调试源码。
2. 给出一套**调试命令序列**（按步骤运行），你可以边执行边观察 dmesg、/proc/interrupts、nvme list、以及 nvmevirt 模块输出，精确定位命令处理路径与延时点。

你想先看源码对应点（1）还是直接拿命令跑验证（2）？
