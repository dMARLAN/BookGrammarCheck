import re
from re import Pattern
from typing import Final

from core.types import Directory, Color
from utilities import print_color


class ChaptersProcessor:
    __FILE_PATTERN: Final[Pattern] = re.compile(r'^(\d+__)?Chapter_\d+_(.*?)\.txt$')
    __CHAPTER_HEADER_PATTERN: Final[Pattern] = re.compile(r"^Trash of the Count’s Family\s+–\s+Chapter\s+\d+\s+–.*$")
    __OUTPUT_DIR_NAME: Final[str] = "grouped_chapters"

    def __init__(self, source_files_dir: Directory):
        self.__source_files_dir = source_files_dir

    def __create_groups(self):
        groups = {}

        for file in sorted(self.__source_files_dir.glob("*.txt")):
            if match := self.__FILE_PATTERN.match(file.name):
                chapter_title = re.sub(r'_\d+$', '', match.group(2)).replace("_", " ")
                if chapter_title not in groups:
                    groups[chapter_title] = []
                groups[chapter_title].append(file)

        return groups

    def group_chapters(self) -> Directory:
        groups = self.__create_groups()

        output_dir = self.__source_files_dir / self.__OUTPUT_DIR_NAME
        output_dir.mkdir(exist_ok=True)

        for index, title in enumerate(groups.keys()):
            out_file = output_dir / f"Chapter {index} - {title}.txt"

            if out_file.exists():
                continue

            with out_file.open("w", encoding="utf-8") as out:
                all_lines = []

                for file in sorted(groups[title]):
                    lines = file.read_text(encoding="utf-8").strip().splitlines()
                    if lines and self.__CHAPTER_HEADER_PATTERN.match(lines[0]):
                        lines = lines[1:]
                        if lines and not lines[0].strip():
                            lines = lines[1:]
                    lines = [line.lstrip() for line in lines]
                    all_lines.extend(lines)

                if all_lines:
                    out.write("\n".join(all_lines))

                print_color(f"Wrote: {out_file}", Color.BLUE)

        return output_dir
