C_END        = '\33[0m'
C_BOLD       = '\33[1m'
C_ITALIC     = '\33[3m'
C_URL        = '\33[4m'
C_BLINK      = '\33[5m'
C_BLINK2     = '\33[6m'
C_SELECTED   = '\33[7m'

C_BLACK      = '\33[30m'
C_RED        = '\33[31m'
C_GREEN      = '\33[32m'
C_YELLOW     = '\33[33m'
C_BLUE       = '\33[34m'
C_VIOLET     = '\33[35m'
C_BEIGE      = '\33[36m'
C_WHITE      = '\33[37m'

C_BG_BLACK   = '\33[40m'
C_BG_RED     = '\33[41m'
C_BG_GREEN   = '\33[42m'
C_BG_YELLOW  = '\33[43m'
C_BG_BLUE    = '\33[44m'
C_BG_VIOLET  = '\33[45m'
C_BG_BEIGE   = '\33[46m'
C_BG_WHITE   = '\33[47m'

C_GREY       = '\33[90m'
C_RED2       = '\33[91m'
C_GREEN2     = '\33[92m'
C_YELLOW2    = '\33[93m'
C_BLUE2      = '\33[94m'
C_VIOLET2    = '\33[95m'
C_BEIGE2     = '\33[96m'
C_WHITE2     = '\33[97m'

C_BG_GREY    = '\33[100m'
C_BG_RED2    = '\33[101m'
C_BG_GREEN2  = '\33[102m'
C_BG_YELLOW2 = '\33[103m'
C_BG_BLUE2   = '\33[104m'
C_BG_VIOLET2 = '\33[105m'
C_BG_BEIGE2  = '\33[106m'
C_BG_WHITE2  = '\33[107m'


class Logger:
    @staticmethod
    def info(message):
        print(C_BLUE + str(message) + C_END)

    @staticmethod
    def warn(message):
        print(C_YELLOW + str(message) + C_END)

    @staticmethod
    def error(message):
        print(C_RED + C_BLINK + str(message) + C_END)
