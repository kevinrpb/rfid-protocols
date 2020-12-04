from base.listener import Listener
from base.message import Message


class Channel(object):
  def __init__(self, id: str):
    self.id = id
    self.listeners = []

    self.log('Created')

  def listen(self, listener: Listener):
    self.listeners.append(listener)

  def send(self, message: Message):
    self.log(
      'Message (kind: {}, label: {}, size: {} bits)'.format(message.kind, message.label, message.size())
    )

    for listener in self.listeners:
      if isinstance(listener, Listener):
        listener.receive(message)

  def log(self, message: str):
    print('[Channel.{}] {}'.format(self.id, message))
