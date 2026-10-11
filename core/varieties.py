# -*- coding: utf-8 -*-
"""
品种数据模块
数据来源于公众号图文《公歧收藏：商品品种资讯导航》内嵌的导航页：
https://mp.weixin.qq.com/s/Qh9bfpa41s_CN9v2-XdIeQ
包含 6 大交易所、88 个期货品种的名称/代码/拼音/分组/资讯检索关键词。
"""

EXCHANGES = {
    "shfe": {
        "short": "上期所",
        "name": "上海期货交易所",
        "en": "SHFE",
        "color": "#c0392b",
    },
    "ine": {
        "short": "上期能源",
        "name": "上海国际能源交易中心",
        "en": "INE",
        "color": "#0f766e",
    },
    "dce": {
        "short": "大商所",
        "name": "大连商品交易所",
        "en": "DCE",
        "color": "#1e7a4a",
    },
    "czce": {
        "short": "郑商所",
        "name": "郑州商品交易所",
        "en": "CZCE",
        "color": "#b45309",
    },
    "cffex": {
        "short": "中金所",
        "name": "中国金融期货交易所",
        "en": "CFFEX",
        "color": "#5b3fd6",
    },
    "gfex": {
        "short": "广期所",
        "name": "广州期货交易所",
        "en": "GFEX",
        "color": "#0e7490",
    },
}

VARIETIES = [
    {"ex": "shfe", "name": "沪铜", "code": "CU", "py": "cu", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪铜"},
    {"ex": "shfe", "name": "沪铝", "code": "AL", "py": "al", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪铝"},
    {"ex": "shfe", "name": "沪锌", "code": "ZN", "py": "zn", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪锌"},
    {"ex": "shfe", "name": "沪铅", "code": "PB", "py": "pb", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪铅"},
    {"ex": "shfe", "name": "沪镍", "code": "NI", "py": "ni", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪镍"},
    {"ex": "shfe", "name": "沪锡", "code": "SN", "py": "sn", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪锡"},
    {"ex": "shfe", "name": "氧化铝", "code": "AO", "py": "ao", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "氧化铝"},
    {"ex": "shfe", "name": "铸造铝合金", "code": "AD", "py": "ad", "group": "有色金属", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "铸造铝合金"},
    {"ex": "shfe", "name": "沪金", "code": "AU", "py": "au", "group": "贵金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪金"},
    {"ex": "shfe", "name": "沪银", "code": "AG", "py": "ag", "group": "贵金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沪银"},
    {"ex": "shfe", "name": "螺纹钢", "code": "RB", "py": "rb", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "螺纹钢"},
    {"ex": "shfe", "name": "线材", "code": "WR", "py": "wr", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "线材"},
    {"ex": "shfe", "name": "热轧卷板", "code": "HC", "py": "hc", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "热卷"},
    {"ex": "shfe", "name": "不锈钢", "code": "SS", "py": "ss", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "不锈钢"},
    {"ex": "shfe", "name": "燃料油", "code": "FU", "py": "fu", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "燃油"},
    {"ex": "shfe", "name": "石油沥青", "code": "BU", "py": "bu", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "沥青"},
    {"ex": "shfe", "name": "天然橡胶", "code": "RU", "py": "ru", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "橡胶"},
    {"ex": "shfe", "name": "合成橡胶", "code": "BR", "py": "br", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "丁二烯胶"},
    {"ex": "shfe", "name": "纸浆", "code": "SP", "py": "sp", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "纸浆"},
    {"ex": "shfe", "name": "胶版印刷纸", "code": "OP", "py": "op", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "胶版印刷纸"},
    {"ex": "ine", "name": "原油", "code": "SC", "py": "sc", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "原油"},
    {"ex": "ine", "name": "低硫燃料油", "code": "LU", "py": "lu", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "低硫燃油"},
    {"ex": "ine", "name": "20号胶", "code": "NR", "py": "nr", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "20号胶"},
    {"ex": "ine", "name": "国际铜", "code": "BC", "py": "bc", "group": "有色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "国际铜"},
    {"ex": "ine", "name": "集运指数(欧线)", "code": "EC", "py": "ec", "group": "航运指数", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "欧线集运"},
    {"ex": "dce", "name": "豆一", "code": "A", "py": "a", "group": "农产品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "豆一"},
    {"ex": "dce", "name": "豆二", "code": "B", "py": "b", "group": "农产品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "豆二"},
    {"ex": "dce", "name": "豆粕", "code": "M", "py": "m", "group": "农产品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "豆粕"},
    {"ex": "dce", "name": "豆油", "code": "Y", "py": "y", "group": "油脂油料", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "豆油"},
    {"ex": "dce", "name": "棕榈油", "code": "P", "py": "p", "group": "油脂油料", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "棕榈油"},
    {"ex": "dce", "name": "玉米", "code": "C", "py": "c", "group": "农产品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "玉米"},
    {"ex": "dce", "name": "淀粉", "code": "CS", "py": "cs", "group": "农产品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "淀粉"},
    {"ex": "dce", "name": "鸡蛋", "code": "JD", "py": "jd", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "鸡蛋"},
    {"ex": "dce", "name": "生猪", "code": "LH", "py": "lh", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "生猪"},
    {"ex": "dce", "name": "粳米", "code": "RR", "py": "rr", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "粳米"},
    {"ex": "dce", "name": "纤维板", "code": "FB", "py": "fb", "group": "林木建材", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "纤维板"},
    {"ex": "dce", "name": "胶合板", "code": "BB", "py": "bb", "group": "林木建材", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "胶合板"},
    {"ex": "dce", "name": "原木", "code": "LG", "py": "lg", "group": "林木建材", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "原木"},
    {"ex": "dce", "name": "焦炭", "code": "J", "py": "j", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "焦炭"},
    {"ex": "dce", "name": "焦煤", "code": "JM", "py": "jm", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "焦煤"},
    {"ex": "dce", "name": "铁矿石", "code": "I", "py": "i", "group": "黑色金属", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "铁矿石"},
    {"ex": "dce", "name": "塑料", "code": "L", "py": "l", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "塑料"},
    {"ex": "dce", "name": "聚丙烯", "code": "PP", "py": "pp", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "聚丙烯"},
    {"ex": "dce", "name": "PVC", "code": "V", "py": "v", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "PVC"},
    {"ex": "dce", "name": "乙二醇", "code": "EG", "py": "eg", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "乙二醇"},
    {"ex": "dce", "name": "苯乙烯", "code": "EB", "py": "eb", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "苯乙烯"},
    {"ex": "dce", "name": "LPG", "code": "PG", "py": "pg", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "LPG"},
    {"ex": "dce", "name": "纯苯", "code": "BZ", "py": "bz", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "纯苯"},
    {"ex": "czce", "name": "白糖", "code": "SR", "py": "sr", "group": "软商品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "白糖"},
    {"ex": "czce", "name": "棉花", "code": "CF", "py": "cf", "group": "软商品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "棉花"},
    {"ex": "czce", "name": "棉纱", "code": "CY", "py": "cy", "group": "软商品", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "棉纱"},
    {"ex": "czce", "name": "苹果", "code": "AP", "py": "ap", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "苹果"},
    {"ex": "czce", "name": "红枣", "code": "CJ", "py": "cj", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "红枣"},
    {"ex": "czce", "name": "花生", "code": "PK", "py": "pk", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "花生"},
    {"ex": "czce", "name": "菜籽", "code": "RS", "py": "rs", "group": "油脂油料", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "菜籽"},
    {"ex": "czce", "name": "菜粕", "code": "RM", "py": "rm", "group": "油脂油料", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "菜粕"},
    {"ex": "czce", "name": "菜油", "code": "OI", "py": "oi", "group": "油脂油料", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "菜油"},
    {"ex": "czce", "name": "普麦", "code": "PM", "py": "pm", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "普麦"},
    {"ex": "czce", "name": "强麦", "code": "WH", "py": "wh", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "强麦"},
    {"ex": "czce", "name": "早籼稻", "code": "RI", "py": "ri", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "早籼稻"},
    {"ex": "czce", "name": "晚籼稻", "code": "LR", "py": "lr", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "晚籼稻"},
    {"ex": "czce", "name": "粳稻", "code": "JR", "py": "jr", "group": "农产品", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "粳稻"},
    {"ex": "czce", "name": "PTA", "code": "TA", "py": "ta", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "PTA"},
    {"ex": "czce", "name": "甲醇", "code": "MA", "py": "ma", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "甲醇"},
    {"ex": "czce", "name": "动力煤", "code": "ZC", "py": "zc", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "动力煤"},
    {"ex": "czce", "name": "玻璃", "code": "FG", "py": "fg", "group": "建材", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "玻璃"},
    {"ex": "czce", "name": "纯碱", "code": "SA", "py": "sa", "group": "建材", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "纯碱"},
    {"ex": "czce", "name": "尿素", "code": "UR", "py": "ur", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "尿素"},
    {"ex": "czce", "name": "短纤", "code": "PF", "py": "pf", "group": "能源化工", "night": 1, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "短纤"},
    {"ex": "czce", "name": "对二甲苯", "code": "PX", "py": "px", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "对二甲苯"},
    {"ex": "czce", "name": "烧碱", "code": "SH", "py": "sh", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "烧碱"},
    {"ex": "czce", "name": "瓶片", "code": "PR", "py": "pr", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "瓶片"},
    {"ex": "czce", "name": "丙烯", "code": "PL", "py": "pl", "group": "能源化工", "night": 1, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "丙烯"},
    {"ex": "czce", "name": "硅铁", "code": "SF", "py": "sf", "group": "铁合金", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "硅铁"},
    {"ex": "czce", "name": "锰硅", "code": "SM", "py": "sm", "group": "铁合金", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 0, "kw": "锰硅"},
    {"ex": "cffex", "name": "沪深300指数", "code": "IF", "py": "if", "group": "股指期货", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 1, "kw": "沪深300指数"},
    {"ex": "cffex", "name": "上证50指数", "code": "IH", "py": "ih", "group": "股指期货", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 1, "kw": "上证50指数"},
    {"ex": "cffex", "name": "中证500指数", "code": "IC", "py": "ic", "group": "股指期货", "night": 0, "isNew": 0, "bond": None, "cffexIdx": 1, "kw": "中证500指数"},
    {"ex": "cffex", "name": "中证1000指数", "code": "IM", "py": "im", "group": "股指期货", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 1, "kw": "中证1000指数"},
    {"ex": "cffex", "name": "二债(2年期国债)", "code": "TS", "py": "ts", "group": "国债期货", "night": 0, "isNew": 0, "bond": 2, "cffexIdx": 0, "kw": "二债(2年期国债)"},
    {"ex": "cffex", "name": "五债(5年期国债)", "code": "TF", "py": "tf", "group": "国债期货", "night": 0, "isNew": 0, "bond": 5, "cffexIdx": 0, "kw": "五债(5年期国债)"},
    {"ex": "cffex", "name": "十债(10年期国债)", "code": "T", "py": "t", "group": "国债期货", "night": 0, "isNew": 0, "bond": 10, "cffexIdx": 0, "kw": "十债(10年期国债)"},
    {"ex": "cffex", "name": "三十债(30年期国债)", "code": "TL", "py": "tl", "group": "国债期货", "night": 0, "isNew": 1, "bond": 30, "cffexIdx": 0, "kw": "三十债(30年期国债)"},
    {"ex": "gfex", "name": "工业硅", "code": "SI", "py": "si", "group": "新能源金属", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "工业硅"},
    {"ex": "gfex", "name": "碳酸锂", "code": "LC", "py": "lc", "group": "新能源金属", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "碳酸锂"},
    {"ex": "gfex", "name": "多晶硅", "code": "PS", "py": "ps", "group": "新能源金属", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "多晶硅"},
    {"ex": "gfex", "name": "铂", "code": "PT", "py": "pt", "group": "贵金属", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "铂"},
    {"ex": "gfex", "name": "钯", "code": "PD", "py": "pd", "group": "贵金属", "night": 0, "isNew": 1, "bond": None, "cffexIdx": 0, "kw": "钯"},
]

# 便捷索引
BY_CODE = {v["code"]: v for v in VARIETIES}
GROUP_ORDER = ["有色金属", "贵金属", "黑色金属", "能源化工", "农产品", "油脂油料",
               "软商品", "建材", "林木建材", "铁合金", "新能源金属", "航运指数",
               "股指期货", "国债期货"]


def get_variety(code):
    return BY_CODE.get(code)


def all_varieties():
    return VARIETIES
