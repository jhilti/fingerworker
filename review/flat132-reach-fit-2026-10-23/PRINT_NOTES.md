# Flat132 R5 — print and assembly

R5 is a coordinated closer-grip prototype. Final nominal native motion and service checks pass. These notes describe geometry and intended assembly; they do not qualify a print process, material or 500 N load rating.

## Parts and files

Replace **P01, P04, P05, P060 and P061 together**, add **P11**, replace H10 with **M3×10**, and move the four existing P07 bumper shapes to their new contacts. P01 extends the front guide X34→29; P04 receives the guided cam well and top clamp slots; P05 shortens only the distal stop fronts X35→30. Its central force web, 10×22 mm roots and two 14×22 mm stop faces remain. The two rear retainers gain four rigid 5 mm return extensions. P02/P03, palm mounts, sensor cassette and steel force interfaces remain.

The guide extension retains the full nominal 14 mm front bearing land at absolute q35. This overlap and the retained P05 face/root dimensions describe geometry; they do not establish printed stiffness or load capacity.

The `print-mm` set contains 15 Pxx parts: P01, P02, P03, P04, P05, P060/P061, P070a/P070b/P071a/P071b, P08, P09, P10 and P11. `assembly-mm` contains 53 device STLs. These are unsliced native millimetre geometry in neutral assembly coordinates; orient and support them during slicing. `hardware-mm` separately contains the two steel ISO81 sleeves H140/H141 in native ISO13/p2 coordinates; they are not print parts. P03 and the four P07 pads are flexible parts. The P07 pads stay **1.5 mm thick**; the extra reach comes from rigid P06 bosses, not longer compressible pads.

## Cam shoe and inserts

The old horizontal H10, insert bore and head recess are removed from the P04 design. Do not drill or retain the former bore in an R5 print. P11 inserts through the front of its well with the clamp removed. Its lower block is X69…73.5/Y−0.7…7.7/Z9…19; its forward upper step starts at Z13.2 to clear the illustrated roller. The P04 well leaves a nominal **1.3 mm local ligament above the guide roof** and a 2.2 mm rear wall before the vertical finger-pocket wall. These are geometry dimensions, not strength margins.

P11 has a nominal Ø4.2 mm M3 insert pilot, entering Z19 and ending at Z14.5. The intended L4 insert ends at Z15. H10 is a vertical M3×10 with maximum modeled Ø5.5×3 mm head at Z25…28, underhead Z25 and tip Z15. This gives nominal 4 mm engagement and 0.5 mm tip-to-pilot-floor clearance. The shoe's minimum axial pilot wall is 0.9 mm and the forward-step floor ligament is 1.3 mm. Check actual stock, heat installation, pullout and clamp stability before use.

There are still **eleven nominal insert locations in the complete assembly**: two M4, five M3 and four M2. The former carriage cam seat is now in P11; no insert body is modeled. Actual manufacturer, OD, length, taper/flange and pilot recommendation remain required. No steel sensor nut/keeper thread is replaced by a heat-set insert.

The switch remains the plain **Omron SS-01GL2 solder-terminal** model in its R4 location, with two nominal M2×10 screws, thin washers and intended L3 M2 inserts. Its pilots remain Ø3.2 × 4 mm blind. Omron's M2.3 mounting instruction does not qualify tightening torque for the current M2/printed joint. Keep all three tab envelopes clear, including the unused NO terminal; the nominal 3.1 mm bare-tab gap at maximum preload excludes solder, insulation, wire bends and strain relief.

## Setup and measurement

Unload the assembly and restrain or remove spring energy before adjustment. The new rest has substantial pretension: nominal light-pair starting force is 39.7…52.9 N and stronger-pair starting force 66.8…81.6 N over 0…2 mm preload. A reading change before the carriage leaves the return pads does not establish full hand force: the pads carry an initial reaction that hand force first unloads. Verify the resulting measurement dead zone, tare and calibration on a prototype.

Measure user travel from the new rest: `u=0…30−preload`. Absolute carriage shift from the R4 rest is `q=5+u`. Set the cam shoe relative to P04 to `k=camTrim−preload`, where trim is −0.8…+0.8 mm and nominally zero. A preload increase of 1 mm requires manually moving the shoe 1 mm backward relative to P04 before recalibration and clamping. The screw clamps a sliding shoe; it no longer directly acts as the switch cam.

The nominal switch lead at zero trim is 1 mm before the P05 stop. Real operating-point tolerance, actual formed lever, release and maximum allowed endpoint require physical calibration. Verify free motion, top driver access and secure clamping throughout adjustment. Current firmware keeps the NC-open block on qualified force/peak readings; no firmware change accompanies this CAD revision.

The selected ISO setup uses **two 81 mm steel sleeves**, nominal Ø16/Ø8 mm, replacing both springs. Seating is `q=20−preload`, bringing absolute grip 5 mm closer than R4 while retaining `u=15−preload` (15/13 mm) approach from the new rest. Replace or shorten both former 86 mm sleeves consistently; square, deburred seating faces and actual fit require fabrication checks. Do not mix sleeve lengths or use the prior 86 mm geometry for this setup.

Final R5 checks certify the declared service paths with their specified removals and safe-unloaded prerequisites; see [validation](validation/validation-summary.md). For P11 service at user0/preload0/trim0, remove H10 fully upward, slide the unclamped shoe **9 mm wristward**, then lift it 25 mm. It does not lift through the narrow roof slot. Palm/case, keeper and complete sensor-stack service retain the explicit removal sequence in the validation manifest; real cables and loaded servicing are outside that proof. Printed force-path strength, deformation, creep, fatigue, one-sided load, shoe retention, return-pad creep and hand comfort remain physically unqualified.
