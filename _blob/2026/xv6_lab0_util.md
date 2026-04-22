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

安装 Clangd，可以直接用包管理器，也可以下载 LLVM 官方版本：
> 安装完成后，可以用 `clangd --version` 检查版本。

```
sudo apt install clangd-16
```

进入 XV6 根目录，然后用 Bear 包裹 Make 命令生成编译数据库：

```
bear -- make
```

生成的 `compile_commands.json` 文件会记录项目里每个源文件的编译选项，包括 include 路径、宏定义和编译器参数，这样 Clangd 就能正确理解代码。

然而由于 xv6 的代码编写风格较古老，clangd 解析经常报红，搞了一晚上也没搞好，因此我不再使用 clangd 的语法检测功能，只使用它的跳转功能，在 `.clangd` 文件中配置如下，可禁用大部分警告。

```yaml
Diagnostics:
  Suppress: "*"
```

## GDB 调试步骤

调试 XV6 需要使用 QEMU 模拟器的调试功能。基本步骤如下：

```bash
# 在一个终端启动调试模式
make qemu-gdb CPUS=1

# 在另一个终端连接调试器
gdb-multiarch
```

调试过程中需要注意以下几个问题：

### 断点设置问题

用户态程序的 `main` 函数位于虚拟地址 0，使用 `b main` 设置断点时会导致 GDB 多次在同一位置停止。只有第一次是真正的函数入口，后续停止是地址重复导致的。

### 用户态和内核态切换

XV6 的用户程序和内核程序需要在 GDB 中分别加载：

```bash
# 切换到内核调试
file kernel/kernel

# 切换到用户程序调试  
file user/_程序名
```

每次系统调用后需要重新加载对应的调试符号，然后在目标位置设置断点。建议专注于调试用户态或内核态中的一个，避免频繁切换。

## Lab: Xv6 and Unix Utilities

这个实验主要学习系统调用的使用。很多函数的实现可以参考作业页面提供的用户程序示例，重点是理解用户态和内核态之间的转换过程。

## 1. Sleep 调用

程序需要接收命令行参数，使用 `argc` 和 `argv` 处理。`argc` 是参数数量，`argv` 是参数数组。参数通过 shell 传递给程序。

`user/sleep.c` 程序的实现步骤：

1. 使用 `atoi` 将字符串参数转换为整数时间
2. 调用系统调用 `sleep()` 传入时间参数
3. 系统调用 `sys_sleep()` 将当前进程状态设置为 SLEEPING 并挂起到等待队列
4. 时间到达后进程被唤醒

这很简单，但我想知道 Kernel 在这期间都做了什么，首先会走到 `sys_sleep()` 这个系统调用。

```c
uint64 sys_sleep(void)
{
	int n;	// times from user/sleep.c
	uint ticks0;

	if (argint(0, &n) < 0)
		return -1;
	acquire(&tickslock);
	ticks0 = ticks;	// global time counter
	while (ticks - ticks0 < n) {	// sleep until > times
		if (myproc()->killed) {
			release(&tickslock);
			return -1;
		}
		sleep(&ticks, &tickslock);
	}
	release(&tickslock);
	return 0;
}
```

其中 `tickslock` 是一个自旋锁，专门用来保护全局变量 `ticks`，这个变量是 timer interrupt 的计数，并且 timer interrupt 是固定频率触发的，类似玩游戏时候的“帧”概念，真实时间 = ticks × 每个 tick 的时间长度。

真正执行 sleep 的逻辑在 `kernel/proc.c` 的 `sleep()` 中。

```c
// Atomically release lock and sleep on chan.
// Reacquires lock when awakened.
void sleep(void *chan, struct spinlock *lk)
{
	struct proc *p = myproc();

	// Must acquire p->lock in order to
	// change p->state and then call sched.
	// Once we hold p->lock, we can be
	// guaranteed that we won't miss any wakeup
	// (wakeup locks p->lock),
	// so it's okay to release lk.

	acquire(&p->lock); //DOC: sleeplock1
	release(lk);

	// Go to sleep.
	p->chan = chan;
	p->state = SLEEPING;

	sched();

	// Tidy up.
	p->chan = 0;

	// Reacquire original lock.
	release(&p->lock);
	acquire(lk);
}
```



## 参考资源

- [MIT 6.S081 课程官网](https://pdos.csail.mit.edu/6.S081/2021/)
- [XV6 手册](https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf)
- [课程中文翻译](https://mit-public-courses-cn-translatio.gitbook.io/mit6-s081)
- [Clangd 官方文档](https://clangd.llvm.org/)
- [QEMU 调试指南](https://www.qemu.org/docs/master/system/debugging.html)

