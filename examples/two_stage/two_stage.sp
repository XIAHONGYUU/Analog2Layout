* Two-stage Miller OTA — Analog2Layout reference example
* Width convention: w is the per-finger width, total W = w * nf * m.
* Annotations:
*   role=   functional role from the taxonomy (input_pair, current_mirror, ...)
*   match=  devices that must be electrically matched
*   group=  functional block used for floorplan grouping (can differ from match)
*   layout= intended layout pattern (common_centroid, interdigitated, stacked, ...)
*
* This netlist is intentionally small but exercises all three handoff steps:
* role-aware area, floorplan intent, and layout-induced delta planning.

.subckt ota2s vinp vinn vout vdd vss en adj

* --- input differential pair -------------------------------------------------
M1 n1 vinp ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid
M2 n2 vinn ntail vss nmos w=5u l=0.5u nf=4 m=1 role=input_pair match=DP group=IN layout=common_centroid

* --- first-stage current-mirror load ----------------------------------------
M3 n1 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated
M4 n2 n1 vdd vdd pmos w=5u l=1u nf=2 m=1 role=current_mirror match=CM group=LOAD layout=interdigitated

* --- tail current source -----------------------------------------------------
M5 ntail nbias vss vss nmos w=10u l=1u nf=4 m=1 role=tail_current match=TAIL group=BIAS layout=common_centroid

* --- second stage ------------------------------------------------------------
M6 n3 n2 vss vss nmos w=10u l=1u nf=4 m=1 role=output_stage group=OUT layout=interdigitated
M7 vout n3 vdd vdd pmos w=10u l=1u nf=8 m=1 role=output_stage group=OUT layout=interdigitated

* --- enable and trim switches ------------------------------------------------
M8 ntail en vss vss nmos w=2u l=0.5u nf=1 m=1 role=enable_switch group=EN layout=minimal
M9 nbias adj vss vss nmos w=1u l=0.5u nf=1 m=1 role=adj_switch group=ADJ layout=minimal

* --- compensation capacitor --------------------------------------------------
C1 n2 vout 1.5p role=compensation group=COMP

.ends ota2s
