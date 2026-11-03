# Review evaluation — ldo

> Sampled human review, not a global accuracy claim.

## Summary

| metric | value |
| --- | --- |
| reviewed / packet | 58 |
| review rate | 100.0% |
| device strict accuracy | 100.0% |
| device lenient accuracy | 100.0% |
| net class accuracy | 100.0% |
| net role accuracy | 100.0% |
| port direction accuracy | 100.0% |
| port class accuracy | 100.0% |
| port interface accuracy | 100.0% |

## Devices

- total: 44
- evaluated: 44
- decisions: {'accept': 44}
- auto precision (tool auto + reviewed): 100.0%
- match accuracy: 100.0%
- group accuracy: 100.0%
- confusion: {'input_pair -> input_pair': 2, 'tail_current -> tail_current': 1, 'output_stage -> output_stage': 1, 'feedback -> feedback': 2, 'pass_device -> pass_device': 1, 'current_mirror -> current_mirror': 12, 'decap -> decap': 1, 'bias -> bias': 7, 'cascode -> cascode': 5, 'logic -> logic': 4, 'enable_switch -> enable_switch': 6, 'adj_switch -> adj_switch': 2}

## Nets

- total: 6
- evaluated: 6
- decisions: {'accept': 6}
- class confusion: {'signal -> signal': 5, 'control -> control': 1}
- role confusion: {'tail -> tail': 1, 'feedback -> feedback': 1, 'gain_node -> gain_node': 1, 'pass_gate -> pass_gate': 1, 'mirror_gate -> mirror_gate': 2}

## Ports

- total: 8
- evaluated: 8
- decisions: {'accept': 8}

## Notes

- This is a sampled human-review result, not a claim of global accuracy.
- Accepted items use the prediction as the expected label.
- Ambiguous items are counted but excluded from accuracy.
