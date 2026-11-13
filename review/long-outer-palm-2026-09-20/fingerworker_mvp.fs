FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker MVP - production-oriented layout for a first 3D printed test.
 *
 * X = pull direction, Y = finger-bar width, Z = height above the base.
 * Purchased hardware is modeled at nominal catalogue size. Printed parts are
 * separated bodies so they can be exported and printed individually.
 * Revision 2026-09-20: fully external palm bolster and forward pocket; 30 mm height.
 * New geometry requires regeneration and motion verification in Onshape.
 */

function makeBox(context is Context, id is Id, corner1 is Vector, corner2 is Vector)
{
    fCuboid(context, id, { "corner1" : corner1, "corner2" : corner2 });
}

function makeCylinder(context is Context, id is Id, bottomCenter is Vector, topCenter is Vector, radius is ValueWithUnits)
{
    fCylinder(context, id, {
                "bottomCenter" : bottomCenter,
                "topCenter" : topCenter,
                "radius" : radius
            });
}

function nameBody(context is Context, query is Query, bodyName is string)
{
    setProperty(context, {
                "entities" : query,
                "propertyType" : PropertyType.NAME,
                "value" : bodyName
            });
}

function finishBody(context is Context, query is Query, appearance is Color)
{
    setProperty(context, {
                "entities" : qUnion([query, qOwnedByBody(query, EntityType.FACE)]),
                "propertyType" : PropertyType.APPEARANCE,
                "value" : appearance
            });
}

function makeCompressionSpring(context is Context, id is Id, startX is ValueWithUnits,
                                endX is ValueWithUnits, centerY is ValueWithUnits,
                                centerZ is ValueWithUnits)
{
    const meanRadius = 6 * millimeter;
    const wireRadius = 2 * millimeter;
    const turns = 12;
    const pitch = (endX - startX) / turns;
    const startPoint = vector(startX, centerY + meanRadius, centerZ);

    opHelix(context, id + "helix", {
                "axisStart" : vector(startX, centerY, centerZ),
                "direction" : vector(1, 0, 0),
                "startPoint" : startPoint,
                "interval" : [0, turns],
                "clockwise" : false,
                "helicalPitch" : pitch,
                "spiralPitch" : 0 * millimeter
            });

    var profileSketch = newSketchOnPlane(context, id + "profile", {
                "sketchPlane" : plane(startPoint, vector(1, 0, 0))
            });
    skCircle(profileSketch, "wire", {
                "center" : vector(0, 0) * millimeter,
                "radius" : wireRadius
            });
    skSolve(profileSketch);

    opSweep(context, id + "sweep", {
                "profiles" : qSketchRegion(id + "profile"),
                "path" : qCreatedBy(id + "helix", EntityType.EDGE)
            });
    opDeleteBodies(context, id + "removeConstruction", {
                "entities" : qUnion([qCreatedBy(id + "profile", EntityType.BODY),
                                      qCreatedBy(id + "helix", EntityType.BODY)])
            });
}

/**
 * Hand reference helper block for Fingerworker. Paste above defineFeature in the
 * existing Feature Studio (geometry.fs is already imported there).
 *
 * Call makeHandReference(context, id + "handReference", displacement);
 * after positioning the machine, with displacement between 0 and 30 mm.
 *
 * Helper coordinates are lowered29.5 mm by the caller for the30 mm device.
 * The external bolster is centered at X-34; radius10.25, wrist face X-44.25.
 * The heel ends at X-44.35 and is wholly outside the frame. The loaded
 * pocket wall moves from X77 to X47. The palm spans over the sensor/yoke.
 * Illustrative reference only; not anthropometric hand-fit or load data.
 *
 * Official APIs: https://cad.onshape.com/FsDoc/library.html#fEllipsoid-Context-Id-map
 * https://cad.onshape.com/FsDoc/library.html#fCone-Context-Id-map
 * https://cad.onshape.com/FsDoc/library.html#color-number-number-number-number
 */

// A rounded, tapered phalange chain. The conical sections meet the joint spheres
// tangentially, avoiding flat ends and abrupt cylinder-to-ball steps.
function makeHandCapsuleChain(context is Context, id is Id, points is array,
                             radii is array) returns Query
{
    var bodies = [];
    for (var i = 0; i < size(points); i += 1)
    {
        const jointId = id + ("joint" ~ i);
        fEllipsoid(context, jointId, {
                    "center" : points[i],
                    "radius" : vector(radii[i], radii[i], radii[i])
                });
        bodies = append(bodies, qCreatedBy(jointId, EntityType.BODY));
    }
    for (var i = 0; i < size(points) - 1; i += 1)
    {
        const axis = normalize(points[i + 1] - points[i]);
        const length = norm(points[i + 1] - points[i]);
        const sine = (radii[i] - radii[i + 1]) / length;
        const cosine = sqrt(1 - sine * sine);
        const segmentId = id + ("segment" ~ i);
        fCone(context, segmentId, {
                    "bottomCenter" : points[i] + axis * radii[i] * sine,
                    "topCenter" : points[i + 1] + axis * radii[i + 1] * sine,
                    "bottomRadius" : radii[i] * cosine,
                    "topRadius" : radii[i + 1] * cosine
                });
        bodies = append(bodies, qCreatedBy(segmentId, EntityType.BODY));
    }
    opBoolean(context, id + "join", {
                "tools" : qUnion(bodies),
                "operationType" : BooleanOperationType.UNION
            });
    return qUnion(bodies);
}

// Upper solution of a two-link planar finger chain. Bone lengths stay constant
// during the 30 mm stroke, rather than stretching a translated finger mesh.
function handProximalJoint(root is Vector, distalJoint is Vector,
                           proximalLength is ValueWithUnits,
                           intermediateLength is ValueWithUnits) returns Vector
{
    const delta = distalJoint - root;
    const distance = norm(delta);
    const along = (proximalLength * proximalLength -
                   intermediateLength * intermediateLength +
                   distance * distance) / (2 * distance);
    const rise = sqrt(proximalLength * proximalLength - along * along);
    const direction = delta / distance;
    const up = vector(-direction[2], 0, direction[0]);
    return root + direction * along + up * rise;
}

function makeHandReference(context is Context, id is Id,
                           displacement is ValueWithUnits)
{
    // Bound only this visualization. The machine's own stroke limit remains
    // the authority for its mechanical configuration.
    const stroke = min(30 * millimeter, max(0 * millimeter, displacement));
    var handBodies = [];

    // The heel sits entirely outside the frame and presses against the
    // wrist-facing roller surface. The metacarpal arch clears the fixed
    // sensor support and floating yoke while fingers pull the forward pocket.
    const palmVolumes = [
        { "suffix" : "wrist", "center" : vector(-91, 0, 76),
          "radius" : vector(39, 23, 12) },
        { "suffix" : "heel", "center" : vector(-56.35, 0, 49.25),
          "radius" : vector(12, 29, 9) },
        { "suffix" : "heelRise", "center" : vector(-56.35, 0, 60),
          "radius" : vector(12, 29, 13) },
        { "suffix" : "palm", "center" : vector(-12, 0, 74.5),
          "radius" : vector(50, 38, 14) },
        { "suffix" : "thenar", "center" : vector(-24, -25, 72),
          "radius" : vector(27, 17, 12) }
    ];
    for (var volume in palmVolumes)
    {
        const volumeId = id + volume.suffix;
        fEllipsoid(context, volumeId, {
                    "center" : volume.center * millimeter,
                    "radius" : volume.radius * millimeter
                });
        handBodies = append(handBodies, qCreatedBy(volumeId, EntityType.BODY));
    }

    // Separate finger silhouettes and a size hierarchy. Distal segments descend
    // into the 20 mm recess; fingertip pads sit 0.1 mm from both its floor and
    // its loaded wall. The PIP joints rise as the fingers curl through the pull.
    // These four linkages keep their segment lengths throughout the stroke.
    const fingers = [
        { "name" : "index", "x" : 24, "y" : -28, "z" : 71,
          "proximal" : 43, "middle" : 29, "radius" : 8.5 },
        { "name" : "middle", "x" : 27, "y" : -8, "z" : 73,
          "proximal" : 44, "middle" : 27, "radius" : 9.0 },
        { "name" : "ring", "x" : 24, "y" : 13, "z" : 72,
          "proximal" : 43, "middle" : 30, "radius" : 8.4 },
        { "name" : "little", "x" : 19, "y" : 31, "z" : 70,
          "proximal" : 43, "middle" : 33, "radius" : 7.2 }
    ];
    for (var finger in fingers)
    {
        const root = vector(finger.x, finger.y, finger.z) * millimeter;
        const tipRadius = finger.radius * 0.74 * millimeter;
        const contactX = 77.1 * millimeter + tipRadius - stroke;
        const distalJointX = 77.1 * millimeter + finger.radius * 0.80 * millimeter - stroke;
        const distalJoint = vector(distalJointX, finger.y * millimeter, 66 * millimeter);
        const proximalJoint = handProximalJoint(root, distalJoint,
                finger.proximal * millimeter, finger.middle * millimeter);
        const tip = vector(contactX, finger.y * millimeter, 39.6 * millimeter + tipRadius);
        const fingerBody = makeHandCapsuleChain(context, id + finger.name,
                [root, proximalJoint, distalJoint, tip],
                [finger.radius * millimeter,
                 finger.radius * 0.90 * millimeter,
                 finger.radius * 0.80 * millimeter,
                 tipRadius]);
        handBodies = append(handBodies, fingerBody);
    }

    // Thumb sweeps beside the open mechanism, visibly separate from the four working
    // fingers. Its tip clears the deck's -62.5 mm side; the distal underside
    // also remains above the 59.5 mm top throughout the moving deck's sweep.
    // It follows the fixed palm, so it cannot imply a moving brace.
    const thumbBody = makeHandCapsuleChain(context, id + "thumb",
            [vector(-13, -30, 71) * millimeter,
             vector(4, -49, 71) * millimeter,
             vector(25, -68, 70) * millimeter,
             vector(41, -71, 69) * millimeter],
            [11 * millimeter, 9.6 * millimeter,
             8.2 * millimeter, 7.1 * millimeter]);
    handBodies = append(handBodies, thumbBody);

    // One coherent body: reference geometry is isolated from every machine
    // boolean and can be hidden with one part selection.
    opBoolean(context, id + "joinHand", {
                "tools" : qUnion(handBodies),
                "operationType" : BooleanOperationType.UNION
            });
    const hand = qUnion(handBodies);
    setProperty(context, {
                "entities" : hand,
                "propertyType" : PropertyType.NAME,
                "value" : "REF Hand - illustrative climbing pull"
            });
    setProperty(context, {
                "entities" : hand,
                "propertyType" : PropertyType.DESCRIPTION,
                "value" : "Illustrative adult-sized hand pulling a 20 mm climbing recess against the wrist-facing side of the rounded palm bolster. Fixed-length finger links follow the 0-30 mm stroke. Not anthropometric validation, a physical clearance guarantee, or a manufactured component."
            });
    setProperty(context, {
                "entities" : hand,
                "propertyType" : PropertyType.APPEARANCE,
                "value" : color(0.78, 0.72, 0.65)
            });
    setProperty(context, {
                "entities" : hand,
                "propertyType" : PropertyType.EXCLUDE_FROM_BOM,
                "value" : true
            });
}


/**
 * Read-only solid collision audit; deliberately separate from the model.
 *
 * Import this helper or paste the functions (without the two header lines)
 * above the model feature, then call after previewMotion and hand creation:
 *
 *     println(auditFingerworkerCollisions(context, id));
 *
 * Regenerate independently with previewTravel = 0, 15 and 30 mm and showHand
 * enabled. The helper examines the exact currently generated solids; it does
 * not synthesize poses, create geometry, or alter the machine.
 *
 * Official API documentation, checked 2026-09-04:
 * https://cad.onshape.com/FsDoc/library.html#evCollision-Context-map
 * https://cad.onshape.com/FsDoc/library.html#ClashType
 * https://cad.onshape.com/FsDoc/library.html#evDistance-Context-map
 *
 * evCollision has no user-set distance/penetration tolerance. Do not pass a
 * made-up tolerance field or use evDistance == 0 to infer overlap depth.
 * INTERFERE and containment are failures. Exterior abutment is boundary contact
 * and is allowed only for explicitly declared contact pairs. Interior abutment
 * is treated conservatively as interference; unclassified abutment needs visual
 * review. Counts below are collision records, not distinct body-pair counts.
 */

function auditSolidPair(context is Context, label is string,
                        tools is Query, targets is Query,
                        allowExteriorContact is boolean) returns map
{
    const solidTools = qBodyType(tools, BodyType.SOLID);
    const solidTargets = qSubtraction(qBodyType(targets, BodyType.SOLID), solidTools);
    const toolCount = size(evaluateQuery(context, solidTools));
    const targetCount = size(evaluateQuery(context, solidTargets));
    if (toolCount == 0 || targetCount == 0)
    {
        return { "pair" : label, "status" : "SKIPPED - missing solid query",
                 "toolBodies" : toolCount, "targetBodies" : targetCount };
    }

    const collisions = evCollision(context, {
                "tools" : solidTools,
                "targets" : solidTargets
            });
    var interference = [];
    var exteriorContact = [];
    var needsReview = [];
    for (var clash in collisions)
    {
        if (clash["type"] == ClashType.INTERFERE ||
            clash["type"] == ClashType.TARGET_IN_TOOL ||
            clash["type"] == ClashType.TOOL_IN_TARGET ||
            clash["type"] == ClashType.ABUT_TOOL_IN_TARGET)
        {
            interference = append(interference, clash);
        }
        else if (clash["type"] == ClashType.ABUT_TOOL_OUT_TARGET)
        {
            exteriorContact = append(exteriorContact, clash);
        }
        else if (clash["type"] != ClashType.NONE)
        {
            // ABUT_NO_CLASS and any curve-only/unexpected result must not be
            // silently converted to a clean pass for a solid collision audit.
            needsReview = append(needsReview, clash);
        }
    }

    var status = "CLEAR";
    if (size(interference) > 0)
        status = "INTERFERENCE";
    else if (size(needsReview) > 0)
        status = "REVIEW - unclassified contact";
    else if (size(exteriorContact) > 0)
        status = allowExteriorContact ? "EXPECTED CONTACT" : "UNEXPECTED CONTACT";

    const separation = evDistance(context, {
                "side0" : solidTools,
                "side1" : solidTargets
            }).distance;
    return {
        "pair" : label,
        "status" : status,
        "minimumSeparation" : separation,
        "toolBodies" : toolCount,
        "targetBodies" : targetCount,
        "interferenceCount" : size(interference),
        "exteriorContactCount" : size(exteriorContact),
        "unclassifiedCount" : size(needsReview),
        "interferenceRecords" : interference,
        "exteriorContactRecords" : exteriorContact,
        "unclassifiedRecords" : needsReview
    };
}


// Extrude a closed YZ polygon along X. Coordinates are dimensional vectors.
function makeXPrism(context is Context, id is Id, x1 is ValueWithUnits,
                    x2 is ValueWithUnits, points is array)
{
    var sketch = newSketchOnPlane(context, id + "profile", {
        "sketchPlane" : plane(vector(x1, 0 * millimeter, 0 * millimeter),
                               vector(1, 0, 0), vector(0, 1, 0)) });
    skPolyline(sketch, "outline", { "points" : append(points, points[0]) });
    skSolve(sketch);
    opExtrude(context, id + "body", {
        "entities" : qSketchRegion(id + "profile"),
        "direction" : vector(1, 0, 0), "endBound" : BoundingType.BLIND,
        "endDepth" : x2 - x1 });
    opDeleteBodies(context, id + "removeProfile", {
        "entities" : qCreatedBy(id + "profile", EntityType.BODY) });
}

function body(id is Id) returns Query
{
    return qCreatedBy(id, EntityType.BODY);
}

function cut(context is Context, id is Id, targets is Query, tools is Query)
{
    opBoolean(context, id, { "targets" : targets, "tools" : tools,
        "operationType" : BooleanOperationType.SUBTRACTION });
}

function join(context is Context, id is Id, bodies is array)
{
    opBoolean(context, id, { "tools" : qUnion(bodies),
        "operationType" : BooleanOperationType.UNION });
}

export function auditFingerworkerCollisions(context is Context, id is Id) returns array
{
    const carriage = body(id + "carriageBridge");
    const base = body(id + "base");
    const hand = body(id + "handReference");
    const palm = body(id + "palmPad");
    const sleeve = body(id + "palmCushion");
    const yoke = body(id + "springAnchor");
    const rods = qUnion([body(id + "rod0"), body(id + "rod1")]);
    const seats = qUnion([body(id + "fixedSeat0"), body(id + "fixedSeat1"),
                         body(id + "movingSeat0"), body(id + "movingSeat1")]);
    const springs = qUnion([body(id + "spring0" + "sweep"), body(id + "spring1" + "sweep")]);
    const actuator = qUnion([body(id + "switchLever"), body(id + "switchRoller")]);
    const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1")]);
    const pads = qUnion([body(id + "returnPad0a"),body(id + "returnPad0b"),
                        body(id + "returnPad1a"),body(id + "returnPad1b")]);
    const stops = qUnion([body(id + "stopScrew0"), body(id + "stopScrew1")]);
    const sensor = qUnion([body(id + "loadCell"),body(id + "loadCellBoss"),
        body(id + "loadCellOvermold"),body(id + "loadCellCable"),body(id + "loadCellConnector")]);
    const device = qBodyType(body(id), BodyType.SOLID);
    return [
        auditSolidPair(context,"Carriage / base and printed tracks",carriage,base,false),
        auditSolidPair(context,"Carriage / guide rods",carriage,rods,false),
        auditSolidPair(context,"Carriage / springs",carriage,springs,false),
        auditSolidPair(context,"Carriage / rear retainers",carriage,rear,false),
        auditSolidPair(context,"Carriage / return pads",carriage,pads,true),
        auditSolidPair(context,"Carriage / full-travel screws",carriage,stops,true),
        auditSolidPair(context,"Carriage / switch case",carriage,body(id + "switchBody"),false),
        auditSolidPair(context,"Carriage / switch actuator",carriage,actuator,true),
        auditSolidPair(context,"Adjustable cam / switch actuator",body(id + "camScrew"),actuator,true),
        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),
        auditSolidPair(context,"Springs / surrounding structure",springs,qUnion([base,yoke,carriage,rear,rods,palm,sleeve]),false),
        auditSolidPair(context,"Spring seats / structure",seats,qUnion([base,yoke,carriage,rear,rods,palm,sleeve]),true),
        auditSolidPair(context,"Yoke / base rods and palm",yoke,qUnion([base,rods,palm,sleeve]),false),
        auditSolidPair(context,"Yoke / sensor",yoke,sensor,false),
        auditSolidPair(context,"Sensor / base",sensor,base,true),
        auditSolidPair(context,"Palm support / base",palm,base,true),
        auditSolidPair(context,"Palm / carriage and switch",qUnion([palm,sleeve]),qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Palm sleeve / rigid support",sleeve,palm,true),
        auditSolidPair(context,"Hand / climbing carriage",hand,carriage,true),
        auditSolidPair(context,"Hand / palm sleeve",hand,sleeve,true),
        auditSolidPair(context,"Hand / remaining device",hand,qSubtraction(device,qUnion([hand,carriage,sleeve])),false)
    ];
}

annotation { "Feature Type Name" : "FingerworkerMVP", "Feature Name Template" : "Fingerworker 30 mm printable" }
export const fingerworkerMVP = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Preview displacement (0 to 30 mm)" }
        isLength(definition.previewTravel, LENGTH_BOUNDS);
        annotation { "Name" : "Show hand reference (exclude from manufacturing)" }
        definition.showHand is boolean;
    }
    {
        const mm = millimeter;
        const stroke = definition.previewTravel;
        if (stroke < 0 * mm || stroke > 30 * mm)
            throw regenError("Preview must be between 0 and 30 mm.", ["previewTravel"]);

        // Fixed dimensions form a coordinated prototype, not independent knobs.
        // Assembled envelope238.25 x210 x30; base216 x210; 20 mm pocket; 3 mm floor; 6 mm base.
        const baseThickness = 6 * mm;
        const gripTopZ = 30 * mm;
        const palmCenterX = -34 * mm;
        const palmCenterZ = 19.75 * mm;
        const palmPlateTopZ = 14.5 * mm;
        const springZ = 18 * mm;
        var baseBodies = [];
        var movingBodies = [];

        makeBox(context,id + "base",vector(-22,-105,0)*mm,vector(194,105,6)*mm);
        opFillet(context,id + "baseRound",{
            "entities": qCreatedBy(id + "base",EntityType.EDGE),
            "radius": 2 * mm, "tangentPropagation": true });
        baseBodies = append(baseBodies,body(id + "base"));

        // The roller is entirely outside the wrist end of the frame.
        // Wrist-facing contact X-44.25, crown Z30. Two mounting ears return
        // to the base outside the sensor wall and stop before the moving yoke.
        makeBox(context,id + "palmFootLeft",vector(-21,-61,5.8)*mm,vector(-8,-40,9.5)*mm);
        makeBox(context,id + "palmFootRight",vector(-21,40,5.8)*mm,vector(-8,61,9.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmFootLeft"));
        baseBodies=append(baseBodies,body(id + "palmFootRight"));
        makeBox(context,id + "palmPad",vector(-44.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);
        opFillet(context,id + "palmCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmPad",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        makeBox(context,id + "palmEarLeft",vector(-30,-61,9.5)*mm,vector(-8,-40,14.5)*mm);
        makeBox(context,id + "palmEarRight",vector(-30,40,9.5)*mm,vector(-8,61,14.5)*mm);
        makeCylinder(context,id + "palmBolsterCore",vector(-34,-58,19.75)*mm,
            vector(-34,58,19.75)*mm,7.75*mm);
        opFillet(context,id + "palmEnds",{
            "entities":qCreatedBy(id + "palmBolsterCore",EntityType.EDGE),
            "radius":2*mm,"tangentPropagation":true });
        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore"),
            body(id + "palmEarLeft"),body(id + "palmEarRight")]);
        var insertTools=[];
        var palmTools=[];
        var n=0;
        for (var x in [-15])
        {
            for (var y in [-56,-45,45,56])
            {
                makeCylinder(context,id + ("palmInsert"~n),vector(x,y,2.5)*mm,vector(x,y,10.5)*mm,2.6*mm);
                insertTools=append(insertTools,body(id + ("palmInsert"~n)));
                makeCylinder(context,id + ("palmHole"~n),vector(x,y,8.5)*mm,vector(x,y,31)*mm,2.2*mm);
                palmTools=append(palmTools,body(id + ("palmHole"~n)));
                makeCylinder(context,id + ("palmHead"~n),vector(x,y,13.5)*mm,vector(x,y,31)*mm,4*mm);
                palmTools=append(palmTools,body(id + ("palmHead"~n)));
                n+=1;
            }
        }
        cut(context,id + "palmMountHoles",body(id + "palmPad"),qUnion(palmTools));
        makeCylinder(context,id + "palmCushion",vector(-34,-43,19.75)*mm,vector(-34,43,19.75)*mm,10.25*mm);
        opFillet(context,id + "sleeveEnds",{
            "entities":qCreatedBy(id + "palmCushion",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeCylinder(context,id + "sleeveCoreTool",vector(-34,-44,19.75)*mm,vector(-34,44,19.75)*mm,7.75*mm);
        makeBox(context,id + "sleeveBottomTool",vector(-50,-45,0)*mm,vector(-18,45,14.6)*mm);
        cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool")]));
        nameBody(context,body(id + "palmPad"),"P02 PRINT - rounded palm bolster");
        nameBody(context,body(id + "palmCushion"),"P03 TPU PRINT - 2.5 mm palm sleeve");

        // Carriage: two outside spring arms joined to a rounded central pocket.
        makeBox(context,id + "carriageBridge",vector(176,-102,7)*mm,vector(184,102,24)*mm);
        var carriageBodies=[body(id + "carriageBridge")];
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const loY = side == -1 ? -102 : 64;
            const hiY = side == -1 ? -64 : 102;
            makeBox(context,id + ("arm"~s),vector(116,loY,7)*mm,vector(184,hiY,30)*mm);
            // R1 outside corners reduce handling sharpness without changing the stop datum.
            opFillet(context,id + ("armRound"~s),{
                "entities":qParallelEdges(qCreatedBy(id + ("arm"~s),EntityType.EDGE),vector(0,0,1)),
                "radius":1*mm,"tangentPropagation":true });
            opFillet(context,id + ("armTopRound"~s),{
                "entities":qContainsPoint(qCreatedBy(id + ("arm"~s),EntityType.EDGE),vector(116,(loY+hiY)/2,30)*mm),
                "radius":1*mm,"tangentPropagation":true });
            carriageBodies=append(carriageBodies,body(id + ("arm"~s)));
            makeBox(context,id + ("stopLug"~s),vector(116,side*94-6,7)*mm,vector(133,side*94+6,26)*mm);
            carriageBodies=append(carriageBodies,body(id + ("stopLug"~s)));
        }
        makeBox(context,id + "switchCam",vector(168,-9,7)*mm,vector(182,1,15)*mm);
        carriageBodies=append(carriageBodies,body(id + "switchCam"));
        makeBox(context,id + "climbingDeck",vector(65,-62.5,7)*mm,vector(184,62.5,30)*mm);
        opFillet(context,id + "deckOuterRound",{
            "entities":qParallelEdges(qCreatedBy(id + "climbingDeck",EntityType.EDGE),vector(0,0,1)),
            "radius":5*mm,"tangentPropagation":true });
        opFillet(context,id + "deckTopRound",{
            "entities":qContainsPoint(qCreatedBy(id + "climbingDeck",EntityType.EDGE),vector(65,0,30)*mm),
            "radius":1*mm,"tangentPropagation":true });
        carriageBodies=append(carriageBodies,body(id + "climbingDeck"));
        join(context,id + "joinCarriage",carriageBodies);
        makeBox(context,id + "pocketTool",vector(77,-47,10)*mm,vector(111,47,36)*mm);
        opFillet(context,id + "pocketPlanRound",{
            "entities":qParallelEdges(qCreatedBy(id + "pocketTool",EntityType.EDGE),vector(0,0,1)),
            "radius":8*mm,"tangentPropagation":true });
        cut(context,id + "cutPocket",body(id + "carriageBridge"),body(id + "pocketTool"));
        opFillet(context,id + "lipRound",{
            "entities":qCreatedBy(id + "cutPocket",EntityType.EDGE),
            "radius":4*mm,"tangentPropagation":true });
        // A through window removes excess material and gives the relocated
        // switch a clear corridor throughout the full30 mm stroke.
        makeBox(context,id + "rearWindowTool",vector(117,-47,6)*mm,vector(166,47,31)*mm);
        opFillet(context,id + "rearWindowRound",{
            "entities":qParallelEdges(qCreatedBy(id + "rearWindowTool",EntityType.EDGE),vector(0,0,1)),
            "radius":5*mm,"tangentPropagation":true });
        cut(context,id + "rearWindow",body(id + "carriageBridge"),body(id + "rearWindowTool"));
        movingBodies=append(movingBodies,body(id + "carriageBridge"));
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT - 20 mm climbing pocket and dovetail carriage");
        // A socket-head M3x12 screw provides +/-1 mm click adjustment. Its flat
        // head face is the nominal X164 contact datum, independent of hard stops.
        makeCylinder(context,id + "camScrew",vector(164,-4.5,10)*mm,vector(167,-4.5,10)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(166.9,-4.5,10)*mm,vector(179,-4.5,10)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        makeCylinder(context,id + "camInsertTool",vector(167.8,-4.5,10)*mm,vector(173,-4.5,10)*mm,2.1*mm);
        makeCylinder(context,id + "camThroughTool",vector(167,-4.5,10)*mm,vector(183,-4.5,10)*mm,1.7*mm);
        cut(context,id + "camMount",body(id + "carriageBridge"),qUnion([body(id + "camInsertTool"),body(id + "camThroughTool")]));
        movingBodies=append(movingBodies,body(id + "camScrew"));
        nameBody(context,body(id + "camScrew"),"H10 M3 x 12 socket-head screw - adjustable click cam");

        // Printed 45-degree male tracks. 0.30 mm roof clearance and 0.45 mm
        // horizontal flank offset (~0.318 mm normal). Calibrate with the printer.
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const y = side*94;
            makeXPrism(context,id + ("track"~s),10*mm,184*mm,
                [vector(y-1.9,5.9)*mm,vector(y+1.9,5.9)*mm,
                 vector(y+6,10)*mm,vector(y-6,10)*mm]);
            baseBodies=append(baseBodies,body(id + ("track"~s) + "body"));
            makeXPrism(context,id + ("channel"~s),115*mm,185*mm,
                [vector(y-2.15,5.7)*mm,vector(y+2.15,5.7)*mm,
                 vector(y+6.75,10.3)*mm,vector(y-6.75,10.3)*mm]);
            cut(context,id + ("guideCut"~s),body(id + "carriageBridge"),body(id + ("channel"~s) + "body"));
        }

        // Floating spring yoke: thickened outside the sensor and behind its
        // upper half. The forward relief admits the cell; only the centered
        // pusher contacts the yoke. A notch clears the cable on the +Y side.
        makeBox(context,id + "springAnchor",vector(-7,-90,7)*mm,vector(9,90,29)*mm);
        opFillet(context,id + "yokeOuterRound",{
            "entities":qParallelEdges(qCreatedBy(id + "springAnchor",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        opFillet(context,id + "yokeTopRound",{
            "entities":qContainsPoint(qCreatedBy(id + "springAnchor",EntityType.EDGE),vector(-7,0,29)*mm),
            "radius":1*mm,"tangentPropagation":true });
        makeBox(context,id + "yokeRib",vector(8.8,-38,15.5)*mm,vector(15.5,38,29)*mm);
        join(context,id + "joinYoke",[body(id + "springAnchor"),body(id + "yokeRib")]);
        makeCylinder(context,id + "yokeSensorTool",vector(-8,0,18)*mm,vector(1,0,18)*mm,10.2*mm);
        makeBox(context,id + "yokeCableTool",vector(-8,7.5,14.5)*mm,vector(-1.5,57,21.5)*mm);
        cut(context,id + "yokeRelief",body(id + "springAnchor"),qUnion([body(id + "yokeSensorTool"),body(id + "yokeCableTool")]));
        nameBody(context,body(id + "springAnchor"),"P05 PRINT - reinforced floating spring yoke");

        // FX1901 moved forward. The rear centre is relieved so the support
        // bears on the outer rim, per the supplier drawing. Nominal envelopes.
        makeBox(context,id + "loadCellWall",vector(-22,-24,5.8)*mm,vector(-8,24,29)*mm);
        makeCylinder(context,id + "cellRearRelief",vector(-9.6,0,18)*mm,vector(-7.8,0,18)*mm,7.5*mm);
        cut(context,id + "cellSupportRelief",body(id + "loadCellWall"),body(id + "cellRearRelief"));
        baseBodies=append(baseBodies,body(id + "loadCellWall"));
        makeCylinder(context,id + "loadCell",vector(-8,0,18)*mm,vector(-2.55,0,18)*mm,9.875*mm);
        makeCylinder(context,id + "loadCellBoss",vector(-2.55,0,18)*mm,vector(-1.9,0,18)*mm,2.5*mm);
        makeBox(context,id + "loadCellOvermold",vector(-7,8,15.5)*mm,vector(-3.5,14,20.5)*mm);
        makeCylinder(context,id + "loadCellCable",vector(-5.25,8.5,18)*mm,vector(-5.25,50,18)*mm,1.2*mm);
        makeBox(context,id + "loadCellConnector",vector(-8.25,47.5,15)*mm,vector(-2.25,55.5,21)*mm);
        makeCylinder(context,id + "loadPusher",vector(-1.9,0,18)*mm,vector(1,0,18)*mm,2*mm);
        nameBody(context,body(id + "loadCell"),"H01 TE FX1901-0001-0200-L compression cell");
        nameBody(context,body(id + "loadCellBoss"),"H01a Sensor force boss");
        nameBody(context,body(id + "loadCellOvermold"),"H01b Sensor cable overmold");
        nameBody(context,body(id + "loadCellCable"),"H01c Sensor cable");
        nameBody(context,body(id + "loadCellConnector"),"H01d Sensor connector");
        nameBody(context,body(id + "loadPusher"),"H02 Steel pusher dia 4 x 2.9 mm");

        // Outboard springs retain the 1 mm preload and 30 mm compression travel.
        // Helical sweeps illustrate coils; axial ends are trimmed to the seats.
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const y = side*75;
            const endX = 113*mm-stroke;
            makeCompressionSpring(context,id + ("spring"~s),12*mm,endX,y*mm,springZ);
            makeBox(context,id + ("springTrimFront"~s),vector(8,y-10,7)*mm,vector(12,y+10,29)*mm);
            makeBox(context,id + ("springTrimRear"~s),vector(endX,(y-10)*mm,7*mm),vector(endX+4*mm,(y+10)*mm,29*mm));
            cut(context,id + ("trimSpring"~s),body(id + ("spring"~s) + "sweep"),
                qUnion([body(id + ("springTrimFront"~s)),body(id + ("springTrimRear"~s))]));
            nameBody(context,body(id + ("spring"~s) + "sweep"),"H03"~s~" norelem 26000-1608102 spring - metal");
            makeCylinder(context,id + ("rod"~s),vector(-16,y,18)*mm,vector(190,y,18)*mm,3*mm);
            nameBody(context,body(id + ("rod"~s)),"H04"~s~" Steel guide rod dia 6 x 206 mm");
            makeCylinder(context,id + ("fixedSeat"~s),vector(9,y,18)*mm,vector(12,y,18)*mm,11*mm);
            makeCylinder(context,id + ("movingSeat"~s),vector(113,y,18)*mm,vector(116,y,18)*mm,11*mm);
            makeCylinder(context,id + ("guideBore"~s),vector(-8,y,18)*mm,vector(185,y,18)*mm,3.3*mm);
            cut(context,id + ("clearRod"~s),qUnion([body(id + "springAnchor"),body(id + "carriageBridge"),
                body(id + ("fixedSeat"~s)),body(id + ("movingSeat"~s))]),body(id + ("guideBore"~s)));
            movingBodies=append(movingBodies,body(id + ("movingSeat"~s)));
            nameBody(context,body(id + ("fixedSeat"~s)),"H05"~s~" Fixed steel spring seat 22 x 6.6 x 3 mm");
            nameBody(context,body(id + ("movingSeat"~s)),"H06"~s~" Moving steel spring seat 22 x 6.6 x 3 mm");
            makeBox(context,id + ("frontRodBlock"~s),vector(-18,y-12,5.8)*mm,vector(-8,y+12,28)*mm);
            makeCylinder(context,id + ("frontSocket"~s),vector(-17,y,18)*mm,vector(-7,y,18)*mm,3.1*mm);
            cut(context,id + ("frontBore"~s),body(id + ("frontRodBlock"~s)),body(id + ("frontSocket"~s)));
            baseBodies=append(baseBodies,body(id + ("frontRodBlock"~s)));
            makeBox(context,id + ("rearBlock"~s),vector(185.5,y-12,6)*mm,vector(193.5,y+12,28)*mm);
            makeCylinder(context,id + ("rearSocket"~s),vector(185,y,18)*mm,vector(191.2,y,18)*mm,3.1*mm);
            cut(context,id + ("rearBore"~s),body(id + ("rearBlock"~s)),body(id + ("rearSocket"~s)));
            nameBody(context,body(id + ("rearBlock"~s)),"P06"~s~" PRINT - removable rear rod and carriage retainer");
            for (var offset in [-8,8])
            {
                const t=offset == -8 ? "a" : "b";
                makeCylinder(context,id + ("rearHole"~s~t),vector(189.5,y+offset,5)*mm,vector(189.5,y+offset,29)*mm,1.7*mm);
                makeCylinder(context,id + ("rearHead"~s~t),vector(189.5,y+offset,10)*mm,vector(189.5,y+offset,29)*mm,3.2*mm);
                cut(context,id + ("rearMount"~s~t),body(id + ("rearBlock"~s)),
                    qUnion([body(id + ("rearHole"~s~t)),body(id + ("rearHead"~s~t))]));
                makeCylinder(context,id + ("rearInsert"~s~t),vector(189.5,y+offset,1.5)*mm,vector(189.5,y+offset,7)*mm,2.1*mm);
                insertTools=append(insertTools,body(id + ("rearInsert"~s~t)));
                const padY=y+(offset == -8 ? -7.5 : 7.5);
                makeBox(context,id + ("returnPad"~s~t),vector(184,padY-2.25,14)*mm,vector(185.5,padY+2.25,20)*mm);
                nameBody(context,body(id + ("returnPad"~s~t)),"P07"~s~t~" TPU PRINT - return bumper");
            }
        }

        // M4 stop screws act on broad printed lugs at X86, setting exactly 30 mm.
        // Captive square M4 nuts sit in open-top 7.2 mm traps for assembly.
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const y = side*94;
            makeBox(context,id + ("stopBlock"~s),vector(75,y-6,5.8)*mm,vector(82,y+6,25)*mm);
            makeCylinder(context,id + ("stopHole"~s),vector(74,y,18)*mm,vector(83,y,18)*mm,2.25*mm);
            makeBox(context,id + ("stopNutSlot"~s),vector(76.8,y-3.6,14.4)*mm,vector(80.2,y+3.6,26)*mm);
            cut(context,id + ("stopCut"~s),body(id + ("stopBlock"~s)),
                qUnion([body(id + ("stopHole"~s)),body(id + ("stopNutSlot"~s))]));
            baseBodies=append(baseBodies,body(id + ("stopBlock"~s)));
            makeCylinder(context,id + ("stopScrew"~s),vector(76,y,18)*mm,vector(86,y,18)*mm,2*mm);
            makeBox(context,id + ("stopNut"~s),vector(77,y-3.5,14.5)*mm,vector(80,y+3.5,21.5)*mm);
            makeCylinder(context,id + ("nutBore"~s),vector(76,y,18)*mm,vector(81,y,18)*mm,2*mm);
            cut(context,id + ("cutNut"~s),body(id + ("stopNut"~s)),body(id + ("nutBore"~s)));
            nameBody(context,body(id + ("stopScrew"~s)),"H07"~s~" M4 x 10 flat-tip stop screw");
            nameBody(context,body(id + ("stopNut"~s)),"H08"~s~" M4 square nut 7 x 7 x 3 mm");
        }

        // SS-01GL2 laid on its broad face: only 6.4 mm above the base. Actual
        // case and mounting dimensions; hinge is an illustrative approximation.
        // OP nominal X135 is 1 mm ahead of cam full-travel face X134.
        makeBox(context,id + "switchBody",vector(118,-24,6)*mm,vector(128.2,-4.2,12.4)*mm);
        for (var y in [-18.9,-9.4])
        {
            const s=y == -18.9 ? "0" : "1";
            makeCylinder(context,id + ("switchMountHole"~s),vector(120.5,y,5)*mm,vector(120.5,y,13)*mm,1.175*mm);
            cut(context,id + ("switchDrill"~s),body(id + "switchBody"),body(id + ("switchMountHole"~s)));
            makeCylinder(context,id + ("switchInsert"~s),vector(120.5,y,2)*mm,vector(120.5,y,6.2)*mm,1.6*mm);
            insertTools=append(insertTools,body(id + ("switchInsert"~s)));
        }
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(137.4*mm,164*mm-stroke-2.4*mm);
        const rollerY=-21.1*mm+sqrt(leverLength*leverLength-(rollerX-129.5*mm)*(rollerX-129.5*mm));
        makeCylinder(context,id + "switchLever",vector(129.5,-21.1,9.2)*mm,
            vector(rollerX,rollerY,9.2*mm),0.45*mm);
        makeCylinder(context,id + "switchRoller",vector(rollerX,rollerY,7.6*mm),
            vector(rollerX,rollerY,10.8*mm),2.4*mm);
        nameBody(context,body(id + "switchBody"),"H09 Omron SS-01GL2 - flat mounting");
        nameBody(context,body(id + "switchLever"),"H09a Switch lever preview");
        nameBody(context,body(id + "switchRoller"),"H09b Switch roller preview");

        join(context,id + "integrateBase",baseBodies);
        cut(context,id + "baseInserts",body(id + "base"),qUnion(insertTools));
        var mountingTools=[];
        n=0;
        for (var x in [-15,187])
        {
            for (var y in [-50,50])
            {
                makeCylinder(context,id + ("benchHole"~n),vector(x,x < 0 ? y*1.96 : y,-1)*mm,vector(x,x < 0 ? y*1.96 : y,7)*mm,2.75*mm);
                mountingTools=append(mountingTools,body(id + ("benchHole"~n)));
                n+=1;
            }
        }
        cut(context,id + "benchMounts",body(id + "base"),qUnion(mountingTools));
        nameBody(context,body(id + "base"),"P01 PRINT - 216 x 210 base with integral dovetail tracks");

        if (stroke > 0*mm)
            opTransform(context,id + "previewMotion",{
                "bodies":qUnion(movingBodies),
                "transform":transform(vector(-stroke,0*mm,0*mm)) });
        // Neutral green frame, warm tan climbing surface, dark soft contact.
        finishBody(context,body(id + "base"),color(0.27,0.30,0.28));
        finishBody(context,body(id + "palmPad"),color(0.27,0.32,0.28));
        finishBody(context,body(id + "palmCushion"),color(0.15,0.20,0.17));
        finishBody(context,body(id + "carriageBridge"),color(0.66,0.46,0.27));
        finishBody(context,body(id + "springAnchor"),color(0.35,0.39,0.35));
        finishBody(context,qUnion([body(id + "rearBlock0"),body(id + "rearBlock1")]),color(0.27,0.30,0.28));
        finishBody(context,qUnion([body(id + "spring0" + "sweep"),body(id + "spring1" + "sweep")]),color(0.14,0.40,0.27));

        if (definition.showHand)
        {
            makeHandReference(context,id + "handReference",stroke);
            opTransform(context,id + "lowerHand",{
                "bodies":body(id + "handReference"),
                "transform":transform(vector(0,0,-29.5)*mm) });
        }
        for (var check in auditFingerworkerCollisions(context,id))
            println({ "pose":stroke,"pair":check.pair,"status":check.status,
                "gap":check.minimumSeparation,"interferences":check.interferenceCount,
                "contacts":check.exteriorContactCount,"unclassified":check.unclassifiedCount });
    }, { "previewTravel":0*millimeter,"showHand":false });
