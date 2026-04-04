from .write_small_dots import WriteSmallDots
from .write_special_functions import WriteSpecialFunctions
from .write_text import WriteText


# just a list of commands as attributes
class Command:
    write_text = WriteText
    write_small_dots = WriteSmallDots
    write_special_functions = WriteSpecialFunctions
