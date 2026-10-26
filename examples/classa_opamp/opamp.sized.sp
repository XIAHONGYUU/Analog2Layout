* Low-voltage class-A CMOS op-amp — user-defined unit W + multiplicity m
* Source: Amirhossein7717/low-voltage-cmos-opamp (MIT), adapted netlist.
* All MOS L = 2 um.  m = parallel multiplicity; total W = W * m.
* M8/M9 changed from 109 um total to 108 um (W=9, m=12).
* R1: w=2 um, L=3 um, m=4.  Cc=5 pF, CL=10 pF external.

.subckt classa_opamp vinp vinn vout vdd vss ibias

* input pair
M1  n007 vinp n010 vss nmos w=10u l=2u m=8
M2  n005 vinn n010 vss nmos w=10u l=2u m=8

* PMOS current-source loads
M3  n007 n002 vdd vdd pmos w=8u  l=2u m=8
M4  n005 n002 vdd vdd pmos w=8u  l=2u m=8
M6  n011 n006 n007 vdd pmos w=12u l=2u m=20
M7  n012 n006 n005 vdd pmos w=12u l=2u m=20
M11 n003 n006 n004 vdd pmos w=8u  l=2u m=30
M12 n004 n003 vdd vdd pmos w=8u  l=2u m=30
M13 vout n003 vdd vdd pmos w=8u  l=2u m=80

* NMOS bias / mirror
M5  n010 ibias vss vss nmos w=2u  l=2u m=81
M8  n011 n011 vss vss nmos w=9u  l=2u m=12
M9  n012 n011 vss vss nmos w=9u  l=2u m=12
M10 n006 ibias vss vss nmos w=2u  l=2u m=97
M14 vout n012 vss vss nmos w=18u l=2u m=100
M15 n002 n002 vdd vdd pmos w=8u  l=2u m=16
M16 ibias ibias vss vss nmos w=2u l=2u m=81

* bias / compensation
I_BIAS n002 ibias 100u
R1 n003 n006 3.33k w=2u l=3u m=4
C1_CC vout n012 5p

.ends classa_opamp
