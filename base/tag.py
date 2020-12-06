from util.logger import Logger, LogLevel

from base.channel import Channel
from base.listener import Listener
from base.message import Message, MessageKind


class Tag(Listener, Logger):

  def __init__(self, id: str, channel: Channel):
    Logger.__init__(self, LogLevel.TAG, 'Tag', id)

    self.id = id
    self.channel = channel

    self.log('Created')

  def start(self):
    pass

  def receive(self, message: Message):
    if message.kind != MessageKind.READER_TO_TAG:
      return

    self.log(f'Received message with label "{message.label}"')
