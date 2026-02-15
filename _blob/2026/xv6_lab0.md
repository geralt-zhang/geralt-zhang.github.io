---
layout: lecture
title: "6.s081 Lab0"
date: 2026-01-09
ready: true
sync: true
syncdate: 2026-01-18
---

## 调试：

调试可以方便定位问题，由于使用 qemu 模拟硬件，因此启动 xv6 的调试需要通过 qemu-gdb，然后另一端 gdb 通过连接这个 qemu-gdb 运行的 kernel 来识别调试信息。

```bash
# 调试使用
make qemu-gdb CPUS=1

# 在另一个 shell session 执行以进行调试
gdb-multiarch
```

然而，要在 debug 时得心应手却并不那么简单，用户态的 main 处在虚拟地址 0，因此 b main 会造成 gdb 多次卡在 main 断点处，但只有第一次 b main 才是真正的进入函数。user 程序和 kernel 没法同时在 gdb 处理，需要使用 file kernel/kernel 和 file user/_xxx 在它们之间转换，即在加载到某一系统调用后，需要 file kernel/kernel，再在对应系统调用打断点。

## Lab: Xv6 and Unix utilities

这个 lab 学一些系统调用，其中很多函数可以通过作业页面给出的那些 user app 的使用方式模仿，主要是要理解 user - kernel 的转换。

## 1. Sleep

> 程序需要接收参数，使用 argc 和 argv，c 是数量，v 是不定长数组，不太清楚这部分的原理，也许是从 shell 读取，sleep 通过系统调用 sleep 带上时间戳，其中 time 需要经过 atoi 将 string 转为 int，系统调用 sleep 的实现在 sys_sleep()，把当前进程挂到 chan 上状态设为 SLEEPING

## ref：

[https://mit-public-courses-cn-translatio.gitbook.io/mit6-s081](https://mit-public-courses-cn-translatio.gitbook.io/mit6-s081)

[https://pdos.csail.mit.edu/6.S081/2021/](https://pdos.csail.mit.edu/6.S081/2021/)

[https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf](https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf)

