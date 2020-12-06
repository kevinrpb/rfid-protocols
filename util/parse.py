import argparse
import os
from enum import Enum

from util.logger import LogLevel


class ProtocolKind(Enum):
  emap = 0

  @staticmethod
  def names() -> str:
    return ['emap']

  @staticmethod
  def names_description() -> str:
    return f'{{{", ".join(ProtocolKind.names())}}}'

class AttackKind(Enum):
  linear = 0

  @staticmethod
  def names() -> str:
    return ['linear']

  @staticmethod
  def names_description() -> str:
    return f'{{{", ".join(AttackKind.names())}}}'

def get_path(path: str) -> str:
  if os.path.isdir(path):
    return os.path.abspath(path)
  elif os.path.isfile(path):
    raise argparse.ArgumentTypeError(f'{path} is not a valid directory')
  else:
    try:
      os.makedirs(path)
      return os.path.abspath(path)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise

def parse_args():
  parser = argparse.ArgumentParser(

  )

  # Protocol to run
  parser.add_argument('protocol',
    type    = str,
    choices = ProtocolKind.names(),
    help    = f'One of {ProtocolKind.names_description()}',
    metavar = 'protocol'
  )

  # Attack to run
  parser.add_argument('-a', '--attack',
    type     = str,
    choices  = AttackKind.names(),
    help     = f'One of {AttackKind.names_description()}',
    metavar  = 'attack',
    required = False
  )

  # Output dir
  parser.add_argument('-o', '--output',
    type     = get_path,
    help     = 'Output directory for attack results',
    metavar  = 'output',
    required = False
  )

  # Log level
  parser.add_argument('-l', '--loglevel',
    type     = str,
    choices  = LogLevel.names(),
    default  = 'INFO',
    help     = f'One of {LogLevel.names_description()}. Default = INFO',
    metavar  = 'log_level',
    required = False
  )

  return parser.parse_args()
