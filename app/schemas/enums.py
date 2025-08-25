from enum import Enum

class LanguageEnum(str, Enum):
    uzbek = "uzbek"
    russian = "russian"
    karakalpak = "karakalpak"
    english = "english"

class FontTypeEnum(str, Enum):
    kirill = "kirill"
    latin = "latin"
    english = "english"

# Генерируем Enum автоматически
YearEnum = Enum(
    "YearEnum",
    {f"y{year}": year for year in range(1991, 2026)},
    type=int,
)

class ConditionEnum(str, Enum):
    actual = "actual"
    unactual = "unactual"

class UsageStatusEnum(str, Enum):
    use = "use"
    unused = "unused"
