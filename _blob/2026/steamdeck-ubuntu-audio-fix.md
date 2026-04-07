---
layout: lecture
title: "Steam Deck安装Ubuntu后无声问题解决全记录"
date: 2026-04-07
ready: true
sync: true
tags: ["Linux"]
---

## 问题描述

最近在Steam Deck上安装了Ubuntu系统，安装完成后发现一个奇怪的问题：系统完全没有声音。无论是播放音乐、视频还是系统提示音，都听不到任何声音。系统显示音频设备正常识别，音量设置也正常，但就是没有声音输出。

## 问题根源

经过深入排查，发现问题的根源在于Steam Deck特殊的音频硬件架构：

1. **特殊的音频芯片**：Steam Deck使用了AMD ACP5x音频协处理器，配合Cirrus Logic CS35L41音频放大器
2. **DSP固件依赖**：音频输出需要加载特定的DSP固件和配置
3. **复杂的路由配置**：音频信号需要经过特定的DSP路由才能正确输出

简单来说，Steam Deck的音频不是简单的"声卡驱动"，而是一个需要特定配置的音频处理系统。

## 解决方案

### 1. 检查音频服务状态

首先确认音频服务是否正常运行：

```bash
systemctl --user status pipewire pipewire-pulse wireplumber
```

如果服务没有运行，需要启动它们：

```bash
systemctl --user start pipewire pipewire-pulse wireplumber
```

### 2. 检查音频设备

查看系统识别到的音频设备：

```bash
pactl list sinks short
aplay -l
```

正常情况下应该能看到类似这样的输出：
- `acp5x` 音频卡（Steam Deck内置音频）
- `HD-Audio Generic`（HDMI音频）

### 3. 关键修复步骤

这是解决问题的核心部分，需要手动配置ALSA混音器：

```bash
# 设置数字音量
amixer -c 2 sset 'Digital' 192

# 设置模拟PCM音量
amixer -c 2 sset 'Left Analog PCM' 17
amixer -c 2 sset 'Right Analog PCM' 17

# 设置数字PCM音量
amixer -c 2 sset 'Left Digital PCM' 870
amixer -c 2 sset 'Right Digital PCM' 870

# 启用耳机/扬声器开关
amixer -c 2 sset 'Headphone' on
amixer -c 2 sset 'Headphone' 2

# 配置DSP路由（关键！）
amixer -c 2 sset 'Left DSP RX1 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX1 Source' 'ASPRX2'
amixer -c 2 sset 'Left DSP RX2 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX2 Source' 'ASPRX2'
amixer -c 2 sset 'Left PCM Source' 'DSP'
amixer -c 2 sset 'Right PCM Source' 'DSP'
```

### 4. 配置PulseAudio

设置默认音频输出设备：

```bash
pactl set-default-sink alsa_output.pci-0000_04_00.5-platform-acp5x_mach.0.HiFi__hw_acp5x_1__sink
pactl set-sink-volume @DEFAULT_SINK@ 100%
pactl set-sink-mute @DEFAULT_SINK@ 0
```

### 5. 测试音频

使用以下命令测试音频是否正常工作：

```bash
# 简单测试
speaker-test -t sine -f 440 -c 2 -l 1

# 播放测试文件
paplay /usr/share/sounds/alsa/Front_Center.wav
```

## 一键修复脚本

为了方便以后使用，我创建了一个一键修复脚本：

```bash
#!/bin/bash
echo "=== Steam Deck Audio Fix ==="

# 停止音频服务
pkill -9 pipewire pipewire-pulse wireplumber 2>/dev/null
sleep 2

# 应用ALSA配置
echo "Applying ALSA mixer settings..."
amixer -c 2 sset 'Digital' 192
amixer -c 2 sset 'Left Analog PCM' 17
amixer -c 2 sset 'Right Analog PCM' 17
amixer -c 2 sset 'Left Digital PCM' 870
amixer -c 2 sset 'Right Digital PCM' 870
amixer -c 2 sset 'Headphone' on
amixer -c 2 sset 'Headphone' 2
amixer -c 2 sset 'Mic' 252
amixer -c 2 sset 'Frontend PGA' 27

# 设置DSP路由
echo "Configuring DSP routing..."
amixer -c 2 sset 'Left DSP RX1 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX1 Source' 'ASPRX2'
amixer -c 2 sset 'Left DSP RX2 Source' 'ASPRX1'
amixer -c 2 sset 'Right DSP RX2 Source' 'ASPRX2'
amixer -c 2 sset 'Left PCM Source' 'DSP'
amixer -c 2 sset 'Right PCM Source' 'DSP'

# 重启音频服务
echo "Restarting audio services..."
systemctl --user start pipewire pipewire-pulse wireplumber
sleep 3

# 设置PulseAudio
echo "Configuring PulseAudio..."
pactl set-default-sink alsa_output.pci-0000_04_00.5-platform-acp5x_mach.0.HiFi__hw_acp5x_1__sink
pactl set-sink-volume @DEFAULT_SINK@ 100%
pactl set-sink-mute @DEFAULT_SINK@ 0

echo "=== Fix applied ==="
echo "Try playing audio now."
```

将上述脚本保存为 `fix_steamdeck_audio.sh`，然后运行：
```bash
chmod +x fix_steamdeck_audio.sh
./fix_steamdeck_audio.sh
```

## 技术原理详解

### 为什么需要手动配置？

Steam Deck的音频系统与普通PC不同：

1. **音频协处理器**：使用AMD ACP5x作为音频协处理器，而不是传统的HD Audio
2. **智能放大器**：使用Cirrus Logic CS35L41，这是一个需要DSP固件的智能放大器
3. **复杂路由**：音频信号需要经过：CPU → ACP5x → DSP处理 → CS35L41放大器 → 扬声器

### 关键配置项说明

- **DSP路由**：`ASPRX1` 和 `ASPRX2` 是音频串行端口的接收通道，必须正确配置才能让音频信号流向放大器
- **PCM源**：必须设置为 `DSP` 而不是 `ASP`，这样才能使用DSP处理后的音频
- **音量层级**：数字音量、模拟音量、数字PCM音量需要特定的值才能正常工作

### 永久配置方案（重启不失效果）

为了让配置在重启后依然有效，有以下几种方法：

#### 方案一：创建systemd用户服务（推荐）

1. **创建修复脚本**：
   ```bash
   # 创建脚本文件
   cat > ~/.local/bin/steamdeck-audio-fix.sh << 'EOF'
   #!/bin/bash
   echo "Applying Steam Deck audio fix..."
   sleep 2
   amixer -c 2 sset "Digital" 192
   amixer -c 2 sset "Left Analog PCM" 17
   amixer -c 2 sset "Right Analog PCM" 17
   amixer -c 2 sset "Left Digital PCM" 870
   amixer -c 2 sset "Right Digital PCM" 870
   amixer -c 2 sset "Headphone" on
   amixer -c 2 sset "Headphone" 2
   amixer -c 2 sset "Mic" 252
   amixer -c 2 sset "Frontend PGA" 27
   amixer -c 2 sset "Left DSP RX1 Source" "ASPRX1"
   amixer -c 2 sset "Right DSP RX1 Source" "ASPRX2"
   amixer -c 2 sset "Left DSP RX2 Source" "ASPRX1"
   amixer -c 2 sset "Right DSP RX2 Source" "ASPRX2"
   amixer -c 2 sset "Left PCM Source" "DSP"
   amixer -c 2 sset "Right PCM Source" "DSP"
   sleep 1
   pactl set-default-sink alsa_output.pci-0000_04_00.5-platform-acp5x_mach.0.HiFi__hw_acp5x_1__sink 2>/dev/null || true
   pactl set-sink-volume @DEFAULT_SINK@ 100% 2>/dev/null || true
   pactl set-sink-mute @DEFAULT_SINK@ 0 2>/dev/null || true
   echo "Steam Deck audio fix applied"
   EOF
   
   # 添加执行权限
   chmod +x ~/.local/bin/steamdeck-audio-fix.sh
   ```

2. **创建systemd服务**：
   ```bash
   # 创建服务文件
   mkdir -p ~/.config/systemd/user/
   cat > ~/.config/systemd/user/steamdeck-audio-fix.service << EOF
   [Unit]
   Description=Fix Steam Deck audio configuration
   After=pipewire.service pipewire-pulse.service wireplumber.service
   Wants=pipewire.service pipewire-pulse.service wireplumber.service
   
   [Service]
   Type=oneshot
   RemainAfterExit=yes
   ExecStart=/home/\$USER/.local/bin/steamdeck-audio-fix.sh
   ExecStop=/bin/true
   
   [Install]
   WantedBy=default.target
   EOF
   
   # 启用服务
   systemctl --user daemon-reload
   systemctl --user enable --now steamdeck-audio-fix.service
   ```

#### 方案二：创建ALSA UCM配置文件

创建ALSA Use Case Manager配置文件：
```bash
sudo mkdir -p /usr/share/alsa/ucm2/conf.d/steamdeck/
sudo tee /usr/share/alsa/ucm2/conf.d/steamdeck/steamdeck.conf << 'EOF'
# Steam Deck ACP5x audio configuration
SectionVerb {
	EnableSequence [
		cdev "hw:acp5x"
		cset "name='Digital Playback Volume' 192"
		cset "name='Left Analog Playback Volume' 17"
		cset "name='Right Analog Playback Volume' 17"
		cset "name='Left Digital Playback Volume' 870"
		cset "name='Right Digital Playback Volume' 870"
		cset "name='Headphone Playback Switch' on"
		cset "name='Headphone Playback Volume' 2"
		cset "name='Mic Capture Volume' 252"
		cset "name='Frontend PGA Volume' 27"
		cset "name='Left DSP RX1 Source' ASPRX1"
		cset "name='Right DSP RX1 Source' ASPRX2"
		cset "name='Left DSP RX2 Source' ASPRX1"
		cset "name='Right DSP RX2 Source' ASPRX2"
		cset "name='Left PCM Source' DSP"
		cset "name='Right PCM Source' DSP"
	]
}
EOF
```

#### 方案三：创建udev规则

创建udev规则在设备连接时自动配置：
```bash
sudo tee /etc/udev/rules.d/91-steamdeck-audio.rules << 'EOF'
# Steam Deck audio fix
ACTION=="add", SUBSYSTEM=="sound", ATTRS{vendor}=="0x1022", ATTRS{device}=="0x15e2", RUN+="/usr/local/bin/steamdeck-audio-fix.sh"
EOF

sudo udevadm control --reload-rules
```

#### 方案四：一键安装脚本（推荐）

下载并运行一键安装脚本：
```bash
# 下载脚本
wget https://raw.githubusercontent.com/zhehuaf/steamdeck-audio-fix/main/steamdeck-audio-permanent-fix.sh

# 运行脚本（需要sudo权限）
chmod +x steamdeck-audio-permanent-fix.sh
sudo ./steamdeck-audio-permanent-fix.sh
```

或者手动创建脚本：
```bash
# 创建一键安装脚本
cat > steamdeck-audio-permanent-fix.sh << 'EOF'
#!/bin/bash
# Steam Deck Audio Permanent Fix Script
# ... (脚本内容见上文)
EOF

chmod +x steamdeck-audio-permanent-fix.sh
sudo ./steamdeck-audio-permanent-fix.sh
```

#### 验证配置

重启后验证配置是否生效：
```bash
# 检查systemd服务状态
systemctl --user status steamdeck-audio-fix.service

# 检查ALSA配置
amixer -c 2 contents | grep -E "(Digital|Analog PCM|Digital PCM|DSP RX|PCM Source)"

# 测试音频
speaker-test -t sine -f 440 -c 2 -l 1

# 查看日志
journalctl --user -u steamdeck-audio-fix.service -f
```

## 常见问题排查

### 如果修复后仍然没有声音

1. **检查物理音量按钮**：Steam Deck侧面的音量按钮可能被静音
2. **使用图形界面检查**：运行 `pavucontrol` 查看输出设备选择
3. **检查内核日志**：`sudo dmesg | grep -i audio` 查看是否有错误信息
4. **验证固件加载**：检查CS35L41固件是否正确加载

### 耳机没有声音

如果扬声器有声音但耳机没有：
```bash
# 切换到耳机输出
pactl set-default-sink alsa_output.pci-0000_04_00.5-platform-acp5x_mach.0.HiFi__hw_acp5x_0__sink
```

### HDMI音频没有声音

如果需要使用HDMI音频：
```bash
# 切换到HDMI输出
pactl set-default-sink alsa_output.pci-0000_04_00.1.hdmi-stereo-extra2
```

## 总结

Steam Deck在Ubuntu上的音频问题主要是由于其特殊的硬件架构导致的。与普通PC不同，它需要手动配置DSP路由和音量层级才能正常工作。通过本文提供的解决方案，应该能够解决大多数音频无声的问题。

这个问题也反映了Linux硬件支持的现状：虽然内核驱动支持很多硬件，但一些特殊设备仍然需要手动配置才能发挥全部功能。希望随着Steam Deck的普及，这些配置能够被更好地集成到发行版中。

## 参考资料

1. [ALSA UCM配置文档](https://www.alsa-project.org/wiki/Use_Case_Manager)
2. [PipeWire音频系统](https://pipewire.org/)
3. [Steam Deck硬件规格](https://www.steamdeck.com/tech)
4. [CS35L41放大器数据手册](https://www.cirrus.com/products/cs35l41/)

---
*本文基于实际故障排除经验编写，测试环境：Steam Deck + Ubuntu 24.04 LTS*
*最后更新：2026年4月7日*