import shutil
from typing import Final

from language_tool_python import LanguageTool as LanguageTool_, Match
from questionary import select, text, Choice

from clients.language_tool.constants import (
    QUESTIONARY_STYLE,
    SKIP_OPTION_NAME,
    CUSTOM_OPTION_NAME,
    DEFAULT_LANGUAGE,
    DISABLED_RULES,
    AUTO_ACCEPTED_RULES,
    AUTO_ACCEPTED_RULE_GROUPS,
)
from core.types import Color, Lines
from utilities import print_color


class LanguageToolClient:
    __LANGUAGE_TOOL: Final[LanguageTool_] = LanguageTool_(DEFAULT_LANGUAGE)
    __LANGUAGE_TOOL.disable_spellchecking()
    __LANGUAGE_TOOL.disabled_rules.update(DISABLED_RULES)

    @staticmethod
    def __get_choice(match: Match, lines: Lines, offset_correction: int) -> str:
        assert match.offset is not None, "Match offset is None"
        assert match.errorLength is not None, "Match error length is None"

        corrected_offset = match.offset + offset_correction
        highlighted_line = (
            lines.line[:corrected_offset]
            + "\033[91m"
            + lines.line[corrected_offset : corrected_offset + match.errorLength]
            + "\033[0m"
            + lines.line[corrected_offset + match.errorLength :]
        )

        terminal_width = shutil.get_terminal_size().columns

        print_color("\n*** CONTEXT " + "*" * (terminal_width - 12), Color.CYAN)
        for i, prev_line in enumerate(lines.prev_lines):
            label = f"-{len(lines.prev_lines) - i}: "
            print_color(label + prev_line, Color.BRIGHT_BLACK)

        print(" 0: " + highlighted_line)
        for i, next_line in enumerate(lines.next_lines, start=1):
            label = f"+{i}: "
            print_color(label + next_line, Color.BRIGHT_BLACK)
        print_color("\n" + "*" * shutil.get_terminal_size().columns, Color.CYAN)

        replacements_choices = [
            Choice(
                title=replacement.replace(" ", "␣") if replacement else "×Blank",
                value=replacement,
            )
            for replacement in match.replacements
        ]

        chosen = select(
            message="Choose a replacement",
            choices=[SKIP_OPTION_NAME] + replacements_choices + [CUSTOM_OPTION_NAME],
            instruction=f"\nRule: {match.message}\n{match.category} - {match.ruleId}",
            style=QUESTIONARY_STYLE,
        ).ask()

        if chosen is None:
            exit(0)

        return chosen

    def check_lines(self, lines: Lines) -> Lines:
        offset = 0

        for match in self.__LANGUAGE_TOOL.check(lines.line):
            assert match.offset is not None, "Match offset is None"
            assert match.errorLength is not None, "Match error length is None"
            assert match.replacements is not None, "Match replacements are None"
            assert match.message is not None, "Match message is None"

            if "Add a space between sentences." in match.message and any(["…" in lines.line, "..." in lines.line]):
                print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
                continue

            if "gallon" in lines.line and "Possible agreement error" in match.message:
                print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
                continue

            if match.ruleId in AUTO_ACCEPTED_RULES or any(
                [group in match.ruleId for group in AUTO_ACCEPTED_RULE_GROUPS]
            ):
                print_color(f"Automatically accepted RuleID: {match.ruleId}", Color.GREEN)
                choice = match.replacements[0]
            else:
                choice = self.__get_choice(match, lines, offset)

            if choice == SKIP_OPTION_NAME:
                continue

            if choice == CUSTOM_OPTION_NAME:
                lines.line = text(
                    message="Enter custom replacement",
                    default=lines.line,
                ).ask()
                break

            lines.line = (
                lines.line[: match.offset + offset] + choice + lines.line[match.offset + offset + match.errorLength :]
            )
            offset += len(choice) - match.errorLength

        if lines.line.strip():
            print_color(f"Line: {lines.line}", Color.BRIGHT_BLACK)

        return lines
