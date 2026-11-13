"""Build the separate +7mm wrist-contact study from the immutable R2 source."""
from pathlib import Path
import hashlib,json,math
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'flat132-strengthened-2026-10-22/fingerworker_flat132_strengthened.fs'
EXPECTED='d5eca2f3d87bf4b9a47c1987ee91ba1d56e8c87003eca101677a148a2e605654'
OUT=HERE/'fingerworker_flat132_palm_fit.fs'
def sha(b):return hashlib.sha256(b).hexdigest()
raw=BASE.read_bytes();assert sha(raw)==EXPECTED;s=raw.decode();changes=[]
def rep(label,old,new):
 global s
 n=s.count(old);assert n==1,(label,n);s=s.replace(old,new);changes.append({'label':label,'count':n,'old':old,'new':new})
rep('contact axis metadata','const palmCenterX = -34 * mm;','const palmCenterX = -27 * mm;')
rep('trim wrist edge of support plate; keep front and all mounts',
 'makeBox(context,id + "palmPad",vector(-44.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);',
 'makeBox(context,id + "palmPad",vector(-37.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);')
rep('move rigid core axis exactly+7mm',
 'makeCylinder(context,id + "palmBolsterCore",vector(-34,-58,19.75)*mm,\n            vector(-34,58,19.75)*mm,7.75*mm);',
 'makeCylinder(context,id + "palmBolsterCore",vector(-27,-58,19.75)*mm,\n            vector(-27,58,19.75)*mm,7.75*mm);')
rep('wrist half core; cut only core after end fillets before plate union',
 '        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore"),',
 '        // Keep the wrist-facing half only. All feet, ears and enclosure pilots\n        // retain their R2 coordinates; the contact face moves exactly+7 mm.\n        makeBox(context,id + "palmCoreForwardHalfTool",vector(-27,-60,0)*mm,vector(0,60,40)*mm);\n        cut(context,id + "palmCoreHalfCut",body(id + "palmBolsterCore"),body(id + "palmCoreForwardHalfTool"));\n        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore"),')
rep('move soft outer axis exactly+7mm',
 'makeCylinder(context,id + "palmCushion",vector(-34,-43,19.75)*mm,vector(-34,43,19.75)*mm,10.25*mm);',
 'makeCylinder(context,id + "palmCushion",vector(-27,-43,19.75)*mm,vector(-27,43,19.75)*mm,10.25*mm);')
rep('move inner mating core axis exactly+7mm',
 'makeCylinder(context,id + "sleeveCoreTool",vector(-34,-44,19.75)*mm,vector(-34,44,19.75)*mm,7.75*mm);',
 'makeCylinder(context,id + "sleeveCoreTool",vector(-27,-44,19.75)*mm,vector(-27,44,19.75)*mm,7.75*mm);')
rep('wrist half cap with simple integral front return bands',
 '        cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool")]));\n        // Clear the M6 adjuster rear shaft over the full0..2 mm preload range.\n        // This is a local opening in the soft sleeve only; preserve the core,\n        // primary wrist contact surface, screw length and thread engagement.\n        makeCylinder(context,id + "sleeveAdjusterRelief",\n            vector(-24.5,0,18)*mm,vector(-21.3,0,18)*mm,3.5*mm);\n        cut(context,id + "sleeveAdjusterClearance",body(id + "palmCushion"),\n            body(id + "sleeveAdjusterRelief"));',
 '        makeBox(context,id + "palmSleeveForwardHalfTool",vector(-27,-45,0)*mm,vector(0,45,40)*mm);\n        cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool"),body(id + "palmSleeveForwardHalfTool")]));\n        // A plain half-shell loses the original over-centre radial capture.\n        // Two integral end returns cover the flat D-core face while leaving\n        // the central mechanism and contact surface clear. Pull-off retention\n        // and real fit remain prototype qualifications; no added cam/hardware.\n        for (var side in [-1,1])\n        {\n            const t=side == -1 ? "0" : "1";\n            const loY=side == -1 ? -43 : 39;\n            makeBox(context,id + ("palmSleeveReturn"~t),vector(-27,loY,14.6)*mm,\n                vector(-24.5,loY+4,30)*mm);\n            join(context,id + ("palmSleeveReturnJoin"~t),\n                [body(id + "palmCushion"),body(id + ("palmSleeveReturn"~t))]);\n        }')
rep('new rigid part name',
 'P02 PRINT STUDY - detachable keyed palm bolster, two M4 mounts',
 'P02 PRINT STUDY - plus7 mm wrist half-round palm, retained R2 keyed mounts')
rep('new soft part name',
 'P03 TPU PRINT - 2.5 mm palm sleeve',
 'P03 TPU PRINT - plus7 mm half-round palm cap, two front returns')
rep('legacy illustrative hand reference comment',
 ' * The external bolster is centered at X-34; radius10.25, wrist face X-44.25.\n * The heel ends at X-44.35 and is wholly outside the frame. The loaded',
 ' * Palm-fit study: external wrist half-round axis X-27, radius10.25,\n * contact face X-37.25. Legacy illustrative hand pose is retained for\n * comparison only and has not been articulated to fit this change. The loaded')
OUT.write_text(s);outsha=sha(OUT.read_bytes())
bond_width=math.sqrt(7.75**2-(19.75-14.5)**2)
mouth_width=math.sqrt(7.75**2-(19.75-14.6)**2)
meta={
 'status':'SOURCE_CANDIDATE_NATIVE_REGENERATION_AND_VALIDATION_PENDING',
 'baseline_source':str(BASE.relative_to(HERE.parent.parent)),
 'baseline_sha256':EXPECTED,'source':OUT.name,'source_sha256':outsha,
 'scope':'Only P02 rigid palm and P03 soft cap geometry changes; exact+7mm wrist-contact shift. R2 reaction portal/stops,132/72/35envelope and28–30mmtravel unchanged. No firmware or metal changes.',
 'changed_device_refs':['P02','P03'],
 'wrist_contact_reference':{'axis_before_mm':[-34,0,19.75],'axis_after_mm':[-27,0,19.75],'TPU_outer_radius_mm':10.25,'contact_x_before_mm':-44.25,'contact_x_after_mm':-37.25,'exact_forward_shift_mm':7,'finger_loaded_wall_formula_mm':'77 - stroke','nominal_contact_span_before_mm':'121.25 - stroke','nominal_contact_span_after_mm':'114.25 - stroke','span_reduction_mm':7},
 'rigid_core':{'radius_mm':7.75,'axis_y_range_mm':[-58,58],'end_fillet_mm':2,'retained_halfspace':'X <= -27','wrist_x_mm':-34.75,'front_flat_x_mm':-27,'bottom_z_mm':12,'top_z_mm':27.5,'plate_bond_vertical_overlap_mm':2.5,'bond_interface_width_at_plate_top_mm':bond_width,'bond_interface_width_relative_to_R2':.5,'bond_strength_qualified':False},
 'palm_plate':{'bounds_mm':[[-37.25,-64,9.5],[-23.25,64,14.5]],'front_and_mount_geometry_unchanged':True,'M4_centres_mm':[[-16,-31.5],[-16,31.5]],'enclosure_pilot_centres_mm':[[-26.5,-59],[-26.5,59]]},
 'TPU_cap':{'thickness_mm':2.5,'outer_radius_mm':10.25,'y_extent_mm':[-43,43],'end_fillet_before_cut_mm':1.2,'bottom_cut_z_mm':14.6,'main_cap_halfspace':'X <= -27','front_return_bands':[{'bounds_mm':[[-27,-43,14.6],[-24.5,-39,30]]},{'bounds_mm':[[-27,39,14.6],[-24.5,43,30]]}],'front_return_thickness_mm':2.5,'inner_open_mouth_width_mm':mouth_width,'rigid_D_core_maximum_width_mm':7.75,'nominal_radial_capture':True,'capture_width_difference_mm':7.75-mouth_width,'axial_retention':'No new axial keys; axial friction/fit remains to be physically checked as on prior sleeve.','retention_qualified':False},
 'nominal_analytical_clearances_mm':{'core_front_to_H13_rear_at_preload0':3,'core_front_to_reaction_wall_rear':4.25,'core_front_to_H15_rear':4,'return_bands_front_to_rod_block_rear':2.5,'return_band_bottom_to_plate_top':.1},
 'preserved':{'frame_width_mm':132,'clear_finger_width_mm':72,'overall_height_mm':35,'preload_mm':[0,2],'max_dynamic_travel_formula_mm':'30 - preload','isometric_travel_formula_mm':'15 - preload','target_force_N':500,'verified_load_rating_N':None,'all_R2_mounting_feet_ears_keys_holes':True,'electronics_tray_lid_battery_pcb_geometry':True,'firmware_changed':False},
 'physical_fit_note':'Enclosure still reachesX−46.1 belowZ9.5; moving the palm contact does not move its lower wrist projection. Verify this contact against the physical hand/first prototype. Original illustrative hand pose is not a re-articulated hand-fit proof.',
 'removed_obsolete_tool':'Old sleeve-only H13 shaft relief lies entirely forward of the new main cap and is omitted; main cap now has3mmshaftrearclearance.',
 'required_native_checks':['P02/P03 single-solid validity and mating separation','All actual device/electronics interference and preload/travel domain','P02-core/plate positive union and end-return union','Exact wrist surface7mmshift atY0/Z19.75','Unloaded removal/assembly routes with unchanged mounts/case','Physical cap pull-off, axial fit and exposed-edge comfort'],
 'changes':changes}
(HERE/'palm-fit-proposal.json').write_text(json.dumps(meta,indent=2)+'\n')
(HERE/'source-build.json').write_text(json.dumps({'file':OUT.name,'bytes':len(OUT.read_bytes()),'sha256':outsha,'baseline_source_sha256':EXPECTED,'scope':meta['scope'],'expected_device_parts':52,'expected_total_with_electronics':105,'native_validation':'PENDING','changes':changes},indent=2)+'\n')
print(json.dumps({'source':str(OUT),'sha256':outsha,'bytes':len(OUT.read_bytes()),'nominal_contact_shift_mm':7,'bond_width_mm':bond_width,'cap_mouth_width_mm':mouth_width,'capture_width_difference_mm':7.75-mouth_width},indent=2))
