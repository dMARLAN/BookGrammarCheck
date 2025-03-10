from core.types import Color


def print_color(text_: str, color: Color) -> None:
    print(f"{color}{text_}{Color.RESET}")
