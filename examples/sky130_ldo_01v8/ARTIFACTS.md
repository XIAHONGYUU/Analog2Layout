# LDO artifacts registry

Single human index for the LDO layout-intent artifacts. The machine geometry
source remains `bank-specs.json` / the generator. States follow `WORKFLOW.md`.

| artifact | version | state | owner | sha256 | verification | open items |
| --- | --- | --- | --- | --- | --- | --- |
| `banks/NMOS_2X0.5_BANK.png` | current | `draft` | layout | see file | selected-rule JSON | head/metal, full DRC |
| `banks/bank-library.png` | current | `draft` | layout | see file | none | 10 other banks not selected-checked |
| `passive-banks/XR_GROUP` | `COMPACT2-v20261105-1542` | `frozen_structural` | layout | `931bd7b0b09f1ec304a0aced8dcc46adff2b5dbf17d44a7dadac11b431ed6664` | `XR_GROUP_FROZEN.md` | DRC, heads, AA enclosure |
| `passive-banks/XC1` | current | `draft` | layout | see file | none | unit split unconfirmed |
| `passive-banks/XC3` | current | `draft` | layout | see file | none | MIM DRC |
| `white-line.png/svg` | `v20261104-2110` | `draft` | layout | `432453318e0ced0057f691f369e7ff904b9e71eede75b769e94ecb0c20a08202` | 78 tests | bank macros not re-assembled |
| `dnw1-area-study.*` | 2026-11-05 | `exploratory` | layout | see file | none | not a baseline |
| `dnw1-assembly.*` | 2026-11-05 | `exploratory` | layout | see file | none | includes DNW2; not a baseline |

## Verification gate

```bash
python3 tools/verify_ldo.py --rebuild
```

The command regenerates the SVG/manifest, compares the locked hashes, and checks
the manifest invariants and frozen XR_GROUP hash. It does not run DRC/LVS/PEX.

## Rule

- Only `frozen_structural` / `verified_selected_rules` artifacts may enter an
  assembly.
- Do not add status prose here for an artifact that has its own freeze record;
  link the record.
- A changed artifact gets a new version and hash.
