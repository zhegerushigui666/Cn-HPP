import re
import json
from collections import defaultdict

import jieba
import jieba.posseg as pseg
from .utils import REGEX_PATTERNS, MEDICAL_TERMS_TO_IGNORE

class MedicalStrategy:
    """
    中文医疗文本隐私处理策略
    
    用于识别和处理中文医疗文本中的敏感信息，如患者姓名、身份证号、电话号码等。
    """
    
    def __init__(self, use_llm=False, llm_config=None):
        """
        初始化中文医疗文本隐私处理策略
        
        参数:
            use_llm: 是否使用大语言模型增强识别能力
            llm_config: 大语言模型配置信息
        """
        self.use_llm = use_llm
        self.llm_config = llm_config or {}
        self._load_medical_dictionary()
        
    def _load_medical_dictionary(self):
        """加载医疗词典"""
        # 加载医疗专用词典到jieba
        for term in MEDICAL_TERMS_TO_IGNORE:
            jieba.add_word(term, freq=1000, tag='n')
            
    def get_entities(self, text):
        """
        从文本中提取实体
        
        参数:
            text: 要处理的文本
            
        返回:
            entities: 识别出的实体信息列表
        """
        entities = []
        
        # 1. 使用正则表达式识别结构化信息
        entities.extend(self._extract_by_regex(text))
        
        # 2. 使用jieba进行分词和命名实体识别
        entities.extend(self._extract_by_jieba(text))
        
        # 3. 使用大语言模型增强识别（如果启用）
        if self.use_llm:
            entities.extend(self._extract_by_llm(text))
            
        # 去重
        unique_entities = []
        seen = set()
        for entity in entities:
            text_span = entity['original']
            if text_span not in seen:
                seen.add(text_span)
                unique_entities.append(entity)
                
        return unique_entities
        
    def _extract_by_regex(self, text):
        """使用正则表达式提取结构化敏感信息"""
        entities = []
        
        for entity_type, pattern in REGEX_PATTERNS.items():
            for match in re.finditer(pattern, text):
                # 获取匹配组，如果有捕获组，使用第一个非空的捕获组
                if match.groups():
                    for group in match.groups():
                        if group:
                            start = text.find(group, match.start())
                            end = start + len(group)
                            entity = {
                                'original': group,
                                'type': entity_type,
                                'replacement': f'[{entity_type}]',
                                'start': start,
                                'end': end
                            }
                            entities.append(entity)
                            break
                else:
                    # 如果没有捕获组，使用整个匹配
                    entity = {
                        'original': match.group(),
                        'type': entity_type,
                        'replacement': f'[{entity_type}]',
                        'start': match.start(),
                        'end': match.end()
                    }
                    entities.append(entity)
                    
        return entities
        
    def _extract_by_jieba(self, text):
        """使用jieba分词提取命名实体"""
        entities = []
        
        # 使用jieba的词性标注功能
        words = pseg.cut(text)
        
        # 姓名识别
        for word, flag in words:
            if flag == 'nr' and len(word) >= 2:  # 人名
                # 搜索所有出现的位置
                start = 0
                while True:
                    start = text.find(word, start)
                    if start == -1:
                        break
                        
                    entity = {
                        'original': word,
                        'type': 'NAME',
                        'replacement': '[姓名]',
                        'start': start,
                        'end': start + len(word)
                    }
                    entities.append(entity)
                    start += len(word)
            
            elif flag == 'ns':  # 地名
                # 搜索所有出现的位置
                start = 0
                while True:
                    start = text.find(word, start)
                    if start == -1:
                        break
                        
                    entity = {
                        'original': word,
                        'type': 'LOCATION',
                        'replacement': '[地址]',
                        'start': start,
                        'end': start + len(word)
                    }
                    entities.append(entity)
                    start += len(word)
                    
            elif flag == 'nt':  # 机构名
                # 搜索所有出现的位置
                start = 0
                while True:
                    start = text.find(word, start)
                    if start == -1:
                        break
                        
                    entity = {
                        'original': word,
                        'type': 'ORGANIZATION',
                        'replacement': '[机构]',
                        'start': start,
                        'end': start + len(word)
                    }
                    entities.append(entity)
                    start += len(word)
                    
        return entities
    
    def _extract_by_llm(self, text):
        """使用大语言模型增强识别能力（需要实现具体的调用逻辑）"""
        entities = []
        
        # TODO: 实现大语言模型调用逻辑
        # 此处需要根据实际使用的大语言模型接口实现
        
        return entities
    
    def redact_text(self, text, entities):
        """
        对文本进行脱敏处理
        
        参数:
            text: 原始文本
            entities: 需要脱敏的实体列表
            
        返回:
            redacted_text: 脱敏后的文本
            entity_map: 实体替换映射
        """
        # 按照起始位置排序实体，从后向前替换，避免位置偏移问题
        sorted_entities = sorted(entities, key=lambda e: e.get('start', 0), reverse=True)
        
        redacted_text = text
        entity_map = {}
        
        for entity in sorted_entities:
            original = entity['original']
            replacement = entity['replacement']
            
            # 如果有位置信息，直接使用
            if 'start' in entity and 'end' in entity:
                start, end = entity['start'], entity['end']
                redacted_text = redacted_text[:start] + replacement + redacted_text[end:]
            else:
                # 否则全局替换，可能会有误替换
                redacted_text = redacted_text.replace(original, replacement)
            
            # 记录替换映射
            entity_map[replacement] = original
            
        return redacted_text, entity_map 