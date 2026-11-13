FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker Flat132 R12 - simplified PLA click assembly.
 * Seven printed device bodies: P01 frame/palm, P04 grip,
 * P05 floating force yoke, P06 fixed rear gate, P08 tray, P09 lid, P11 cam.
 * All preload adjustment is removed: a=p=0, q=5+u, 0<=u<=30.
 * H12 bears on a broad fixed support integral with P01 at X=-12 mm.
 * P11 retains camTrim +/-0.8 mm only for physical switch calibration.
 * ISO sleeves remain81 mm with fixed15 mm approach, q=20.
 * One plain removable rear gate replaces both caps and return shoes.
 * Rear M4 adjusters/nuts/washers/jam nuts and M2 shoe pins are omitted.
 * PLA gate latches permit unloaded fitting; four M3 securing screws remain
 * for the loaded assembly. Release both side arms outward0.9mm then+X12mm.
 * Keep the separately printable P09 click lid with integral wire support.
 * Spread P08 hooks0.6mm then lower20mm; open P09 only after removal.
 * Two obsolete former P10 screw pilot holes in P08 are omitted.
 * H11/H13/H15/H16/H17/H21/H22 and their service pockets are omitted.
 * Sensor stack service remains+X3.2mm then+Z40mm after unloading,
 * removing springs, rods, rear gate and side retainers H18/H19.
 * P04/P05 and the central sensor force path retain exact R11 geometry.
 * P04 print orientation stays front end down with bed-only slim trees.
 * Nominal base width132mm; rear latch outer envelope135.2mm.
 * PLA fit, snap cycling, creep and loaded performance require physical tests.
 * No500N qualification; printed rods/Q01 are unloaded fit aids only.
 * Coordinates: X pull direction, Y grip width, Z above base; nominal floor6mm.
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
                                centerZ is ValueWithUnits, lightPair is boolean)
{
    // Illustrative round-wire envelopes, not manufacturing spring drawings.
    const meanRadius = (lightPair ? 6.4 : 6.25) * millimeter;
    const wireRadius = 1 * millimeter;
    const turns = lightPair ? 25 : 24; // indicative total turns from catalog block length / wire diameter
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
 * Palm-fit study: external wrist half-round axis X-27, radius10.25,
 * contact face X-37.25. Legacy illustrative hand pose is retained for
 * comparison only and has not been articulated to fit this change. The loaded
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
    const stroke = min(35 * millimeter, max(0 * millimeter, displacement));
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
 * R10 calls this BEFORE final P01/P02 fusion. The construction regions
 * retain their own contact policies; their intended internal connection is
 * not an interference pair. All external geometry is still checked.
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
            println({"collisionPair":label,"toolBounds":evBox3d(context,{"topology":clash.toolBody}),"targetBounds":evBox3d(context,{"topology":clash.targetBody}),"clashType":clash["type"]});
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

// Extrude a closed XZ polygon along Y. The sketch local +Y is world +Z.
function makeYPrism(context is Context, id is Id, y1 is ValueWithUnits,
                    y2 is ValueWithUnits, points is array)
{
    var sketch = newSketchOnPlane(context, id + "profile", {
        "sketchPlane" : plane(vector(0 * millimeter, y1, 0 * millimeter),
                               vector(0, -1, 0), vector(1, 0, 0)) });
    skPolyline(sketch, "outline", { "points" : append(points, points[0]) });
    skSolve(sketch);
    opExtrude(context, id + "body", {
        "entities" : qSketchRegion(id + "profile"),
        "direction" : vector(0, 1, 0), "endBound" : BoundingType.BLIND,
        "endDepth" : y2 - y1 });
    opDeleteBodies(context, id + "removeProfile", {
        "entities" : qCreatedBy(id + "profile", EntityType.BODY) });
}

function makeZPrismR12(context is Context, id is Id, z1 is ValueWithUnits, z2 is ValueWithUnits, points is array)
{
    var sketch = newSketchOnPlane(context, id + "profile", { "sketchPlane" : plane(vector(0 * millimeter,0 * millimeter,z1), vector(0,0,1), vector(1,0,0)) });
    for (var i = 0; i < size(points); i += 1)
        skLineSegment(sketch, "edge" ~ i, { "start" : points[i], "end" : points[(i + 1) % size(points)] });
    skSolve(sketch);
    opExtrude(context, id + "body", { "entities" : qSketchRegion(id + "profile"), "direction" : vector(0,0,1),
        "endBound" : BoundingType.BLIND, "endDepth" : z2-z1 });
    opDeleteBodies(context,id + "removeProfile",{ "entities":qCreatedBy(id + "profile",EntityType.BODY) });
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
    if (size(evaluateQuery(context,qBodyType(qUnion(bodies),BodyType.SOLID))) < 2)
        throw regenError("R12 union requires two separate solids: " ~ toString(id));
    opBoolean(context, id, { "tools" : qUnion(bodies),
        "operationType" : BooleanOperationType.UNION });
}

export function auditFingerworkerCollisions(context is Context, id is Id, sensor is Query) returns array
{
    const carriage = body(id + "carriageBridge");
    const base = body(id + "base");
    const hand = body(id + "handReference");
    const palm = body(id + "palmPad");
    const yoke = body(id + "springAnchor");
    const rods = qUnion([body(id + "rod0"), body(id + "rod1")]);
    const seats = qUnion([body(id + "fixedSeat0"), body(id + "fixedSeat1"),
                         body(id + "movingSeat0"), body(id + "movingSeat1")]);
    const springs = qUnion([body(id + "spring0" + "sweep"), body(id + "spring1" + "sweep"),
        body(id + "isoSleeve0"), body(id + "isoSleeve1")]);
    const actuator = qUnion([body(id + "switchLever"), body(id + "switchRoller")]);
    const rear = body(id + "rearBlock0");
    const pads = body(id + "rearBlock0"); // R12 fixed return gate
    const stops = yoke; // Integral printed sensing-stop faces are part of P05.
    const captureHardware=qUnion([body(id + "captureScrew0"),body(id + "captureScrew1"),body(id + "captureSpacer0"),body(id + "captureSpacer1")]);
    const device = qBodyType(qUnion([body(id),sensor]), BodyType.SOLID);
    return [
        auditSolidPair(context,"Cassette retainers / guides",captureHardware,base,true),
        auditSolidPair(context,"Cassette retainers / cassette",captureHardware,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette retainers / mechanism",captureHardware,qUnion([palm,yoke,carriage,rods,sensor]),false),
        auditSolidPair(context,"Pusher / sensor and yoke",qUnion([body(id + "loadPusher"),body(id + "pusherNut")]),qUnion([sensor,yoke]),true),
        auditSolidPair(context,"Springs or lock sleeves / seats",springs,seats,true),
        auditSolidPair(context,"Sensor / fixed cassette",sensor,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette / fixed reaction and guide",body(id + "sensorCassette"),base,true),
        auditSolidPair(context,"Cassette / yoke",body(id + "sensorCassette"),yoke,false),
        auditSolidPair(context,"Carriage / open frame and central guide",carriage,base,false),
        auditSolidPair(context,"Carriage / spring mandrels",carriage,rods,false),
        auditSolidPair(context,"Carriage / springs",carriage,springs,false),
        auditSolidPair(context,"Carriage / fixed return gate",carriage,body(id + "rearBlock0"),true),
        auditSolidPair(context,"Carriage / integral return lands and shoes",carriage,pads,true),
        auditSolidPair(context,"Carriage / integral sensing-stop yoke",carriage,stops,true),
        auditSolidPair(context,"Carriage / switch case",carriage,body(id + "switchBody"),false),
        auditSolidPair(context,"Carriage / switch actuator",carriage,actuator,true),
        auditSolidPair(context,"Cam shoe / switch actuator",body(id + "camShoe"),actuator,true),
        auditSolidPair(context,"Cam shoe / carriage well",body(id + "camShoe"),carriage,true),
        auditSolidPair(context,"Cam clamp / carriage and shoe",body(id + "camScrew"),qUnion([carriage,body(id + "camShoe")]),true),
        auditSolidPair(context,"Cam shoe / fixed mechanism",body(id + "camShoe"),qUnion([base,yoke,palm,body(id + "switchBody"),sensor]),false),
        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),
        auditSolidPair(context,"Switch case and actuator / fixed frame",qUnion([body(id + "switchBody"),actuator]),base,true),
        auditSolidPair(context,"Springs / surrounding structure",springs,qUnion([base,yoke,carriage,rear,rods,palm]),false),
        auditSolidPair(context,"Spring seats / structure",seats,qUnion([base,yoke,carriage,rear,rods,palm]),true),
        auditSolidPair(context,"Yoke / base rods and palm",yoke,qUnion([base,rods,palm]),false),
        auditSolidPair(context,"Yoke / sensor",yoke,sensor,false),
        auditSolidPair(context,"Sensor / base",sensor,base,false),
        // R10 Palm/Base is an internal fused interface, not a collision pair.
        auditSolidPair(context,"Palm / carriage and switch",palm,qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Hand / climbing carriage",hand,carriage,true),
        auditSolidPair(context,"Hand / rigid palm block",hand,palm,true),
        auditSolidPair(context,"Hand / remaining device",hand,qSubtraction(device,qUnion([hand,carriage,palm])),false)
    ];
}

// BEGIN GENERATED ENCLOSURE REV A
// Generated from source/build_models.py; coordinates already include clearance shift.
function makeElectronicsEnclosure(context is Context, id is Id) returns Query
{
    const mm=millimeter;
    makeBox(context,id + "P08_Electronics_tray",vector(-46.1,-55,0)*mm,vector(-23.6,55,8.1)*mm);
    makeBox(context,id + "P08_Electronics_tray_1",vector(-45.1,-54,1)*mm,vector(-24.6,54,8.2)*mm);
    cut(context,id + "P08_Electronics_tray_1Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_1"));
    makeBox(context,id + "P08_Electronics_tray_2",vector(-41.75,-56,2)*mm,vector(-28.75,-49,7.6)*mm);
    cut(context,id + "P08_Electronics_tray_2Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_2"));
    makeBox(context,id + "P08_Electronics_tray_3",vector(-47,-9.6,2.5)*mm,vector(-43.2,-1.6,5.4)*mm);
    cut(context,id + "P08_Electronics_tray_3Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_3"));
    makeBox(context,id + "P08_Electronics_tray_4",vector(-25,-8,5.4)*mm,vector(-22,5,7.6)*mm);
    cut(context,id + "P08_Electronics_tray_4Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_4"));
    makeBox(context,id + "P08_Electronics_tray_5",vector(-44.6,-52.8,1)*mm,vector(-44,14.8,1.3)*mm);
    join(context,id + "P08_Electronics_tray_5Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_5")]);
    makeBox(context,id + "P08_Electronics_tray_6",vector(-25.7,-52.8,1)*mm,vector(-25.1,14.8,1.3)*mm);
    join(context,id + "P08_Electronics_tray_6Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_6")]);
    makeBox(context,id + "P08_Electronics_tray_7",vector(-44.7,-54,1)*mm,vector(-25,-53.7,2.05)*mm);
    join(context,id + "P08_Electronics_tray_7Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_7")]);
    makeBox(context,id + "P08_Electronics_tray_8",vector(-44.7,15.2,1)*mm,vector(-25,15.5,2.05)*mm);
    join(context,id + "P08_Electronics_tray_8Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_8")]);
    makeBox(context,id + "P08_Electronics_tray_9",vector(-41.75,21.5,1)*mm,vector(-29.25,53.5,1.3)*mm);
    join(context,id + "P08_Electronics_tray_9Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_9")]);
    makeBox(context,id + "P08_Electronics_tray_10",vector(-42.55,21.5,1)*mm,vector(-41.75,54,2.3)*mm);
    join(context,id + "P08_Electronics_tray_10Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_10")]);
    makeBox(context,id + "P08_Electronics_tray_11",vector(-29.25,21.5,1)*mm,vector(-28.45,54,2.3)*mm);
    join(context,id + "P08_Electronics_tray_11Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_11")]);
    makeBox(context,id + "P08_Electronics_tray_12",vector(-42.55,21.5,1)*mm,vector(-28.45,21.8,2.3)*mm);
    join(context,id + "P08_Electronics_tray_12Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_12")]);
    makeBox(context,id + "P08_Electronics_tray_13",vector(-42.55,53.5,1)*mm,vector(-28.45,54,2.3)*mm);
    join(context,id + "P08_Electronics_tray_13Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_13")]);
    makeCylinder(context,id + "P08_Electronics_tray_14",vector(-43.2,18,0.9)*mm,vector(-43.2,18,8.1)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_14Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_14")]);
    makeCylinder(context,id + "P08_Electronics_tray_15",vector(-43.2,18,3.8)*mm,vector(-43.2,18,8.2)*mm,0.625*mm);
    cut(context,id + "P08_Electronics_tray_15Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_15"));
    makeCylinder(context,id + "P08_Electronics_tray_16",vector(-43.2,50,0.9)*mm,vector(-43.2,50,8.1)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_16Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_16")]);
    makeCylinder(context,id + "P08_Electronics_tray_17",vector(-43.2,50,3.8)*mm,vector(-43.2,50,8.2)*mm,0.625*mm);
    cut(context,id + "P08_Electronics_tray_17Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_17"));
    makeCylinder(context,id + "P08_Electronics_tray_18",vector(-26.5,50,0.9)*mm,vector(-26.5,50,8.1)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_18Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_18")]);
    makeCylinder(context,id + "P08_Electronics_tray_19",vector(-26.5,50,3.8)*mm,vector(-26.5,50,8.2)*mm,0.625*mm);
    cut(context,id + "P08_Electronics_tray_19Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_19"));
    makeCylinder(context,id + "P08_Electronics_tray_20",vector(-26.5,24,0.9)*mm,vector(-26.5,24,3.4)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_20Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_20")]);
    makeCylinder(context,id + "P08_Electronics_tray_22",vector(-26.5,31,0.9)*mm,vector(-26.5,31,3.4)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_22Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_22")]);
    makeBox(context,id + "P08_Electronics_tray_24",vector(-29,-59,8.1)*mm,vector(-24,-54,8.9)*mm);
    join(context,id + "P08_Electronics_tray_24Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_24")]);
    makeBox(context,id + "P08_Electronics_tray_25",vector(-29,-62,7)*mm,vector(-24,-56,8.9)*mm);
    join(context,id + "P08_Electronics_tray_25Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_25")]);
    makeCylinder(context,id + "P08_Electronics_tray_26",vector(-26.5,-59,8.8)*mm,vector(-26.5,-59,9.5)*mm,2.1*mm);
    join(context,id + "P08_Electronics_tray_26Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_26")]);
    makeCylinder(context,id + "P08_Electronics_tray_27",vector(-26.5,-59,6.9)*mm,vector(-26.5,-59,9.6)*mm,1.1*mm);
    cut(context,id + "P08_Electronics_tray_27Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_27"));
    makeBox(context,id + "P08_Electronics_tray_28",vector(-29,54,8.1)*mm,vector(-24,59,8.9)*mm);
    join(context,id + "P08_Electronics_tray_28Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_28")]);
    makeBox(context,id + "P08_Electronics_tray_29",vector(-29,56,7)*mm,vector(-24,62,8.9)*mm);
    join(context,id + "P08_Electronics_tray_29Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_29")]);
    makeCylinder(context,id + "P08_Electronics_tray_30",vector(-26.5,59,8.8)*mm,vector(-26.5,59,9.5)*mm,2.1*mm);
    join(context,id + "P08_Electronics_tray_30Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_30")]);
    makeCylinder(context,id + "P08_Electronics_tray_31",vector(-26.5,59,6.9)*mm,vector(-26.5,59,9.6)*mm,1.1*mm);
    cut(context,id + "P08_Electronics_tray_31Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_31"));

    // R11 additive outside clips; existing R10 P01 remains reusable.
    makeBox(context,id + "R11TraypalmRootL",vector(-46.1,-65.5,0)*mm,vector(-45.1,-54.6,2.4)*mm);
    join(context,id + "R11TraypalmRootLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRootL")]);
    makeBox(context,id + "R11TraypalmBeamL",vector(-45.5,-65.5,0)*mm,vector(-25.6,-64.3,2.4)*mm);
    join(context,id + "R11TraypalmBeamLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmBeamL")]);
    makeBox(context,id + "R11TraypalmPostL",vector(-29,-65.5,0)*mm,vector(-25.6,-64.3,14.9)*mm);
    join(context,id + "R11TraypalmPostLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmPostL")]);
    makeBox(context,id + "R11TraypalmLipL",vector(-29,-65.5,14.7)*mm,vector(-25.6,-63.6,15.5)*mm);
    join(context,id + "R11TraypalmLipLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmLipL")]);
    makeXPrism(context,id + "R11TraypalmRampL",-29*mm,-25.6*mm,[vector(-65.5,15.45)*mm,vector(-65.5,16.2)*mm,vector(-64.3,16.2)*mm,vector(-63.6,15.5)*mm]);
    join(context,id + "R11TraypalmRampLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRampL" + "body")]);
    makeBox(context,id + "R11TraypalmRootBlendL",vector(-45.15,-64.35,0)*mm,vector(-44.5,-63.7,2.4)*mm);
    makeCylinder(context,id + "R11TraypalmRootBlendLTool",vector(-44.5,-63.7,-0.1)*mm,vector(-44.5,-63.7,2.5)*mm,0.6*mm);
    cut(context,id + "R11TraypalmRootBlendLRound",body(id + "R11TraypalmRootBlendL"),body(id + "R11TraypalmRootBlendLTool"));
    join(context,id + "R11TraypalmRootBlendLJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRootBlendL")]);
    makeBox(context,id + "R11TraypalmRootR",vector(-46.1,54.6,0)*mm,vector(-45.1,65.5,2.4)*mm);
    join(context,id + "R11TraypalmRootRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRootR")]);
    makeBox(context,id + "R11TraypalmBeamR",vector(-45.5,64.3,0)*mm,vector(-25.6,65.5,2.4)*mm);
    join(context,id + "R11TraypalmBeamRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmBeamR")]);
    makeBox(context,id + "R11TraypalmPostR",vector(-29,64.3,0)*mm,vector(-25.6,65.5,14.9)*mm);
    join(context,id + "R11TraypalmPostRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmPostR")]);
    makeBox(context,id + "R11TraypalmLipR",vector(-29,63.6,14.7)*mm,vector(-25.6,65.5,15.5)*mm);
    join(context,id + "R11TraypalmLipRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmLipR")]);
    makeXPrism(context,id + "R11TraypalmRampR",-29*mm,-25.6*mm,[vector(63.6,15.5)*mm,vector(64.3,16.2)*mm,vector(65.5,16.2)*mm,vector(65.5,15.45)*mm]);
    join(context,id + "R11TraypalmRampRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRampR" + "body")]);
    makeBox(context,id + "R11TraypalmRootBlendR",vector(-45.15,63.7,0)*mm,vector(-44.5,64.35,2.4)*mm);
    makeCylinder(context,id + "R11TraypalmRootBlendRTool",vector(-44.5,63.7,-0.1)*mm,vector(-44.5,63.7,2.5)*mm,0.6*mm);
    cut(context,id + "R11TraypalmRootBlendRRound",body(id + "R11TraypalmRootBlendR"),body(id + "R11TraypalmRootBlendRTool"));
    join(context,id + "R11TraypalmRootBlendRJoin",[body(id + "P08_Electronics_tray"),body(id + "R11TraypalmRootBlendR")]);
    makeBox(context,id + "R11TraylidCatch0",vector(-47.1,-28.2,5.8)*mm,vector(-46,-24.8,6.8)*mm);
    join(context,id + "R11TraylidCatch0Join",[body(id + "P08_Electronics_tray"),body(id + "R11TraylidCatch0")]);
    makeBox(context,id + "R11TraylidCatch1",vector(-47.1,39.8,5.8)*mm,vector(-46,43.2,6.8)*mm);
    join(context,id + "R11TraylidCatch1Join",[body(id + "P08_Electronics_tray"),body(id + "R11TraylidCatch1")]);
    nameBody(context,body(id + "P08_Electronics_tray"),"P08 PRINT - Snap electronics tray, optional M2 mount");
    finishBody(context,body(id + "P08_Electronics_tray"),color(0.15,0.65,0.78));
    makeBox(context,id + "P09_Electronics_lid",vector(-46.1,-55,8.1)*mm,vector(-23.6,55,8.9)*mm);
    makeBox(context,id + "P09_Electronics_lid_1",vector(-29.1,-56.1,8)*mm,vector(-23.9,-53.9,9)*mm);
    cut(context,id + "P09_Electronics_lid_1Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_1"));
    makeBox(context,id + "P09_Electronics_lid_2",vector(-29.1,53.9,8)*mm,vector(-23.9,56.1,9)*mm);
    cut(context,id + "P09_Electronics_lid_2Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_2"));
    makeCylinder(context,id + "P09_Electronics_lid_3",vector(-43.2,18,8)*mm,vector(-43.2,18,9)*mm,0.9*mm);
    cut(context,id + "P09_Electronics_lid_3Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_3"));
    fCone(context,id + "P09_Electronics_lid_4",{"bottomCenter":vector(-43.2,18,8.3)*mm,"topCenter":vector(-43.2,18,8.9)*mm,"bottomRadius":0.9*mm,"topRadius":1.5*mm});
    cut(context,id + "P09_Electronics_lid_4Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_4"));
    makeCylinder(context,id + "P09_Electronics_lid_5",vector(-43.2,50,8)*mm,vector(-43.2,50,9)*mm,0.9*mm);
    cut(context,id + "P09_Electronics_lid_5Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_5"));
    fCone(context,id + "P09_Electronics_lid_6",{"bottomCenter":vector(-43.2,50,8.3)*mm,"topCenter":vector(-43.2,50,8.9)*mm,"bottomRadius":0.9*mm,"topRadius":1.5*mm});
    cut(context,id + "P09_Electronics_lid_6Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_6"));
    makeCylinder(context,id + "P09_Electronics_lid_7",vector(-26.5,50,8)*mm,vector(-26.5,50,9)*mm,0.9*mm);
    cut(context,id + "P09_Electronics_lid_7Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_7"));
    fCone(context,id + "P09_Electronics_lid_8",{"bottomCenter":vector(-26.5,50,8.3)*mm,"topCenter":vector(-26.5,50,8.9)*mm,"bottomRadius":0.9*mm,"topRadius":1.5*mm});
    cut(context,id + "P09_Electronics_lid_8Cut",body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_8"));
    makeBox(context,id + "P09_Electronics_lid_9",vector(-44.6,-27,2.15)*mm,vector(-25.1,-25,8.2)*mm);
    join(context,id + "P09_Electronics_lid_9Join",[body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_9")]);
    makeBox(context,id + "P09_Electronics_lid_10",vector(-41.5,36,6.6)*mm,vector(-29.5,39,8.2)*mm);
    join(context,id + "P09_Electronics_lid_10Join",[body(id + "P09_Electronics_lid"),body(id + "P09_Electronics_lid_10")]);
    // R11 lid-integral P10 clamp: same contact footprint, no loose tiny bar.
    makeBox(context,id + "R11LidlidRoot0",vector(-48.6,-52,8.1)*mm,vector(-45.9,-48.8,8.9)*mm);
    join(context,id + "R11LidlidRoot0Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidRoot0")]);
    makeBox(context,id + "R11LidlidBeam0",vector(-48.6,-49.2,4.8)*mm,vector(-47.4,-25,8.9)*mm);
    join(context,id + "R11LidlidBeam0Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidBeam0")]);
    makeYPrism(context,id + "R11LidlidHook0",-28*mm,-25*mm,[vector(-47.5,4.2)*mm,vector(-47.4,4.2)*mm,vector(-46.3,4.8)*mm,vector(-46.3,5.7)*mm,vector(-47.5,5.7)*mm]);
    join(context,id + "R11LidlidHook0Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidHook0" + "body")]);
    makeBox(context,id + "R11LidlidRoot1",vector(-48.6,16,8.1)*mm,vector(-45.9,19.2,8.9)*mm);
    join(context,id + "R11LidlidRoot1Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidRoot1")]);
    makeBox(context,id + "R11LidlidBeam1",vector(-48.6,18.8,4.8)*mm,vector(-47.4,43,8.9)*mm);
    join(context,id + "R11LidlidBeam1Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidBeam1")]);
    makeYPrism(context,id + "R11LidlidHook1",40*mm,43*mm,[vector(-47.5,4.2)*mm,vector(-47.4,4.2)*mm,vector(-46.3,4.8)*mm,vector(-46.3,5.7)*mm,vector(-47.5,5.7)*mm]);
    join(context,id + "R11LidlidHook1Join",[body(id + "P09_Electronics_lid"),body(id + "R11LidlidHook1" + "body")]);
    makeBox(context,id + "R11LidintegralWireClamp",vector(-28.1,22.4,3.4)*mm,vector(-24.9,32.6,8.2)*mm);
    join(context,id + "R11LidintegralWireClampJoin",[body(id + "P09_Electronics_lid"),body(id + "R11LidintegralWireClamp")]);
    nameBody(context,body(id + "P09_Electronics_lid"),"P09 PRINT - Snap lid with integral wire clamp");
    finishBody(context,body(id + "P09_Electronics_lid"),color(0.15,0.65,0.78));
    return qUnion([body(id + "P08_Electronics_tray"),body(id + "P09_Electronics_lid")]);
}
// END GENERATED ENCLOSURE REV A

// Printable Rev A enclosure plus nominal PCB/cell/plug envelopes.
// Physical fitting, thermal and RF qualification remain hardware checks.
function makeElectronicsStudy(context is Context, id is Id, actualSensor is Query) returns array
{
    const mm = millimeter;
    const enclosure=makeElectronicsEnclosure(context,id);
    makeBox(context,id + "elecCarrier",vector(-43.35,-53.5,1.3)*mm,vector(-23.85,15,2.1)*mm);
    nameBody(context,body(id + "elecCarrier"),"REF E01 - KiCad PCB 19.5 x 68.5 x 0.8");
    finishBody(context,body(id + "elecCarrier"),color(0.10,0.42,0.27));
    makeBox(context,id + "elecPartU1",vector(-42.5625,-53.554,2.1)*mm,vector(-24.6725,-32.514,7.1)*mm);
    nameBody(context,body(id + "elecPartU1"),"REF PCB U1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartU1"),color(0.15,0.40,0.90));
    makeBox(context,id + "elecPartU2",vector(-38.295,-17.395,2.1)*mm,vector(-34.805,-13.205,3.75)*mm);
    nameBody(context,body(id + "elecPartU2"),"REF PCB U2 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartU2"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartL1",vector(-42.495,-19.695,2.1)*mm,vector(-38.705,-15.905,3.75)*mm);
    nameBody(context,body(id + "elecPartL1"),"REF PCB L1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartL1"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartD1",vector(-43.345,-15.095,2.1)*mm,vector(-38.555,-12.705,3.75)*mm);
    nameBody(context,body(id + "elecPartD1"),"REF PCB D1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartD1"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC3",vector(-38.295,-19.825,2.1)*mm,vector(-34.805,-17.775,3.75)*mm);
    nameBody(context,body(id + "elecPartC3"),"REF PCB C3 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC3"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC4",vector(-42.845,-12.525,2.1)*mm,vector(-39.355,-10.475,3.75)*mm);
    nameBody(context,body(id + "elecPartC4"),"REF PCB C4 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC4"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR3",vector(-34.625,-17.025,2.1)*mm,vector(-33.075,-13.975,3.75)*mm);
    nameBody(context,body(id + "elecPartR3"),"REF PCB R3 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR3"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR4",vector(-34.625,-13.525,2.1)*mm,vector(-33.075,-10.475,3.75)*mm);
    nameBody(context,body(id + "elecPartR4"),"REF PCB R4 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR4"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC5",vector(-32.875,-17.025,2.1)*mm,vector(-31.325,-13.975,3.75)*mm);
    nameBody(context,body(id + "elecPartC5"),"REF PCB C5 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC5"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartU3",vector(-29.595,-15.195,2.1)*mm,vector(-26.105,-11.005,3.75)*mm);
    nameBody(context,body(id + "elecPartU3"),"REF PCB U3 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartU3"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC7",vector(-29.595,-17.475,2.1)*mm,vector(-26.105,-15.425,3.75)*mm);
    nameBody(context,body(id + "elecPartC7"),"REF PCB C7 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC7"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC6",vector(-28.625,-10.875,2.1)*mm,vector(-27.075,-7.825,3.75)*mm);
    nameBody(context,body(id + "elecPartC6"),"REF PCB C6 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC6"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartU4",vector(-37.245,-7.295,2.1)*mm,vector(-29.455,-1.705,3.75)*mm);
    nameBody(context,body(id + "elecPartU4"),"REF PCB U4 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartU4"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC14",vector(-29.125,-7.725,2.1)*mm,vector(-27.575,-4.675,3.75)*mm);
    nameBody(context,body(id + "elecPartC14"),"REF PCB C14 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC14"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC12",vector(-29.125,-4.525,2.1)*mm,vector(-27.575,-1.475,3.75)*mm);
    nameBody(context,body(id + "elecPartC12"),"REF PCB C12 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC12"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC13",vector(-33.375,-9.775,2.1)*mm,vector(-30.325,-8.225,3.75)*mm);
    nameBody(context,body(id + "elecPartC13"),"REF PCB C13 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC13"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartSW2",vector(-43.145,-9.545,2.1)*mm,vector(-37.555,-1.655,4.6)*mm);
    nameBody(context,body(id + "elecPartSW2"),"REF PCB SW2 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartSW2"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartJ1",vector(-36.495,4.355,2.1)*mm,vector(-27.205,14.645,7.75)*mm);
    nameBody(context,body(id + "elecPartJ1"),"REF PCB J1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartJ1"),color(0.86,0.86,0.82));
    makeBox(context,id + "elecPartJ2",vector(-26.895,-7.145,2.1)*mm,vector(-24.205,3.745,4.4)*mm);
    nameBody(context,body(id + "elecPartJ2"),"REF PCB J2 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartJ2"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartJ3",vector(-42.695,6.915,2.1)*mm,vector(-40.005,12.085,4.4)*mm);
    nameBody(context,body(id + "elecPartJ3"),"REF PCB J3 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartJ3"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR13",vector(-27.075,3.975,2.1)*mm,vector(-24.025,5.525,3.75)*mm);
    nameBody(context,body(id + "elecPartR13"),"REF PCB R13 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR13"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC8",vector(-31.875,-1.025,2.1)*mm,vector(-30.325,2.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC8"),"REF PCB C8 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC8"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR7",vector(-30.075,-1.275,2.1)*mm,vector(-27.025,0.275,3.75)*mm);
    nameBody(context,body(id + "elecPartR7"),"REF PCB R7 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR7"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR8",vector(-30.075,0.725,2.1)*mm,vector(-27.025,2.275,3.75)*mm);
    nameBody(context,body(id + "elecPartR8"),"REF PCB R8 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR8"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC9",vector(-33.625,-1.025,2.1)*mm,vector(-32.075,2.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC9"),"REF PCB C9 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC9"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC10",vector(-35.375,-1.025,2.1)*mm,vector(-33.825,2.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC10"),"REF PCB C10 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC10"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC11",vector(-37.125,-1.025,2.1)*mm,vector(-35.575,2.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC11"),"REF PCB C11 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC11"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR9",vector(-40.375,-0.275,2.1)*mm,vector(-37.325,1.275,3.75)*mm);
    nameBody(context,body(id + "elecPartR9"),"REF PCB R9 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR9"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR10",vector(-40.375,1.475,2.1)*mm,vector(-37.325,3.025,3.75)*mm);
    nameBody(context,body(id + "elecPartR10"),"REF PCB R10 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR10"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC1",vector(-34.595,-20.525,2.1)*mm,vector(-31.105,-18.475,3.75)*mm);
    nameBody(context,body(id + "elecPartC1"),"REF PCB C1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC1"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartQ1",vector(-41.325,3.255,2.1)*mm,vector(-37.375,6.745,3.75)*mm);
    nameBody(context,body(id + "elecPartQ1"),"REF PCB Q1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartQ1"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC15",vector(-43.125,0.975,2.1)*mm,vector(-41.575,4.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC15"),"REF PCB C15 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC15"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC16",vector(-37.125,2.225,2.1)*mm,vector(-34.075,3.775,3.75)*mm);
    nameBody(context,body(id + "elecPartC16"),"REF PCB C16 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC16"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartC2",vector(-26.875,5.975,2.1)*mm,vector(-25.325,9.025,3.75)*mm);
    nameBody(context,body(id + "elecPartC2"),"REF PCB C2 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartC2"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR1",vector(-26.875,9.225,2.1)*mm,vector(-25.325,12.275,3.75)*mm);
    nameBody(context,body(id + "elecPartR1"),"REF PCB R1 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR1"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR11",vector(-37.125,-10.775,2.1)*mm,vector(-35.575,-7.725,3.75)*mm);
    nameBody(context,body(id + "elecPartR11"),"REF PCB R11 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR11"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR12",vector(-32.875,-13.025,2.1)*mm,vector(-31.325,-9.975,3.75)*mm);
    nameBody(context,body(id + "elecPartR12"),"REF PCB R12 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR12"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR14",vector(-26.875,-10.525,2.1)*mm,vector(-25.325,-7.475,3.75)*mm);
    nameBody(context,body(id + "elecPartR14"),"REF PCB R14 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR14"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR15",vector(-30.875,-19.275,2.1)*mm,vector(-27.825,-17.725,3.75)*mm);
    nameBody(context,body(id + "elecPartR15"),"REF PCB R15 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR15"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR16",vector(-25.875,-14.025,2.1)*mm,vector(-24.325,-10.975,3.75)*mm);
    nameBody(context,body(id + "elecPartR16"),"REF PCB R16 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR16"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR17",vector(-39.875,6.975,2.1)*mm,vector(-36.825,8.525,3.75)*mm);
    nameBody(context,body(id + "elecPartR17"),"REF PCB R17 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR17"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR18",vector(-39.875,8.725,2.1)*mm,vector(-36.825,10.275,3.75)*mm);
    nameBody(context,body(id + "elecPartR18"),"REF PCB R18 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR18"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR19",vector(-33.875,2.225,2.1)*mm,vector(-30.825,3.775,3.75)*mm);
    nameBody(context,body(id + "elecPartR19"),"REF PCB R19 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR19"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR2",vector(-30.375,2.475,2.1)*mm,vector(-27.325,4.025,3.75)*mm);
    nameBody(context,body(id + "elecPartR2"),"REF PCB R2 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR2"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR20",vector(-39.875,10.475,2.1)*mm,vector(-36.825,12.025,3.75)*mm);
    nameBody(context,body(id + "elecPartR20"),"REF PCB R20 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR20"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR21",vector(-40.875,12.225,2.1)*mm,vector(-37.825,13.775,3.75)*mm);
    nameBody(context,body(id + "elecPartR21"),"REF PCB R21 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR21"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR5",vector(-27.625,-19.275,2.1)*mm,vector(-24.575,-17.725,3.75)*mm);
    nameBody(context,body(id + "elecPartR5"),"REF PCB R5 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR5"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecPartR6",vector(-25.875,-17.275,2.1)*mm,vector(-24.325,-14.225,3.75)*mm);
    nameBody(context,body(id + "elecPartR6"),"REF PCB R6 - courtyard and height envelope");
    finishBody(context,body(id + "elecPartR6"),color(0.20,0.70,0.48));
    makeBox(context,id + "elecBattery",vector(-40,22,1.5)*mm,vector(-28.5,53,5.3)*mm);
    nameBody(context,body(id + "elecBattery"),"REF E05 - 100mAh LiPo nominal 11.5 x 31 x 3.8");
    finishBody(context,body(id + "elecBattery"),color(0.92,0.68,0.16));
    makeBox(context,id + "elecUsb",vector(-39.5,-74,2.4)*mm,vector(-28.5,-54,7.3)*mm);
    nameBody(context,body(id + "elecUsb"),"REF E06 - USB approach clearance");
    finishBody(context,body(id + "elecUsb"),color(0.66,0.40,0.90,0.35));
    makeBox(context,id + "elecMate",vector(-35.85,14.7,2.45)*mm,vector(-27.85,20.7,7.75)*mm);
    nameBody(context,body(id + "elecMate"),"REF E07 - battery mating plug and lead allowance");
    finishBody(context,body(id + "elecMate"),color(0.85,0.75,0.55,0.4));
    makeBox(context,id + "elecButton",vector(-45.25,-7.1,2.8)*mm,vector(-42.55,-4.1,5.1)*mm);
    nameBody(context,body(id + "elecButton"),"REF E08 - side-button actuator travel envelope");
    finishBody(context,body(id + "elecButton"),color(0.90,0.45,0.16,0.35));
    const housing=enclosure;
    const carrier=body(id + "elecCarrier");
    const battery=body(id + "elecBattery");
    const populated=qUnion([body(id + "elecPartU1"),body(id + "elecPartU2"),body(id + "elecPartL1"),body(id + "elecPartD1"),body(id + "elecPartC3"),body(id + "elecPartC4"),body(id + "elecPartR3"),body(id + "elecPartR4"),body(id + "elecPartC5"),body(id + "elecPartU3"),body(id + "elecPartC7"),body(id + "elecPartC6"),body(id + "elecPartU4"),body(id + "elecPartC14"),body(id + "elecPartC12"),body(id + "elecPartC13"),body(id + "elecPartSW2"),body(id + "elecPartJ1"),body(id + "elecPartJ2"),body(id + "elecPartJ3"),body(id + "elecPartR13"),body(id + "elecPartC8"),body(id + "elecPartR7"),body(id + "elecPartR8"),body(id + "elecPartC9"),body(id + "elecPartC10"),body(id + "elecPartC11"),body(id + "elecPartR9"),body(id + "elecPartR10"),body(id + "elecPartC1"),body(id + "elecPartQ1"),body(id + "elecPartC15"),body(id + "elecPartC16"),body(id + "elecPartC2"),body(id + "elecPartR1"),body(id + "elecPartR11"),body(id + "elecPartR12"),body(id + "elecPartR14"),body(id + "elecPartR15"),body(id + "elecPartR16"),body(id + "elecPartR17"),body(id + "elecPartR18"),body(id + "elecPartR19"),body(id + "elecPartR2"),body(id + "elecPartR20"),body(id + "elecPartR21"),body(id + "elecPartR5"),body(id + "elecPartR6")]);
    const cable=body(id + "elecMate");
    const actuator=body(id + "elecButton");
    const components=qUnion([carrier,populated,battery,cable,actuator]);
    const usb=body(id + "elecUsb");
    opTransform(context,id + "electronicsClearanceShift",{"bodies":qUnion([components,usb]),"transform":transform(vector(-1.25,0,0)*mm)});
    const electronics=qUnion([housing,components,usb]);
    const hand=body(id + "handReference");
    const mechanism=qSubtraction(qBodyType(qUnion([body(id),actualSensor]),BodyType.SOLID),qUnion([electronics,hand]));
    return [
        auditSolidPair(context,"Electronics housing / mechanism",housing,mechanism,true),
        auditSolidPair(context,"Electronics components / mechanism",components,mechanism,false),
        auditSolidPair(context,"Electronics components / housing",components,housing,true),
        auditSolidPair(context,"Battery / populated carrier and plug",battery,qUnion([carrier,populated,cable]),false),
        auditSolidPair(context,"USB approach / mechanism",usb,mechanism,false),
        auditSolidPair(context,"USB approach / housing",usb,housing,false),
        auditSolidPair(context,"Electronics study / hand",electronics,hand,false)
    ];
}

annotation { "Feature Type Name" : "FingerworkerFlat132ActualSensor", "Feature Name Template" : "Flat132 R12 - simplified click assembly" }
export const fingerworkerMVP = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Aligned official TE FX1901 solid (derive before this feature)",
            "Filter" : EntityType.BODY && BodyType.SOLID, "MaxNumberOfPicks" : 1 }
        definition.actualSensor is Query;
        annotation { "Name" : "User travel (0 to 30 mm; fixed rest and sensor reaction)" }
        isLength(definition.previewTravel, LENGTH_BOUNDS);
        annotation { "Name" : "Cam trim (-0.8 to +0.8 mm; physical calibration)" }
        isLength(definition.camTrim, { (millimeter) : [-0.8, 0, 0.8] } as LengthBoundSpec);
        annotation { "Name" : "Febrotec pair: ON = 0X-DF2194 (lighter), OFF = 0X-DF2185" }
        definition.lightSprings is boolean;
        annotation { "Name" : "Isometric: BOTH81 mm sleeves; fixed15 mm approach" }
        definition.isometricLock is boolean;
        annotation { "Name" : "Show hand reference (exclude from manufacturing)" }
        definition.showHand is boolean;
        annotation { "Name" : "Show electronics enclosure and component references" }
        definition.showElectronics is boolean;
    }
    {
        const mm = millimeter;
        if (size(evaluateQuery(context,definition.actualSensor)) != 1)
            throw regenError("Select the aligned, unmodified official TE FX1901 manufacturer solid.",["actualSensor"]);
        const sensorBox = evBox3d(context,{"topology":definition.actualSensor,"tight":true});
        if (norm(sensorBox.minCorner-vector(-9.85,-12.5,5.5)*mm)>0.05*mm ||
            norm(sensorBox.maxCorner-vector(-1.9,27,30.5)*mm)>0.05*mm)
            throw regenError("Use the apex-aligned official STEP at its base origin; do not rescale or offset it.",["actualSensor"]);
        nameBody(context,definition.actualSensor,"H01 ACTUAL TE FX1901-0001-0200-L manufacturer STEP rev F");
        finishBody(context,definition.actualSensor,color(0.75,0.76,0.77));
        const preload = 0*mm; // R12 fixed sensor reaction, no adjustable preload.
        // q is absolute carriage displacement from the R4 rest. User travel
        // u starts at the new5 mm closer rest; full dynamic travel is retained.
        const rearAdvance=0*mm;
        const restOffset=5*mm+rearAdvance;
        const camTrim=definition.camTrim;
        if (camTrim < -0.8*mm || camTrim > 0.8*mm)
            throw regenError("Cam trim must be between-0.8 and+0.8 mm.",["camTrim"]);
        const maxDynamicTravel = 30 * mm - preload - rearAdvance;
        if (!definition.isometricLock && definition.previewTravel > maxDynamicTravel + 1e-6*mm)
            throw regenError("R12 user travel is0..30 mm with fixed rest and sensor reaction.", ["previewTravel"]);
        // Selected81 mm sleeves move ISO grip5 mm closer than R4.
        // They seat after u=15 mm from the fixed rest.
        const stroke = definition.isometricLock ? 20 * mm - preload : restOffset+definition.previewTravel;
        const userTravel=stroke-restOffset;
        if (stroke < restOffset || stroke > 35*mm)
            throw regenError("R5 absolute carriage offset must be5..35 mm; user travel must be nonnegative.", ["previewTravel"]);

        // Fixed dimensions form a coordinated prototype, not independent knobs.
        // Envelope176.5 x132 x35 at rear advance0; base151 x132, floor6 (Z-2 to Z4); rear washer pocket retains2.8 mm floor.
        const baseThickness = 6 * mm;
        const gripTopZ = 30 * mm;
        const palmCenterX = -27 * mm;
        const palmCenterZ = 19.75 * mm;
        const palmPlateTopZ = 14.5 * mm;
        const springZ = 18 * mm;
        var baseBodies = [];
        var movingBodies = [];

        makeBox(context,id + "base",vector(-22,-66,-2)*mm,vector(129,66,4)*mm);
        opFillet(context,id + "baseRound",{
            "entities": qCreatedBy(id + "base",EntityType.EDGE),
            "radius": 1.5 * mm, "tangentPropagation": true });
        // Two open windows remove the broad unused floor, leaving a central
        // spine and two spring ribs connected at the fixed and return ends.
        var baseWindowTools=[];
        for (var side in [-1,1])
        {
            const suffix=side == -1 ? "0" : "1";
            const lowY=side == -1 ? -38 : 27;
            const highY=side == -1 ? -27 : 38;
            makeBox(context,id + ("baseWindow"~suffix),vector(22,lowY,-3)*mm,vector(110,highY,5)*mm);
            opFillet(context,id + ("baseWindowRound"~suffix),{
                "entities":qParallelEdges(qCreatedBy(id + ("baseWindow"~suffix),EntityType.EDGE),vector(0,0,1)),
                "radius":5*mm,"tangentPropagation":true });
            baseWindowTools=append(baseWindowTools,body(id + ("baseWindow"~suffix)));
        }
        cut(context,id + "openBase",body(id + "base"),qUnion(baseWindowTools));
        baseBodies = append(baseBodies,body(id + "base"));

        // R10 integral palm: retain two feet outside the sensor wall and
        // inside the rod blocks; their former locating keys are omitted.
        // Case frontX-23.6 clears foot wrist edgeX-23 by0.6 mm.
        // Feet and upper drops receive0.2 mm positive vertical overlap.
        makeBox(context,id + "palmFootLeft",vector(-23,-37,3.8)*mm,vector(-17,-26,6.5)*mm);
        makeBox(context,id + "palmFootRight",vector(-23,26,3.8)*mm,vector(-17,37,6.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmFootLeft"));
        baseBodies=append(baseBodies,body(id + "palmFootRight"));
        makeBox(context,id + "palmPad",vector(-37.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);
        opFillet(context,id + "palmCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmPad",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        makeBox(context,id + "palmEarLeft",vector(-30,-37,9.5)*mm,vector(-17,-26,14.5)*mm);
        makeBox(context,id + "palmEarRight",vector(-30,26,9.5)*mm,vector(-17,37,14.5)*mm);
        // Only the forward clamp drops belowZ9.5, retaining0.6 mm case gap
        // atX-23. The original upper root stays above the unchanged case.
        makeBox(context,id + "palmClampDropLeft",vector(-23,-37,6.3)*mm,vector(-17,-26,9.6)*mm);
        makeBox(context,id + "palmClampDropRight",vector(-23,26,6.3)*mm,vector(-17,37,9.6)*mm);
        join(context,id + "palmEarDropJoinLeft",[body(id + "palmEarLeft"),body(id + "palmClampDropLeft")]);
        join(context,id + "palmEarDropJoinRight",[body(id + "palmEarRight"),body(id + "palmClampDropRight")]);
        makeCylinder(context,id + "palmBolsterCore",vector(-27,-58,19.75)*mm,
            vector(-27,58,19.75)*mm,7.75*mm);
        opFillet(context,id + "palmEnds",{
            "entities":qCreatedBy(id + "palmBolsterCore",EntityType.EDGE),
            "radius":2*mm,"tangentPropagation":true });
        // Keep the wrist-facing half only. All feet, ears and enclosure pilots
        // retain their R2 coordinates; the contact face moves exactly+7 mm.
        makeBox(context,id + "palmCoreForwardHalfTool",vector(-27,-60,0)*mm,vector(0,60,40)*mm);
        cut(context,id + "palmCoreHalfCut",body(id + "palmBolsterCore"),body(id + "palmCoreForwardHalfTool"));
        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore"),
            body(id + "palmEarLeft"),body(id + "palmEarRight")]);
        // Electronics enclosure M2 insert pilots in underside of fixed palm.
        // Blind depth 4 mm; 1 mm remains to the flat plate top.
        for (var y in [-59,59])
        {
            const suffix=y < 0 ? "0" : "1";
            makeCylinder(context,id + ("enclosurePalmPilot"~suffix),
                vector(-26.5,y,9.4)*mm,vector(-26.5,y,13.5)*mm,1.6*mm);
            cut(context,id + ("enclosurePalmPilotCut"~suffix),
                body(id + "palmPad"),body(id + ("enclosurePalmPilot"~suffix)));
        }
        // R10: no palm attachment hardware or key slots. Keep the later
        // rear-cap and switch insert pilots in this shared tools collection.
        var insertTools=[];
        var n=0;
        // R6 one-piece rigid palm block. Preserve the former cap's outer
        // wrist-facing half-round and rounded ends, but omit its core bore and
        // bottom cut. Solid stock joins the original core and plate, including
        // the old0.1 mm plate-to-cap split; there is no internal sleeve seam.
        // Former front retaining returns are unnecessary without a loose cap.
        makeCylinder(context,id + "palmContactStock",vector(-27,-43,19.75)*mm,
            vector(-27,43,19.75)*mm,10.25*mm);
        opFillet(context,id + "palmContactEnds",{
            "entities":qCreatedBy(id + "palmContactStock",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeBox(context,id + "palmContactForwardHalfTool",vector(-27,-45,0)*mm,
            vector(0,45,40)*mm);
        cut(context,id + "palmContactHalfCut",body(id + "palmContactStock"),
            body(id + "palmContactForwardHalfTool"));
        join(context,id + "palmSolidBlockJoin",
            [body(id + "palmPad"),body(id + "palmContactStock")]);
        // R8: extend the existing flat underside over the exposed enclosure.
        // Actual P09 lid is square X-46.1..-23.6, Y+/-55, topZ8.9.
        // R2 plan corners lie outside that footprint because this ledge spans
        // Y+/-64. Its wrist datum is flushX-46.1, so whole-device X is unchanged.
        // Four-and-a-quarter mm overlap into the old plate gives a continuous
        // union through its rounded corners; neither mounts nor lid are cut.
        makeBox(context,id + "palmCoverLedge",vector(-46.1,-64,9.5)*mm,
            vector(-33,64,11.5)*mm);
        opFillet(context,id + "palmCoverCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmCoverLedge",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        // Round the upper perimeter only. Keep underside and lower wrist band
        // intact so top-view projection still fully covers the square lid.
        opFillet(context,id + "palmCoverUpperEdge",{
            "entities":qContainsPoint(qOwnedByBody(body(id + "palmCoverLedge"),EntityType.EDGE),
                vector(-46.1,0,11.5)*mm),
            "radius":0.5*mm,"tangentPropagation":true });
        join(context,id + "palmCoverJoin",[body(id + "palmPad"),body(id + "palmCoverLedge")]);
        // R10: retain R9 broad braces and blend roots, and extend their
        // ends0.2 mm into the FIXED portal starting atX-22.75. This positive
        // volume becomes one printed body at the final union, never a fit.
        // The obsolete H15 service notch is filled; the palm remains integral.
        // Moving P05 and the sensor stack are not part of this fusion.
        // Explicit box-minus-cylinder root stocks formR1.2 concave blends;
        // this avoids topology-dependent post-union fillet selection.
        var palmBraceStocks=[body(id + "palmPad")];
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const loY=side == -1 ? -25 : 18;
            const hiY=loY+7;
            makeBox(context,id + ("palmBracePad"~s),vector(-29,loY,14)*mm,
                vector(-22.55,hiY,27)*mm);
            palmBraceStocks=append(palmBraceStocks,body(id + ("palmBracePad"~s)));
            // Side-root wedges are tangent atX-27 and the pad side. Their
            // extra0.1 mm rear overlap guarantees positive fusion to P02.
            for (var edge in [0,1])
            {
                const t=s~edge;
                const edgeY=edge == 0 ? loY : hiY;
                const centerY=edge == 0 ? edgeY-1.2 : edgeY+1.2;
                const wedgeLoY=edge == 0 ? centerY : edgeY;
                const wedgeHiY=edge == 0 ? edgeY : centerY;
                makeBox(context,id + ("palmBraceSideRoot"~t),
                    vector(-27.1,wedgeLoY,14)*mm,vector(-25.8,wedgeHiY,27)*mm);
                makeCylinder(context,id + ("palmBraceSideRoundTool"~t),
                    vector(-25.8,centerY,13.9)*mm,
                    vector(-25.8,centerY,27.1)*mm,1.2*mm);
                cut(context,id + ("palmBraceSideRound"~t),
                    body(id + ("palmBraceSideRoot"~t)),
                    body(id + ("palmBraceSideRoundTool"~t)));
                palmBraceStocks=append(palmBraceStocks,body(id + ("palmBraceSideRoot"~t)));
            }
            // Upper-rootR1.2 tangent blends spread the root into the solid
            // half-round. The lower root already overlaps its5 mm plate.
            makeBox(context,id + ("palmBraceTopRoot"~s),
                vector(-27.1,loY,27)*mm,vector(-25.8,hiY,28.2)*mm);
            makeCylinder(context,id + ("palmBraceTopRoundTool"~s),
                vector(-25.8,loY-0.1,28.2)*mm,
                vector(-25.8,hiY+0.1,28.2)*mm,1.2*mm);
            cut(context,id + ("palmBraceTopRound"~s),
                body(id + ("palmBraceTopRoot"~s)),
                body(id + ("palmBraceTopRoundTool"~s)));
            palmBraceStocks=append(palmBraceStocks,body(id + ("palmBraceTopRoot"~s)));
        }
        join(context,id + "palmBraceJoin",palmBraceStocks);
        nameBody(context,body(id + "palmPad"),
            "R10 construction region - solid palm and braces, fused into P01 at feature end");

        // Carriage: two outside spring arms joined to a rounded central pocket.
        makeBox(context,id + "carriageBridge",vector(116,-63,5)*mm,vector(124,63,24)*mm);
        var carriageBodies=[body(id + "carriageBridge")];
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const loY = side == -1 ? -63 : 40;
            const hiY = side == -1 ? -40 : 63;
            makeBox(context,id + ("arm"~s),vector(116,loY,7)*mm,vector(124,hiY,30)*mm);
            // R1 outside corners reduce handling sharpness without changing the stop datum.
            opFillet(context,id + ("armRound"~s),{
                "entities":qParallelEdges(qCreatedBy(id + ("arm"~s),EntityType.EDGE),vector(0,0,1)),
                "radius":1*mm,"tangentPropagation":true });
            opFillet(context,id + ("armTopRound"~s),{
                "entities":qContainsPoint(qCreatedBy(id + ("arm"~s),EntityType.EDGE),vector(116,(loY+hiY)/2,30)*mm),
                "radius":1*mm,"tangentPropagation":true });
            carriageBodies=append(carriageBodies,body(id + ("arm"~s)));
        }
        makeBox(context,id + "switchCam",vector(65,-2,7)*mm,vector(78,8,15)*mm);
        carriageBodies=append(carriageBodies,body(id + "switchCam"));
        makeBox(context,id + "climbingDeck",vector(65,-42,5)*mm,vector(124,42,30)*mm);
        opFillet(context,id + "deckOuterRound",{
            "entities":qParallelEdges(qCreatedBy(id + "climbingDeck",EntityType.EDGE),vector(0,0,1)),
            "radius":5*mm,"tangentPropagation":true });
        opFillet(context,id + "deckTopRound",{
            "entities":qContainsPoint(qCreatedBy(id + "climbingDeck",EntityType.EDGE),vector(65,0,30)*mm),
            "radius":1*mm,"tangentPropagation":true });
        carriageBodies=append(carriageBodies,body(id + "climbingDeck"));
        join(context,id + "joinCarriage",carriageBodies);
        makeBox(context,id + "pocketTool",vector(77,-36,10)*mm,vector(111,36,36)*mm);
        opFillet(context,id + "pocketPlanRound",{
            "entities":qParallelEdges(qCreatedBy(id + "pocketTool",EntityType.EDGE),vector(0,0,1)),
            "radius":8*mm,"tangentPropagation":true });
        cut(context,id + "cutPocket",body(id + "carriageBridge"),body(id + "pocketTool"));
        opFillet(context,id + "lipRound",{
            "entities":qCreatedBy(id + "cutPocket",EntityType.EDGE),
            "radius":4*mm,"tangentPropagation":true });
        // Restore the local upper roof after deckTopRound's tangent R1 blend.
        // Two shallow caps stay within the existing84 mm deck width andZ30.
        // R0.35 plan corners blend each short cap; no spring-facing projection.
        // Join before cutting R12 so the steel-seat clearance stays unchanged.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const lowY=side == -1 ? -42 : 40.5;
            const highY=side == -1 ? -40.5 : 42;
            makeBox(context,id + ("rearRoofCap"~t),
                vector(111.5,lowY,28.5)*mm,vector(116.5,highY,30)*mm);
            opFillet(context,id + ("rearRoofCapPlanRound"~t),{
                "entities":qParallelEdges(qCreatedBy(id + ("rearRoofCap"~t),EntityType.EDGE),vector(0,0,1)),
                "radius":0.35*mm,"tangentPropagation":true });
            join(context,id + ("rearRoofCapJoin"~t),
                [body(id + "carriageBridge"),body(id + ("rearRoofCap"~t))]);
        }
        // R12 clearance lies entirely behind pocket X111. Steel seat OD22
        // occupies X113..116; retain its X116 planar reaction datum.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            makeCylinder(context,id + ("movingSeatRelief"~t),
                vector(112,side*51,18)*mm,vector(116,side*51,18)*mm,12*mm);
            cut(context,id + ("movingSeatReliefCut"~t),body(id + "carriageBridge"),
                body(id + ("movingSeatRelief"~t)));
        }
        movingBodies=append(movingBodies,body(id + "carriageBridge"));
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT STUDY - Flat132 72 mm clear pocket, radius12 seat reliefs");
        // P11 is a manually positioned, top-clamped cam shoe. It carries
        // switch actuation only; it is outside the500 N sensor force path.
        // camTrim represents physical switch calibration, independent of the fixed stops.
        // The entire old horizontal cam bore is omitted, restoring that stock.
        makeBox(context,id + "camShoeWell",vector(64,-1,8.6)*mm,vector(74.8,8,19)*mm);
        makeBox(context,id + "camLeverRelief",vector(64,-14,8.6)*mm,vector(67.2,8,19)*mm);
        // Roof slot covers e-p=-2.8..+0.8; head is recessed below the rolled lip.
        makeCylinder(context,id + "camRoofSlot0",vector(67.7,3.5,18.9)*mm,vector(67.7,3.5,25.2)*mm,1.7*mm);
        makeCylinder(context,id + "camRoofSlot1",vector(71.3,3.5,18.9)*mm,vector(71.3,3.5,25.2)*mm,1.7*mm);
        makeBox(context,id + "camRoofSlotMid",vector(67.7,1.8,18.9)*mm,vector(71.3,5.2,25.2)*mm);
        makeCylinder(context,id + "camHeadSlot0",vector(67.7,3.5,25)*mm,vector(67.7,3.5,31)*mm,3*mm);
        makeCylinder(context,id + "camHeadSlot1",vector(71.3,3.5,25)*mm,vector(71.3,3.5,31)*mm,3*mm);
        makeBox(context,id + "camHeadSlotMid",vector(67.7,0.5,25)*mm,vector(71.3,6.5,31)*mm);
        cut(context,id + "camShoeMount",body(id + "carriageBridge"),qUnion([
            body(id + "camShoeWell"),body(id + "camLeverRelief"),
            body(id + "camRoofSlot0"),body(id + "camRoofSlot1"),body(id + "camRoofSlotMid"),
            body(id + "camHeadSlot0"),body(id + "camHeadSlot1"),body(id + "camHeadSlotMid")]));
        makeBox(context,id + "camShoe",vector(69,-0.7,9)*mm,vector(73.5,7.7,19)*mm);
        // Forward upper boss stays above roller topZ12.3 by0.9 mm nominally.
        makeBox(context,id + "camShoeBoss",vector(67.5,-0.7,13.2)*mm,vector(69,7.7,19)*mm);
        join(context,id + "joinCamShoe",[body(id + "camShoe"),body(id + "camShoeBoss")]);
        makeCylinder(context,id + "camShoeInsertPilot",vector(70.5,3.5,14.5)*mm,vector(70.5,3.5,19.2)*mm,2.1*mm);
        cut(context,id + "camShoeInsertCut",body(id + "camShoe"),body(id + "camShoeInsertPilot"));
        // Nominal L4 insert entersZ19 and endsZ15. M3x10 underheadZ25
        // endsZ15: full4 mm thread and0.5 mm gap to pilot floorZ14.5.
        makeCylinder(context,id + "camScrew",vector(70.5,3.5,25)*mm,vector(70.5,3.5,28)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(70.5,3.5,15)*mm,vector(70.5,3.5,25.1)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        nameBody(context,body(id + "camScrew"),"H10 M3 x10 vertical cam-shoe clamp - manual setup");
        nameBody(context,body(id + "camShoe"),"P11 PRINT STUDY - guided switch cam, physical calibration trim only");
        finishBody(context,body(id + "camShoe"),color(0.88,0.53,0.20));
        const camShift=camTrim-preload;
        if (camShift != 0*mm)
            opTransform(context,id + "configuredManualCamShoe",{
                "bodies":qUnion([body(id + "camScrew"),body(id + "camShoe")]),
                "transform":transform(vector(camShift,0*mm,0*mm)) });
        movingBodies=append(movingBodies,body(id + "camScrew"));
        movingBodies=append(movingBodies,body(id + "camShoe"));

        // Single32 mm central profile under the existing20 mm pocket. The
        // base is6 mm with topZ4; rail topZ7 and female roofZ7.3 leave2.7 mm below the
        // pocket floor. Two14 mm bearing lands are45 mm apart longitudinally.
        makeXPrism(context,id + "centralTrack",29*mm,124*mm,
            [vector(-12.9,3.9)*mm,vector(12.9,3.9)*mm,
             vector(16,7)*mm,vector(-16,7)*mm]);
        baseBodies=append(baseBodies,body(id + "centralTrack" + "body"));
        makeXPrism(context,id + "centralChannel",64*mm,125*mm,
            [vector(-13.15,3.7)*mm,vector(13.15,3.7)*mm,
             vector(16.75,7.3)*mm,vector(-16.75,7.3)*mm]);
        cut(context,id + "centralGuideCut",body(id + "carriageBridge"),body(id + "centralChannel" + "body"));
        makeBox(context,id + "guideReliefTool",vector(79,-18,4)*mm,vector(110,18,7.3)*mm);
        cut(context,id + "guideBearingRelief",body(id + "carriageBridge"),body(id + "guideReliefTool"));

        // Floating spring yoke: thickened outside the sensor and behind its
        // upper half. The forward relief admits the cell; only the centered
        // pusher contacts the yoke. A notch clears the cable on the +Y side.
        makeBox(context,id + "springAnchor",vector(-7,-63,7)*mm,vector(9,63,29)*mm);
        opFillet(context,id + "yokeOuterRound",{
            "entities":qParallelEdges(qCreatedBy(id + "springAnchor",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        opFillet(context,id + "yokeTopRound",{
            "entities":qContainsPoint(qCreatedBy(id + "springAnchor",EntityType.EDGE),vector(-7,0,29)*mm),
            "radius":1*mm,"tangentPropagation":true });
        makeBox(context,id + "yokeRib",vector(8.8,-38,15.5)*mm,vector(15.5,38,29)*mm);
        join(context,id + "joinYoke",[body(id + "springAnchor"),body(id + "yokeRib")]);
        // Real TE body plus independent loose keeper. Rear opening admits the
        // 30 mm backing plate / corner spacers; the X1 shoulder datum remains.
        makeBox(context,id + "yokeSensorTool",vector(-10.5,-15.3,2.5)*mm,vector(1,15.3,33.5)*mm);
        makeBox(context,id + "yokeCableTool",vector(-10.5,10,12)*mm,vector(-1.4,40,24)*mm);
        cut(context,id + "yokeRelief",body(id + "springAnchor"),qUnion([body(id + "yokeSensorTool"),body(id + "yokeCableTool")]));
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const loY=side == -1 ? -21 : 15;
            makeBox(context,id + ("yokeGuideCapTool"~t),vector(-8.2,loY,3.3)*mm,
                vector(-6.0,loY+6,12.2)*mm);
            cut(context,id + ("yokeGuideCapClearance"~t),body(id + "springAnchor"),
                body(id + ("yokeGuideCapTool"~t)));
        }
        var keeperCorner=0;
        for (var keeperY in [-10.5,10.5])
        {
            for (var keeperZ in [7.5,28.5])
            {
                // Head ends X0.7, relieved to X1.4: 0.7 mm axial gap.
                makeCylinder(context,id + ("keeperHeadClearance"~keeperCorner),
                    vector(-1.5,keeperY,keeperZ)*mm,vector(1.4,keeperY,keeperZ)*mm,2.6*mm);
                cut(context,id + ("keeperHeadRelief"~keeperCorner),body(id + "springAnchor"),body(id + ("keeperHeadClearance"~keeperCorner)));
                keeperCorner+=1;
            }
        }
        nameBody(context,body(id + "springAnchor"),"P05 PRINT STUDY - Flat132 reinforced yoke with broad integral sensing stops");

        // One M6x1 screw translates the complete sensor support, cell, pusher
        // and yoke. Both seats therefore advance equally, without bypassing
        // the sensor. Hardware below is nominal/unthreaded CAD envelope only.
        // Print-only strengthened reaction portal. Hardware and force datum unchanged.
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
        // R12: no preload mechanism. H12 rear datum X-12 bears on this
        // broad fixed support. Lower pillar and45-degree shoulders print
        // upward from the base and clear all four rear keeper-screw tips.
        makeXPrism(context,id + "fixedSensorReaction",-16.2*mm,-12*mm,
            [vector(-9,3.8)*mm,vector(9,3.8)*mm,vector(9,9.5)*mm,
             vector(11,11.5)*mm,vector(11,26)*mm,vector(-11,26)*mm,
             vector(-11,11.5)*mm,vector(-9,9.5)*mm]);
        join(context,id + "fixedSensorReactionJoin",[body(id + "loadCellWall"),body(id + "fixedSensorReaction" + "body")]);
        baseBodies=append(baseBodies,body(id + "loadCellWall"));
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const lo=side == -1 ? -20.5 : 15.5;
            makeBox(context,id + ("cassetteGuide"~t),vector(-16.2,lo,3.8)*mm,vector(-8,lo+5,29)*mm);
            // Retain 2.3 mm at the closed slot end; this cap stays below the lead.
            makeBox(context,id + ("cassetteGuideEndCap"~t),vector(-8.1,lo,3.8)*mm,
                vector(-6.5,lo+5,11.7)*mm);
            join(context,id + ("cassetteGuideEndCapJoin"~t),
                [body(id + ("cassetteGuide"~t)),body(id + ("cassetteGuideEndCap"~t))]);
            if (side == 1)
            {
                // Keep the entire lower closed-ended retention slot. Only the
                // upper forward corner obstructs the genuine radial leadbase.
                makeBox(context,id + "cassetteGuideLeadNotch",vector(-10.35,15.3,12)*mm,vector(-7.4,20.7,24)*mm);
                cut(context,id + "cassetteGuideLeadExit",body(id + ("cassetteGuide"~t)),body(id + "cassetteGuideLeadNotch"));
            }
            baseBodies=append(baseBodies,body(id + ("cassetteGuide"~t)));
        }
        // Genuine rear support is planar at X-9.85; do not retain the old
        // FX1900-derived central relief. S355 steel, finish support flat.
        makeBox(context,id + "sensorCassette",vector(-12,-15,3)*mm,vector(-9.85,15,33)*mm);
        makeCylinder(context,id + "cellLocatingCollar",vector(-9.85,0,18)*mm,vector(-8.65,0,18)*mm,13.5*mm);
        makeCylinder(context,id + "cellLocatingBore",vector(-10,0,18)*mm,vector(-8.5,0,18)*mm,12.75*mm);
        cut(context,id + "cellLocatingRing",body(id + "cellLocatingCollar"),body(id + "cellLocatingBore"));
        makeBox(context,id + "cellLocatingLeadNotch",vector(-10,10,10.5)*mm,vector(-8.5,29,25.5)*mm);
        cut(context,id + "cellLocatingLeadExit",body(id + "cellLocatingCollar"),body(id + "cellLocatingLeadNotch"));
        join(context,id + "cellCollarJoin",[body(id + "sensorCassette"),body(id + "cellLocatingCollar")]);
        // Laser-cut 0.5 mm stainless keeper: no load may pass through it.
        // Rear face X-1.4 is 0.5 mm ahead of the housing front/rim X-1.9.
        makeCylinder(context,id + "cellFrontKeeper",vector(-1.4,0,18)*mm,vector(-0.9,0,18)*mm,13.5*mm);
        makeCylinder(context,id + "cellFrontKeeperBore",vector(-1.5,0,18)*mm,vector(-0.8,0,18)*mm,10*mm);
        cut(context,id + "cellFrontKeeperOpening",body(id + "cellFrontKeeper"),body(id + "cellFrontKeeperBore"));
        var cellRetainerIndex=0;
        for (var keeperY in [-10.5,10.5])
        {
            for (var keeperZ in [7.5,28.5])
            {
                const ci=cellRetainerIndex;
                // Spacer clearance scallops affect the locating collar only;
                // the planar rear support remains continuous except M2 taps.
                makeCylinder(context,id + ("cellCollarSpacerNotch"~ci),
                    vector(-9.85,keeperY,keeperZ)*mm,vector(-8.5,keeperY,keeperZ)*mm,2.2*mm);
                cut(context,id + ("cellCollarSpacerRelief"~ci),body(id + "sensorCassette"),body(id + ("cellCollarSpacerNotch"~ci)));
                makeBox(context,id + ("cellKeeperEar"~ci),
                    vector(-1.4,keeperY-4,keeperZ-4)*mm,vector(-0.9,keeperY+4,keeperZ+4)*mm);
                join(context,id + ("cellKeeperEarJoin"~ci),[body(id + "cellFrontKeeper"),body(id + ("cellKeeperEar"~ci))]);
                makeCylinder(context,id + ("cellKeeperHole"~ci),
                    vector(-1.5,keeperY,keeperZ)*mm,vector(-0.8,keeperY,keeperZ)*mm,1.1*mm);
                cut(context,id + ("cellKeeperHoleCut"~ci),body(id + "cellFrontKeeper"),body(id + ("cellKeeperHole"~ci)));
                makeCylinder(context,id + ("cellRetainerThread"~ci),
                    vector(-12.1,keeperY,keeperZ)*mm,vector(-9.75,keeperY,keeperZ)*mm,0.85*mm);
                cut(context,id + ("cellRetainerTap"~ci),body(id + "sensorCassette"),body(id + ("cellRetainerThread"~ci)));
                makeCylinder(context,id + ("cellRetainerSpacer"~ci),
                    vector(-9.85,keeperY,keeperZ)*mm,vector(-1.4,keeperY,keeperZ)*mm,2*mm);
                makeCylinder(context,id + ("cellRetainerSpacerBore"~ci),
                    vector(-9.95,keeperY,keeperZ)*mm,vector(-1.3,keeperY,keeperZ)*mm,1.1*mm);
                cut(context,id + ("cellRetainerSpacerClearance"~ci),body(id + ("cellRetainerSpacer"~ci)),body(id + ("cellRetainerSpacerBore"~ci)));
                makeCylinder(context,id + ("cellRetainerScrew"~ci),
                    vector(-12.9,keeperY,keeperZ)*mm,vector(-0.9,keeperY,keeperZ)*mm,1*mm);
                makeCylinder(context,id + ("cellRetainerScrewHead"~ci),
                    vector(-0.9,keeperY,keeperZ)*mm,vector(0.7,keeperY,keeperZ)*mm,2*mm);
                join(context,id + ("cellRetainerScrewJoin"~ci),[body(id + ("cellRetainerScrew"~ci)),body(id + ("cellRetainerScrewHead"~ci))]);
                nameBody(context,body(id + ("cellRetainerSpacer"~ci)),"H24"~ci~" Steel sensor keeper spacer OD4 ID2.2 x8.45");
                nameBody(context,body(id + ("cellRetainerScrew"~ci)),"H25"~ci~" M2 x12 panhead sensor keeper screw - head height max1.6");
                cellRetainerIndex+=1;
            }
        }
        // Re-open the full diameter after adding pads; diagonal pad corners
        // otherwise intrude slightly into a nominal 20 mm central opening.
        makeCylinder(context,id + "cellFrontKeeperFinalBore",vector(-1.5,0,18)*mm,vector(-0.8,0,18)*mm,10*mm);
        cut(context,id + "cellFrontKeeperFinalOpening",body(id + "cellFrontKeeper"),body(id + "cellFrontKeeperFinalBore"));
        nameBody(context,body(id + "cellFrontKeeper"),"H23 Stainless loose sensor keeper 0.5 mm - 0.5 mm housing gap");
        // Side ears retain the cassette even with both springs removed.
        // OD4/ID3.2 x6 spacers prevent screw tightening from clamping the guides.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const lowY=side == -1 ? -15 : 11.5;
            makeBox(context,id + ("cassetteEar"~t),vector(-15.5,lowY,4.5)*mm,vector(-9.85,lowY+3.5,11)*mm);
            join(context,id + ("cassetteEarJoin"~t),[body(id + "sensorCassette"),body(id + ("cassetteEar"~t))]);
            // Flat-bottom blind pilot dia2.5, TAP M3x0.5 to |Y|11.9; 2 mm engaged from |Y|13..15
            // plus 1.1 mm thread runout. Light cassette retention only.
            makeCylinder(context,id + ("cassetteThread"~t),vector(-12.8,side*11.9,8.5)*mm,vector(-12.8,side*15.2,8.5)*mm,1.25*mm);
            cut(context,id + ("cassettePinTap"~t),body(id + "sensorCassette"),body(id + ("cassetteThread"~t)));
            // Fixed cassette retention: no deliberate axial adjustment slot.
            // ExistingOD4 steel spacers have0.2mm nominal radial clearance.
            makeCylinder(context,id + ("captureFixedBore"~t),vector(-12.8,side*15.3,8.5)*mm,
                vector(-12.8,side*20.7,8.5)*mm,2.2*mm);
            cut(context,id + ("captureFixedDrill"~t),body(id + ("cassetteGuide"~t)),body(id + ("captureFixedBore"~t)));
            makeCylinder(context,id + ("captureSpacer"~t),vector(-12.8,side*15,8.5)*mm,vector(-12.8,side*21,8.5)*mm,2*mm);
            makeCylinder(context,id + ("captureSpacerBore"~t),vector(-12.8,side*14.9,8.5)*mm,vector(-12.8,side*21.1,8.5)*mm,1.6*mm);
            cut(context,id + ("captureSpacerCut"~t),body(id + ("captureSpacer"~t)),body(id + ("captureSpacerBore"~t)));
            makeCylinder(context,id + ("captureScrew"~t),vector(-12.8,side*13,8.5)*mm,vector(-12.8,side*21.1,8.5)*mm,1.5*mm);
            makeCylinder(context,id + ("captureHead"~t),vector(-12.8,side*21,8.5)*mm,vector(-12.8,side*24,8.5)*mm,2.75*mm);
            join(context,id + ("captureScrewJoin"~t),[body(id + ("captureScrew"~t)),body(id + ("captureHead"~t))]);
            nameBody(context,body(id + ("captureScrew"~t)),"H18"~t~" M3 x 8 cassette retention screw");
            nameBody(context,body(id + ("captureSpacer"~t)),"H19"~t~" Steel spacer 4 x 3.2 x 6 - fixed cassette retention");
        }
        nameBody(context,body(id + "sensorCassette"),"H12 S355 steel planar sensor backing plate 30 x30 x2.15 with locating collar");
        // H01 is the genuine STEP solid selected above, with its original shape.
        // The full flexible lead/connector is a routing requirement, not invented CAD.
        makeCylinder(context,id + "loadPusher",vector(-1.9,0,18)*mm,vector(0.1,0,18)*mm,2*mm);
        makeCylinder(context,id + "pusherShoulder",vector(0,0,18)*mm,vector(1,0,18)*mm,4*mm);
        makeCylinder(context,id + "pusherTail",vector(0.9,0,18)*mm,vector(7.5,0,18)*mm,1.5*mm);
        join(context,id + "pusherJoin",[body(id + "loadPusher"),body(id + "pusherShoulder"),body(id + "pusherTail")]);
        makeCylinder(context,id + "pusherTailBore",vector(0.8,0,18)*mm,vector(8,0,18)*mm,1.6*mm);
        cut(context,id + "pusherTailClearance",body(id + "springAnchor"),body(id + "pusherTailBore"));
        makeBox(context,id + "pusherNutTrap",vector(5,-2.85,15.15)*mm,vector(7,2.85,30)*mm);
        cut(context,id + "pusherNutSlot",body(id + "springAnchor"),body(id + "pusherNutTrap"));
        makeBox(context,id + "pusherNut",vector(5.1,-2.75,15.25)*mm,vector(6.9,2.75,20.75)*mm);
        makeCylinder(context,id + "pusherNutHole",vector(5,0,18)*mm,vector(7,0,18)*mm,1.55*mm);
        cut(context,id + "pusherNutThread",body(id + "pusherNut"),body(id + "pusherNutHole"));
        nameBody(context,body(id + "pusherNut"),"H20 M3 square nut - retains shouldered force pusher");
        nameBody(context,body(id + "loadPusher"),"H02 Retained steel pusher: dia4 tip x1.9, dia8 shoulder x1, M3 tail x6.5");

        // R12 fixed rest compression: DF2194 6 mm; DF2185 9 mm; user travel30 mm.
        // Isometric sleeves REPLACE springs and react through the same sensor.
        // Helical sweeps illustrate coils; axial ends are trimmed to the seats.
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const y = side*51;
            const endX = 113*mm-stroke;
            if (definition.isometricLock)
            {
                makeCylinder(context,id + ("isoSleeve"~s),vector(12*mm+preload,y*mm,18*mm),
                    vector(endX,y*mm,18*mm),8*mm);
                makeCylinder(context,id + ("isoBore"~s),vector(11*mm+preload,y*mm,18*mm),
                    vector(endX+mm,y*mm,18*mm),4*mm);
                cut(context,id + ("isoTube"~s),body(id + ("isoSleeve"~s)),body(id + ("isoBore"~s)));
                nameBody(context,body(id + ("isoSleeve"~s)),"H14"~s~" ISOMETRIC steel compression lock sleeve 16 x 8 x 81 mm");
            }
            else
            {
                makeCompressionSpring(context,id + ("spring"~s),12*mm+preload,endX,y*mm,springZ,definition.lightSprings);
                makeBox(context,id + ("springTrimFront"~s),vector(8*mm+preload,(y-10)*mm,7*mm),vector(12*mm+preload,(y+10)*mm,29*mm));
                makeBox(context,id + ("springTrimRear"~s),vector(endX,(y-10)*mm,7*mm),vector(endX+4*mm,(y+10)*mm,29*mm));
                cut(context,id + ("trimSpring"~s),body(id + ("spring"~s) + "sweep"),
                    qUnion([body(id + ("springTrimFront"~s)),body(id + ("springTrimRear"~s))]));
                nameBody(context,body(id + ("spring"~s) + "sweep"),definition.lightSprings ?
                    "H03"~s~" Febrotec 0X-DF2194 14.8/10.8 x 102 mm, 3.307 N/mm - indicative coil" :
                    "H03"~s~" Febrotec 0X-DF2185 14.5/10.5 x 105 mm, 3.709 N/mm - indicative coil");
            }
            makeCylinder(context,id + ("rod"~s),vector(-16,y,18)*mm,vector(125,y,18)*mm,3*mm);
            nameBody(context,body(id + ("rod"~s)),"H04"~s~" Steel guide rod dia 6 x 141 mm");
            makeCylinder(context,id + ("fixedSeat"~s),vector(9,y,18)*mm,vector(12,y,18)*mm,11*mm);
            makeCylinder(context,id + ("movingSeat"~s),vector(113,y,18)*mm,vector(116,y,18)*mm,11*mm);
            makeCylinder(context,id + ("guideBore"~s),vector(-8,y,18)*mm,vector(125,y,18)*mm,3.3*mm);
            cut(context,id + ("clearRod"~s),qUnion([body(id + "springAnchor"),
                body(id + ("fixedSeat"~s))]),body(id + ("guideBore"~s)));
            // Large clearances prevent the spring mandrels becoming a second
            // parallel carriage guide. Moving seats use8 mm bores as well.
            makeCylinder(context,id + ("movingRodBore"~s),vector(112,y,18)*mm,vector(125,y,18)*mm,4*mm);
            cut(context,id + ("clearMovingRod"~s),qUnion([body(id + "carriageBridge"),
                body(id + ("movingSeat"~s))]),body(id + ("movingRodBore"~s)));
            movingBodies=append(movingBodies,body(id + ("movingSeat"~s)));
            nameBody(context,body(id + ("fixedSeat"~s)),"H05"~s~" Fixed steel spring seat 22 x 6.6 x 3 mm");
            nameBody(context,body(id + ("movingSeat"~s)),"H06"~s~" Moving steel spring seat 22 x 8 x 3 mm");
            makeBox(context,id + ("frontRodBlock"~s),vector(-18,y-12,3.8)*mm,vector(-8,y+12,28)*mm);
            makeCylinder(context,id + ("frontSocket"~s),vector(-17,y,18)*mm,vector(-7,y,18)*mm,3.1*mm);
            cut(context,id + ("frontBore"~s),body(id + ("frontRodBlock"~s)),body(id + ("frontSocket"~s)));
            baseBodies=append(baseBodies,body(id + ("frontRodBlock"~s)));
            // R12 fixed rear datum: one large gate replaces both caps/shoes.
            // Gate is installed axially over rods after inserting the carriage.
            makeBox(context,id + ("rearFoot"~s),vector(119.5,y-14,3.8)*mm,vector(129,y+14,4.5)*mm);
            baseBodies=append(baseBodies,body(id + ("rearFoot"~s)));
            makeBox(context,id + ("rearBlock"~s),vector(119,y-14,4.5)*mm,vector(129,y+14,28)*mm);
            makeCylinder(context,id + ("rearSocket"~s),vector(118.8,y,18)*mm,vector(126.2,y,18)*mm,3.1*mm);
            makeXPrism(context,id + ("rearSocketRoof"~s),118.8*mm,126.2*mm,
                [vector(y-2.192031022,20.192031022)*mm,vector(y+2.192031022,20.192031022)*mm,
                 vector(y,22.384062044)*mm]);
            cut(context,id + ("rearBore"~s),body(id + ("rearBlock"~s)),
                qUnion([body(id + ("rearSocket"~s)),body(id + ("rearSocketRoof"~s) + "body")]));
            for (var offset in [-9.5,9.5])
            {
                const t=offset < 0 ? "a" : "b";
                makeCylinder(context,id + ("rearHole"~s~t),vector(124.5,y+offset,4)*mm,vector(124.5,y+offset,29)*mm,1.7*mm);
                makeCylinder(context,id + ("rearHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,29)*mm,3.2*mm);
                cut(context,id + ("rearMount"~s~t),body(id + ("rearBlock"~s)),qUnion([
                    body(id + ("rearHole"~s~t)),body(id + ("rearHead"~s~t))]));
                makeCylinder(context,id + ("rearInsert"~s~t),vector(124.5,y+offset,0.5)*mm,vector(124.5,y+offset,4.6)*mm,2.1*mm);
                insertTools=append(insertTools,body(id + ("rearInsert"~s~t)));
                makeCylinder(context,id + ("rearMountScrew"~s~t),vector(124.5,y+offset,2)*mm,vector(124.5,y+offset,10.1)*mm,1.5*mm);
                makeCylinder(context,id + ("rearMountHead"~s~t),vector(124.5,y+offset,10)*mm,vector(124.5,y+offset,13)*mm,2.75*mm);
                join(context,id + ("rearMountScrewJoin"~s~t),[body(id + ("rearMountScrew"~s~t)),body(id + ("rearMountHead"~s~t))]);
                nameBody(context,body(id + ("rearMountScrew"~s~t)),"H30"~s~t~" M3x8 rear gate screw - optional fitting/functional securing");
            }

        }


        // One transverse bridge starts after rail end X124:1 mm clearance.
        makeBox(context,id + "rearGateBridge",vector(125,-51,4.5)*mm,vector(129,51,10)*mm);
        // The bridge overlaps the two inner M3 bores. Clear it BEFORE union
        // so both securing screws retain their complete through passages.
        for (var side in [-1,1])
        {
            const s=side < 0 ? "0" : "1";
            makeCylinder(context,id + ("rearBridgeBoltRelief"~s),vector(124.5,side*41.5,4)*mm,
                vector(124.5,side*41.5,10.1)*mm,1.7*mm);
            cut(context,id + ("rearBridgeBoltClearance"~s),body(id + "rearGateBridge"),body(id + ("rearBridgeBoltRelief"~s)));
        }
        join(context,id + "rearGateJoin",[body(id + "rearBlock0"),body(id + "rearBlock1"),body(id + "rearGateBridge")]);
        for (var side in [-1,1])
        {
            const s=side < 0 ? "0" : "1";
            const loY=side < 0 ? -67.6 : 64.8;
            const hiY=side < 0 ? -64.8 : 67.6;
            const beamLo=side < 0 ? -67.6 : 66.4;
            const beamHi=side < 0 ? -66.4 : 67.6;
            makeBox(context,id + ("rearLatchRoot"~s),vector(126.6,loY,4.5)*mm,vector(129,hiY,8)*mm);
            makeBox(context,id + ("rearLatchPost"~s),vector(126.6,beamLo,4.5)*mm,vector(129,beamHi,8)*mm);
            makeBox(context,id + ("rearLatchBeam"~s),vector(104.8,beamLo,4.5)*mm,vector(127,beamHi,7.5)*mm);
            const blendLo=side < 0 ? -66.4 : 65.8;
            const blendHi=side < 0 ? -65.8 : 66.4;
            makeBox(context,id + ("rearLatchBlend"~s),vector(126,blendLo,4.5)*mm,vector(126.6,blendHi,7.5)*mm);
            makeCylinder(context,id + ("rearLatchBlendTool"~s),vector(126,side*65.8,4.4)*mm,vector(126,side*65.8,7.6)*mm,0.6*mm);
            cut(context,id + ("rearLatchBlendRound"~s),body(id + ("rearLatchBlend"~s)),body(id + ("rearLatchBlendTool"~s)));
            // Z extrusion via a planar polygon to make the axial insertion ramp.
            makeZPrismR12(context,id + ("rearLatchHook"~s),4.5*mm,7.5*mm,
                [vector(104.8,side*66.4)*mm,vector(105.6,side*65.6)*mm,
                 vector(108,side*65.6)*mm,vector(108,side*66.6)*mm,vector(104.8,side*66.6)*mm]);
            join(context,id + ("rearLatchJoin"~s),[body(id + "rearBlock0"),body(id + ("rearLatchRoot"~s)),
                body(id + ("rearLatchPost"~s)),body(id + ("rearLatchBeam"~s)),body(id + ("rearLatchBlend"~s)),body(id + ("rearLatchHook"~s) + "body")]);
            const notchLo=side < 0 ? -66.2 : 64.2;
            const notchHi=side < 0 ? -64.2 : 66.2;
            makeBox(context,id + ("rearLatchCatch"~s),vector(108.2,notchLo,3)*mm,vector(110.5,notchHi,7.8)*mm);
            baseBodies=append(baseBodies,body(id + ("rearLatchCatch"~s)));
        }
        nameBody(context,body(id + "rearBlock0"),"P06 PRINT - one-piece fixed rear gate with PLA assembly latches");

        // Broad integral PRINTED sensing stops replace both M4 screws/nuts.
        // End force returns P04 -> these P05 arms -> pusher -> actual sensor;
        // no fixed P01 full-travel stop bypasses the cell.
        // Fixed stop faceX30 meets P04front65-q at q=35.
        // With q=5+u the retained user travel is u<=30 mm.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const y=side*24;
            // Axial-compression root section10 x22, centredonforceheightZ18.
            makeBox(context,id + ("sensingStopArm"~t),vector(8.5,y-5,7)*mm,
                vector(25,y+5,29)*mm);
            // Broad14 x22 flat bearing faces, no small M4 tip stress raiser.
            // R2 flare X24.7 is retained; the shifted R4 case overlaps in X
            // and clears the negative stop by1 mm in Y (case-16, stop-17).
            makeBox(context,id + ("sensingStopFace"~t),vector(24.7,y-7,7)*mm,
                vector(30,y+7,29)*mm);
            join(context,id + ("sensingStopJoin"~t),[body(id + "springAnchor"),
                body(id + ("sensingStopArm"~t)),body(id + ("sensingStopFace"~t))]);
        }

        // SS-01GL2 manufacturer DRAWING reference: no factory STEP claim.
        // Omron B032-E1 pages4/6: major body19.8 x10.2 x6.4, two9.5-spaced
        // mounts, three solder tabs and0.4 mm lower-lug projection.
        // Exact terminal holes/corners and lug width/profile are unspecified;
        // use solid tab boxes and a conservative full-housing-width lug strip.
        // The strip assumes the lug stays within the stated6.4 mm thickness.
        // Shift +4 X / +1 Y / +1.5 Z clears the intact P05 force web.
        // Extend the pedestal upward from the base; do not lift its bottom.
        // Trim Ymin to-16.5 for0.5 mm stop gap and0.5 mm body support margin.
        makeBox(context,id + "switchPedestal",vector(17,-16.5,3.8)*mm,vector(29,5,7.5)*mm);
        baseBodies=append(baseBodies,body(id + "switchPedestal"));
        makeBox(context,id + "switchBody",vector(18,-16,7.5)*mm,vector(28.2,3.8,13.9)*mm);
        var switchReferenceBodies=[body(id + "switchBody")];
        var terminalIndex=0;
        for (var terminalY in [-14.4,-5.6,1.7])
        {
            makeBox(context,id + ("switchTerminalEnvelope"~terminalIndex),
                vector(14.1,terminalY-0.25,9.1)*mm,vector(18,terminalY+0.25,12.3)*mm);
            switchReferenceBodies=append(switchReferenceBodies,
                body(id + ("switchTerminalEnvelope"~terminalIndex)));
            terminalIndex+=1;
        }
        makeBox(context,id + "switchLugEnvelope",vector(17.6,-16,7.5)*mm,vector(18,3.8,13.9)*mm);
        switchReferenceBodies=append(switchReferenceBodies,body(id + "switchLugEnvelope"));
        join(context,id + "joinSwitchDrawingReference",switchReferenceBodies);
        for (var y in [-10.9,-1.4])
        {
            const s=y == -10.9 ? "0" : "1";
            makeCylinder(context,id + ("switchMountHole"~s),vector(20.5,y,6.5)*mm,vector(20.5,y,14.5)*mm,1.175*mm);
            cut(context,id + ("switchDrill"~s),body(id + "switchBody"),body(id + ("switchMountHole"~s)));
            // Four-mm blind pilot fromZ7.5; nominal L3 M2 insert endsZ4.5.
            // M2x10/washer engagement is unchanged; match actual insert stock.
            makeCylinder(context,id + ("switchInsert"~s),vector(20.5,y,3.5)*mm,vector(20.5,y,7.7)*mm,1.6*mm);
            insertTools=append(insertTools,body(id + ("switchInsert"~s)));
        }
        // Illustrative fixed-length motion, not the real formed0.3 mm lever.
        // Manufacturer OP14.5 +/-0.8 is measured from mount lineX20.5.
        // Shoe faceX69+camTrim-preload-q reachesX34+camTrim at the stop:
        // one-mm nominal trip lead only; calibrate and check actual overtravel.
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(37.4*mm,69*mm+camTrim-stroke-preload-2.4*mm);
        const rollerY=-13.1*mm+sqrt(leverLength*leverLength-(rollerX-29.5*mm)*(rollerX-29.5*mm));
        makeCylinder(context,id + "switchLever",vector(29.5,-13.1,10.7)*mm,
            vector(rollerX,rollerY,10.7*mm),0.45*mm);
        makeCylinder(context,id + "switchRoller",vector(rollerX,rollerY,9.1*mm),
            vector(rollerX,rollerY,12.3*mm),2.4*mm);
        nameBody(context,body(id + "switchBody"),"H09 Omron SS-01GL2 DRAWING REF - solder tabs and conservative lug envelope");
        nameBody(context,body(id + "switchLever"),"H09a SS-01GL2 approximate lever motion - drawing reference");
        nameBody(context,body(id + "switchRoller"),"H09b SS-01GL2 nominal roller - approximate motion");

        // 13.10.2026: cord eyes removed to restore rear carriage assembly access.

        join(context,id + "integrateBase",baseBodies);
        cut(context,id + "baseInserts",body(id + "base"),qUnion(insertTools));
        var mountingTools=[];
        n=0;
        for (var x in [16,122])
        {
            for (var y in [-28,28])
            {
                makeCylinder(context,id + ("benchHole"~n),vector(x,y,-3)*mm,vector(x,y,5)*mm,2.75*mm);
                mountingTools=append(mountingTools,body(id + ("benchHole"~n)));
                // Flush M5 90-degree heads (maximum diameter 10 mm): rear
                // mounting heads must remain below the moving carriage Z5.
                fCone(context,id + ("benchCountersink"~n),{
                    "bottomCenter":vector(x,y,1.65)*mm,
                    "topCenter":vector(x,y,4.1)*mm,
                    "bottomRadius":2.75*mm,"topRadius":5.2*mm });
                mountingTools=append(mountingTools,body(id + ("benchCountersink"~n)));
                n+=1;
            }
        }
        cut(context,id + "benchMounts",body(id + "base"),qUnion(mountingTools));
        // Lower edges of backing and keeper sweep through this shallow pocket.
        // Z2.7 floor retains 4.7 mm solid frame thickness above Z-2.
        makeBox(context,id + "realSensorFloorPocket",vector(-12.3,-15.3,2.7)*mm,vector(2.9,15.3,4.2)*mm);
        cut(context,id + "realSensorFloorRelief",body(id + "base"),body(id + "realSensorFloorPocket"));
        // R10 service-access fix: at PRELOAD0 the H18 M3 cassette
        // retainers and H19 spacers need a clear lateral removal/tool route.
        // Trimmed palm feet/ears/drops end atX-17,1 mm clear of these bores.
        // Cut ONLY the outer front rod blocks, leaving the cassette guides,
        // floor and high rod sockets intact. AtZ11.7 bore top, the original
        // rod-socket bottomZ14.9 retains3.2 mm nominal intervening material.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const fromY=side == -1 ? -66.5 : 38.8;
            const toY=side == -1 ? -38.8 : 66.5;
            makeCylinder(context,id + ("captureServiceBore"~t),
                vector(-12.8,fromY,8.5)*mm,vector(-12.8,toY,8.5)*mm,3.2*mm);
            cut(context,id + ("captureServiceBoreCut"~t),body(id + "base"),
                body(id + ("captureServiceBore"~t)));
        }
        nameBody(context,body(id + "base"),"P01 PRINT STUDY - Flat132 fixed rear gate frame, 5 mm cassette guides, 6 mm nominal floor");

        println({"mode":definition.isometricLock ? "ISOMETRIC compression lock" : "DYNAMIC",
            "additionalPreload":preload,"actualStroke":stroke,
            "userTravelFromCloserRest":userTravel,"restOffset":restOffset,"rearAdvance":rearAdvance,"camTrim":camTrim,
            "springArticle":definition.lightSprings ? "0X-DF2194" : "0X-DF2185",
            "springRateEachNPerMm":definition.lightSprings ? 3.307 : 3.709,
            "springFreeLengthMm":definition.lightSprings ? 102 : 105,
            "springInstalledLength":101*mm-preload-stroke,
            "nominalPairForceN":definition.isometricLock ? 0 :
                2*(definition.lightSprings ? 3.307 : 3.709)*((definition.lightSprings ? 102 : 105)-(101*mm-preload-stroke)/mm)});
        if (stroke > 0*mm)
            opTransform(context,id + "previewMotion",{
                "bodies":qUnion(movingBodies),
                "transform":transform(vector(-stroke,0*mm,0*mm)) });
        // Neutral green frame and one-piece rigid palm; warm tan climbing surface.
        finishBody(context,body(id + "base"),color(0.27,0.30,0.28));
        finishBody(context,body(id + "palmPad"),color(0.27,0.32,0.28));
        finishBody(context,body(id + "carriageBridge"),color(0.66,0.46,0.27));
        finishBody(context,body(id + "springAnchor"),color(0.35,0.39,0.35));
        finishBody(context,qUnion([body(id + "rearBlock0"),body(id + "rearBlock1")]),color(0.27,0.30,0.28));
        if (!definition.isometricLock)
            finishBody(context,qUnion([body(id + "spring0" + "sweep"),body(id + "spring1" + "sweep")]),
                definition.lightSprings ? color(0.2,0.55,0.85) : color(0.14,0.40,0.27));

        if (definition.showHand)
        {
            makeHandReference(context,id + "handReference",stroke);
            opTransform(context,id + "lowerHand",{
                "bodies":body(id + "handReference"),
                "transform":transform(vector(0,0,-29.5)*mm) });
        }
        for (var check in auditFingerworkerCollisions(context,id,definition.actualSensor))
            println({ "pose":stroke,"pair":check.pair,"status":check.status,
                "gap":check.minimumSeparation,"interferences":check.interferenceCount,
                "contacts":check.exteriorContactCount,"unclassified":check.unclassifiedCount });
        if (definition.showElectronics)
        {
            for (var check in makeElectronicsStudy(context,id,definition.actualSensor))
                println({ "pose":stroke,"pair":check.pair,"status":check.status,
                    "gap":check.minimumSeparation,"interferences":check.interferenceCount,
                    "contacts":check.exteriorContactCount,"unclassified":check.unclassifiedCount });
        }

        // R10 final operation: all audits and electronics creation above use
        // distinct construction regions. After this union qCreatedBy(palmPad)
        // can trace the whole frame, so do not run region audits below it.
        const frameAndPalm=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);
        if (size(evaluateQuery(context,frameAndPalm)) != 2)
            throw regenError("R10 requires the two complete frame/palm construction regions before final fusion.");
        join(context,id + "integratePalmIntoFrame",[body(id + "base"),body(id + "palmPad")]);
        // R13: one constant-radius palm rail and one broad continuous web.
        // R12 underside, electronics catches and functional sensor portal stay.
        makeCylinder(context,id + "R13PalmUniformRail",vector(-27,-58,19.75)*mm,
            vector(-27,58,19.75)*mm,10.25*mm);
        opFillet(context,id + "R13PalmEndRound",{
            "entities":qCreatedBy(id + "R13PalmUniformRail",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeBox(context,id + "R13PalmForwardHalfTool",vector(-27,-60,0)*mm,
            vector(0,60,40)*mm);
        cut(context,id + "R13PalmHalfCut",body(id + "R13PalmUniformRail"),
            body(id + "R13PalmForwardHalfTool"));
        makeBox(context,id + "R13PalmContinuousWeb",vector(-27,-58,9.5)*mm,
            vector(-17.1,58,30)*mm);
        opFillet(context,id + "R13PalmWebCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "R13PalmContinuousWeb",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        //45-degree underside spans the old plate/rod-block gap without a
        // flat ceiling. Cut only new web stock; original P01 stays intact.
        makeYPrism(context,id + "R13PalmUndersideTool",-58.1*mm,58.1*mm,
            [vector(-23.25,9.4)*mm,vector(-18,9.4)*mm,vector(-18,9.5)*mm,
             vector(-20.625,12.125)*mm,vector(-23.25,9.5)*mm]);
        cut(context,id + "R13PalmUndersideCut",body(id + "R13PalmContinuousWeb"),
            body(id + "R13PalmUndersideTool" + "body"));
        join(context,id + "R13PalmContinuousJoin",[body(id + "base"),
            body(id + "R13PalmUniformRail"),body(id + "R13PalmContinuousWeb")]);
        // New web reaches the inner edges of the existing optional M2 pilots.
        // Recut them after union so both original mounting routes remain open.
        for (var y in [-59,59])
        {
            const s=y < 0 ? "0" : "1";
            makeCylinder(context,id + ("R13PalmPilot"~s),
                vector(-26.5,y,9.4)*mm,vector(-26.5,y,13.5)*mm,1.6*mm);
            cut(context,id + ("R13PalmPilotCut"~s),body(id + "base"),
                body(id + ("R13PalmPilot"~s)));
        }
        const integratedFrame=qBodyType(qUnion([body(id + "base"),body(id + "palmPad")]),BodyType.SOLID);
        if (size(evaluateQuery(context,integratedFrame)) != 1)
            throw regenError("R10 frame and palm must regenerate as exactly ONE continuous solid.");
        nameBody(context,integratedFrame,
            "P01 PRINT STUDY - Flat132 continuous palm rail and web, fixed sensor support");
        finishBody(context,integratedFrame,color(0.27,0.30,0.28));
        println({"R10IntegralFramePalmSolidCount":size(evaluateQuery(context,integratedFrame)),
            "palmFasteners":0,"palmSleeve":false,"palmRemovable":false});

    }, { "previewTravel":0*millimeter,"camTrim":0*millimeter,
        "lightSprings":true,"isometricLock":false,"showHand":false,"showElectronics":false });
