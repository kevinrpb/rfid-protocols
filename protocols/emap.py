import os

from base.channel import Channel
from base.message import Message, MessageKind
from base.protocol import Protocol
from base.reader import Reader
from base.tag import Tag

MESSAGE_SIZE_BYTES = 12

# --------------------
# EMAPReader
# --------------------
class EMAPReader(Reader):

  def __init__(self, channel: Channel):
    Reader.__init__(self, 'emap', channel)

  def start(self):
    hello_message = Message(
      label   = 'hello',
      kind    = MessageKind.READER_TO_TAG,
      content = bytearray(0)
    )

    self.channel.send(hello_message)

  def handle_IDS_message(self, message: Message):
    pass

  def receive(self, message: Message):
    super(EMAPReader, self).receive(message)

    if message.id == 'IDS':
      self.handle_IDS_message(message)

# --------------------
# EMAPTag
# --------------------
class EMAPTag(Tag):

  def __init__(self, channel: Channel):
    self.ID  = bytearray(os.urandom(MESSAGE_SIZE_BYTES))
    self.IDS = bytearray(os.urandom(MESSAGE_SIZE_BYTES))
    self.K1  = bytearray(os.urandom(MESSAGE_SIZE_BYTES))
    self.K2  = bytearray(os.urandom(MESSAGE_SIZE_BYTES))
    self.K3  = bytearray(os.urandom(MESSAGE_SIZE_BYTES))
    self.K4  = bytearray(os.urandom(MESSAGE_SIZE_BYTES))

    Tag.__init__(self, 'emap', channel)

  def handle_hello_message(self):
    self.log('Handle "hello" message')

    IDS_message = Message(
      label = 'IDS',
      kind = MessageKind.TAG_TO_READER,
      content = self.IDS
    )

    self.channel.send(IDS_message)

  def receive(self, message: Message):
    super(EMAPTag, self).receive(message)

    if message.label == 'hello':
      self.handle_hello_message()

# --------------------
# EMAPProtocol
# --------------------
class EMAPProtocol(Protocol):

  def __init__(self):
    Protocol.__init__(self, 'emap')

    self.reader = EMAPReader(self.channel)
    self.tag = EMAPTag(self.channel)

    # start Secure channel
    self.reader.K1 = self.tag.K1
    self.reader.K2 = self.tag.K2
    self.reader.K3 = self.tag.K3
    self.reader.K4 = self.tag.K4
    # end Secure channel

    self.channel.listen(self.reader)
    self.channel.listen(self.tag)

  def start(self):
    super(EMAPProtocol, self).start()

    self.reader.start()
    self.tag.start()
