import os
from .utils import is_chinese
from .strategies import HanlpStrategy, LLMStrategy, RegexStrategy, HybridStrategy, MedicalStrategy
from .handlers import TextFileHandler, DocxFileHandler

class PrivacyRedactor:
    """
    隐私信息处理工具包的主类，用于识别和替换中文医疗文本中的隐私信息。
    """
    def __init__(self, strategy='medical', enable_llm=False, model_name="qwen2:7b", url="http://127.0.0.1:11434"):
        """
        初始化隐私信息处理器
        
        参数:
            strategy: 使用的策略，可选值有 'hanlp', 'llm', 'regex', 'medical', 'hybrid'
            enable_llm: 是否启用大语言模型增强
            model_name: 大语言模型名称
            url: 大语言模型API地址
        """
        # 根据策略名称实例化相应的策略类
        strategy_map = {
            'hanlp': HanlpStrategy(),
            'llm': LLMStrategy(model_name=model_name, url=url),
            'regex': RegexStrategy(),
            'medical': MedicalStrategy(),
            'hybrid': HybridStrategy()
        }
        
        if strategy not in strategy_map:
            raise ValueError(f"不支持的策略: {strategy}，可选值为: {', '.join(strategy_map.keys())}")
        
        self.strategy = strategy_map[strategy]
        
        # 如果启用LLM，为策略配置LLM
        if enable_llm and strategy in ['medical', 'hybrid']:
            self.strategy.enable_llm(model_name=model_name, url=url)
        
        # 文件处理器映射
        self.file_handlers = {
            '.txt': TextFileHandler(),
            '.docx': DocxFileHandler()
        }
        
    def redact_text(self, text):
        """
        处理中文医疗文本中的隐私信息
        
        参数:
            text: 要处理的文本
            
        返回:
            redacted_text: 处理后的文本
            entities: 识别出的实体列表，每个实体是一个包含原文、类型、替换文本的字典
        """
        # 提取实体
        entities = self.strategy.extract_entities(text)
        
        # 替换文本
        redacted_text = text
        for entity in entities:
            redacted_text = redacted_text.replace(entity['original'], entity['replacement'])
            
        return redacted_text, entities
        
    def redact_file(self, input_path, output_path=None):
        """
        处理文件中的隐私信息
        
        参数:
            input_path: 输入文件路径
            output_path: 输出文件路径，如果为None则自动生成
            
        返回:
            output_path: 输出文件路径
            entities: 识别出的实体列表
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(input_path)
        
        # 如果未指定输出路径，自动生成
        if output_path is None:
            base_name = os.path.basename(input_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(os.path.dirname(input_path), f"{name}_redacted{ext}")
        
        # 获取对应的文件处理器
        if ext not in self.file_handlers:
            raise ValueError(f"不支持的文件类型: {ext}，支持的文件类型: {', '.join(self.file_handlers.keys())}")
            
        handler = self.file_handlers[ext]
        
        # 处理文件
        handler.redact(input_path, output_path, self.strategy)
        
        return output_path, handler.get_entities()
        
    def get_entities(self, text):
        """
        仅识别文本中的隐私实体，不进行替换
        
        参数:
            text: 要处理的文本
            
        返回:
            entities: 识别出的实体列表
        """
        return self.strategy.extract_entities(text) 