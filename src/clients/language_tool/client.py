from typing import Final

from language_tool_python import LanguageTool as LanguageTool_, Match
from questionary import select, text

from clients.language_tool.constants import (
    QUESTIONARY_STYLE,
    SKIP_OPTION_NAME,
    CUSTOM_OPTION_NAME,
    DEFAULT_LANGUAGE,
    AUTO_SKIPPED_RULES,
    AUTO_ACCEPTED_RULES, AUTO_ACCEPTED_RULE_GROUPS,
)
from core.types import Color, Lines
from utilities import print_color


class LanguageToolClient:
    __LANGUAGE_TOOL: Final[LanguageTool_] = LanguageTool_(DEFAULT_LANGUAGE)
    __LANGUAGE_TOOL.disable_spellchecking()
    __LANGUAGE_TOOL.disabled_rules.add("ENGLISH_WORD_REPEAT_BEGINNING_RULE")

    @staticmethod
    def __get_choice(match: Match, lines: Lines, offset_correction: int) -> str:
        corrected_offset = match.offset + offset_correction
        highlighted_line = (
            lines.line[:corrected_offset]
            + "\033[91m"
            + lines.line[corrected_offset: corrected_offset + match.errorLength]
            + "\033[0m"
            + lines.line[corrected_offset + match.errorLength:]
        )

        print("\nCONTEXT:")
        if lines.prev_line:
            print_color(lines.prev_line, Color.BRIGHT_BLACK)

        print("> " + highlighted_line)
        if lines.next_line:
            print_color(lines.next_line, Color.BRIGHT_BLACK)

        chosen = select(
            message="Choose a replacement",
            choices=[SKIP_OPTION_NAME] + match.replacements + [CUSTOM_OPTION_NAME],
            instruction=f"\nRule: {match.message}\n{match.category} - {match.ruleId}",
            style=QUESTIONARY_STYLE,
        ).ask()

        if chosen is None:
            exit(0)

        return chosen

    def check_lines(self, lines: Lines) -> Lines:
        offset = 0

        for match in self.__LANGUAGE_TOOL.check(lines.line):
            if (
                "Add a space between sentences." in match.message
                and any(["…" in lines.line, "..." in lines.line])
            ):
                print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
                continue

            if "gallon" in lines.line and "Possible agreement error" in match.message:
                print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
                continue

            if match.ruleId in AUTO_SKIPPED_RULES:
                print_color(f"Skipped RuleID: {match.ruleId}", Color.BLUE)
                continue

            if (
                match.ruleId in AUTO_ACCEPTED_RULES
                or any([group in match.ruleId for group in AUTO_ACCEPTED_RULE_GROUPS])
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
                lines.line[: match.offset + offset]
                + choice
                + lines.line[match.offset + offset + match.errorLength:]
            )
            offset += len(choice) - match.errorLength

        if lines.line.strip():
            print_color(f"Line: {lines.line}", Color.BRIGHT_BLACK)

        return lines
