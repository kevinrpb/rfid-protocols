from base.protocol import Protocol
from util.logger import Logger

class Attack(Logger):

  def __init__(self, id: str, protocol: Protocol):
    self.id = f'{id}->{protocol.id}'
    self.protocol = protocol

    Logger.__init__(self, 'Attack', self.id)


  def run(self):
    self.info('Started')
