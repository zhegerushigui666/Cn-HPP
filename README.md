# Privacy Redactor - 隐私信息处理工具

Privacy Redactor 是一个用于识别和替换文本中隐私信息的Python工具包，支持中文文本和Word文档处理，特别适用于医疗文本的隐私保护处理。

## 功能特点

- **多语言支持**：自动识别并处理中文和英文文本
- **多种处理策略**：
  - HanLP策略：使用HanLP进行命名实体识别
  - 正则表达式策略：使用预定义的正则表达式匹配模式固定的信息
  - LLM策略：使用大语言模型(如Qwen2)进行更灵活的识别，支持多次采样置信度筛选
  - 混合策略：结合以上策略的优点
  - 医疗策略：专门针对医疗文本的实体识别
- **文件格式支持**：
  - 纯文本文件(.txt)
  - Word文档(.docx)，保留原始文档格式
- **结构化输出**：提供识别的实体信息，包括原文、类型和替换文本
- **可扩展性**：易于定制和扩展，支持添加自定义策略和实体类型

## 安装方法

```bash
# 从源码安装
git clone https://github.com/yourusername/privacy-redactor.git
cd privacy-redactor
pip install -e .

# 或直接使用pip安装
pip install privacy-redactor
```

## 基本使用示例

### 文本处理

```python
from privacy_redactor import PrivacyRedactor

# 创建一个隐私信息处理器（默认使用医疗策略）
redactor = PrivacyRedactor(strategy='medical')

# 处理包含敏感信息的文本
text = """
患者张三，男，45岁，身份证号码330102197508124567，
家庭住址：浙江省杭州市西湖区文三路123号，联系电话13812345678。
患者因持续发热三天，伴有咳嗽、咳痰，于2023年5月10日来我院就诊。
患者既往有高血压病史，目前口服硝苯地平缓释片控制。
入院后完善相关检查，诊断为：1.肺炎 2.高血压（2级）
"""

# 处理文本并获取识别的实体
redacted_text, entities = redactor.redact_text(text)

print("原文:", text)
print("处理后:", redacted_text)

# 打印识别的实体
for entity in entities:
    print(f"类型: {entity['type']}, 原文: {entity['original']}, 替换为: {entity['replacement']}")
```

### 文件处理

```python
# 处理Word文档
input_file = "medical_report.docx"
output_file = "redacted_report.docx"
output_path, doc_entities = redactor.redact_file(input_file, output_file)

print(f"处理完成，输出文件: {output_path}")
print(f"识别到 {len(doc_entities)} 个敏感实体")
```

## 选择不同的策略

```python
# 使用正则表达式策略
regex_redactor = PrivacyRedactor(strategy='regex')

# 使用混合策略
hybrid_redactor = PrivacyRedactor(strategy='hybrid')

# 使用LLM策略（需要安装并运行Ollama）
llm_redactor = PrivacyRedactor(strategy='llm', 
                               enable_llm=True, 
                               model_name="qwen2:7b", 
                               url="http://127.0.0.1:11434")

# 创建一个使用LLM增强的医疗策略
medical_llm_redactor = PrivacyRedactor(strategy='medical', enable_llm=True)
```

## 自定义策略示例

您可以通过扩展现有策略类来创建自定义策略：

```python
import re
from privacy_redactor.strategies import RegexStrategy

class CustomMedicalStrategy(RegexStrategy):
    """自定义医疗文本处理策略"""
    
    def __init__(self):
        super().__init__()
        
        # 添加自定义的正则表达式模式
        self.custom_patterns = {
            'DRUG_NAME': r'(?:服用|用药|药品名称|处方)[：:]\s*([\u4e00-\u9fa5]{2,10}(?:片|胶囊|注射液|口服液))',
            'LABORATORY_VALUE': r'(?:血糖|血压|体温)[：:]\s*(\d+(?:\.\d+)?(?:\s*[-~～至]\s*\d+(?:\.\d+)?)?(?:\s*[a-zA-Z/%]+)?)',
            'MEDICAL_DEVICE': r'(?:使用|植入|置入)[：:]\s*([\u4e00-\u9fa5]{2,15}(?:导管|支架|起搏器|呼吸机))',
        }
        
        # 添加自定义的替换模板
        self.custom_replacements = {
            'DRUG_NAME': '[药品名]',
            'LABORATORY_VALUE': '[检验值]',
            'MEDICAL_DEVICE': '[医疗器械]',
        }
    
    def extract_entities(self, text, language='zh'):
        # 先使用父类方法提取基本实体
        entities = super().extract_entities(text, language)
        
        # 使用自定义模式提取额外实体
        if language == 'zh':
            for entity_type, pattern in self.custom_patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    original = match.group(1)
                    if original:
                        entities.append({
                            'type': entity_type,
                            'original': original,
                            'replacement': self.custom_replacements.get(entity_type, f'[{entity_type}]')
                        })
        
        return entities

# 使用自定义策略
custom_strategy = CustomMedicalStrategy()
redacted_text = custom_strategy.redact_text("患者服用二甲双胍片控制血糖：7.8-10.4 mmol/L")
```

## 支持的实体类型

### 通用实体类型
- **人名**：[NAME]
- **组织名**：[ORGANIZATION]
- **地址**：[LOCATION]
- **邮箱**：[EMAIL]
- **电话**：[PHONE]
- **身份证号**：[ID_CARD]
- **银行卡号**：[BANK_CARD]
- **日期**：[DATE]
- **时间**：[TIME]

### 医疗特有实体类型
- **患者ID**：[PATIENT_ID] - 病历号、住院号、门诊号等
- **医疗记录号**：[MEDICAL_RECORD_NO]
- **住院号**：[ADMISSION_NO]
- **医保号**：[MEDICAL_INSURANCE_NO]
- **社保号**：[SOCIAL_SECURITY_NO]
- **医疗费用**：[MEDICAL_EXPENSES]
- **医生姓名**：[DOCTOR_NAME]

## LLM增强功能

使用LLM增强功能需要本地运行Ollama服务：

1. 安装[Ollama](https://ollama.com/)
2. 拉取支持的模型：`ollama pull qwen2:7b`
3. 启动Ollama服务

然后可以启用LLM增强：

```python
redactor = PrivacyRedactor(strategy='medical', enable_llm=True)
```

## 依赖库

- jieba
- python-docx

## 示例代码

项目包含多个示例脚本，展示了不同场景下的使用方法：

- `example_usage.py`: 基本文本处理示例
- `example_docx.py`: Word文档处理示例
- `custom_strategy.py`: 自定义策略示例

## 许可证

MIT 
