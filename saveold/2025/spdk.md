---
layout: lecture
title: "SPDK Leanring"
details:
date: 2025-09-29
ready: false
sync: true
tags: [learan]
syncdate: 2025-09-29
---

## 什么是 The Storage Performance Development Kit (SPDK) ？

介绍：<https://spdk.io/doc/about.html> 

Intel 研发的用户态的 NVMe 驱动

1. 用户空间避免零拷贝

2. 轮询硬件降低延迟

3. 避免IO锁，依赖消息传递

## NVMe Driver of SPDK

它可以直接映射一个应用程序，使程序与 NVMe SSD 连接，无线程的零拷贝数据传输，并且是被动的等待应用程序调用接口，没有主动操作

该库通过将 PCI BAR 直接映射到本地进程并执行 MMIO 来控制 NVMe 设备

I/O 通过队列对异步提交，一般流程与 Linux 的 libaio 并不完全不同

> Q: PCI BAR、MMIO、libaio ?
>
> A: 

