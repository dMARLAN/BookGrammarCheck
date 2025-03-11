from typing import Final

import questionary

from clients import LanguageToolClient
from core.types import Directory, Lines


class GrammarProcessor:
    __OUTPUT_DIR_NAME: Final[str] = "grammar_processed"

    def __init__(self, source_directory: Directory):
        self.__source_directory = source_directory
        self.__language_tool = LanguageToolClient()

    @staticmethod
    def __get_prev_non_blank(lines, index, count=2):
        result = []
        for j in range(index - 1, -1, -1):
            if lines[j].strip():
                result.append(lines[j])
                if len(result) == count:
                    break
        return result[::-1]

    @staticmethod
    def __get_next_non_blank(lines, index, count=2):
        result = []
        for j in range(index + 1, len(lines)):
            if lines[j].strip():
                result.append(lines[j])
                if len(result) == count:
                    break
        return result

    def process(self) -> Directory:
        output_dir = self.__source_directory / self.__OUTPUT_DIR_NAME
        output_dir.mkdir(exist_ok=True)

        files_to_process = Directory.difference_file_stems(
            return_directory=self.__source_directory,
            diff_directory=output_dir,
        ).natural_sort()

        for file in files_to_process:
            print(f"Processing: {file.name}")
            lines = file.read_text(encoding="utf-8").splitlines()

            fixed_lines = []
            for i, line in enumerate(lines):
                fixed_lines.append(
                    self.__language_tool.check_lines(
                        Lines(
                            prev_lines=self.__get_prev_non_blank(lines, i, count=3) if i > 0 else [],
                            line=line,
                            next_lines=self.__get_next_non_blank(lines, i, count=3) if i < len(lines) - 1 else [],
                        )
                    ).line
                )

            with (output_dir / file.name).open("w", encoding="utf-8") as out:
                out.write("\n".join(fixed_lines))
            print(f"Wrote: {file} \n")

            response = questionary.press_any_key_to_continue(
                message=f"Finished processing: {file.name}, press any key to continue..."
            ).ask()
            if response is None:
                exit(0)

        return output_dir
