---
layout: lecture
title: "SPDK Environment Issue"
details:
date: 2025-10-13
ready: false
sync: true
tags: [env_issue]
syncdate: "{{ page.last_modified_at | date: '%Y-%m-%d' }}"
---

## 背景

在执行 SPDK 自带的依赖安装脚本时：

```bash
sudo ./scripts/pkgdep.sh
```

出现错误：

```
Error: Command '['/var/spdk/dependencies/pip/bin/python3', '-m', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
```

脚本执行到创建 Python 虚拟环境（`python3 -m venv`）这一步失败。

---

## 分析

SPDK 的安装脚本会自动执行：

```bash
python3 -m venv --upgrade-deps --system-site-packages /var/spdk/dependencies/pip
```

但我机器上安装过 **pyenv**，系统中同时存在两个 Python：
- `/usr/bin/python3`（系统自带 3.10）
- `~/.pyenv/versions/3.11.9/bin/python3`（pyenv 版本）

结果 `pkgdep.sh` 在 root 环境中混用了两个 Python，导致：
- `_posixsubprocess` 模块缺失  
- `ensurepip` 执行失败  
- pip 无法正确安装  

---

## 解决过程

清理旧环境

```bash
sudo rm -rf /var/spdk/dependencies/pip
sudo mkdir -p /var/spdk/dependencies
sudo chown -R $USER:$USER /var/spdk
```

手动创建虚拟环境并安装 pip

```bash
python3 -m venv --without-pip /var/spdk/dependencies/pip
source /var/spdk/dependencies/pip/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
deactivate
```

重新运行安装脚本

```bash
sudo ./scripts/pkgdep.sh
```

依赖安装成功，SPDK 环境正常。

---

## pyenv 卸载

```bash
pyenv deactivate 2>/dev/null || true
rm -rf ~/.pyenv
sed -i '/pyenv/d' ~/.bashrc ~/.profile ~/.bash_profile ~/.zshrc
exec $SHELL -l
which python3  # 应该输出 /usr/bin/python3
```

- SPDK 的脚本假设使用系统自带 Python；
- 不建议在 root 环境混用 pyenv；
- 遇到 `ensurepip` 报错时，手动创建虚拟环境最直接；
- 保持 `/usr/bin/python3` 为默认环境最稳。
