# Flat132 R2 — print and assembly notes

**R2 nominal geometry and service checks pass.** Use the matched source-bound R2 P01/P05 files and the final native STEP. The 500 N target is not a verified device rating, and this revision assigns no filament, print orientation, perimeter/infill recipe, process allowable or proof-load procedure.

## Parts to replace

Replace P01 and P05 together. P01 incorporates the 6.75 mm reaction wall, 5 mm guides, upper gussets and continuous top bridge. Its floor pocket extends to X2.9 for the revised service path. P05 is one continuous printed pressbar/yoke incorporating both 14 × 22 mm stop faces and their arms. Remove the previous fixed stop blocks and H070/H071/H080/H081 screws/nuts; they are absent from R2. No new metal bracket is specified.

Native comparison confirms the other 12 printed parts retain their R1 geometry, with only P04 triangle ordering changed. The genuine sensor, backing plate, pusher, adjuster and remaining hardware retain the source-defined interfaces. Use the matched R2 P01/P05 models, not earlier proposal or mock meshes. The source retains the 132 mm frame width, 72 mm opening and 35 mm overall height.

## Preload, travel and click setup

1. With the mechanism unloaded, release the existing H21 preload lock and set additional preload within 0–2 mm. Restore that lock according to the existing assembly arrangement.
2. Reset H10 manually to an axial offset of **−preload** from its zero-preload setting. When changing between two preload settings, the required cam change is the negative of the preload change. H21 does not automatically adjust or lock H10; R2 adds no cam linkage or cam lock.
3. Check unloaded motion and switch action. The user-confirmed simple 28–30 mm travel ends at `30 − preload` mm, with the nominal switch trip at `29 − preload` mm. At 2 mm preload those positions are 28 mm and 27 mm. Confirm actual cam retention and switch clearance on the prototype.
4. Use both matching springs or both isometric sleeves. Isometric seating remains `15 − preload` mm. Preserve the genuine sensor's central pusher contact, rear bearing face and loose keeper clearance.

The integral stops route the endpoint reaction through the sensor pressbar. Qualified endpoint force display is a separate firmware function: the current NC LOW/open-line behavior blocks qualified force/peak updates and remains unchanged. Mechanical assembly alone does not enable endpoint Newton readings.

## Unloaded service sequence

The following paths were checked in the final nominal R2 service validation, with the stated prerequisites. Release/remove stored spring force before disassembly. Retain the R1 prerequisites and hardware identities; the R2 offsets below supersede the shorter R1 offsets.

- **Palm/case module:** release H21, remove/restrain spring energy, set preload to 2 mm and remove both palm M4 bolts. Lift the complete palm/electronics module vertically along the established R1 path. Keep its electronics references with that module.
- **H15 keeper:** after removing the complete palm/case module, H160/H161 screws and H13 adjuster, shift H15 wristward **2 mm in −X**, then lift **35 mm in +Z**. This is a separate keeper-removal operation.
- **Complete sensor/yoke stack:** at **zero preload**, remove the palm/case module, springs or sleeves, rear caps/bumpers, both guide rods and H180/H181 plus H190/H191 retention hardware. Keep sensor H01, pusher H02, backing H12, loose keeper H23, its H24/H25 hardware and P05 together. Shift the complete stack **3.5 mm forward in +X**, then lift **40 mm in +Z**. Preserve the flexible lead's clearance and service slack.

Reverse the verified removal path for assembly, then confirm free cassette movement, correct central force contact, loose keeper clearance, manual H10 setup and the reduced travel domain before qualification work. Driver access and fit are geometry checks, not evidence of joint strength.

## Qualification still required

The local section comparison is geometric evidence only. The actual polymer/process, layer bonding, deformation and sensor alignment, sustained-load creep, cyclic fatigue, eccentric/one-sided stop loads and the H11/H15 keeper/fastener joint require qualification as a complete assembly. The hand scan remains approximate. No load rating or material-strength margin is assigned by these notes.
