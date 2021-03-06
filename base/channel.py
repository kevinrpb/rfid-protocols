from util.logger import Logger, LogLevel

from base.listener import Listener
from base.message import Message


class Channel(Logger):
  def __init__(self, id: str):
    Logger.__init__(self, LogLevel.CHANNEL, 'Channel', id)

    self.id = id
    self.listeners = []

    self.log('Created')

  def listen(self, listener: Listener):
    self.listeners.append(listener)

  def send(self, message: Message):
    self.log(
      f'Message (kind: {message.kind}, label: {message.label}, size: {message.size()} bits)'
    )

    for listener in self.listeners:
      if isinstance(listener, Listener):
        listener.receive(message)
