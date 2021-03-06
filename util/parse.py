import argparse
import errno
import os
from enum import Enum

from util.logger import LogLevel


class ProtocolKind(Enum):
  EMAP = 0
  DP = 1

  @staticmethod
  def all():
    return list(map(lambda element: element.name, ProtocolKind))

  @staticmethod
  def help_list() -> str:
    return f'{{{", ".join(ProtocolKind.all())}}}'

class AttackKind(Enum):
  LINEAR = 0

  @staticmethod
  def all():
    return list(map(lambda element: element.name, AttackKind))

  @staticmethod
  def help_list() -> str:
    return f'{{{", ".join(AttackKind.all())}}}'

def get_path(path: str) -> str:
  if os.path.isdir(path):
    raise argparse.ArgumentTypeError(f'{path} is not a valid file')
  elif os.path.isfile(path):
    return os.path.abspath(path)
  else:
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
      try:
        os.makedirs(dirname)
      except OSError as e:
        if e.errno != errno.EEXIST:
          raise

    return os.path.abspath(path)


def parse_args():
  parser = argparse.ArgumentParser(

  )

  # Protocol to run
  parser.add_argument('protocol',
    type    = str.upper,
    choices = ProtocolKind.all(),
    help    = f'One of {ProtocolKind.help_list()}',
    metavar = 'protocol'
  )

  # Attack to run
  parser.add_argument('-a', '--attack',
    type     = str.upper,
    choices  = AttackKind.all(),
    help     = f'One of {AttackKind.help_list()}',
    metavar  = 'attack',
    required = False
  )

  # Target of the attack
  parser.add_argument('-t', '--target',
    type     = str,
    help     = 'Target attribute in Tag to be attacked',
    metavar  = 'target',
    default  = None,
    required = False
  )

  # Output dir
  parser.add_argument('-o', '--output',
    type     = get_path,
    help     = 'Output file for attack results',
    metavar  = 'output',
    required = False
  )

  # Log level
  parser.add_argument('-l', '--loglevel',
    type     = str.upper,
    choices  = LogLevel.all(),
    default  = 'ALL',
    help     = f'One of {LogLevel.help_list()}. Default = ALL',
    metavar  = 'log_level',
    required = False
  )

  # Iterations
  parser.add_argument('-i', '--iterations',
    type     = int,
    default  = 1,
    help     = 'Number of iterations to be run when doing an attack',
    metavar  = 'iterations',
    required = False
  )

  # Log level
  parser.add_argument('-c', '--combinations',
    type     = int,
    default  = 2,
    help     = 'Maximum umber of combinations to be created when running the attack',
    metavar  = 'combinations',
    required = False
  )

  return parser.parse_args()
