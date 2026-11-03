# LDO matching review — needs owner confirmation

This packet is deliberately a **proposal**, not a matching signoff. The compiler
only clusters a device when the input has a `match` token; unmatched devices are
not silently merged. Each row must be confirmed or corrected by the analog owner.

Legend: `match` is the current overlay token; `matched=True` means the compiler
uses a shared interdigitated cluster. `cluster` is the current physical cluster.

## AMP

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM46 | 1 | 7 | 1 | current_mirror | `LOAD_AMP` | True | `XM46/XM56` |
| XM48 | 1 | 7 | 1 | current_mirror | `MIR_AMP_net2` | True | `XM48/XM55` |
| XM52 | 2 | 0.5 | 1 | input_pair | `DP_AMP` | True | `XM52/XM53` |
| XM53 | 2 | 0.5 | 1 | input_pair | `DP_AMP` | True | `XM52/XM53` |
| XM54 | 3 | 9 | 1 | tail_current | `—` | False | `XM54` |
| XM55 | 1 | 7 | 1 | current_mirror | `MIR_AMP_net2` | True | `XM48/XM55` |
| XM56 | 1 | 7 | 1 | current_mirror | `LOAD_AMP` | True | `XM46/XM56` |
| XM57 | 1 | 0.5 | 1 | cascode | `CAS_AMP` | True | `XM57/XM58` |
| XM58 | 1 | 0.5 | 1 | cascode | `CAS_AMP` | True | `XM57/XM58` |

## BIAS

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM62 | 1 | 7 | 1 | current_mirror | `MIR_BIAS_VBIAS_P` | True | `XM62/XM64` |
| XM63 | 1 | 0.5 | 1 | cascode | `CAS_BIAS` | True | `XM63/XM65` |
| XM64 | 1 | 7 | 1 | current_mirror | `MIR_BIAS_VBIAS_P` | True | `XM62/XM64` |
| XM65 | 1 | 0.5 | 1 | cascode | `CAS_BIAS` | True | `XM63/XM65` |
| XM66 | 1 | 9 | 20 | current_mirror | `MIR_BIAS_DEG` | True | `XM66/XM67` |
| XM67 | 1 | 9 | 5 | current_mirror | `MIR_BIAS_DEG` | True | `XM66/XM67` |
| XM68 | 1 | 10 | 1 | bias | `—` | False | `XM68` |
| XM69 | 1 | 9 | 5 | current_mirror | `—` | False | `XM69` |
| XR6 | — | — | — | degeneration | passive | — | `XR6` |

## CTRL_EN

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM83 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM83` |
| XM84 | 2.5 | 0.5 | 1 | enable_switch | `—` | False | `XM84` |
| XM85 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM85` |
| XM86 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM86` |
| XM87 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM87` |
| XM88 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM88` |
| XM89 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM89` |
| XM90 | 1 | 0.5 | 1 | enable_switch | `—` | False | `XM90` |

## CTRL_SEL

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM75 | 1 | 0.5 | 1 | adj_switch | `—` | False | `XM75` |
| XM76 | 2.5 | 0.5 | 1 | adj_switch | `—` | False | `XM76` |
| XM77 | 1 | 0.5 | 1 | adj_switch | `—` | False | `XM77` |
| XM78 | 1 | 0.5 | 1 | adj_switch | `—` | False | `XM78` |

## FB

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XR4 | — | — | — | feedback | passive | — | `XR4` |
| XR5 | — | — | — | feedback | passive | — | `XR5` |

## OUT

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM59 | 1 | 0.5 | 1 | output_stage | `—` | False | `XM59` |
| XM60 | 1 | 7 | 1 | current_mirror | `—` | False | `XM60` |
| XM61 | 5 | 0.5 | 1000 | output_stage | `—` | False | `XM61` |

## PASSIVE

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XC1 | — | — | — | decap | passive | — | `XC1` |
| XC3 | — | — | — | decap | passive | — | `XC3` |

## REF

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM79 | 1 | 7 | 1 | current_mirror | `—` | False | `XM79` |
| XM80 | 1 | 10 | 1 | cascode | `—` | False | `XM80` |
| XM81 | 1 | 10 | 1 | bias | `—` | False | `XM81` |
| XM82 | 1 | 10 | 1 | bias | `—` | False | `XM82` |

## START

| device | W (µm) | L (µm) | fingers | role | current match | matched | compiler cluster |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| XM70 | 1 | 0.5 | 1 | bias | `—` | False | `XM70` |
| XM71 | 1 | 2 | 1 | bias | `—` | False | `XM71` |
| XM72 | 1 | 2 | 1 | bias | `—` | False | `XM72` |
| XM73 | 1 | 2 | 1 | bias | `—` | False | `XM73` |
| XM74 | 1 | 9 | 5 | current_mirror | `—` | False | `XM74` |

## Required decisions

- Confirm the matched pairs and the polarity/order (`A/B`, `M1/M2`) for each cluster.
- Mark any pair that is **not** truly matched, especially REF/START/CTRL rows with no `match` token.
- Confirm whether a matched cluster gets two shared end dummies; current compiler does that.
- Confirm the AA ring target. Current compiler: **1.0 µm ring / 0.8 µm gap** (inherited heuristic; not a PDK value).
- Confirm DNW enclosure margin. Current compiler: **3.0 µm** (heuristic; separate from the AA ring).

Corrections should be made in `white-line-input.json` or reported back as a table;
the compiler will then be rerun deterministically.
