---
layout: lecture
title: "6.s081 lab0 util"
date: 2026-01-09
ready: true
sync: true
syncdate: 2026-01-18
tags: 6.s081
---
GCC (GNU Compiler Collection) 和  LLVM 往往代表两种索引代码的方式，GCC 是一个编译器，它不会关心怎么跳转代码，LLVM 则代表一种前后段处理的方式，其搭配 Clang 实现 LSP（Language Server Protocol，语言服务器协议），我的理解它通过编译后的结果（语法和语义信息）来指导编辑器跳转代码符号。

虽然 LSP 很厉害，但它搭配 GCC 有一些莫名其妙的警告和 ERR，这些报错应当是 GCC 与 LLVM 的差异导致的，而不用 LSP 的话，可以用 GCC + Ctags / Cscope 这种方式来索引代码，这本质上是通过正则搜索来实现的，因此它往往没那么精准，以下是通过配置 NVim 插件实现的 Cscope 功能跳转。

```bash
ctags -R
cscope -Rbq
```

<script src="https://asciinema.org/a/UW1ZUHRzyvfKqo6j.js" id="asciicast-UW1ZUHRzyvfKqo6j" async="true"></script>

Clangd 是基于 LLVM 的语言服务器，可以让编辑器理解 C/C++ 代码，提供补全、跳转、查找引用和错误提示等功能。但把它用到 XV6 教学操作系统上就没那么简单。XV6 是为教学设计的 RISC-V 内核，它有自己的头文件、自定义的库函数，还有一些早期 C 的写法，这些在现代编译器眼里往往不规范。

Clangd 默认理解的是宿主机环境和标准 C，而 XV6 既有内核代码也有用户程序，还有工具链本身，这些都不在它熟悉的世界里。加上 XV6 的 Makefile 不会生成 Clangd 需要的编译数据库，直接用的话会报一堆莫名其妙的错误。要让 Clangd 在 XV6 项目里顺利工作，必须做一些配置。

## 配置 Clangd

首先安装 Bear，这是一个用来生成 `compile_commands.json` 的工具：

```
sudo apt install bear
```

安装 Clangd，可以直接用包管理器，也可以下载 LLVM 官方版本，安装完成后，可以用 `clangd --version` 检查版本。
```
sudo apt install clangd-18
```

进入 XV6 根目录，然后用 Bear 包裹 Make 命令生成编译数据库：

```
bear -- make
```

生成的 `compile_commands.json` 文件会记录项目里每个源文件的编译选项，包括 include 路径、宏定义和编译器参数，这样 Clangd 就能正确理解代码。

然而由于 xv6 的代码编写风格较古老，Clangd 解析经常报红，搞了一晚上也没搞好，因此我不再使用 Clangd 的语法检测功能，只使用它的跳转功能，在 `.clangd` 文件中配置如下，可禁用大部分警告。

```yaml
Diagnostics:
  Suppress: "*"
```

但如果 clangd 本身因为太多崩掉，仍然会在文件开始报 `Too many fails xxx`，要禁用这些警告，还需要在 ~/.config/nvim/init.lua 里配置一下。

```bash
vim.api.nvim_create_autocmd('LspAttach', {
  callback = function(args)
    local client = args.data and vim.lsp.get_client_by_id(args.data.client_id)
    if client and client.name == 'clangd' then vim.diagnostic.enable(false, { bufnr = args.buf }) end
  end,
})
```

## GDB 调试步骤

调试 XV6 需要使用 QEMU 模拟器的调试功能。基本步骤如下：

```bash
# 在一个终端启动调试模式
make qemu-gdb CPUS=1

# 在另一个终端连接调试器
gdb-multiarch
```

用户态程序的 `main` 函数位于虚拟地址 0，使用 `b main` 设置断点时会导致 GDB 多次在同一位置停止。只有第一次是真正的函数入口，后续停止是地址重复导致的。

XV6 的用户程序和内核程序需要在 GDB 中分别加载：

```bash
# 切换到内核调试
file kernel/kernel

# 切换到用户程序调试  
file user/_程序名
```

每次系统调用后需要重新加载对应的调试符号，然后在目标位置设置断点。建议专注于调试用户态或内核态中的一个，避免频繁切换。

## Lab: Xv6 and Unix Utilities

当用户程序调用 user/sleep.c 时，首先通过 argc 和 argv 处理命令行参数。由于 shell 传递的所有参数均为字符串，程序需要调用 atoi 函数将其转换为整数。随后，该整数被作为参数传递给 sleep 系统调用。此时，执行流穿过特权级边界进入内核，由 sys_sleep 函数进行响应。在内核函数内部，首先会获取全局的 tickslock 锁，并通过一个 while 循环不断检测当前系统时间 ticks 与目标时间的差值。

在循环体内，内核会持续检查当前进程是否收到了杀掉请求。如果进程尚未被杀死，则会进入核心的 sleep 函数流程。这里的锁处理逻辑是理解内核并发控制的关键。进入 sleep 后，内核会先获取当前进程 p 的进程锁 p->lock，随后再释放之前持有的全局 tickslock。这种“先拿进程锁，再放全局锁”的顺序是为了严格避免死锁。如果内核不释放全局锁就进入调度状态，时钟中断处理函数将因为无法获取该锁而无法更新系统 ticks，从而导致休眠进程因等待条件永远无法达成而陷入永久阻塞。

为什么必须在释放全局锁之前先抢占进程锁呢？这涉及到了著名的丢失唤醒（Lost Wakeup）问题。在内核中，wakeup 函数同样需要竞争进程的锁来修改其状态。如果睡眠流程在设置进程状态为 SLEEPING 之前就释放了所有的同步保护，那么时钟中断可能在此时介入并调用 wakeup。由于此时进程状态仍为 RUNNING，唤醒逻辑会将其跳过。

对于基于时钟的休眠，跳过一次唤醒或许可以通过下一次时钟中断补救，但对于等待磁盘 IO 或网络信号的任务，这种丢失是致命的。硬件产生的电信号通常不会重复触发，一旦错过当下的唤醒信号，进程将永远无法从睡眠队列中脱离。因此，通过进程锁的持有，内核确保了“检查条件、设置状态、进入调度”这三个动作对于唤醒逻辑是原子化的。在后续对 sched 函数的分析中，我们将进一步探讨这种锁的持有状态如何在进程上下文切换中被最终交付给调度器。


- [MIT 6.S081 课程官网](https://pdos.csail.mit.edu/6.S081/2021/)
- [XV6 手册](https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf)
- [课程中文翻译](https://mit-public-courses-cn-translatio.gitbook.io/mit6-s081)
- [Clangd 官方文档](https://clangd.llvm.org/)
- [QEMU 调试指南](https://www.qemu.org/docs/master/system/debugging.html)

