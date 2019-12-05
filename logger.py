from enum import Enum


class Logger:
    class TextColor(Enum):
        END = '\33[0m'
        BOLD = '\33[1m'
        ITALIC = '\33[3m'
        URL = '\33[4m'
        BLINK = '\33[5m'
        BLINK2 = '\33[6m'
        SELECTED = '\33[7m'

        BLACK = '\33[30m'
        RED = '\33[31m'
        GREEN = '\33[32m'
        YELLOW = '\33[33m'
        BLUE = '\33[34m'
        VIOLET = '\33[35m'
        BEIGE = '\33[36m'
        WHITE = '\33[37m'

        BG_BLACK = '\33[40m'
        BG_RED = '\33[41m'
        BG_GREEN = '\33[42m'
        BG_YELLOW = '\33[43m'
        BG_BLUE = '\33[44m'
        BG_VIOLET = '\33[45m'
        BG_BEIGE = '\33[46m'
        BG_WHITE = '\33[47m'

        GREY = '\33[90m'
        RED2 = '\33[91m'
        GREEN2 = '\33[92m'
        YELLOW2 = '\33[93m'
        BLUE2 = '\33[94m'
        VIOLET2 = '\33[95m'
        BEIGE2 = '\33[96m'
        WHITE2 = '\33[97m'

        BG_GREY = '\33[100m'
        BG_RED2 = '\33[101m'
        BG_GREEN2 = '\33[102m'
        BG_YELLOW2 = '\33[103m'
        BG_BLUE2 = '\33[104m'
        BG_VIOLET2 = '\33[105m'
        BG_BEIGE2 = '\33[106m'
        BG_WHITE2 = '\33[107m'

    @staticmethod
    def info(message):
        Logger.color(str(message), Logger.TextColor.VIOLET)

    @staticmethod
    def warn(message):
        Logger.color(str(message), Logger.TextColor.YELLOW)

    @staticmethod
    def error(message):
        Logger.color(str(message), Logger.TextColor.BG_RED)

    @staticmethod
    def color(message, color: TextColor):
        print(color.value + str(message) + Logger.TextColor.END.value)
