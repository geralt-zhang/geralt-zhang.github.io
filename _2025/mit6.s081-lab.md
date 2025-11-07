---
layout: lecture
title: "mit6.s081 labs"
details:
date: 2025-10-23
ready: true
sync: true
syncdate: 2025-10-23
---

## 🧭 一、GDB 的使用与思维方式

在操作系统开发中，调试是理解的开始。  
编写内核代码不像写普通用户程序：你没有标准输出、没有 printf、没有文件系统能帮你写日志。  
当陷入系统挂起或 panic 时，唯一可靠的工具就是 GDB（GNU Debugger）。

### 🧩 GDB 帮助你回答六个关键问题：

1. **它现在卡在哪？**  
   使用 `bt`（backtrace）命令打印当前的调用栈，帮助你确定程序运行到哪一步被卡住。  
   栈信息展示了函数的调用路径，是排查逻辑错误的第一步。

2. **它在执行哪一行？**  
   使用 `info line` 或 `list` 命令，可以查看当前 PC 对应的源代码。  
   当内核陷入中断或页错误时，这一步非常关键。

3. **它在用哪些数据？**  
   使用 `info locals`、`info args`、`p var` 等命令，查看当前函数的变量值与寄存器状态。  
   在 xv6 中，许多 bug 来自结构体指针被误写、页表项错位等，这些都可在这里发现。

4. **为什么它走到这里？**  
   使用条件断点 (`break if condition`) 或监视点 (`watch var`)，追踪变量何时被修改。  
   这对调试内存分配器和同步原语尤为重要。

5. **我能重现吗？**  
   用 `run < input` 或者在 QEMU 中重启指定测试程序，验证问题是否稳定重现。  
   这可以帮助你判断是偶发竞争条件还是确定性 bug。

6. **如果我改变量呢？**  
   使用 `set var = xxx` 可以修改运行时变量。  
   例如，你可以强制把 `proc->state` 改为 `RUNNING` 来观察后续调度行为。

---

### ⚙️ GDB 与 QEMU 的配合

xv6 提供 `make qemu-gdb`，它启动 QEMU 并开放一个 GDB 远程端口（通常是 `localhost:26000`）。  
然后你可以在另一个终端中运行：

```bash
gdb-multiarch kernel/kernel
(gdb) target remote localhost:26000
(gdb) symbol-file kernel/kernel
```