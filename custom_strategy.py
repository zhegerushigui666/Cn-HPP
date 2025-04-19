#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from privacy_redactor import PrivacyRedactor
from privacy_redactor.strategies import RegexStrategy

class CustomMedicalStrategy(RegexStrategy):
    """
    自定义医疗文本处理策略
    
    这个示例展示如何扩展现有策略，添加特定领域的实体识别功能
    """
    
    def __init__(self):
        """初始化自定义医疗文本处理策略"""
        super().__init__()
        
        # 添加自定义的正则表达式模式
        self.custom_patterns = {
            'DRUG_NAME': r'(?:服用|用药|药品名称|处方)[：:]\s*([\u4e00-\u9fa5]{2,10}(?:片|胶囊|注射液|口服液|滴剂|溶液|喷雾剂|贴剂|粉剂|颗粒|混悬液))',
            'LABORATORY_VALUE': r'(?:血糖|血压|体温|心率|呼吸|血红蛋白|白细胞|血小板|肌酐|尿素氮)[：:]\s*(\d+(?:\.\d+)?(?:\s*[-~～至]\s*\d+(?:\.\d+)?)?(?:\s*[a-zA-Z/%]+)?)',
            'MEDICAL_DEVICE': r'(?:使用|植入|置入)[：:]\s*([\u4e00-\u9fa5]{2,15}(?:导管|支架|起搏器|呼吸机|监护仪|泵|针|管|器))',
            'SURGERY_NAME': r'(?:手术名称|手术|术式)[：:]\s*([\u4e00-\u9fa5]{2,20}(?:手术|切除术|成形术|修复术|置换术|重建术|吻合术|固定术|摘除术|造瘘术))',
        }
        
        # 添加自定义的替换模板
        self.custom_replacements = {
            'DRUG_NAME': '[药品名]',
            'LABORATORY_VALUE': '[检验值]',
            'MEDICAL_DEVICE': '[医疗器械]',
            'SURGERY_NAME': '[手术名称]',
        }
    
    def extract_entities(self, text, language='zh'):
        """
        从文本中提取实体
        
        参数:
            text: 要处理的文本
            language: 文本语言，默认为中文
            
        返回:
            entities: 识别出的实体列表
        """
        # 先使用父类方法提取基本实体
        entities = super().extract_entities(text, language)
        
        # 如果不是中文文本，直接返回基本实体
        if language != 'zh':
            return entities
        
        # 使用自定义模式提取额外实体
        for entity_type, pattern in self.custom_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(1)
                if original:
                    entities.append({
                        'type': entity_type,
                        'original': original,
                        'replacement': self.custom_replacements.get(entity_type, f'[{entity_type}]'),
                        'start': match.start(1),
                        'end': match.end(1)
                    })
        
        return entities

def main():
    """
    自定义策略示例用法
    """
    print("=== 自定义策略示例 ===")
    
    # 创建自定义策略实例
    custom_strategy = CustomMedicalStrategy()
    
    # 测试文本
    text = """
    患者王某，男，65岁，因"发热、咳嗽3天"入院。
    既往有糖尿病病史5年，服用二甲双胍片控制。
    测量血压: 145/90mmHg，体温: 38.5℃，心率: 92次/分。
    血糖: 7.8-10.4 mmol/L，血红蛋白: 13.5g/dL。
    入院后使用: 输液泵给药，置入中心静脉导管。
    手术名称: 冠状动脉搭桥术。
    诊断: 1.重症肺炎 2.2型糖尿病 3.高血压 4.冠心病
    """
    
    print("\n原始文本:")
    print(text)
    
    # 使用自定义策略提取实体
    entities = custom_strategy.extract_entities(text)
    
    print("\n识别出的实体:")
    for i, entity in enumerate(entities, 1):
        print(f"{i}. 类型: {entity['type']}, 原文: {entity['original']}, 替换为: {entity['replacement']}")
    
    # 使用自定义策略替换文本
    redacted_text = custom_strategy.redact_text(text)
    
    print("\n处理后文本:")
    print(redacted_text)
    
    # 也可以通过以下方式直接集成到PrivacyRedactor
    print("\n集成到PrivacyRedactor:")
    
    # 方法1: 使用实例化后的策略
    from privacy_redactor.redactor import PrivacyRedactor as PR
    
    # 创建不带类型提示的工厂函数
    def get_custom_strategy():
        return CustomMedicalStrategy()
    
    # 添加自定义策略到策略映射
    PR._strategy_map = {'custom': get_custom_strategy}
    
    # 创建使用自定义策略的PrivacyRedactor
    try:
        redactor = PR(strategy='custom')
        print("成功创建使用自定义策略的PrivacyRedactor实例")
    except Exception as e:
        print(f"创建使用自定义策略的PrivacyRedactor实例失败: {e}")
    
    print("\n=== 示例结束 ===")

if __name__ == "__main__":
    main() 