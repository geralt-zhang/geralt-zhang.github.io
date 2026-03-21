---
layout: lecture
title: "Docker 的实现原理"
date: 2026-02-14
ready: true
sync: true
syncdate: 2026-02-14
---

Docker 的实现原理是 Namespace 和 Cgroup，它是由 Linux 的 Container 发展而来的， 我理解容器技术大多用于隔离操作，一方面方便打包环境，再来也不容易污染主机。

Namespace 用于单独创建一份空间给进程使用，这份空间可以独立出来一部分的东西，比如 UTS (Unix Time-sharing System，在 Linux 中基本等同于 Hostname)、IPC、PID、Mount、User、Network 等等，它可以隔离一系列的系统资源，很多人会想到一个命令 `chroot`，就像 `chroot` 允许把当前目录变成根目录一样（被隔离开来的）。