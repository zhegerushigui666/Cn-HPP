#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from privacy_redactor import PrivacyRedactor

def main():
    """
    Privacy Redactor处理Word文档示例
    """
    print("=== Privacy Redactor Word文档处理示例 ===")
    
    # 1. 创建一个PrivacyRedactor实例
    print("\n1. 创建PrivacyRedactor实例")
    redactor = PrivacyRedactor(strategy='medical', enable_llm=False)
    
    # 2. 检查示例文档是否存在
    docx_file = "example_medical.docx"
    if not os.path.exists(docx_file):
        print(f"示例文档 '{docx_file}' 不存在，请先创建一个包含医疗敏感信息的Word文档")
        return
    
    # 3. 设置输出文件路径
    output_file = "example_medical_redacted.docx"
    
    # 4. 处理Word文档
    print(f"\n2. 处理Word文档 '{docx_file}'")
    try:
        output_path, entities = redactor.redact_file(docx_file, output_file)
        print(f"处理完成，输出文件: {output_path}")
        print(f"识别到 {len(entities)} 个敏感实体")
        
        # 5. 打印识别到的实体
        if entities:
            print("\n识别到的部分敏感实体:")
            # 只显示前10个实体，避免输出过多
            for i, entity in enumerate(entities[:10], 1):
                print(f"{i}. 类型: {entity['type']}, 原文: {entity['original']}, 替换为: {entity['replacement']}")
            
            if len(entities) > 10:
                print(f"... 还有 {len(entities) - 10} 个实体未显示")
    except Exception as e:
        print(f"处理文档时出错: {e}")
    
    # 6. 使用不同的策略
    print("\n3. 使用Hybrid策略处理文档")
    try:
        hybrid_redactor = PrivacyRedactor(strategy='hybrid')
        hybrid_output = "example_medical_hybrid.docx"
        hybrid_path, hybrid_entities = hybrid_redactor.redact_file(docx_file, hybrid_output)
        print(f"处理完成，输出文件: {hybrid_path}")
        print(f"Hybrid策略识别到 {len(hybrid_entities)} 个敏感实体")
    except Exception as e:
        print(f"使用Hybrid策略处理文档时出错: {e}")
    
    print("\n=== 示例结束 ===")
    print("提示: 请使用Word打开生成的 '*_redacted.docx' 和 '*_hybrid.docx' 文件查看处理效果")
    print("敏感实体信息会被保存在同目录下的 '*_entities.json' 文件中")

if __name__ == "__main__":
    main() 