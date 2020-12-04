#!/usr/bin/env python3

from protocols.emap import EMAPProtocol

def main():
  protocol = EMAPProtocol()
  protocol.run()

if __name__ == '__main__':
  main()
