# Flat132 R4 — print and assembly

R4 corrects switch-terminal packaging in the 132 mm R3 palm-fit design. Final nominal native motion/service checks pass. These notes describe the intended prototype assembly, not a load-qualified print process.

## Parts and files

Replace **P01 and P04 together**. P01 carries the relocated, raised switch pedestal; P04 carries the revised recessed cam head and insert pocket. Keep the R3 P02/P03 half-round palm pair and the reinforced P05 with its integral sensing stops. H10 changes from M3×12 to **M3×8**, nominal maximum head Ø5.5 × 3 mm. Its axis also moves with the switch. Do not retain the old cam screw and location.

The full `print-mm` set contains 14 Pxx parts: P01, P02, P03, P04, P05, P060/P061, P070a/P070b/P071a/P071b, P08, P09 and P10. Files remain in millimetres and neutral assembly coordinates; they are unsliced. The `assembly-mm` set adds purchased/reference hardware for 52 device STLs. H09/H09a/H09b are switch references, not print parts. P03 and the four P07 bumpers are flexible parts; no material or slicing recipe is qualified for the 500 N target.

## Switch and cam

Use the exact **SS-01GL2 solder-terminal** switch. The main body occupies X18…28.2, Y−16…3.8, Z7.5…13.9 mm. Mount axes are X20.5, Y−10.9 and −1.4, parallel to Z. Existing intent is two M2×10 screws with thin washers and nominal L3 M2 inserts. The manufacturer's M2.3 mounting guidance is a documented difference; do not transfer its tightening torque to the M2/printed joint.

Nominal switch insert pilots are Ø3.2 × 4 mm blind from Z7.5 to Z3.5. Actual insert manufacturer, OD, length, taper/flange and pilot recommendation remain required. The eleven nominal insert locations in the complete assembly include these two switch seats; no separate insert bodies are modeled. The steel sensor nut, keeper and their fasteners remain steel interfaces.

H10 is M3×8, head X64…67 mm at neutral zero preload, axis Y3.5/Z11.5. Its Ø5.8 head recess ends at X68; a nominal L4 M3 insert sits flush there and ends at X72. The pilot ends at X73 and the smaller shaft passage at X76.5. Match actual insert and screw dimensions before installation. The head recess leaves a nominal 1.3 mm web above the female guide roof. Check free adjustment and reliable locking; smooth CAD cylinders do not define a working lock.

The drawing-based terminal boxes retain all three tabs, including unused NO. Nominal terminal clearance to P05 is 3.1 mm at 2 mm preload. This clearance excludes solder blobs, wire insulation and bends. Route and strain-relieve the actual wires, insulate the unused contact and verify clearance throughout adjustment without cutting the force-transmitting P05 web. Exact terminal corner/hole and lug profiles are not represented by factory CAD.

## Setup and service

Unload the device and restrain or remove spring energy before assembly or adjustment. Mount the switch on the flat pedestal and verify its fastening and actual terminal/wire route. Install the revised cam hardware. Dynamic travel is 30 − preload mm, giving 30 mm at zero and 28 mm at 2 mm preload; isometric seating is 15 − preload mm.

After changing preload, back H10 out by the same axial amount, then calibrate its real trip point and secure the setting. The intended trip lead is 1 mm before the mechanical stop. Manufacturer OP tolerance alone permits 0.2…1.8 mm variation, and minimum specified overtravel is not a maximum permitted endpoint. Check NC state, release and remaining travel on the actual switch. Firmware behavior is unchanged: an open NC switch continues to block qualified force/peak readings.

The retained service sequence requires the palm/case module removed with both M4 palm bolts released and the specified 2 mm service preload. H15 then releases 2 mm wristward and 35 mm upward after the keeper screws and H13 are removed. The complete sensor/yoke stack uses zero preload, the established hardware removals, 3.5 mm forward and 40 mm upward. Final R4 native validation confirms these nominal paths with the stated prerequisites; it does not validate real cable routing or loaded servicing.

Printed strength, deformation, creep/fatigue, cap retention, off-axis loading and the palm joint require prototype qualification. The retained 500 N target is not a verified rating. The hand scan remains an approximate visual reference.
