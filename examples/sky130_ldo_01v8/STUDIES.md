# LDO exploratory studies

These files are **exploratory**, not baselines. They are preserved for audit and
history; do not consume them in assembly.

## DNW studies

```text
dnw1-area-study.*
dnw1-assembly.*
dnw1-packing-study.*
make_dnw1_area_study.py
make_dnw1_assembly.py
make_packing_study.py
```

DNW1/DNW2 assembly is paused.

## Resistor-group variants

```text
make_resistor_group*.py
passive-banks/XR_GROUP*.svg/png/json
```

The frozen resistor baseline is:

```text
passive-banks/XR_GROUP_FROZEN.md
passive-banks/XR_GROUP_COMPACT2.png
```

Everything else in this directory is a rejected/alternative exploration.

## Passive references

```text
passive-banks/XR4.*, XR5.*, XR6.*   individual array references
passive-banks/XC1.*, XC3.*          draft MIM structures
```

No file here is a DRC/LVS/PEX release.
