#!/usr/bin/env python
# -*- coding: utf-8 -*-

from privacy_redactor import PrivacyRedactor

def main():
    """
    Privacy Redactor示例用法
    """
    print("=== Privacy Redactor 示例用法 ===")
    
    # 1. 创建一个PrivacyRedactor实例，使用medical策略
    print("\n1. 创建PrivacyRedactor实例")
    redactor = PrivacyRedactor(strategy='medical', enable_llm=False)
    
    # 2. 处理包含敏感信息的文本
    print("\n2. 处理包含敏感信息的文本")
    text = """
    患者张三，男，45岁，身份证号码330102197508124567，
    家庭住址：浙江省杭州市西湖区文三路123号，联系电话13812345678。
    患者因持续发热三天，伴有咳嗽、咳痰，于2023年5月10日来我院就诊。
    患者既往有高血压病史，目前口服硝苯地平缓释片控制。
    入院后完善相关检查，诊断为：1.肺炎 2.高血压（2级）
    """
    
    print("\n原始文本:")
    print(text)
    
    # 3. 调用redact_text方法进行处理
    print("\n处理后文本:")
    redacted_text, entities = redactor.redact_text(text)
    print(redacted_text)
    
    # 4. 打印识别到的实体
    print("\n识别到的敏感实体:")
    for i, entity in enumerate(entities, 1):
        print(f"{i}. 类型: {entity['type']}, 原文: {entity['original']}, 替换为: {entity['replacement']}")
    
    # 5. 仅识别敏感实体，不进行替换
    print("\n5. 仅识别敏感实体，不进行替换")
    entities_only = redactor.get_entities(text)
    print(f"识别到 {len(entities_only)} 个敏感实体")
    
    # 6. 使用不同的策略
    print("\n6. 使用Regex策略")
    regex_redactor = PrivacyRedactor(strategy='regex')
    _, regex_entities = regex_redactor.redact_text(text)
    print(f"Regex策略识别到 {len(regex_entities)} 个敏感实体")
    
    # 7. 尝试启用LLM增强（注：实际使用需要确保LLM服务可用）
    print("\n7. 创建带LLM增强的PrivacyRedactor实例")
    print("注意：如果没有可用的LLM服务，这一步可能会失败")
    try:
        llm_redactor = PrivacyRedactor(strategy='medical', enable_llm=True)
        print("LLM增强功能已启用")
    except Exception as e:
        print(f"启用LLM增强失败: {e}")
    
    print("\n=== 示例结束 ===")

if __name__ == "__main__":
    main() 