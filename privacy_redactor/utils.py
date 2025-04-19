import re
import os
import json

def is_chinese(text):
    """
    检测文本是否主要为中文
    
    参数:
        text: 需要检测的文本
        
    返回:
        bool: 如果中文字符占比超过50%则返回True，否则返回False
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    chinese_chars = chinese_pattern.findall(text)
    
    # 计算中文字符占比
    if not text or len(text) == 0:
        return False
        
    return len(chinese_chars) / len(text) > 0.5

def is_medical_text(text):
    """
    检测文本是否为医疗相关文本
    
    参数:
        text: 需要检测的文本
        
    返回:
        bool: 如果包含医疗相关关键词则返回True，否则返回False
    """
    # 医疗相关关键词
    medical_keywords = [
        '患者', '医生', '护士', '病人', '医院', '诊所', '药物', '治疗', '疾病', '症状',
        '病历', '手术', '检查', '化验', '诊断', '用药', '住院', '出院', '病房', '门诊',
        '急诊', '医嘱', '护理', '康复', '病史', '血压', '体温', '心率', '呼吸'
    ]
    
    for keyword in medical_keywords:
        if keyword in text:
            return True
            
    return False

# 医疗文本中常见的需要忽略的医学术语
MEDICAL_TERMS_TO_IGNORE = [
    '高血压', '糖尿病', '冠心病', '肺炎', '肝炎', '胃炎', '贫血', '心肌梗死',
    '脑梗塞', '心功能不全', '肝功能不全', '肾功能不全', '慢性阻塞性肺疾病',
    '哮喘', '肺结核', '甲状腺功能亢进', '甲状腺功能减退', '类风湿性关节炎',
    '骨质疏松', '癫痫', '帕金森', '阿尔茨海默', '精神分裂', '抑郁症', '焦虑症',
    '白细胞', '红细胞', '血小板', '中性粒细胞', '淋巴细胞', '单核细胞',
    '血红蛋白', '肌酐', '尿素氮', '谷丙转氨酶', '谷草转氨酶', '总胆红素',
    '直接胆红素', '白蛋白', '球蛋白', '甘油三酯', '总胆固醇', '低密度脂蛋白',
    '高密度脂蛋白', '空腹血糖', '糖化血红蛋白', '凝血酶原时间', '活化部分凝血活酶时间'
]

# 正则表达式模式
REGEX_PATTERNS = {
    # 个人信息
    'ID_CARD': r'[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]',  # 身份证号
    'PHONE': r'(?:13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}',  # 手机号
    'EMAIL': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # 电子邮箱
    'BANK_CARD': r'(?:62|4|5)\d{14,18}',  # 银行卡号
    
    # 医疗相关
    'PATIENT_ID': r'门诊号[：:]?\s*(\d{6,12})|住院号[：:]?\s*(\d{6,12})|病案号[：:]?\s*(\d{6,12})',  # 患者ID
    'MEDICAL_RECORD_NO': r'病历号[：:]?\s*([A-Za-z0-9]+)|病案号[：:]?\s*([A-Za-z0-9]+)|门诊号[：:]?\s*([A-Za-z0-9]+)',  # 病历号
    'ADMISSION_NO': r'住院号[：:]?\s*([A-Za-z0-9]+)',  # 住院号
    'MEDICAL_INSURANCE_NO': r'医保号[：:]?\s*([A-Za-z0-9]+)',  # 医保号
    'SOCIAL_SECURITY_NO': r'社保号[：:]?\s*(\d{10,20})',  # 社保号
    'MEDICAL_EXPENSES': r'(?:医疗费用|总费用|自费金额)[：:]?\s*[¥￥]?(\d+(?:\.\d+)?)',  # 医疗费用
    'DOCTOR_NAME': r'(?:主治|主管|经治|值班|记录)医师[：:]?\s*([张李王赵刘陈杨黄周吴徐孙马朱胡林郭何高罗郑梁谢宋唐许邓冯韩曹曾彭萧蒋蔡沈韦江童陆姜戴崔邹潘'
                r'薛叶阎余袁侯贺龚顾毛郝龙邵钱汪石井廖洪姚欧艾熊孟贾范宁庄马苏何傅俞'
                r'章萧程于舒康齐吕金陶沈伍刘)'
                r'[\u4e00-\u9fa5]{1,2})',  # 医生姓名
    'DATE': r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',  # 日期
    'TIME': r'(\d{1,2}[:：]\d{1,2}(?:[:：]\d{1,2})?)',  # 时间
    'LOCATION': r'(?:地址|住址|家庭住址|现住址)[：:]\s*([\u4e00-\u9fa5]+(?:省|市|区|县|镇|乡|村|路|街|号|室)(?:[\u4e00-\u9fa5]*(?:省|市|区|县|镇|乡|村|路|街|号|室)){0,5}[\u4e00-\u9fa5\d]*)'  # 地址
}

def save_entities(entities, output_path):
    """
    保存识别出的实体到文件
    
    参数:
        entities: 实体列表
        output_path: 输出文件路径
    """
    dirname = os.path.dirname(output_path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
        
    # 生成实体保存路径
    base_name = os.path.basename(output_path)
    name, ext = os.path.splitext(base_name)
    entities_path = os.path.join(os.path.dirname(output_path), f"{name}_entities.json")
    
    # 保存实体到JSON文件
    with open(entities_path, 'w', encoding='utf-8') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2) 