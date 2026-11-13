# Flat132 R3 — palm fit and assembly

This update is based on the reinforced 132 mm R2 assembly. The working palm contact surface moves 7 mm toward the fingers. It is not a retrofit specification for an older 158 mm Rev D print set.

## Replacement parts

Replace P02 rigid palm support and P03 TPU cap together. Their circular axis moves from X−34 to X−27 mm. The wrist-facing curved surface keeps its 10.25 mm outer radius and becomes a half-round profile, with its main flat back at X−27 mm. Its central wrist tangent changes from X−44.25 to X−37.25 mm. The shortened rigid support plate also starts at X−37.25 mm. Both M4 mounts, positive keys, enclosure pilots and finger mechanism remain at their existing locations.

The TPU cap has two 4 mm wide return bands at its ends. These wrap the flat front of the rigid half-round and provide nominal capture. The cap is a flexible part; verify seating, stretch fit and unloaded retention on the print. It must not obstruct the sensor adjuster, the cassette or the palm mounting bolts. No adhesive or additional purchased fastener is specified.

The full print-mm set contains 14 Pxx parts in millimetres and neutral assembly coordinates. These are unsliced CAD exports. Other Pxx geometry is retained from R2. Hxx hardware and electronics reference solids in the full STEP are separate from this print set.

## Retained setup and service

Use the R2 reinforced frame and integral-stop yoke with the retained purchased hardware. The frame remains 132 mm wide, the finger pocket 72 mm clear and the overall height 35 mm. Free travel remains 30 mm minus the 0–2 mm preload. Reset H10 manually by minus the preload change after every preload adjustment. The current firmware still blocks qualified force/peak readings when the NC end switch opens; this CAD update does not change the firmware.

Follow the R2 unloaded service sequence: remove the complete palm/case module after removing both M4 bolts and releasing stored spring force; at the specified 2 mm service preload the module lifts vertically. H15 removal requires the palm/case module, keeper screws and H13 adjuster removed, then 2 mm wristward and 35 mm upward. The complete sensor/yoke stack is removed at zero preload by 3.5 mm forward followed by 40 mm upward, with the same R2 prerequisites. Final native R3 validation records whether these paths remain clear.

## Physical qualification

The hand scan remains an approximate visual reference. The 7 mm change is a nominal CAD contact-surface measurement, not a validated hand-fit result. Printed joint strength, cap retention, comfort, deformation, tolerances and fatigue require prototype checks. The retained 500 N target is not a verified load rating. No filament or slicing recipe is certified by this update.
