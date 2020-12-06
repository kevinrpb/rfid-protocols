from enum import Enum, Flag, auto

__SPACE__ = 25

class LogLevel(Flag):
  NONE     = 0
  ATTACK   = auto()
  CHANNEL  = auto()
  PROTOCOL = auto()
  READER   = auto()
  TAG      = auto()

  ALL      = ATTACK | CHANNEL | PROTOCOL | READER | TAG
  SIMPLE   = ATTACK | CHANNEL | PROTOCOL

  @staticmethod
  def all():
    return list(map(lambda element: element.name, LogLevel))

  @staticmethod
  def help_list() -> str:
    return f'{{{", ".join(LogLevel.all())}}}'

class LogModifier(Enum):
  RED       = "\033[0;31m"
  GREEN     = "\033[0;32m"
  YELLOW    = "\033[0;33m"
  BLUE      = "\033[0;34m"
  BOLD      = "\033[1m"
  FAINT     = "\033[2m"
  ITALIC    = "\033[3m"
  UNDERLINE = "\033[4m"
  END       = "\033[0m"

class Logger(object):
  n = 1
  _level = LogLevel.ALL

  def __init__(self, level: LogLevel, prefix: str, id: str):
    self.level = level
    self.prefix = prefix
    self.id = id

  def log(self, message: str, modifiers = [LogModifier.YELLOW]):
    if (self.level & Logger._level) != self.level:
      return

    l = len(self.prefix + self.id)
    space = ' ' * (__SPACE__ - l)

    mod = ''.join([mod.value for mod in modifiers])
    end = LogModifier.END.value * len(modifiers)

    print(f'{Logger.n:3d} [{self.prefix}{space}{self.id}] {mod}{message}{end}')

    Logger.n = Logger.n + 1

  def error(self, message: str, exception: Exception = None):
    self.log(message, modifiers = [LogModifier.RED, LogModifier.BOLD])
    if exception is not None:
      raise exception
