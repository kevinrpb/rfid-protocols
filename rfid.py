#!/usr/bin/env python3
from attacks.linear import LinearAttack
from protocols.emap import EMAPProtocol
from protocols.dp import DPProtocol
from util.logger import Logger, LogLevel
from util.parse import AttackKind, ProtocolKind, parse_args

_PROTOCOLS = {
  ProtocolKind.EMAP: EMAPProtocol,
  ProtocolKind.DP: DPProtocol
}

_ATTACKS = {
  AttackKind.LINEAR: LinearAttack
}

def main():
  args = parse_args()
  print(args) # TODO: Remove

  # Set logging level
  Logger._level = LogLevel[args.loglevel]

  # Create protocol
  protocol = _PROTOCOLS[ProtocolKind[args.protocol]]()

  # Create attack if appropriate
  attack = None
  if args.attack is not None:
    attack = _ATTACKS[AttackKind[args.attack]](protocol, args.iterations, args.combinations)

  # Execute according
  if attack is not None:
    results = attack.run()

    # TODO: Do something with attack results (save to csv)
    print(results.head())
  else:
    protocol.run()
    protocol.verify()

if __name__ == '__main__':
  main()
