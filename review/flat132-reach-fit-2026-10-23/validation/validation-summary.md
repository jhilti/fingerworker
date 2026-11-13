# R5 reach fit: nominal native validation

**NOMINAL_GEOMETRY_CHECKS_PASS**; **0 failed**, **0 unresolved**. [Immutable Onshape R5 ISO81](https://cad.onshape.com/documents/15316cc6370631845af136b2/v/ef00e6d9683bc3bffae42912/e/d253eb87b70818ebde8215f0).

Final source SHA256: `d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a`.

Both dynamic rest/end contact positions move5mm closer while retaining30mm user travel at zero preload and28mm at2mm preload. The user selected81mm isometric sleeves; their13–15mm approach also puts the fixed grip5mm closer than R4. Native exports contain106 solids:53 device parts and53 electronics references, including15 printed parts.

P05 retains its primary web/root and shortens its two stop faces5mm. Four rigid return bosses establish the closer rest. P01 extends the fixed guide to preserve both14mm carriage lands. P04 carries a new stepped P11 shoe with vertical M3x10 H10 clamp. Nominal section witnesses check1.3mm guide roof,2.2mm well rear wall,0.9mm pilot ligaments,0.9mm roller-to-upper-boss height separation,4mm nominal insert engagement and0.5mm pilot-floor reserve. A continuous geometric lower bound gives6.3456mm² under-head support; these dimensions do not qualify clamp strength or insert installation.

Continuous geometry covers u≥0, preload0–2mm, u+preload≤30mm and camTrim−0.8…+0.8mm. P11 must be physically set to camTrim−preload and clamped after preload changes. The source actuator is a manufacturer-drawing approximation; actual operating/total travel, switch click, hardware stock and clamp durability remain unqualified. The new81mm ISO native witness is checked separately.

The five neutral/dynamic inputs retain their original61885 source association. An independently rechecked exact inverse certificate restores the entire old source byte-for-byte and proves that only the isometric conditional branch changes coordinates. Those inputs are reused only for isometricLock=false. The new81mm ISO archive originates from the final source. No blanket final-source export claim is made.

Independent exact STEP CSG reconstructs the seven changed rigid parts and compares all97 otherwise-preserved BReps, six under their declared5mm shift. All106 native STEP solids must be valid positive volumes and uniquely match their native STL bodies. The genuine TE sensor stays unscaled. P02/P03 exact intersection is zero, supported by a separate source separation proof. Four translated return-pad STL boxes have one-ULP coordinate quantization differences; exact STEP preservation and strictly bound box checks resolve that without mesh rounding or a collision waiver.

New nominal installed spring lengths are96–94mm at rest and66mm at full user travel. The separate manufacturer spring study records operating-length reserves; no fatigue or printed-load qualification follows. **500N remains a design target.** Prototype force-path, return-boss, fit, creep, fatigue, comfort, actual wire routing and switch/insert/clamp checks remain required.

See [full checks](validation.json), [exact STEP inventory](native-step-inventory.json), [independent CSG/access audit](reach-fit-audit.json), [mode equivalence](dynamic-mode-equivalence.json) and [evidence index](validation-summary.json).
