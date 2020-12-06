from enum import IntEnum

__SPACE__ = 25

class LogLevel(IntEnum):
  NONE    = 0
  ERROR   = 1
  WARNING = 2
  INFO    = 3

  @staticmethod
  def names() -> str:
    return ['NONE', 'ERROR', 'WARNING', 'INFO']

  @staticmethod
  def names_description() -> str:
    return f'{{{", ".join(LogLevel.names())}}}'

class Logger(object):
  n = 1
  level = LogLevel.INFO

  def __init__(self, prefix: str, id: str):
    self.prefix = prefix
    self.id = id

  def _log(self, message: str):
    l = len(self.prefix + self.id)
    space = ' ' * (__SPACE__ - l)

    print(f'{Logger.n:3d} [{self.prefix}{space}{self.id}] {message}')

    Logger.n = Logger.n + 1

  def info(self, message: str):
    if Logger.level > LogLevel.WARNING:
      self._log(message)

  def warning(self, message: str):
    if Logger.level > LogLeve.ERROR:
      self._log(message)

  def error(self, message: str):
    if Logger.level > LogLeve.NONE:
      self._log(message)
