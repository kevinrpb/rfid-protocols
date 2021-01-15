from util.logger import Logger, LogLevel

from base.listener import Listener
from base.message import Message
from base.protocol import Protocol


class Attack(Listener, Logger):

  def __init__(self, id: str, protocol: Protocol):
    self.id = f'{id}->{protocol.id}'
    self.protocol = protocol
    self.messages = []

    Logger.__init__(self, LogLevel.ATTACK, 'Attack', self.id)

  def run(self):
    self.log('Started')
