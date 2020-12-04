from enum import Enum

from bitarray import bitarray


class MessageKind(Enum):
  READER_TO_TAG = 0
  TAG_TO_READER = 1

  def __str__(self) -> str:
    if self == MessageKind.READER_TO_TAG:
      return 'READER_TO_TAG'
    elif self == MessageKind.TAG_TO_READER:
      return 'TAG_TO_READER'
    else:
      return ''

class Message(object):
  def __init__(self, label: str, kind: MessageKind, content: bitarray):
    self.label = label
    self.kind = kind
    self.content = content

  def size(self) -> int:
    return self.content.length()
