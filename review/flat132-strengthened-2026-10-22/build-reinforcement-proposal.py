from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'flat132-finished-2026-10-22/fingerworker_flat132_finished.fs'
s=BASE.read_text();assert hashlib.sha256(s.encode()).hexdigest()=='041056629440056626b2f2f88a0db216693e48fff178687174478cb1f34227ef'
changes=[]
def replace(old,new,n=1):
 global s
 assert s.count(old)==n,(old,s.count(old))
 s=s.replace(old,new)
 changes.append(dict(old=old,new=new,count=n))
old='makeBox(context,id + "loadCellWall",vector(-22,-24,3.8)*mm,vector(-16,24,29)*mm);'
new='''// Print-only strengthened reaction portal. Hardware and force datum unchanged.
        // Main wall is6.75 mm deep; new upper bridge remains inside35 mm height.
        makeBox(context,id + "loadCellWall",vector(-22.75,-25.4,3.8)*mm,vector(-16,25.4,33)*mm);
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const loY=side == -1 ? -25.4 : 20.3;
            makeYPrism(context,id + ("reactionButtress"~t),loY*mm,(loY+5.1)*mm,
                [vector(-22.75,11.75)*mm,vector(-7.6,11.75)*mm,
                 vector(-7.6,13)*mm,vector(-12.5,33)*mm,vector(-22.75,33)*mm]);
            if (side == 1)
            {
                // Full lead exit: no thin forward lip remains after relief.
                makeBox(context,id + "reactionLeadWindow",vector(-10.35,20.1,11.5)*mm,
                    vector(-7.4,27.5,24.5)*mm);
                cut(context,id + "reactionLeadClearance",body(id + ("reactionButtress"~t) + "body"),
                    body(id + "reactionLeadWindow"));
            }
            join(context,id + ("reactionButtressJoin"~t),
                [body(id + "loadCellWall"),body(id + ("reactionButtress"~t) + "body")]);
        }
        makeBox(context,id + "reactionTopBridge",vector(-16.2,-25.4,30)*mm,
            vector(-12.5,25.4,33)*mm);
        join(context,id + "reactionTopBridgeJoin",[body(id + "loadCellWall"),body(id + "reactionTopBridge")]);'''
replace(old,new)
replace('vector(-22.1,-16.2,8.8)*mm,vector(-20.9,16.2,28.2)*mm','vector(-23.1,-16.2,8.8)*mm,vector(-20.9,16.2,28.2)*mm')
replace('makeCylinder(context,id + "preloadLockScrew",vector(-19,0,22)*mm,vector(-19,0,26.1)*mm,1.5*mm);','''// P01-only upper driver access; original H15/H11 hardware holes remain exact.
        makeCylinder(context,id + "reactionLockAccess",vector(-19,0,29.2)*mm,
            vector(-19,0,34)*mm,3.1*mm);
        cut(context,id + "reactionLockAccessCut",body(id + "loadCellWall"),body(id + "reactionLockAccess"));
        makeCylinder(context,id + "preloadLockScrew",vector(-19,0,22)*mm,vector(-19,0,26.1)*mm,1.5*mm);''')
replace('const lo=side == -1 ? -18.5 : 15.5;','const lo=side == -1 ? -20.5 : 15.5;')
replace('vector(-16.2,lo,3.8)*mm,vector(-8,lo+3,29)*mm','vector(-16.2,lo,3.8)*mm,vector(-8,lo+5,29)*mm')
replace('vector(-6.5,lo+3,11.7)*mm','vector(-6.5,lo+5,11.7)*mm')
replace('vector(-10.2,15.3,12)*mm,vector(-7.8,18.7,24)*mm','vector(-10.35,15.3,12)*mm,vector(-7.4,20.7,24)*mm')
replace('const loY=side == -1 ? -19 : 15;','const loY=side == -1 ? -21 : 15;')
replace('vector(-6.0,loY+4,12.2)*mm','vector(-6.0,loY+6,12.2)*mm')
replace('vector(-12.6,side*18.7,8.5)*mm','vector(-12.6,side*20.7,8.5)*mm')
replace('vector(-11,side*18.7,8.5)*mm','vector(-11,side*20.7,8.5)*mm')
replace('const slotLow=side == -1 ? -18.7 : 15.3;','const slotLow=side == -1 ? -20.7 : 15.3;')
replace('vector(-11,slotLow+3.4,10.7)*mm','vector(-11,slotLow+5.4,10.7)*mm')
replace('vector(1.4,15.3,4.2)*mm','vector(2.9,15.3,4.2)*mm')
# Keep manufacturing names clear for native part-list/archive consumers.
replace('P01 PRINT STUDY - Flat132 fixed frame, keyed detachable palm feet, 6 mm floor','P01 PRINT STUDY - Flat132 reinforced reaction portal, 5 mm cassette guides, 6 mm floor')
(HERE/'reinforcement-proposal.fs').write_text(s)
(HERE/'reinforcement-proposal.json').write_text(json.dumps(dict(scope='PRINT_ONLY_NOMINAL_GEOMETRY_CANDIDATE',source_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),proposal_sha256=hashlib.sha256(s.encode()).hexdigest(),changes=changes,dimensions_mm=dict(wall_x=[-22.75,-16],wall_y=[-25.4,25.4],wall_z=[3.8,33],upper_cap_x=[-22.75,-12.5],upper_cap_z=[30,33],guide_inner_abs_y=15.5,guide_outer_abs_y=20.5,buttress_inner_abs_y=20.3,buttress_outer_abs_y=25.4,buttress_bottom_z=11.75),limitations=['500 N is a target, not an established printed working-load rating','Native regeneration and full geometry/continuous service audit remain required','No new hardware and no manufacturer sensor edits']),indent=2)+'\n')
print(hashlib.sha256(s.encode()).hexdigest())
