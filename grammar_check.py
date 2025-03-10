import re
from enum import StrEnum
from pathlib import Path
from re import Pattern
from typing import Final

import questionary
from language_tool_python import LanguageTool, Match
from questionary import select, text, Style, Choice

XHTML_DIRECTORY: Final[Path] = Path(r"C:\Users\Nina\Documents\TotCF\source_text\main")
TEXT_DIR = XHTML_DIRECTORY / "txt"
GROUPED_DIR = TEXT_DIR / "grouped"
GRAMMAR_PROCESSED_DIR = GROUPED_DIR / "grammar_processed"
FILE_PATTERN: Final[Pattern] = re.compile(r'^(\d+__)?Chapter_\d+_(.*?)\.txt$')
CHAPTER_HEADER_PATTERN = re.compile(r"^Trash of the Count’s Family\s+–\s+Chapter\s+\d+\s+–.*$")

LANGUAGE_TOOL: Final[LanguageTool] = LanguageTool('en-US')
LANGUAGE_TOOL.disable_spellchecking()
LANGUAGE_TOOL.disabled_rules.add("ENGLISH_WORD_REPEAT_BEGINNING_RULE")

QUESTIONARY_STYLE = Style([
    ("question", "fg:#FFFFFF"),
    ("instruction", "fg:#ecb25f"),
    ("pointer", "fg:#FF9D00"),
    ("selected", "fg:#FF9D00"),
    ("system-choice", "fg:#DDDDDD"),
])
SKIP_OPTION_NAME: Final[str] = "*Skip"
SKIP_CHOICE: Choice = Choice(
    title=[("class:system-choice", "*Skip")]
)
CUSTOM_OPTION_NAME: Final[str] = "*Custom"
CUSTOM_CHOICE: Choice = Choice(
    title=[("class:system-choice", "*Custom")]
)

AUTO_ACCEPT_RULES: Final[set] = {
    "COMMA_COMPOUND_SENTENCE",
    "COMMA_COMPOUND_SENTENCE_2",
    "YEAR_OLD_HYPHEN",
    "NO_COMMA_BEFORE_INDIRECT_QUESTION",
    "ANYWAYS",
    "DIFFERENT_THAN",
    "ALL_OF_THE",
    "EVERYDAY_EVERY_DAY",
    "COMMA_PARENTHESIS_WHITESPACE",
    "FINAL_ADVERB_COMMA",
    "EN_COMPOUNDS_NIGHT_TIME",
    "MISSING_HYPHEN",
    "EN_A_VS_AN",
    "GATHER_UP",
    "BUNCH_OF",
    "RETURN_BACK"
}

AUTO_SKIP_RULES: Final[set] = {
    "CAPITALIZATION_NNP_DERIVED",
}


def __create_groups() -> dict[str, list[Path]]:
    groups = {}

    for file in sorted(TEXT_DIR.glob("*.txt")):
        if match := FILE_PATTERN.match(file.name):
            chapter_title = re.sub(r'_\d+$', '', match.group(2)).replace("_", " ")
            if chapter_title not in groups:
                groups[chapter_title] = []
            groups[chapter_title].append(file)

    return groups


def __write_grouped_chapters():
    if len(list(GRAMMAR_PROCESSED_DIR.iterdir())) > 0:
        return

    groups = __create_groups()

    for index, title in enumerate(groups.keys()):
        out_file = GROUPED_DIR / f"Chapter {index} - {title}.txt"

        with out_file.open("w", encoding="utf-8") as out:
            all_lines = []

            for file in sorted(groups[title]):
                lines = file.read_text(encoding="utf-8").strip().splitlines()
                if lines and CHAPTER_HEADER_PATTERN.match(lines[0]):
                    lines = lines[1:]
                    if lines and not lines[0].strip():
                        lines = lines[1:]
                lines = [line.lstrip() for line in lines]
                all_lines.extend(lines)

            if all_lines:
                out.write("\n".join(all_lines))
            print(f"Wrote: {out_file}")


class Color(StrEnum):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    RESET = "\033[0m"


def __print_color(text_: str, color: Color) -> None:
    print(f"{color}{text_}{Color.RESET}")


def __get_choice(match: Match, line: str, prev_line: str | None, next_line: str | None, offset_correction: int) -> str:
    corrected_offset = match.offset + offset_correction
    highlighted_line = (
        line[:corrected_offset]
        + "\033[91m"
        + line[corrected_offset: corrected_offset + match.errorLength]
        + "\033[0m"
        + line[corrected_offset + match.errorLength:]
    )

    print("\nCONTEXT:")
    if prev_line:
        __print_color(prev_line, Color.BRIGHT_BLACK)

    print("> " + highlighted_line)
    if next_line:
        __print_color(next_line, Color.BRIGHT_BLACK)

    chosen = select(
        message="Choose a replacement",
        choices=[SKIP_CHOICE] + match.replacements + [CUSTOM_CHOICE],
        instruction=f"\nRule: {match.message}\n{match.category} - {match.ruleId}",
        style=QUESTIONARY_STYLE,
    ).ask()

    if chosen is None:
        exit(0)

    return chosen


def __fix_grammar(line: str, prev_line: str | None, next_line: str | None) -> str:
    offset_correction = 0

    for match in LANGUAGE_TOOL.check(line):
        if (
            "Add a space between sentences." in match.message
            and any(["…" in line, "..." in line])
        ):
            __print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
            continue

        if "gallon" in line and "Possible agreement error" in match.message:
            __print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
            continue

        if match.ruleId in AUTO_SKIP_RULES:
            __print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
            continue

        if match.ruleId in AUTO_ACCEPT_RULES:
            __print_color(f"Automatically accepted RuleID: {match.ruleId}", Color.GREEN)
            chosen = match.replacements[0]
        else:
            chosen = __get_choice(match, line, prev_line, next_line, offset_correction)

        if chosen == SKIP_OPTION_NAME:
            continue

        if chosen == CUSTOM_OPTION_NAME:
            line = text(
                message="Enter custom replacement",
                default=line,
            ).ask()
            break

        line = (
            line[: match.offset + offset_correction]
            + chosen
            + line[match.offset + offset_correction + match.errorLength:]
        )
        offset_correction += len(chosen) - match.errorLength

    if line.strip():
        __print_color(f"Line: {line}", Color.BRIGHT_BLACK)

    return line


def __sort_natural_key(s: str) -> list:
    return [int(text_) if text_.isdigit() else text_.lower() for text_ in re.split(r'(\d+)', s)]


def __get_prev_non_blank(lines, index):
    for j in range(index - 1, -1, -1):
        if lines[j].strip():
            return lines[j]
    return ""


def __get_next_non_blank(lines, index):
    for j in range(index + 1, len(lines)):
        if lines[j].strip():
            return lines[j]
    return ""


def __write_grammar_processed():
    grammar_processed_file_names = [file.stem for file in GRAMMAR_PROCESSED_DIR.iterdir() if file.is_file()]
    files_to_process = sorted([
        file for file in GROUPED_DIR.iterdir()
        if file.stem not in grammar_processed_file_names and file.is_file()
    ],
        key=lambda file: __sort_natural_key(file.stem)
    )

    for file in files_to_process:
        print(f"Processing: {file.name}")
        lines = file.read_text(encoding="utf-8").splitlines()

        fixed_lines = []
        for i, line in enumerate(lines):
            prev_line = __get_prev_non_blank(lines, i) if i > 0 else ""
            next_line = __get_next_non_blank(lines, i) if i < len(lines) - 1 else ""
            fixed_lines.append(__fix_grammar(line, prev_line, next_line))

        with (GRAMMAR_PROCESSED_DIR / file.name).open("w", encoding="utf-8") as out:
            out.write("\n".join(fixed_lines))
        print(f"Wrote: {file} \n\n\n")

        questionary.press_any_key_to_continue().ask()


def __write_text_files_from_xtml_files() -> None:
    if len(list(GRAMMAR_PROCESSED_DIR.iterdir())) > 0:
        return

    for file in XHTML_DIRECTORY.iterdir():
        if file.suffix == ".xhtml":
            content = file.read_text(encoding="utf-8")
            text_only = re.sub(r"<[^>]*>", "", content).strip()
            (TEXT_DIR / file.with_suffix(".txt").name).write_text(text_only, encoding="utf-8")
        print(f"Wrote: {file}")


def __create_out_dirs():
    dirs = [TEXT_DIR, GROUPED_DIR, GRAMMAR_PROCESSED_DIR]
    for dir_ in dirs:
        if not dir_.exists():
            dir_.mkdir(exist_ok=True, parents=True)
            print(f"Created: {dir_}")


def __main():
    __create_out_dirs()

    if list([file for file in GROUPED_DIR.iterdir() if file.is_file()]):
        print("Grouped files already exist. Skipping grouping.")
    else:
        __write_text_files_from_xtml_files()
        __write_grouped_chapters()

    __write_grammar_processed()


if __name__ == "__main__":
    __main()
