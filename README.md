# RFID Protocols

A simple tool to analyze your RFID cryptographic protocol.

## Setup

In order to use the tool, you need to first install the dependencies. This can be done:

- With **pip**: `pip install -r requirements.txt`
- With **Pipenv**: `pipenv install`

> NOTE: Pipenv will create a virtualenv for the project. You must then activate the virtualenv with `pipenv shell` before running the tool.

## Running

The best source to figure out how to run the program is running it as `python rfid.py --help`. This will print the following:

```
usage: rfid.py [-h] [-a attack] [-t target] [-o output] [-l log_level]
  [-i iterations] [-c combinations] protocol

positional arguments:
  protocol              One of {EMAP, DP}

optional arguments:
  -h, --help            show this help message and exit
  -a attack, --attack attack
                        One of {LINEAR}
  -t target, --target target
                        Target attribute in Tag to be attacked
  -o output, --output output
                        Output file for attack results
  -l log_level, --loglevel log_level
                        One of {NONE, ATTACK, CHANNEL, PROTOCOL,
                        READER, TAG, ALL, SIMPLE}. Default = ALL
  -i iterations, --iterations iterations
                        Number of iterations to be run when doing an
                        attack
  -c combinations, --combinations combinations
                        Maximum umber of combinations to be created
                        when running the attack
```

Some examples to run:

- `python rfid.py DP`: Will run a simulation of the DP protocol
- `python rfid.py -a linear -t ID -l attack -i 100 -c 3 -o results.csv EMAP`: Will run a linear attack on the EMAP protocol using combinations of up to 3 elements for 100 iterations and save the results to the `results.csv` file.

## Supported Protocols

### David-Prasad

```bibtex
@inproceedings{david2009providing,
  title={Providing strong security and high privacy in low-cost RFID networks},
  author={David, Mathieu and Prasad, Neeli R},
  booktitle={International conference on Security and privacy in mobile information and communication systems},
  pages={172--179},
  year={2009},
  organization={Springer}
}
```

### EMAP

```bibtex
@inproceedings{peris2006emap,
  title={EMAP: An efficient mutual-authentication protocol for low-cost RFID tags},
  author={Peris-Lopez, Pedro and Hernandez-Castro, Julio Cesar and Estevez-Tapiador, Juan M and Ribagorda, Arturo},
  booktitle={OTM Confederated International Conferences" On the Move to Meaningful Internet Systems"},
  pages={352--361},
  year={2006},
  organization={Springer}
}
```

## Adding a Protocol

> TODO: Instructions to come...

## Supported Attacks

### Linear Attack

The attack calculates combinations from parts of the messages using bitwise operators. It will evaluate the combination against a target (tipically the tag's ID or a key).

The attack can be set to run a number of iterations and will summarize the results for each combination, calculating the average bits of the target it gets and the standard deviation.

## Adding an Attack

> TODO: Instructions to come...
