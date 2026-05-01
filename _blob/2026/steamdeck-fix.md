---
layout: lecture
title: "Steam Deck无声问题"
date: 2026-04-07
ready: false
sync: true
tags: ["Linux"]
---

在使用 Steam Deck 安装 Ubuntu 或 Arch Linux 等非 SteamOS 系统时，扬声器完全没有声音。这并非简单的声卡驱动缺失，而是由其特殊的硬件架构决定的。

## 核心概念：什么是 DSP、ASP 与路由

要理解 Steam Deck 的音频，必须先拆解其内部的三个核心术语：

1. DSP（Digital Signal Processor）：数字信号处理器。你可以把它想象成一个内置的调音室。Steam Deck 的扬声器功率较大且体积受限，为了防止爆音并提升音质，所有的音频信号在传给喇叭之前，必须经过 DSP 进行动态范围压缩和均衡处理。如果 DSP 没工作，信号就无法抵达下一站。

2. ASP（Audio Serial Port）：音频串行端口。这是数据传输的传送带，负责在 AMD 处理器的计算核心与音频硬件之间搬运原始采样数据。

3. 路由（Routing）：这是音频信号的地图。在普通电脑上，音频路径是固定的；但在 Steam Deck 上，信号路径是可编程的。你需要明确告诉硬件：信号从 ASP 传送带出来后，进入 DSP 调音室的哪扇门，最后再从哪个出口送到放大器。



## 问题根源：为什么没有声音

Steam Deck 使用了 AMD ACP5x 音频协处理器和 Cirrus Logic CS35L41 智能放大器。在标准的 Linux 内核驱动下，系统能识别到声卡硬件，但却不知道如何正确配置上述的路由。

问题通常出在以下两点：
- 阀门未开：音频放大器的保护开关和增益通道默认处于静音或关闭状态。
- 路径中断：原始音频信号走到了 ASP 接口就停止了，没有指令引导它们进入 DSP 进行处理，导致放大器接收不到任何有效信号。

## 修复步骤：如何接通音频路径

修复的核心在于通过 ALSA 工具手动重建信号路由并开启增益。

```bash
1. 确认音频服务
首先确保 PipeWire 或 PulseAudio 及其调度器 WirePlumber 正在运行，它们负责处理软件层的音频流：
systemctl --user restart pipewire pipewire-pulse wireplumber

2. 配置数字路由
这一步是告诉硬件将 ASP 的数据流导入 DSP：
amixer -c 2 sset 'Left DSP RX1 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX1 Source' 'ASPRX2'
amixer -c 2 sset 'Left DSP RX2 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX2 Source' 'ASPRX2'

3. 指定 PCM 源
明确让系统输出经过 DSP 处理后的声音：
amixer -c 2 sset 'Left PCM Source' 'DSP'
amixer -c 2 sset 'Right PCM Source' 'DSP'

4. 开启增益与开关
最后，拧开音量的“数字阀门”并合上硬件开关：
amixer -c 2 sset 'Digital' 192
amixer -c 2 sset 'Left Digital PCM' 870
amixer -c 2 sset 'Right Digital PCM' 870
amixer -c 2 sset 'Headphone' on
amixer -c 2 sset 'Headphone' 2
```


## 自动化建议

由于这些设置存储在硬件寄存器中，重启系统后通常会重置。为了永久解决，将上述命令写入一个脚本文件，并利用 systemd 用户服务或系统的启动管理器在开机时自动运行。

通过理解 DSP 与路由的概念，会发现 Steam Deck 的音频系统更像是一套软件定义的专业音响设备，而不仅仅是一个插电即用的声卡。这种设计虽然增加了配置难度，但也为在 Linux 下进行更深度的音频定制提供了可能。
