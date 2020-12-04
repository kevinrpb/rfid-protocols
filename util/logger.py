from enum import IntEnum

class LogLevel(IntEnum):
  NONE    = 0
  ERROR   = 1
  WARNING = 2
  INFO    = 3

class Logger(object):
  n = 1
  level = LogLevel.INFO

  def __init__(self, prefix: str, id: str):
    self.prefix = prefix
    self.id = id

  def _log(self, message: str):
    l = len(self.prefix + self.id)
    space = ' ' * (20 - l)

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
