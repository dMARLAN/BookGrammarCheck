from typing import Final

from questionary import Style

QUESTIONARY_STYLE = Style([
    ("question", "fg:#FFFFFF"),
    ("instruction", "fg:#ecb25f"),
    ("pointer", "fg:#FF9D00"),
    ("selected", "fg:#FF9D00"),
    ("system-choice", "fg:#DDDDDD"),
])
SKIP_OPTION_NAME: Final[str] = "*Skip"
CUSTOM_OPTION_NAME: Final[str] = "*Custom"

DEFAULT_LANGUAGE: Final[str] = "en-US"
AUTO_ACCEPTED_RULES: Final[set] = {
    "COMMA_COMPOUND_SENTENCE",
    "COMMA_COMPOUND_SENTENCE_2",
    "NO_COMMA_BEFORE_INDIRECT_QUESTION",
    "ANYWAYS",
    "DIFFERENT_THAN",
    "ALL_OF_THE",
    "EVERYDAY_EVERY_DAY",
    "COMMA_PARENTHESIS_WHITESPACE",
    "FINAL_ADVERB_COMMA",
    "EN_COMPOUNDS_NIGHT_TIME",
    "EN_A_VS_AN",
    "GATHER_UP",
    "BUNCH_OF",
    "RETURN_BACK",
    "THE_PUNCT",
    "FIRST_SERVED",
    "A_UNCOUNTABLE",
    "OUTSIDE_OF",
    "CONSECUTIVE_SPACES",
}
AUTO_ACCEPTED_RULE_GROUPS: Final[set] = {
    "_HYPHEN",
    "_COMPOUNDS",
}
AUTO_SKIPPED_RULES: Final[set] = {
    "CAPITALIZATION_NNP_DERIVED",
}
