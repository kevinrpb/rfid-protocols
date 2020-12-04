from base.channel import Channel

class Protocol(object):

  def __init__(self, id: str):
    self.id = id
    self.channel = Channel(id)

    self.log('Created')

  def start(self):
    self.log('Started')

  def log(self, message: str):
    print('[Protocol.{}] {}'.format(self.id, message))
