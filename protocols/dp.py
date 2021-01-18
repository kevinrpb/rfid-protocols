from base.channel import Channel
from base.message import Message, MessageKind
from base.protocol import Protocol
from base.reader import Reader
from base.tag import Tag
from bitarray import bitarray

MESSAGE_SIZE = 96

# --------------------
# Functions
# --------------------

# --------------------
# DPReader
# --------------------
class DPReader(Reader):

  def __init__(self, channel: Channel):
    self.PID  = None
    self.PID2 = None
    self.K1   = None
    self.K2   = None
    self.n1   = None
    self.n2   = None

    Reader.__init__(self, 'emap', channel)

  def start(self):
    """Starts the protocol by sending the hello message.
    """
    if self.K1 is None or len(self.K1) != MESSAGE_SIZE:
      self.error('Missing K1 or incorrect size')
    if self.K2 is None or len(self.K2) != MESSAGE_SIZE:
      self.error('Missing K2 or incorrect size')

    hello_message = Message(
      label   = 'hello',
      kind    = MessageKind.READER_TO_TAG,
      content = bitarray(0)
    )

    self.log('Sent hello message')
    self.channel.send(hello_message)

  def update(self):
    """Updates the keys and PID of the tag. This should happen once authentication is over.
    """
    self.PID = self.PID2
    self.PID2 = self.PID2 ^ self.n1 ^ self.n2

  def handle_PID2_message(self, message: Message):
    """Handles message containing PID2 from the tag.

    Args:
        message (Message): The message that contains the PID2
    """
    # Capture PID2
    self.PID2 = message.content
    if self.PID2 is None or len(self.PID2) != MESSAGE_SIZE:
      self.error('Missing PID2 or incorrect size')

    self.log('PID2 Valid')

    # First, create n1 & n2
    self.n1 = bitarray(MESSAGE_SIZE)
    self.n2 = bitarray(MESSAGE_SIZE)

    self.log('Created n1, n2')

    # Then, create A, B, C
    A = (self.PID2 & self.K1 & self.K2) ^ self.n1
    B = (self.PID2 & self.K2 & self.K1) ^ self.n2
    D = (self.K1 & self.n2) ^ (self.K2 & self.n1)

    self.log('Created A, B, D')

    # Create and send message
    content = bitarray(0)
    content.extend(A)
    content.extend(B)
    content.extend(D)

    # Create and send message
    content = bitarray(0)
    content.extend(A)
    content.extend(B)
    content.extend(D)

    abd_message = Message(
      label   = 'ABD',
      kind    = MessageKind.READER_TO_TAG,
      content = content
    )

    self.log('Sent ABD message')
    self.channel.send(abd_message)

  def handle_EF_message(self, message: Message):
    """Handles the message containing E and F from the tag.

    Args:
        message (Message): The message containing E || F
    """
    EF = message.content
    if EF is None or len(EF) != 2 * MESSAGE_SIZE:
      self.error('Missing EF or incorrect size')

    # Get D, E
    E = EF[:MESSAGE_SIZE]
    F = EF[MESSAGE_SIZE:]

    self.log('Got E, F')

    # Verify F
    _F = (self.K1 & self.n1) ^ (self.K2 & self.n2)

    if _F != F:
      self.error('Incorrect F received')
    else:
      self.log('Tag verified')

    # Extract PID
    self.PID = self.K1 ^ self.n1 ^ (E ^ (self.K2 & self.n2))

    self.log('Got PID')

    # Update PIDs
    self.update()

  def receive(self, message: Message):
    super(DPReader, self).receive(message)

    if message.label == 'PID2':
      self.handle_PID2_message(message)
    elif message.label == 'EF':
      self.handle_EF_message(message)

# --------------------
# DPTag
# --------------------
class DPTag(Tag):

  def __init__(self, channel: Channel):
    self.PID  = bitarray(MESSAGE_SIZE)
    self.PID2 = bitarray(MESSAGE_SIZE)
    self.K1   = bitarray(MESSAGE_SIZE)
    self.K2   = bitarray(MESSAGE_SIZE)
    self.n1   = None
    self.n2   = None

    Tag.__init__(self, 'emap', channel)

  def reset(self):
    pass

  def update(self):
    """
    """
    self.PID = self.PID2
    self.PID2 = self.PID2 ^ self.n1 ^ self.n2

  def handle_hello_message(self):
    """Handles initial hello message from the reader.
    """
    PID2_message = Message(
      label = 'PID2',
      kind = MessageKind.TAG_TO_READER,
      content = self.PID2
    )

    self.log('Sent "PID2" message')
    self.channel.send(PID2_message)

  def handle_ABD_message(self, message: Message):
    """Handles message containing A, B, and D from the reader.

    Args:
        message (Message): The message containing A || B || D
    """
    ABD = message.content
    if ABD is None or len(ABD) != 3 * MESSAGE_SIZE:
      self.error('Missing ABD or incorrect size')

    # Get A, B, D
    A = ABD[:MESSAGE_SIZE]
    B = ABD[MESSAGE_SIZE:2*MESSAGE_SIZE]
    D = ABD[2*MESSAGE_SIZE:]

    self.log('Got A, B, D')

    # Get n1, n2
    n1 = (self.PID2 & self.K1 & self.K2) ^ A
    n2 = (self.PID2 & self.K2 & self.K1) ^ B

    _D = (self.K1 & n2) ^ (self.K2 & n1)

    if D != _D:
      self.error('Error in D verification')
    else:
      self.n1 = n1
      self.n2 = n2
      self.log('Got n1, n2. Reader verified')

    # Create E, F
    E = (self.K1 ^ self.n1 ^ self.PID) ^ (self.K2 & self.n2)
    F = (self.K1 & self.n1) ^ (self.K2 & self.n2)

    self.log('Created E, F')

    # Create message and send
    content = bitarray(0)
    content.extend(E)
    content.extend(F)

    ef_message = Message(
      label   = 'EF',
      kind    = MessageKind.TAG_TO_READER,
      content = content
    )

    self.log('Sent EF message')

    # Update keys in b4
    self.update()

    self.channel.send(ef_message)

  def receive(self, message: Message):
    super(DPTag, self).receive(message)

    if message.label == 'hello':
      self.handle_hello_message()
    elif message.label == 'ABD':
      self.handle_ABD_message(message)

# --------------------
# DPProtocol
# --------------------
class DPProtocol(Protocol):

  def __init__(self):
    Protocol.__init__(self, 'dp')

    self.reader = DPReader(self.channel)
    self.tag = DPTag(self.channel)

    # start Secure channel
    self.reader.K1 = self.tag.K1
    self.reader.K2 = self.tag.K2
    self.log('Transferred secret keys through secure channel')
    # end Secure channel

    self.channel.listen(self.reader)
    self.channel.listen(self.tag)

  def run(self):
    super(DPProtocol, self).run()

    self.reader.start()
    self.log('End')

  def verify(self) -> bool:
    if self.reader.PID != self.tag.PID:
      self.error('PID verification mismatch')
      return False

    if self.reader.PID2 != self.tag.PID2:
      self.error('PID2 verification mismatch')
      return False

    if self.reader.K1 != self.tag.K1:
      self.error('K1 verification mismatch')
      return False

    if self.reader.K2 != self.tag.K2:
      self.error('K2 verification mismatch')
      return False

    if self.reader.n1 != self.tag.n1:
      self.error('n1 verification mismatch')
      return False

    if self.reader.n2 != self.tag.n2:
      self.error('n2 verification mismatch')
      return False

    self.success('Verification successful')
    return True
