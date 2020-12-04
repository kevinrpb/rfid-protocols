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
def parity(b: bitarray, n: int = 4) -> bitarray:
  # Divide in chunks of 4 bits
  chunks = [b[i:i + n] for i in range(0, len(b), n)]

  # Calc parity for each chunk
  parities = [c.count(True) % 2 == 0 for c in chunks]

  # Return bitarray
  return bitarray(parities)

def update(ID: bitarray, IDS: bitarray, K1: bitarray, K2: bitarray, K3: bitarray, K4: bitarray, n1: bitarray, n2: bitarray):
  IDS_ = IDS ^ n2 ^ K1

  idx = int(MESSAGE_SIZE/2)

  K1_delta = ID[:idx]
  K1_delta.extend(parity(K4))
  K1_delta.extend(parity(K3))
  K1_ = K1 ^ n2 ^ K1_delta

  K2_delta = parity(K1)
  K2_delta.extend(parity(K4))
  K2_delta.extend(ID[idx:])
  K2_ = K2 ^ n2 ^ K2_delta

  K3_delta = ID[:idx]
  K3_delta.extend(parity(K4))
  K3_delta.extend(parity(K2))
  K3_ = K3 ^ n1 ^ K3_delta

  K4_delta = parity(K3)
  K4_delta.extend(parity(K1))
  K4_delta.extend(ID[idx:])
  K4_ = K4 ^ n1 ^ K4_delta

  return (IDS, K1, K2, K3, K4)

# --------------------
# EMAPReader
# --------------------
class EMAPReader(Reader):

  def __init__(self, channel: Channel):
    self.ID  = None
    self.IDS = None
    self.K1  = None
    self.K2  = None
    self.K3  = None
    self.K4  = None
    self.n1  = None
    self.n2  = None

    Reader.__init__(self, 'emap', channel)

  def start(self):
    """Starts the protocol by sending the hello message.
    """
    if self.K1 is None or len(self.K1) != MESSAGE_SIZE:
      self.error('Missing K1 or incorrect size')
    if self.K2 is None or len(self.K2) != MESSAGE_SIZE:
      self.error('Missing K2 or incorrect size')
    if self.K3 is None or len(self.K3) != MESSAGE_SIZE:
      self.error('Missing K3 or incorrect size')
    if self.K4 is None or len(self.K4) != MESSAGE_SIZE:
      self.error('Missing K4 or incorrect size')

    hello_message = Message(
      label   = 'hello',
      kind    = MessageKind.READER_TO_TAG,
      content = bitarray(0)
    )

    self.channel.send(hello_message)

  def update(self):
    """Updates the keys and IDS of the tag. This should happen once authentication is over.
    """
    IDS_, K1_, K2_, K3_, K4_ = update(self.ID, self.IDS, self.K1, self.K2, self.K3, self.K4, self.n1, self.n2)

    self.IDS = IDS_
    self.K1 = K1_
    self.K2 = K2_
    self.K3 = K3_
    self.K4 = K4_
    self.info('Updated keys and IDS')

  def handle_IDS_message(self, message: Message):
    """Handles message containing IDS from the tag.

    Args:
        message (Message): The message that contains the IDS
    """
    # Capture IDS
    self.IDS = message.content
    if self.IDS is None or len(self.IDS) != MESSAGE_SIZE:
      self.error('Missing IDS or incorrect size')

    self.info('IDS Valid')

    # First, create n1 & n2
    self.n1 = bitarray(MESSAGE_SIZE)
    self.n2 = bitarray(MESSAGE_SIZE)

    self.info('Created n1, n2')

    # Then, create A, B, C
    A =  self.IDS ^ self.K1  ^ self.n1
    B = (self.IDS | self.K2) ^ self.n1
    C =  self.IDS ^ self.K3  ^ self.n2
    self.info('Created A, B, C')

    # Create and send message
    content = bitarray(0)
    content.extend(A)
    content.extend(B)
    content.extend(C)

    abc_message = Message(
      label   = 'ABC',
      kind    = MessageKind.READER_TO_TAG,
      content = content
    )

    self.info('Sent ABC message')
    self.channel.send(abc_message)

  def handle_ED_message(self, message: Message):
    """Handles the message containing E and D from the tag.

    Args:
        message (Message): The message containing E || D
    """
    DE = message.content
    if DE is None or len(DE) != 2 * MESSAGE_SIZE:
      self.error('Missing DE or incorrect size')

    # Get D, E
    D = DE[:MESSAGE_SIZE]
    E = DE[MESSAGE_SIZE:]

    self.info('Got D, E')

    # Verify n2
    n2_ = (self.IDS & self.K4) ^ D

    if n2_ != self.n2:
      self.error('Incorrect n2 received')
    else:
      self.info('Tag verified')

    # Extract ID
    self.ID = (self.IDS & self.n1 | self.n2) ^ E ^ self.K1 ^ self.K2 ^ self.K3 ^ self.K4

    self.info('Got ID')

    # Update keys
    self.update()

  def receive(self, message: Message):
    super(EMAPReader, self).receive(message)

    if message.label == 'IDS':
      self.handle_IDS_message(message)
    elif message.label == 'DE':
      self.handle_ED_message(message)

# --------------------
# EMAPTag
# --------------------
class EMAPTag(Tag):

  def __init__(self, channel: Channel):
    self.ID  = bitarray(MESSAGE_SIZE)
    self.IDS = bitarray(MESSAGE_SIZE)
    self.K1  = bitarray(MESSAGE_SIZE)
    self.K2  = bitarray(MESSAGE_SIZE)
    self.K3  = bitarray(MESSAGE_SIZE)
    self.K4  = bitarray(MESSAGE_SIZE)
    self.n1  = None
    self.n2  = None

    Tag.__init__(self, 'emap', channel)

  def reset(self):
    self.n1  = None
    self.n2  = None

  def update(self):
    """Updates the keys and IDS of the tag. This should happen once authentication is over.
    """
    IDS_, K1_, K2_, K3_, K4_ = update(self.ID, self.IDS, self.K1, self.K2, self.K3, self.K4, self.n1, self.n2)

    self.IDS = IDS_
    self.K1 = K1_
    self.K2 = K2_
    self.K3 = K3_
    self.K4 = K4_

    self.info('Updated keys and IDS')

  def handle_hello_message(self):
    """Handles initial hello message from the reader.
    """
    IDS_message = Message(
      label = 'IDS',
      kind = MessageKind.TAG_TO_READER,
      content = self.IDS
    )

    self.info('Sent "IDS" message')
    self.channel.send(IDS_message)

  def handle_ABC_message(self, message: Message):
    """Handles message containing A, B, and C from the reader.

    Args:
        message (Message): The message containing A || B || C
    """
    ABC = message.content
    if ABC is None or len(ABC) != 3 * MESSAGE_SIZE:
      self.error('Missing ABC or incorrect size')

    # Get A, B, C
    A = ABC[:MESSAGE_SIZE]
    B = ABC[MESSAGE_SIZE:2*MESSAGE_SIZE]
    C = ABC[2*MESSAGE_SIZE:]

    self.info('Got A, B, C')

    # Get n1, n2
    n1  =  self.IDS ^ self.K1  ^ A
    n1_ = (self.IDS | self.K2) ^ B
    n2  =  self.IDS ^ self.K3  ^ C

    if n1 != n1_:
      self.error('Error in n1 verification')
    else:
      self.n1 = n1
      self.n2 = n2
      self.info('Got n1, n2. Reader verified')

    # Create D, E
    D = (self.IDS & self.K4) ^ self.n2
    E = (self.IDS & self.n1 | self.n2) ^ self.ID ^ self.K1 ^ self.K2 ^ self.K3 ^ self.K4

    self.info('Created D, E')

    # Create message and send
    content = bitarray(0)
    content.extend(D)
    content.extend(E)

    de_message = Message(
      label   = 'DE',
      kind    = MessageKind.TAG_TO_READER,
      content = content
    )

    self.info('Sent DE message')

    # Update keys in b4
    self.update()

    self.channel.send(de_message)


  def receive(self, message: Message):
    super(EMAPTag, self).receive(message)

    if message.label == 'hello':
      self.handle_hello_message()
    elif message.label == 'ABC':
      self.handle_ABC_message(message)

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
    self.info('Transferred secret keys through secure channel')
    # end Secure channel

    self.channel.listen(self.reader)
    self.channel.listen(self.tag)

  def run(self):
    super(EMAPProtocol, self).run()

    self.reader.start()
    self.tag.start()

  def verify(self):
    # TODO: Verify
    pass
