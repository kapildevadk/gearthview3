"""
This module provides console text formatting options.
For usage, please refer to the helper.py module.
"""

class Format:
    CLEAR = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERSCORE = 4
    BLINK_SLOW = 5
    BLINK_FAST = 6
    REVERSE = 7
    CONCEALED = 8

    class Colors:
        FG_BLACK = 30
        FG_RED = 31
        FG_GREEN = 32
        FG_YELLOW = 33
        FG_BLUE = 34
        FG_MAGENTA = 35
        FG_CYAN = 36
        FG_WHITE = 37

        BG_BLACK = 40
        BG_RED = 41
        BG_GREEN = 42
        BG_YELLOW = 43
        BG_BLUE = 44
        BG_MAGENTA = 45
        BG_CYAN = 46
        BG_WHITE = 47
