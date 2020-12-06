from util.logger import Logger

from base.channel import Channel


class Protocol(Logger):

  def __init__(self, id: str):
    Logger.__init__(self, 'Protocol', id)

    self.id = id
    self.channel = Channel(id)

    self.info('Created')

  def run(self):
    self.info('Started')

  def verify(self) -> bool:
    pass
