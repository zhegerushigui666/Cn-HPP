#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def run_command(cmd, title):
    """运行命令并显示标题"""
    separator = "="*80
    print(f"\n{separator}")
    print(f"  {title}")
    print(f"{separator}\n")
    return subprocess.call(cmd, shell=True)

def check_dependencies():
    """检查并安装依赖"""
    try:
        import jieba
        import docx
    except ImportError:
        print("安装必要的依赖...")
        subprocess.call([sys.executable, "-m", "pip", "install", "jieba", "python-docx"])

def main():
    """运行所有示例"""
    print("\n欢迎使用 Privacy Redactor 示例程序!\n")
    
    # 检查依赖
    check_dependencies()
    
    # 1. 首先创建示例Word文档
    print("\n第1步：创建示例Word文档")
    if not os.path.exists("example_medical.docx"):
        run_command("python create_example_docx.py", "创建示例医疗Word文档")
    else:
        print("示例Word文档已存在，跳过创建步骤。")
    
    # 2. 运行文本处理示例
    run_command("python example_usage.py", "运行文本处理示例")
    
    # 3. 运行Word文档处理示例
    run_command("python example_docx.py", "运行Word文档处理示例")
    
    # 4. 运行自定义策略示例
    run_command("python custom_strategy.py", "运行自定义策略示例")
    
    # 总结
    print("\n所有示例运行完成！生成的文件：")
    for file in os.listdir("."):
        if file.endswith((".docx", ".json")) and (file.startswith("example_") or "redacted" in file):
            print(f" - {file} ({os.path.getsize(file) / 1024:.1f} KB)")
    
    print("\n你可以打开生成的Word文档查看处理结果，或查看*_entities.json文件了解识别到的敏感实体。")

if __name__ == "__main__":
    main() 