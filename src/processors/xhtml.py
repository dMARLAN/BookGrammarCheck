import re
from re import Pattern
from typing import Final

from core.types import Directory


class XHTMLProcessor:
    __TEXT_ONLY_PATTERN: Final[Pattern] = re.compile(r"<[^>]*>")
    __OUTPUT_DIR_NAME: Final[str] = "txt"

    def __init__(self, source_files_dir: Directory):
        self.__source_files_dir = source_files_dir

    def process_main(self) -> Directory:
        main_source_files_dir = self.__source_files_dir / "main"
        main_source_files_dir.mkdir(exist_ok=True)

        output_dir = main_source_files_dir / self.__OUTPUT_DIR_NAME
        output_dir.mkdir(exist_ok=True)

        files_to_process = (
            Directory.difference_file_stems(
                return_directory=main_source_files_dir,
                diff_directory=output_dir,
            )
            .natural_sort()
            .glob("*.xhtml")
        )

        for file in files_to_process:
            content = file.read_text(encoding="utf-8")
            text_only = re.sub(self.__TEXT_ONLY_PATTERN, "", content).strip()
            (output_dir / file.with_suffix(".txt").name).write_text(text_only, encoding="utf-8")
            print(f"Wrote: {file}")

        return output_dir
