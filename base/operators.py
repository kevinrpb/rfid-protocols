from abc import ABC, abstractmethod
from enum import Enum

from bitarray import bitarray

class OperatorKind(Enum):
  AND = '&'
  OR  = '|'
  XOR = '^'

  @staticmethod
  def all() -> list:
    return [
      OperatorKind.AND,
      OperatorKind.OR,
      OperatorKind.XOR
    ]

  @property
  def operator(self):
    if self == OperatorKind.AND:
      return AndOperator()
    elif self == OperatorKind.OR:
      return OrOperator()
    else:
      return XorOperator()

class Operator(ABC):

  @abstractmethod
  def __init__(self):
    self._kind = None
    raise NotImplementedError

  @abstractmethod
  def apply(self, left: bitarray, right: bitarray) -> bitarray:
    raise NotImplementedError

  @property
  def description(self) -> str:
    return self._kind.value

  @staticmethod
  def all():
    return OperatorKind.all().map(lambda kind: kind.operator)

class AndOperator(Operator):

  def __init__(self):
    self._kind = OperatorKind.AND

  def apply(self, left: bitarray, right: bitarray) -> bitarray:
    return (left & right)

class OrOperator(Operator):

  def __init__(self):
    self._kind = OperatorKind.OR

  def apply(self, left: bitarray, right: bitarray) -> bitarray:
    return (left | right)

class XorOperator(Operator):

  def __init__(self):
    self._kind = OperatorKind.XOR

  def apply(self, left: bitarray, right: bitarray) -> bitarray:
    return (left ^ right)
