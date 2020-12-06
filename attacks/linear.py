from base.attack import Attack
from base.protocol import Protocol


class LinearAttack(Attack):

  def __init__(self, protocol: Protocol):
    Attack.__init__(self, 'linear', protocol)
