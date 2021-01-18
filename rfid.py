#!/usr/bin/env python3
from attacks.linear import LinearAttack
from protocols.emap import EMAPProtocol
from protocols.dp import DPProtocol
from util.logger import Logger, LogLevel, ForceLogger
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
  logger = ForceLogger('RFID', 'main')

  # Create protocol
  protocol = _PROTOCOLS[ProtocolKind[args.protocol]]()

  # Create attack if appropriate
  attack = None
  if args.attack is not None:
    attack = _ATTACKS[AttackKind[args.attack]](protocol, args.iterations, args.combinations)
  target_name = args.target

  # Execute according
  if attack is not None:
    if target_name is None:
      logger.error('Attack was specified without a target. Please, indicate the target (ID, PID, ...)')
      exit(1)

    logger.log('Running Attack')
    results = attack.run(target_name)

    # TODO: Do something with attack results (save to csv)
    results = results.sort_values(by = ['mean', 'stdev', 'combination'], ascending = False)

  else:
    logger.log('Running Protocol')
    protocol.run()
    protocol.verify()


  logger.log('Finished running')

if __name__ == '__main__':
  main()
