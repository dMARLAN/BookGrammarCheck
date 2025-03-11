from core.constants import SOURCE_DIR
from core.types import Color
from processors import XHTMLProcessor, ChaptersProcessor, GrammarProcessor
from processors.gtlt import GTLTReplacer
from utilities import print_color


def __main():
    xhtml_dir = XHTMLProcessor(SOURCE_DIR).process_main()
    grouped_chapters_dir = ChaptersProcessor(xhtml_dir).group_chapters()
    grammar_processed_dir = GrammarProcessor(grouped_chapters_dir).process()
    _ = GTLTReplacer(grammar_processed_dir).process()

    print_color("Done!", Color.BRIGHT_CYAN)


if __name__ == "__main__":
    __main()
