#!/usr/bin/env python3
"""Compose verified R19 native rim source and independent rigid-mount source patch."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RIM=STUDY/'fingerworker_R19_variable_trial.fs';RIM_SHA='b5dd5d89f56a76fbb0dd57891c3835278440a3747937f94eab8598030d076448'
PATCH=STUDY/'latches/rigid_mounts.py';PATCH_SHA='7b8224a69351d31e42621610e363e2ec4d4d7e20f3832e99799a98bc8a88f5db'
SOURCE=STUDY/'fingerworker_R19_thumb_rim.fs'
HEADER='''/**
 * Fingerworker Flat132 R19 - softly rounded thumb rims and rigid screw mounts.
 * One integral organic palm support retains the R18 contact geometry:
 * wristward extent aboutX-31, crownZ34.5. The underlying pre-loft rail
 * has its original wrist face atX-29 and crownZ33.
 * Both outside thumb mouths have variable rounds: top controlsR2,
 * wrist-side controlsR1, fading to the retained lower-lipR0.4.
 * The lower floor, rod bores, sensor force path and25mm strap slots remain.
 * P01 also omits the obsolete rear latch catches.
 * Eight printed device bodies: P01 frame/palm, P04 grip, P05 force yoke,
 * P06L/P06R separate solid rod blocks, P08 screw-mounted tray, P09 lid, P11 cam.
 * The assembly has94 native bodies;90 prior bodies retain their geometry.
 * Both rear blocks require two M3x8 screws each in the existing M3 inserts.
 * Remove each block's screws before axial+X12mm withdrawal; no latch flexing.
 * P08 uses two required M2x8 screws in the existing M2 insert locations.
 * Remove these screws and lower the tray20mm; its tall snap clips are omitted.
 * The separate P09 click lid and its wire support remain unchanged.
 * All preload adjustment remains removed: a=p=0, q=5+u, 0<=u<=30.
 * P11 camTrim+/-0.8mm remains only for physical switch calibration.
 * ISO sleeves remain81mm with fixed15mm approach, q=20.
 * Sensor service remains+X3.2mm then+Z40mm after unloading and removing
 * springs, rods, rear blocks and side retainersH18/H19.
 * P04 print orientation remains front end down with bed-only supports.
 * The nominal6mm floor is retained; inboard27x4mm strap slots
 * atX28/65,Y+/-57.5 accept two25mm bands outside the mechanism.
 * PLA fit, comfort, insert retention and loaded performance need physical tests.
 * No500N qualification; printed rods/Q01 are unloaded fit aids only.
 * Coordinates: X pull direction, Y grip width, Z above base.
 */'''
def compose():
 assert sha(RIM)==RIM_SHA and sha(PATCH)==PATCH_SHA
 spec=importlib.util.spec_from_file_location('r19_rigid',PATCH);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 s=mod.patch_source(RIM.read_text());a=s.index('/**');z=s.index(' */',a)+3;s=s[:a]+HEADER+s[z:]
 s=s.replace('Flat132 R19 - softly rounded thumb mouths and organic palm','Flat132 R19 - rounded thumb rims and rigid mounts')
 s=s.replace('P01 PRINT STUDY - Flat132 organic palm bolster, side thumb seats, inboard straps','P01 PRINT - Flat132 organic palm, rounded thumb rims, rigid rear mounts')
 s=s.replace('// R12 fixed rear datum: one large gate replaces both caps/shoes.','// R19 fixed rear datum: two independent solid rod blocks.')
 s=s.replace('// Gate is installed axially over rods after inserting the carriage.','// Each block installs axially over its rod after inserting the carriage.')
 s=s.replace(' M3x8 rear gate screw - optional fitting/functional securing',' M3x8 rear block screw - required fastening')
 s=s.replace('P01 PRINT STUDY - Flat132 fixed rear gate frame, 5 mm cassette guides, 6 mm nominal floor','P01 PRINT - Flat132 fixed rear block frame, 5 mm cassette guides, 6 mm nominal floor')
 assert 'R19RawMouthEdges' in s and 'rearGateBridge' not in s and 'R11TraypalmBeam' not in s
 assert 'optional M2 mount' not in s and 'PLA assembly latches' not in s
 # No edits to the organic loft operation/profile block.
 base=RIM.read_text();start='        // R18: matched rounded profiles';end='        const integratedFrame='
 assert s[s.index(start):s.index(end)]==base[base.index(start):base.index(end)]
 return s
if __name__=='__main__':
 SOURCE.write_text(compose());d=dict(status='STAGED_R19_SOURCE_PENDING_NATIVE_FINAL',source_sha256=sha(SOURCE),rim_probe_source_sha256=RIM_SHA,rigid_generator_sha256=PATCH_SHA,native_body_count_expected=94,unchanged_prior_geometry=90,changed_prior_refs=['P01','P06','P08'],new_refs=['P06L','P06R'],source_generator_sha256=sha(__file__))
 (HERE/'integrated-source.json').write_text(json.dumps(d,indent=2)+'\n');Path('/tmp/r19-integrated-sha').write_text(sha(SOURCE))
