#!/usr/bin/env python3
"""
SSD Log Parser - 解析Test Log和SSD FW Log的主脚本
"""

import argparse
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_analyzer import SSDFirmwareAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description='SSD Log Analyzer - 分析Test Log和SSD FW Log',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -f test.log
  %(prog)s -f log1.log log2.log -o report.html
  %(prog)s -d logs/ --format markdown
  %(prog)s -f test.log --source-lookup -v
        """
    )
    
    parser.add_argument('-f', '--files', nargs='+', 
                       help='要分析的日志文件')
    parser.add_argument('-d', '--dir', 
                       help='包含日志文件的目录')
    parser.add_argument('-c', '--config', default='config/analyzer_config.yaml',
                       help='配置文件路径 (默认: config/analyzer_config.yaml)')
    parser.add_argument('-o', '--output', 
                       help='输出报告文件路径')
    parser.add_argument('--format', choices=['html', 'markdown', 'json', 'text'],
                       default='html', help='输出格式 (默认: html)')
    parser.add_argument('--source-lookup', action='store_true',
                       help='启用源码查找功能')
    parser.add_argument('--no-source-lookup', action='store_false', 
                       dest='source_lookup',
                       help='禁用源码查找功能')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出模式')
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return 1
    
    args = parser.parse_args()
    
    # 验证输入
    if not args.files and not args.dir:
        print("错误: 必须指定文件(-f)或目录(-d)")
        return 1
    
    # 收集要分析的文件
    files_to_analyze = []
    
    if args.files:
        for file_path in args.files:
            if os.path.exists(file_path):
                files_to_analyze.append(file_path)
            else:
                print(f"警告: 文件不存在: {file_path}")
    
    if args.dir:
        if os.path.exists(args.dir) and os.path.isdir(args.dir):
            for root, _, filenames in os.walk(args.dir):
                for filename in filenames:
                    if filename.endswith(('.log', '.txt', '.err', '.out')):
                        files_to_analyze.append(os.path.join(root, filename))
        else:
            print(f"错误: 目录不存在: {args.dir}")
            return 1
    
    if not files_to_analyze:
        print("错误: 没有找到要分析的文件")
        return 1
    
    print(f"找到 {len(files_to_analyze)} 个日志文件")
    
    try:
        # 创建分析器
        analyzer = SSDFirmwareAnalyzer(args.config)
        
        # 覆盖配置中的源码查找设置
        if args.source_lookup is not None:
            analyzer.config['enable_source_lookup'] = args.source_lookup
        
        # 解析所有文件
        total_entries = 0
        for file_path in files_to_analyze:
            print(f"解析文件: {file_path}")
            entries = analyzer.parse_log_file(file_path)
            total_entries += len(entries)
            if args.verbose:
                print(f"  找到 {len(entries)} 条日志条目")
        
        print(f"总共解析 {total_entries} 条日志条目")
        
        # 分析日志
        print("分析日志...")
        analysis = analyzer.analyze_logs()
        
        # 生成报告
        print("生成报告...")
        report = analyzer.generate_report(args.format)
        
        # 输出报告
        if args.output:
            output_path = args.output
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {output_path}")
        else:
            if args.format == 'json':
                print(report)
            else:
                # 对于非JSON格式，直接打印可能太长，建议保存到文件
                print("报告内容:")
                print("-" * 80)
                if args.format == 'text':
                    print(report)
                else:
                    print(f"报告已生成 ({args.format}格式)，建议使用 -o 参数保存到文件")
        
        # 显示摘要
        print("\n" + "=" * 80)
        print("分析摘要:")
        print(f"  日志文件: {len(files_to_analyze)} 个")
        print(f"  日志条目: {total_entries} 条")
        
        if analysis.get('summary', {}).get('by_severity'):
            print("  严重性分布:")
            for severity, count in analysis['summary']['by_severity'].items():
                print(f"    {severity}: {count}")
        
        if analysis.get('issues'):
            print(f"  发现问题: {len(analysis['issues'])} 个")
        
        if analysis.get('bug_candidates'):
            print(f"  Bug候选: {len(analysis['bug_candidates'])} 个")
        
        if analysis.get('recommendations'):
            print(f"  建议: {len(analysis['recommendations'])} 条")
        
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())