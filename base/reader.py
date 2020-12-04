from base.channel import Channel
from base.listener import Listener
from base.message import Message, MessageKind


class Reader(Listener):

  def __init__(self, id: str, channel: Channel):
    self.id = id
    self.channel = channel

    self.log('Created')

  def start(self):
    pass

  def receive(self, message: Message):
    if message.kind != MessageKind.TAG_TO_READER:
      return

    self.log('Received message with label "{}"'.format(message.label))

  def log(self, message: str):
    print('[Reader.{}] {}'.format(self.id, message))
