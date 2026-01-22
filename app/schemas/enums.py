from enum import Enum

class LanguageEnum(str, Enum):
    uzbek = "o'zbek"
    russian = "rus"
    karakalpak = "qoraqolpoq"
    english = "ingliz"


class FontTypeEnum(str, Enum):
    kirill = "kirill"
    latin = "lotin"
    english = "ingliz"


class ConditionEnum(str, Enum):
    actual = "Zamon talabiga mos"
    unactual = "Zamon talabiga mos emas"


class UsageStatusEnum(str, Enum):
    use = "Fan dasturida foydalaniladi"
    unused = "Fan dasturida foydalanilmaydi"
