import functools
import itertools
import statistics

from base.attack import Attack
from base.message import Message
from base.operators import Operator, OperatorKind
from base.protocol import Protocol
from bitarray import bitarray
from pandas import DataFrame


class LinearAttack(Attack):

  def __init__(self, protocol: Protocol, iterations = 1, max_combinations = 2):
    Attack.__init__(self, 'linear', protocol)

    self.iterations = iterations
    self.max_combinations = max_combinations

  def run_analysis(self, parts: dict, target: bitarray, iteration: int, max_combinations: int) -> list:
    def evaluate(value: bitarray, target: bitarray) -> int:
      # Number of equal bits is count of 0s (falses) in XOR
      xor = value ^ target
      return xor.count(False)

    _parts = parts.copy()

    # Add negated parts
    for part_key, part_value in parts.items():
      _parts[f'not_{part_key}'] = ~ part_value

    parts = _parts

    # Get combinations of keys
    combinations = set([])

    for L in range(1, max_combinations + 1):
      combinations = combinations.union(set(itertools.combinations(parts.keys(), L)))

    # Generate operations
    # operators = [&, |, ^]
    results = []
    operator_kinds = [kind.value for kind in OperatorKind.all()]

    for combination in combinations:
      # When only one element, use it
      if len(combination) < 2:
        description = combination[0]
        value = parts[description]
        similarity = evaluate(value, target)

        results.append({
          'description': description,
          'value': value,
          'similarity': similarity
        })
      # When several elements, calculate combinations of operators
      else:
        n_operators = len(combination) - 1

        operator_combinations = itertools.combinations(operator_kinds, n_operators)

        # And iterate to create combination of parts and operators
        for operator_combination in operator_combinations:
          elements = list(combination)
          operators = list(operator_combination)

          description = elements.pop(0)
          value       = parts[description] # value starts as the first element

          # While we have elements in the list of elements,
          # If we still have operators, we should have another element
          while len(operators) > 0 and len(elements) > 0:
            # Get the kind of operator and the element and update the description
            operator_kind = operators.pop()
            element_desc = elements.pop(0)

            description += f' {operator_kind} {element_desc}'

            # Apply the operator to the value with the element
            operator = OperatorKind(operator_kind).operator
            element = parts[element_desc]

            value = operator.apply(value, element)

          similarity  = evaluate(value, target)

          # And add the result
          results.append({
            'description': description,
            'value': value,
            'similarity': similarity
          })

    self.warn(f'(iter {iteration:4d}) Evaluated {len(results)} combinations')
    return results

  def run_attack(self, iteration: int = 1, max_combinations: int = 2):
    # Empty messages
    self.messages = []

    # Reinit protocol
    self.protocol.__init__()
    self.log(f'(iter {iteration:4d}) Started protocol')

    # Attach to channel
    self.log(f'(iter {iteration:4d}) Attached to channel')
    self.protocol.channel.listen(self)

    # Let protocol run
    self.protocol.run()

    # Get messages
    messages = self.messages
    self.warn(f'(iter {iteration:4d}) Intercepted {len(messages)} messages')

    # Check that we have a target
    target = None

    if hasattr(self.protocol.tag, 'ID'): # EMAP
      target = self.protocol.tag.ID
    elif hasattr(self.protocol.tag, 'PID'): # DP
      target = self.protocol.tag.PID

    if target is None:
      self.error(f'(iter {iteration:4d}) Tag doesn\'t have an ID!')
    else:
      self.log(f'(iter {iteration:4d}) Target ID has length {target.length()}')

    # Naive infer length
    L = None

    for message in messages:
      l = message.content.length()

      # Empty message (hello?)
      if l < 1:
        continue

      # Is it a smaller length?
      if L is None:
        L = l
      elif l < L and (L % l) == 0:
        L = l

    if L == target.length():
      self.log(f'(iter {iteration:4d}) Inferred length {L} (same as ID)')
    else:
      self.error(f'(iter {iteration:4d}) Inferred length {L} doesn\'t match target ID length of {target.length()}')

    # Get parts
    parts = {}

    for message in messages:
      l = message.content.length()

      # Empty message
      if l < 1:
        continue

      # Get # of 'parts'
      if (l % L != 0):
        self.error(f'(iter {iteration:4d}) Message `{message.label}´ has irregular length {l}, base is {L}')
      else:
        _parts = [message.content[i:i + L] for i in range(0, l, L)]
        _labels = [f'{message.label}_{i}' for i in range(len(_parts))]

        self.log(f'(iter {iteration:4d}) Message `{message.label}´ has regular length {l}, {len(_parts)} parts detected -> {_labels}')

        _parts_labels = list(zip(_labels, _parts))
        for _label, _part in _parts_labels:
          parts[_label] = _part

    self.warn(f'(iter {iteration:4d}) Got {len(parts)} total parts -> {list(parts.keys())}')

    # Time to analyze combinations and return results
    results = self.run_analysis(parts, target, iteration, max_combinations)
    return results

  def summarize_results(self, results_lists: list) -> DataFrame:
    self.log('Summarizing results')

    # Extract keys (descriptions)
    keys = [set([item['description'] for item in _list]) for _list in results_lists]
    keys = functools.reduce((lambda history, new: history & new), keys)

    # Now for each of these keys
    results = []

    for key in keys:
      # Obtain the relevant elements for each results
      relevant = [[item for item in _list if item['description'] == key] for _list in results_lists]
      relevant = functools.reduce((lambda history, new: history + new), relevant)

      # Obtain the similarities
      simil = [item['similarity'] for item in relevant]

      # Obtain mean & stdev
      mean = statistics.mean(simil)
      stdev = statistics.stdev(simil) if len(simil) > 1 else 0

      # Add it to results
      results.append({
        'combination': key,
        'mean': mean,
        'stdev': stdev
      })

    # Create dataframe & return
    df = DataFrame(results, columns=['combination', 'mean', 'stdev'])
    self.warn(f'Summarized {len(keys)} results for {len(results_lists)} iterations')

    return df

  def run(self) -> DataFrame:
    super(LinearAttack, self).run()

    results = []

    # Run N times
    for i in range(1, self.iterations + 1):
      results.append(self.run_attack(i, self.max_combinations))

    # Get summary
    return self.summarize_results(results)

  def receive(self, message: Message):
    self.messages.append(message)
