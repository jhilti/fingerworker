# Fingerworker A-P1 - assembly instructions

This is an unprogrammed prototype PCBA order. Populate all **46 components** in `BOM.csv`, top side only. J2 and J3 are solder-wire lands, not purchased connectors. BT1, H1 and SW1 are external and are not part of the PCBA supply scope. Deliver with no battery attached.

## Fabrication and panel process

Use the four-layer, 0.8 mm ENIG build specified in the package README. All 75 through-vias require nonconductive resin filling, planarization and copper capping (IPC-4761 Type VII). This is mandatory because the existing layout contains via centers within U4 pad 4 and U1 pad 12. Mask tenting alone is not an equivalent process. The bare-board fabrication notes take precedence over generic quote defaults.

Make the assembly panel and tooling rails as needed, with global fiducials outside the finished board. No tabs, routing scars or remaining rails may obstruct the XIAO USB socket at the Y=68.5 mm end in the supplied placement coordinate system, J1 entry, or SW2 actuator. Deliver separated 19.5 x 68.5 mm boards. No metal tooling, added fiducials or copper may be left inside the defined RF keepout regions.

## Coordinates and orientation

`positions-kicad.csv`: mm, TOP view, origin at the finished board's lower-left corner, X right and Y up. `pad-map.csv` uses the same axes and origin. Gerbers and drill files use this origin too. Positive rotations are KiCad top-view counterclockwise. The CAD zero orientation is not necessarily the supplier's tape zero; use numbered pads and the assembly drawing for machine-library translation.

**The positions file contains footprint anchors, not guaranteed package pickup centers.** Most components are centered. U1 uses the original Seeed library anchor near a board corner. Its nominal PCB body center is offset +8.890 mm X and +10.5205 mm Y from its CSV anchor at rotation 0. The assembler must apply this pickup offset; do not center the module on the raw U1 coordinate. USB faces the upper short board edge. J1 is centered laterally; its mating opening faces the lower short edge. SW2 is mounted at 90 degrees with its actuator facing the left long board edge. Use `review/assembly-top.svg` and the exact local footprint geometry if there is any machine-library ambiguity.

| Component | Orientation / assembly requirement |
|---|---|
| U1 | Seeed 102010448 original XIAO nRF52840, without headers. NOT Sense, Plus, or a bare nRF52840 IC. USB points outward past the short edge. Retain factory USB bootloader. |
| U1 bottom | Battery lands 19 = VBAT and 20 = GND must be electrically joined. Side castellations alone do not connect the battery. Use the supplied Seeed footprint including bottom lands. Inspect hidden joints by X-ray or another validated process and verify continuity. Confirm delivered module revision and underside geometry before reflow. |
| U2 | TPS61041DBVR; 1=SW, 2=GND, 3=FB, 4=EN, 5=VIN. |
| U3 | TPS7A2050PDBVR; 1=IN, 2=GND, 3=EN, 4=NC, 5=OUT. |
| U4 | ADS1220IPWR, TSSOP-16/PW. Pin 1 follows the F.Fab corner mark. No QFN substitution. |
| D1 | MBR0520LT1G cathode (stripe) to pad 1 / VBOOST; anode to pad 2 / SW. |
| Q1 | 2N7002,215: 1=G, 2=S, 3=D. |
| L1 | XFL3012-103MEC, exact shielded 10 uH device. Winding start/dot to pad 2 / SW per the supplied footprint. |
| J1 | JST PH horizontal socket. Pad 1 = VBAT positive, pad 2 = GND. Mounting pads are mechanical. No pre-connected cell. |
| SW2 | Panasonic EVQPUC02K; duplicate contact pads share their numbered net. Do not rotate based on a generic two-pin switch image. |
| C4, C7 | Both 22 uF in this issue. The old 10/4.7 uF values are superseded. |
| R7, R8 | Same MPN and lot, individual 0.1% parts. |

Do not add headers, sockets, a battery holder, adhesive under RF components, or conformal coating. No part substitution without engineering approval. XIAO is a preassembled module: use a supplier-approved secondary soldering process compatible with the module and the other components. The module body must clear the carrier and be parallel; do not force underside components against the carrier. Include process confirmation in the quotation.

## External connection after PCBA acceptance

See `pad-map.csv` for physical positions. Factory PCBA delivery leaves J2/J3 unwired.

| Landing | Connection |
|---|---|
| J1.1 | Battery + (red), verified on the actual plug before connection |
| J1.2 | Battery - (black) |
| J2.1 | Sensor EXC+ / red |
| J2.2 | Sensor SIG+ / yellow |
| J2.3 | Sensor SIG- / white |
| J2.4 | Sensor EXC- / black |
| J2.5 / J2.6 | Internal sense lands, connected in copper to 1 / 4. No extra external wires. |
| J3.1 | Omron NC |
| J3.2 | Omron COM |
| Omron NO | Unconnected and insulated |

Confirm wire colors against the supplied TE sensor documentation. Keep the sensor leads short, strain-relieved and clear of the moving mechanism. The force sensor has four conductors; this is not a six-wire remote-sense interface.

## Acceptance on delivery

- 100% netlist-based bare-board electrical test; top-side AOI and polarity inspection.
- Check XIAO underside battery solder joints and continuity from J1.1 to U1.19 and J1.2 to U1.20.
- Verify no short between VBAT/GND, V3V3/GND, VBOOST/GND or V5A/GND before power.
- No application firmware or sensor calibration is requested from the assembler. Do not claim functional force measurement as part of this manufacturing test.
- No battery, USB power or sensor connection during packaging. Use ESD packaging and identify each PCBA as A-P1.
