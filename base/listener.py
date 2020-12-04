from abc import ABC, abstractmethod

from base.message import Message


class Listener(ABC):
  def receive(self, message: Message):
    pass
