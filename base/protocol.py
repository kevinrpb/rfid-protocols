from util.logger import Logger, LogLevel

from base.channel import Channel


class Protocol(Logger):

  def __init__(self, id: str):
    Logger.__init__(self, LogLevel.PROTOCOL, 'Protocol', id)

    self.id = id
    self.channel = Channel(id)

    self.log('Created')

  def run(self):
    self.log('Started')

  def verify(self) -> bool:
    return False
