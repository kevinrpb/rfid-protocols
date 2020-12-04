from base.channel import Channel
from base.listener import Listener
from base.message import Message, MessageKind


class Tag(Listener):

  def __init__(self, id: str, channel: Channel):
    self.id = id
    self.channel = channel

    self.log('Created')

  def start(self):
    pass

  def receive(self, message: Message):
    if message.kind != MessageKind.READER_TO_TAG:
      return

    self.log('Received message with label "{}"'.format(message.label))

  def log(self, message: str):
    print('[Tag.{}] {}'.format(self.id, message))
