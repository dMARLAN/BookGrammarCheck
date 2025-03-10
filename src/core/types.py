import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterator, Self


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


@dataclass
class Lines:
    prev_line: str | None
    line: str
    next_line: str | None


class File(Path):
    def __init__(self, *args):
        super().__init__(*args)


class Files:
    def __init__(self, files: list[File]):
        self.__files = files

    @staticmethod
    def __sort_natural_key(s: str) -> list:
        return [int(text_) if text_.isdigit() else text_.lower() for text_ in re.split(r'(\d+)', s)]

    def natural_sort(self) -> Self:
        self.__files = sorted(self.__files, key=lambda file: self.__sort_natural_key(file.name))
        return self

    def glob(self, pattern) -> Iterator[File]:
        yield from (
            file for file in self.__files if file.match(pattern)
        )

    def __iter__(self):
        return iter(self.__files)


class Directory(Path):
    def glob(self, pattern, *, case_sensitive=None) -> Iterator[File | Self]:
        yield from (
            File(file) if file.is_file() else Directory(file)
            for file in super().glob(pattern)
        )

    def iterdir(self) -> Iterator[File | Self]:
        yield from (
            File(file) if file.is_file() else Directory(file)
            for file in super().iterdir()
        )

    def files(self) -> list[File]:
        return [File(file) for file in self.iterdir() if file.is_file()]

    def file_names(self) -> list[str]:
        return [file.name for file in self.files()]

    def file_stems(self) -> list[str]:
        return [file.stem for file in self.files()]

    def num_files(self) -> int:
        return len(self.files())

    @classmethod
    def difference_file_stems(cls, return_directory: "Directory", diff_directory: "Directory") -> Files:
        dir2_stems = {file.stem for file in diff_directory.files()}
        return Files([file for file in return_directory.files() if file.stem not in dir2_stems])

    @classmethod
    def from_path(cls, path: Path) -> "Directory":
        if not path.is_dir():
            raise FileNotFoundError(f"{path} is not a directory.")
        return cls(path)
