# SSD Log Analyzer

一个专门用于分析Test Log和SSD FW Log的工具集，帮助识别bug根因并提供源码查找功能。

## 功能特性

- **自动日志解析**：支持Test Log、SSD FW Log、Kernel Log等多种日志格式
- **智能模式匹配**：内置常见SSD错误模式和bug模式识别
- **源码查找**：遇到可疑打印时自动在源码中查找对应位置
- **根因分析**：基于模式匹配和统计分析识别bug根因
- **多格式报告**：支持HTML、Markdown、JSON、文本格式报告
- **可扩展配置**：支持自定义日志模式和bug模式

## 快速开始

### 安装依赖

```bash
# 运行安装脚本
./scripts/install_dependencies.sh
```

### 基本使用

```bash
# 分析单个日志文件
python scripts/log_parser.py -f /path/to/test.log

# 分析多个日志文件
python scripts/log_parser.py -f log1.log log2.log -o report.html

# 启用源码查找
python scripts/log_parser.py -f test.log --source-lookup

# 使用配置文件
python scripts/log_parser.py -c config/analyzer_config.yaml -f logs/
```

### 命令行选项

```
usage: log_parser.py [-h] [-f FILES [FILES ...]] [-d DIR] [-c CONFIG]
                     [-o OUTPUT] [--format {html,markdown,json,text}]
                     [--source-lookup] [--no-source-lookup] [-v]

SSD Log Analyzer - 分析Test Log和SSD FW Log

optional arguments:
  -h, --help            显示帮助信息
  -f FILES [FILES ...]  要分析的日志文件
  -d DIR                包含日志文件的目录
  -c CONFIG             配置文件路径
  -o OUTPUT             输出报告文件路径
  --format {html,markdown,json,text}
                        输出格式 (默认: html)
  --source-lookup       启用源码查找功能
  --no-source-lookup    禁用源码查找功能
  -v, --verbose         详细输出模式
```

## 目录结构

```
ssd-log-analyzer/
├── README.md           # 本文档
├── scripts/            # Python脚本
│   ├── log_parser.py   # 主分析脚本
│   ├── log_analyzer.py # 分析器核心类
│   └── utils.py        # 工具函数
├── config/             # 配置文件
│   ├── analyzer_config.yaml    # 分析器配置
│   ├── log_patterns.yaml       # 日志模式配置
│   └── bug_patterns.yaml       # bug模式配置
├── tools/              # 辅助工具
│   ├── install_dependencies.sh # 依赖安装脚本
│   ├── nvme_tools.sh           # NVMe工具脚本
│   └── log_collector.sh        # 日志收集脚本
├── docs/               # 文档
│   ├── usage_guide.md          # 使用指南
│   ├── pattern_reference.md    # 模式参考
│   └── troubleshooting.md      # 故障排除
└── examples/           # 示例文件
    ├── sample_test.log         # 测试日志示例
    └── sample_analysis_report.html # 分析报告示例
```

## 配置说明

### 日志模式配置 (config/log_patterns.yaml)

定义要匹配的日志模式，包括：
- 错误代码模式
- 超时模式
- 数据损坏模式
- 固件崩溃模式
- 坏块模式
- 温度警告模式
- 掉电保护模式

### Bug模式配置 (config/bug_patterns.yaml)

定义已知的bug模式，包括：
- 固件死锁
- NAND读干扰
- DRAM ECC错误
- 温度节流
- 掉电保护失效

### 分析器配置 (config/analyzer_config.yaml)

配置分析器行为，包括：
- 源码查找目录
- 阈值设置
- 输出格式
- 时间格式

## 分析流程

1. **日志解析**：读取日志文件，提取时间戳、严重性、组件、消息
2. **模式匹配**：匹配预定义的日志模式和bug模式
3. **统计分析**：按严重性、组件、模式进行统计
4. **问题识别**：识别高频错误和异常模式
5. **源码查找**：对可疑打印在源码中查找对应位置
6. **根因分析**：基于模式匹配和统计分析推断bug根因
7. **报告生成**：生成详细的分析报告

## 输出报告

报告包含以下部分：
- **摘要**：日志条目统计、按严重性分布
- **发现问题**：识别的高频错误和异常
- **Bug候选**：匹配的已知bug模式
- **建议**：基于分析结果的行动建议
- **统计信息**：错误率、警告率等统计指标
- **源码引用**：找到的相关源码位置（如果启用）

## 扩展开发

### 添加新的日志模式

1. 编辑 `config/log_patterns.yaml`
2. 添加新的模式定义
3. 重启分析器

### 添加新的Bug模式

1. 编辑 `config/bug_patterns.yaml`
2. 添加新的bug模式定义
3. 包括模式、描述、根因、解决方案、参考

### 自定义源码查找

1. 编辑 `config/analyzer_config.yaml`
2. 修改 `source_code_dirs` 配置
3. 添加您的源码目录路径

## 故障排除

常见问题请参考 `docs/troubleshooting.md`

## 许可证

MIT License