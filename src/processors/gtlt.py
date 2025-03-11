from typing import Final

from core.types import Directory


class GTLTReplacer:
    __OUTPUT_DIR_NAME: Final[str] = "gtlt_processed"

    def __init__(self, source_directory: Directory):
        self.__source_directory = source_directory

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
            for line in lines:
                fixed_lines.append(line.replace("&gt;", ">").replace("&lt;", "<"))

            with (output_dir / file.name).open("w", encoding="utf-8") as out:
                out.write("\n".join(fixed_lines))

            print(f"Wrote: {file} \n")

        return output_dir