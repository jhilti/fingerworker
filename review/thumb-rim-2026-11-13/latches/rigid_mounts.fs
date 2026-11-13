    // R19: two broad rigid screw ears replace the exposed tray snap clips.
    // M2x8 from below:5.5mm land +2.5mm engagement in existing M2 inserts.
    for (var side in [-1,1])
    {
        const s=side < 0 ? "0" : "1";
        const rootLo=side < 0 ? -56 : 53.8;
        const rootHi=side < 0 ? -53.8 : 56;
        const padLo=side < 0 ? -62 : 54;
        const padHi=side < 0 ? -54 : 62;
        makeBox(context,id + ("R19TrayMountRoot"~s),vector(-29,rootLo,0)*mm,vector(-23.8,rootHi,8.1)*mm);
        makeBox(context,id + ("R19TrayMountPad"~s),vector(-29,padLo,4)*mm,vector(-24,padHi,9.5)*mm);
        opFillet(context,id + ("R19TrayMountPadRound"~s),{
            "entities":qParallelEdges(qCreatedBy(id + ("R19TrayMountPad"~s),EntityType.EDGE),vector(0,0,1)),
            "radius":1*mm,"tangentPropagation":true });
        join(context,id + ("R19TrayMountJoin"~s),[body(id + "P08_Electronics_tray"),body(id + ("R19TrayMountRoot"~s)),body(id + ("R19TrayMountPad"~s))]);
        makeCylinder(context,id + ("R19TrayMountHole"~s),vector(-26.5,side*59,3.9)*mm,vector(-26.5,side*59,9.6)*mm,1.1*mm);
        cut(context,id + ("R19TrayMountHoleCut"~s),body(id + "P08_Electronics_tray"),body(id + ("R19TrayMountHole"~s)));
    }

        // R19: independent solid rod supports; two M3 screws per block.
        // No crossbar, latch beams or unused frame catches.
        nameBody(context,body(id + "rearBlock0"),"P06L PRINT - rigid rear rod block, two M3 screws");
        nameBody(context,body(id + "rearBlock1"),"P06R PRINT - rigid rear rod block, two M3 screws");
