* Low-voltage class-A CMOS op-amp — adapted from an MIT-licensed LTspice design
* Source: https://github.com/Amirhossein7717/low-voltage-cmos-opamp
* Original: src/AHLowVoltageOpAmp.net, 0.8 um Level=1 models, 2 V supply.
* This adaptation keeps the 15-MOS topology and renames the supply/load nodes.
* External 10 pF load is documented but not included in the core area.

.subckt classa_opamp vinp vinn vout vdd vss ibias

* input pair
M1  n007 vinp n010 vss nmos w=80u   l=2u
M2  n005 vinn n010 vss nmos w=80u   l=2u

* PMOS current sources / loads
M3  n007 n002 vdd vdd pmos w=64u   l=2u
M4  n005 n002 vdd vdd pmos w=64u   l=2u
M6  n011 n006 n007 vdd pmos w=240u l=2u
M7  n012 n006 n005 vdd pmos w=240u l=2u
M11 n003 n006 n004 vdd pmos w=240u l=2u
M12 n004 n003 vdd vdd pmos w=240u l=2u
M13 vout n003 vdd vdd pmos w=640u l=2u

* NMOS bias / mirror
M5  n010 ibias vss vss nmos w=162u l=2u
M8  n011 n011 vss vss nmos w=109u l=2u
M9  n012 n011 vss vss nmos w=109u l=2u
M10 n006 ibias vss vss nmos w=194u l=2u
M14 vout n012 vss vss nmos w=1800u l=2u
M15 n002 n002 vdd vdd pmos w=128u l=2u
M16 ibias ibias vss vss nmos w=162u l=2u

* bias / compensation
I_BIAS n002 ibias 100u
R1 n003 n006 3.33k
C1_CC vout n012 5p

.ends classa_opamp
