from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE/'reinforcement-proposal.fs'
s=BASE.read_text();assert hashlib.sha256(s.encode()).hexdigest()=='64b844211e5e562e5350327e8f9b6902fd8cb77e152984461e4020b42a2d451d'
changes=[]
def replace(old,new,n=1):
 global s
 assert s.count(old)==n,(old,s.count(old))
 s=s.replace(old,new);changes.append(dict(old=old,new=new,count=n))
replace('annotation { "Name" : "Preview displacement (0 to 30 mm)" }','annotation { "Name" : "Frame travel (0 to 30 mm minus preload; reset click cam after preload)" }')
replace('const stroke = definition.isometricLock ? 15 * mm - preload : definition.previewTravel;','''const maxDynamicTravel = 30 * mm - preload;
        if (!definition.isometricLock && definition.previewTravel > maxDynamicTravel + 1e-6*mm)
            throw regenError("Integral sensing stops limit frame travel to30 mm minus preload. Use28 mm at2 mm preload; manually reset the click cam after changing preload.", ["previewTravel", "preloadAdjustment"]);
        const stroke = definition.isometricLock ? 15 * mm - preload : definition.previewTravel;''')
start=s.index('        // M4 stops meet the pocket deck front at X35 after30 mm travel.')
end=s.index('        // SS-01GL2 laid on its broad face:',start)
old=s[start:end]
new='''        // Broad integral PRINTED sensing stops replace both M4 screws/nuts.
        // End force returns P04 -> these P05 arms -> pusher -> actual sensor;
        // no fixed P01 full-travel stop bypasses the cell.
        // FaceX35+preload meets P04front65-stroke: stroke+preload<=30.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const y=side*24;
            // Axial-compression root section10 x22, centredonforceheightZ18.
            makeBox(context,id + ("sensingStopArm"~t),vector(8.5,y-5,7)*mm,
                vector(25,y+5,29)*mm);
            // Broad14 x22 flat bearing faces, no small M4 tip stress raiser.
            // Inner flare starts0.5 mm ahead of the fixed switchcaseX24.2.
            makeBox(context,id + ("sensingStopFace"~t),vector(24.7,y-7,7)*mm,
                vector(35,y+7,29)*mm);
            join(context,id + ("sensingStopJoin"~t),[body(id + "springAnchor"),
                body(id + ("sensingStopArm"~t)),body(id + ("sensingStopFace"~t))]);
        }

'''
replace(old,new)
replace('const stops = qUnion([body(id + "stopScrew0"), body(id + "stopScrew1")]);','const stops = yoke; // Integral printed sensing-stop faces are part of P05.')
replace('"Carriage / full-travel screws"','"Carriage / integral sensing-stop yoke"')
replace('''// A socket-head M3x12 screw provides +/-1 mm click adjustment. Its flat
        // head face is the nominal X60 contact datum, independent of hard stops.''','''// MANUAL click-cam setup: after changing preload, back out the M3x12
        // screw by the same axial distance as that preload. This model shows
        // the required configured position X60-preload; there is no automatic
        // physical coupling. Check switch operation and re-lock before use.''')
replace('nameBody(context,body(id + "camScrew"),"H10 M3 x 12 socket-head screw - adjustable click cam");','''nameBody(context,body(id + "camScrew"),"H10 M3 x12 manual click cam - reset by preload amount");
        if (preload > 0*mm)
            opTransform(context,id + "configuredManualClickCam",{
                "bodies":body(id + "camScrew"),
                "transform":transform(vector(-preload,0*mm,0*mm)) });''')
replace('''// OP nominal X31 is 1 mm ahead of cam full-travel face X30.''','''// The manually reset cam preserves the original one-mm trip margin:
        // cam faceX60-preload-stroke reachesX30 at the integral stop.''')
replace('const rollerX=min(33.4*mm,60*mm-stroke-2.4*mm);','const rollerX=min(33.4*mm,60*mm-stroke-preload-2.4*mm);')
replace('P05 PRINT STUDY - Flat132 reinforced floating spring yoke','P05 PRINT STUDY - Flat132 reinforced yoke with broad integral sensing stops')
(HERE/'sensed-stops-proposal.fs').write_text(s)
(HERE/'sensed-stops-proposal.json').write_text(json.dumps(dict(scope='PRINT_ONLY_BROAD_INTEGRAL_SENSED_END_STOP_CANDIDATE',source_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),proposal_sha256=hashlib.sha256(s.encode()).hexdigest(),changes=changes,policy=dict(frame_stroke_max_mm='30 - preload_mm',neutral_max_mm=30,preload2_max_mm=28,isometric_stroke_mm='15 - preload_mm',stop_face_x_mm='35 + preload_mm',manual_click_cam_reset_mm='back out by preload_mm, model headfaceX60-preload before carriage stroke',automatic_physical_cam_coupling=False,ui_roundoff_guard_tolerance_mm=1e-6,geometry_and_validation_domain_extension=False),removed_refs=['H070','H071','H080','H081'],dimensions_mm=dict(arm_x=[8.5,25],arm_abs_y=[19,29],arm_z=[7,29],face_x=[24.7,35],face_abs_y=[17,31],face_area_each_mm2=308),limitations=['500 N remains an unqualified target','Both arms share full end load; one-sided loading must be considered separately','Nominal axial reaction includes sensor; friction and physical deflection require loaded testing','Manually reconfigure click cam after preload adjustment; modeled setting is not a physical automatic linkage','Native regeneration and continuous geometry audit required']),indent=2)+'\n')
print(hashlib.sha256(s.encode()).hexdigest())
