FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker MVP - reviewed development prototype; load rating unverified.
 *
 * X = pull direction, Y = finger-bar width, Z = height above the base.
 * Purchased hardware is modeled at nominal catalogue size. Printed parts are
 * separated bodies so they can be exported and printed individually.
 * SEPARATE BRANCH STUDY 2026-10-19: flat 132 mm frame, 72 mm clear pocket,
 * 84 mm deck, 102 mm spring-axis spacing, 6 mm base, 32 mm total height.
 * P01/P02 are one integral printed frame and palm support; the existing palm
 * contact geometry, 86 mm sleeve and electronics enclosure are retained.
 * Derived from protected Rev D; this study does not supersede production files.
 * Native regeneration, motion/assembly checks and physical strength validation
 * are required. No tested load capacity or functional equivalence is claimed.
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
    const sleeve = body(id + "palmCushion");
    const yoke = body(id + "springAnchor");
    const rods = qUnion([body(id + "rod0"), body(id + "rod1")]);
    const seats = qUnion([body(id + "fixedSeat0"), body(id + "fixedSeat1"),
                         body(id + "movingSeat0"), body(id + "movingSeat1")]);
    const springs = qUnion([body(id + "spring0" + "sweep"), body(id + "spring1" + "sweep"),
        body(id + "isoSleeve0"), body(id + "isoSleeve1")]);
    const actuator = qUnion([body(id + "switchLever"), body(id + "switchRoller")]);
    const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1")]);
    const pads = qUnion([body(id + "returnPad0a"),body(id + "returnPad0b"),
                        body(id + "returnPad1a"),body(id + "returnPad1b")]);
    const stops = qUnion([body(id + "stopScrew0"), body(id + "stopScrew1")]);
    const sensor = qUnion([body(id + "loadCell"),body(id + "loadCellBoss"),
        body(id + "loadCellOvermold"),body(id + "loadCellCable"),body(id + "loadCellConnector")]);
    const keeperHardware=qUnion([body(id + "keeperScrew0"),body(id + "keeperScrew1"),body(id + "keeperNut0"),body(id + "keeperNut1"),body(id + "preloadLockScrew"),body(id + "preloadLockPad")]);
    const captureHardware=qUnion([body(id + "captureScrew0"),body(id + "captureScrew1"),body(id + "captureSpacer0"),body(id + "captureSpacer1")]);
    const device = qBodyType(body(id), BodyType.SOLID);
    return [
        auditSolidPair(context,"Keeper hardware / fixed wall and keeper",keeperHardware,qUnion([base,body(id + "nutKeeper")]),true),
        auditSolidPair(context,"Keeper hardware / moving stack and sleeve",keeperHardware,qUnion([body(id + "sensorCassette"),yoke,sleeve]),false),
        auditSolidPair(context,"Cassette retainers / guides",captureHardware,base,true),
        auditSolidPair(context,"Cassette retainers / cassette",captureHardware,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette retainers / mechanism",captureHardware,qUnion([sleeve,yoke,carriage,rods,sensor,body(id + "preloadScrew"),keeperHardware]),false),
        auditSolidPair(context,"Preload lock / adjusting screw",qUnion([body(id + "preloadLockScrew"),body(id + "preloadLockPad")]),body(id + "preloadScrew"),true),
        auditSolidPair(context,"Pusher / sensor and yoke",qUnion([body(id + "loadPusher"),body(id + "pusherNut")]),qUnion([sensor,yoke]),true),
        auditSolidPair(context,"Springs or lock sleeves / seats",springs,seats,true),
        auditSolidPair(context,"Adjustment hardware / base",qUnion([body(id + "preloadScrew"),
            body(id + "preloadNut"),body(id + "nutKeeper")]),base,true),
        auditSolidPair(context,"Adjustment hardware / yoke carriage sleeve",qUnion([body(id + "preloadScrew"),
            body(id + "preloadNut"),body(id + "nutKeeper"),body(id + "sensorCassette")]),qUnion([yoke,carriage,sleeve]),false),
        auditSolidPair(context,"Sensor / translating cassette",sensor,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette / fixed guide",body(id + "sensorCassette"),base,false),
        auditSolidPair(context,"Cassette / yoke",body(id + "sensorCassette"),yoke,false),
        auditSolidPair(context,"Preload screw / cassette",body(id + "preloadScrew"),body(id + "sensorCassette"),true),
        auditSolidPair(context,"Carriage / open frame and central guide",carriage,base,false),
        auditSolidPair(context,"Carriage / spring mandrels",carriage,rods,false),
        auditSolidPair(context,"Carriage / springs",carriage,springs,false),
        auditSolidPair(context,"Carriage / rear retainers",carriage,rear,false),
        auditSolidPair(context,"Carriage / return pads",carriage,pads,true),
        auditSolidPair(context,"Carriage / full-travel screws",carriage,stops,true),
        auditSolidPair(context,"Carriage / switch case",carriage,body(id + "switchBody"),false),
        auditSolidPair(context,"Carriage / switch actuator",carriage,actuator,true),
        auditSolidPair(context,"Adjustable cam / switch actuator",body(id + "camScrew"),actuator,true),
        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),
        auditSolidPair(context,"Springs / surrounding structure",springs,qUnion([base,yoke,carriage,rear,rods,sleeve]),false),
        auditSolidPair(context,"Spring seats / structure",seats,qUnion([base,yoke,carriage,rear,rods,sleeve]),true),
        auditSolidPair(context,"Yoke / integral frame rods and sleeve",yoke,qUnion([base,rods,sleeve]),false),
        auditSolidPair(context,"Yoke / sensor",yoke,sensor,false),
        auditSolidPair(context,"Sensor / base",sensor,base,true),
        // Palm support is integral with base: no self-pair or missing P02 query.
        auditSolidPair(context,"Palm sleeve / carriage and switch",sleeve,qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Switch case and actuator / integral frame",qUnion([body(id + "switchBody"),actuator]),base,true),
        auditSolidPair(context,"Palm sleeve / integral rigid support",sleeve,base,true),
        auditSolidPair(context,"Hand / climbing carriage",hand,carriage,true),
        auditSolidPair(context,"Hand / palm sleeve",hand,sleeve,true),
        auditSolidPair(context,"Hand / remaining device",hand,qSubtraction(device,qUnion([hand,carriage,sleeve])),false)
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
    makeCylinder(context,id + "P08_Electronics_tray_21",vector(-26.5,24,1.2)*mm,vector(-26.5,24,3.5)*mm,0.625*mm);
    cut(context,id + "P08_Electronics_tray_21Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_21"));
    makeCylinder(context,id + "P08_Electronics_tray_22",vector(-26.5,31,0.9)*mm,vector(-26.5,31,3.4)*mm,1.6*mm);
    join(context,id + "P08_Electronics_tray_22Join",[body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_22")]);
    makeCylinder(context,id + "P08_Electronics_tray_23",vector(-26.5,31,1.2)*mm,vector(-26.5,31,3.5)*mm,0.625*mm);
    cut(context,id + "P08_Electronics_tray_23Cut",body(id + "P08_Electronics_tray"),body(id + "P08_Electronics_tray_23"));
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
    nameBody(context,body(id + "P08_Electronics_tray"),"P08 PRINT - Electronics tray");
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
    nameBody(context,body(id + "P09_Electronics_lid"),"P09 PRINT - Electronics lid");
    finishBody(context,body(id + "P09_Electronics_lid"),color(0.15,0.65,0.78));
    makeBox(context,id + "P10_Wire_clamp",vector(-28.1,22.4,3.4)*mm,vector(-24.9,32.6,4.4)*mm);
    makeCylinder(context,id + "P10_Wire_clamp_1",vector(-26.5,24,3.3)*mm,vector(-26.5,24,4.5)*mm,0.9*mm);
    cut(context,id + "P10_Wire_clamp_1Cut",body(id + "P10_Wire_clamp"),body(id + "P10_Wire_clamp_1"));
    makeCylinder(context,id + "P10_Wire_clamp_2",vector(-26.5,31,3.3)*mm,vector(-26.5,31,4.5)*mm,0.9*mm);
    cut(context,id + "P10_Wire_clamp_2Cut",body(id + "P10_Wire_clamp"),body(id + "P10_Wire_clamp_2"));
    nameBody(context,body(id + "P10_Wire_clamp"),"P10 PRINT - Wire clamp");
    finishBody(context,body(id + "P10_Wire_clamp"),color(0.15,0.65,0.78));
    return qUnion([body(id + "P08_Electronics_tray"),body(id + "P09_Electronics_lid"),body(id + "P10_Wire_clamp")]);
}
// END GENERATED ENCLOSURE REV A

// Printable Rev A enclosure plus nominal PCB/cell/plug envelopes.
// Physical fitting, thermal and RF qualification remain hardware checks.
function makeElectronicsStudy(context is Context, id is Id) returns array
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
    const mechanism=qSubtraction(qBodyType(body(id),BodyType.SOLID),qUnion([electronics,hand]));
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

annotation { "Feature Type Name" : "FingerworkerFlat132Study", "Feature Name Template" : "Flat132 study 30 mm" }
export const fingerworkerMVP = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Preview displacement (0 to 30 mm)" }
        isLength(definition.previewTravel, LENGTH_BOUNDS);
        annotation { "Name" : "Additional synchronized preload (0 to 2 mm)" }
        isLength(definition.preloadAdjustment, LENGTH_BOUNDS);
        annotation { "Name" : "Febrotec pair: ON = 0X-DF2194 (lighter), OFF = 0X-DF2185" }
        definition.lightSprings is boolean;
        annotation { "Name" : "Isometric mode: replace BOTH springs with 86 mm steel sleeves" }
        definition.isometricLock is boolean;
        annotation { "Name" : "Show hand reference (exclude from manufacturing)" }
        definition.showHand is boolean;
        annotation { "Name" : "Show electronics enclosure and component references" }
        definition.showElectronics is boolean;
    }
    {
        const mm = millimeter;
        const preload = definition.preloadAdjustment;
        if (preload < 0 * mm || preload > 2 * mm)
            throw regenError("Additional preload must be between 0 and 2 mm.", ["preloadAdjustment"]);
        // Fixed-length compression locks set the grip position geometrically.
        const stroke = definition.isometricLock ? 15 * mm - preload : definition.previewTravel;
        if (stroke < 0 * mm || stroke > 30 * mm)
            throw regenError("Preview must be between 0 and 30 mm.", ["previewTravel"]);

        // Fixed dimensions form a coordinated prototype, not independent knobs.
        // Envelope180.1 x132 x32 including enclosure; base156 x132, floor6 (Z-2 to Z4); pocket20 deep, floor2.7 above guide.
        const baseThickness = 6 * mm;
        const gripTopZ = 30 * mm;
        const palmCenterX = -34 * mm;
        const palmCenterZ = 19.75 * mm;
        const palmPlateTopZ = 14.5 * mm;
        const springZ = 18 * mm;
        var baseBodies = [];
        var movingBodies = [];

        makeBox(context,id + "base",vector(-22,-66,-2)*mm,vector(134,66,4)*mm);
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

        // Flat132: fixed palm and frame form one printed body. Two wristward
        // raised bridges overlap the sensor wall at X[-22,-18.5], |Y|17..24.
        // They clear the enclosure lid Z8.9 by0.6, H15 |Y|16 by1, front rod
        // blocks X-18 by0.5, and capture-head minimum X-15.75 by2.75.
        // Bridge/joint strength remains unqualified; no old four-M4 mount.
        makeBox(context,id + "palmBridgeLeft",vector(-26,-33,9.5)*mm,vector(-18.5,-17,14.5)*mm);
        makeBox(context,id + "palmBridgeRight",vector(-26,17,9.5)*mm,vector(-18.5,33,14.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmBridgeLeft"));
        baseBodies=append(baseBodies,body(id + "palmBridgeRight"));
        makeBox(context,id + "palmPad",vector(-44.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);
        opFillet(context,id + "palmCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmPad",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        makeCylinder(context,id + "palmBolsterCore",vector(-34,-58,19.75)*mm,
            vector(-34,58,19.75)*mm,7.75*mm);
        opFillet(context,id + "palmEnds",{
            "entities":qCreatedBy(id + "palmBolsterCore",EntityType.EDGE),
            "radius":2*mm,"tangentPropagation":true });
        join(context,id + "palmJoin",[body(id + "palmPad"),body(id + "palmBolsterCore")]);
        // Service notch clears the keeper plate's wristward disengagement.
        // Retained core ends at X-26.25; this notch starts at X-24.4, clear1.85.
        // Bridge inner |Y|17 remains0.7 beyond the notch |Y|16.3.
        makeBox(context,id + "keeperPalmServiceTool",vector(-24.4,-16.3,9.4)*mm,
            vector(-23.0,16.3,14.6)*mm);
        cut(context,id + "keeperPalmServiceCut",body(id + "palmPad"),
            body(id + "keeperPalmServiceTool"));
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
        var insertTools=[];
        var n=0;
        // P01/P02 are united below after all fixed frame elements exist.
        makeCylinder(context,id + "palmCushion",vector(-34,-43,19.75)*mm,vector(-34,43,19.75)*mm,10.25*mm);
        opFillet(context,id + "sleeveEnds",{
            "entities":qCreatedBy(id + "palmCushion",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeCylinder(context,id + "sleeveCoreTool",vector(-34,-44,19.75)*mm,vector(-34,44,19.75)*mm,7.75*mm);
        makeBox(context,id + "sleeveBottomTool",vector(-50,-45,0)*mm,vector(-18,45,14.6)*mm);
        cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool")]));
        nameBody(context,body(id + "palmPad"),"P02 STUDY intermediate palm - united into P01");
        nameBody(context,body(id + "palmCushion"),"P03 TPU PRINT - 2.5 mm palm sleeve");

        // Carriage: two outside spring arms joined to a rounded central pocket.
        makeBox(context,id + "carriageBridge",vector(116,-63,5)*mm,vector(124,63,24)*mm);
        var carriageBodies=[body(id + "carriageBridge")];
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const loY = side == -1 ? -63 : 43;
            const hiY = side == -1 ? -43 : 63;
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
        makeBox(context,id + "switchCam",vector(64,-2,7)*mm,vector(78,8,15)*mm);
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
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT STUDY - Flat132 72 mm clear pocket, R12 seat reliefs");
        // A socket-head M3x12 screw provides +/-1 mm click adjustment. Its flat
        // head face is the nominal X60 contact datum, independent of hard stops.
        makeCylinder(context,id + "camScrew",vector(60,2.5,10)*mm,vector(63,2.5,10)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(62.9,2.5,10)*mm,vector(75,2.5,10)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        makeCylinder(context,id + "camInsertTool",vector(63.8,2.5,10)*mm,vector(69,2.5,10)*mm,2.1*mm);
        makeCylinder(context,id + "camThroughTool",vector(63,2.5,10)*mm,vector(76.5,2.5,10)*mm,1.7*mm);
        cut(context,id + "camMount",body(id + "carriageBridge"),qUnion([body(id + "camInsertTool"),body(id + "camThroughTool")]));
        movingBodies=append(movingBodies,body(id + "camScrew"));
        nameBody(context,body(id + "camScrew"),"H10 M3 x 12 socket-head screw - adjustable click cam");

        // Single32 mm central profile under the existing20 mm pocket. The
        // base is6 mm with topZ4; rail topZ7 and female roofZ7.3 leave2.7 mm below the
        // pocket floor. Two14 mm bearing lands are45 mm apart longitudinally.
        makeXPrism(context,id + "centralTrack",34*mm,124*mm,
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
        makeCylinder(context,id + "yokeSensorTool",vector(-8,0,18)*mm,vector(1,0,18)*mm,10.2*mm);
        makeBox(context,id + "yokeCableTool",vector(-8,7.5,14.5)*mm,vector(-1.5,40,21.5)*mm);
        cut(context,id + "yokeRelief",body(id + "springAnchor"),qUnion([body(id + "yokeSensorTool"),body(id + "yokeCableTool")]));
        nameBody(context,body(id + "springAnchor"),"P05 PRINT STUDY - Flat132 reinforced floating spring yoke");

        // One M6x1 screw translates the complete sensor support, cell, pusher
        // and yoke. Both seats therefore advance equally, without bypassing
        // the sensor. Hardware below is nominal/unthreaded CAD envelope only.
        makeBox(context,id + "loadCellWall",vector(-22,-24,3.8)*mm,vector(-16,24,29)*mm);
        makeCylinder(context,id + "preloadBore",vector(-23,0,18)*mm,vector(-15,0,18)*mm,3.2*mm);
        cut(context,id + "preloadClearance",body(id + "loadCellWall"),body(id + "preloadBore"));
        // Captive custom square steel nut, M6x1, 12 x 12 x 6.
        makeBox(context,id + "nutPocket",vector(-22.1,-6.2,11.8)*mm,vector(-15.9,6.2,24.2)*mm);
        cut(context,id + "preloadNutPocket",body(id + "loadCellWall"),body(id + "nutPocket"));
        makeBox(context,id + "preloadNut",vector(-21,-6,12)*mm,vector(-16,6,24)*mm);
        makeCylinder(context,id + "nutBore",vector(-23,0,18)*mm,vector(-15,0,18)*mm,3.05*mm);
        cut(context,id + "nutThreadEnvelope",body(id + "preloadNut"),body(id + "nutBore"));
        nameBody(context,body(id + "preloadNut"),"H11 Custom steel M6x1 square nut 12 x 12 x 5");
        // A 2 mm steel keeper is recessed 1 mm into the wall. Through screws
        // react into captive steel nuts; no tapped-plastic load-bearing threads.
        makeBox(context,id + "keeperRecess",vector(-22.1,-16.2,8.8)*mm,vector(-20.9,16.2,28.2)*mm);
        cut(context,id + "keeperSeat",body(id + "loadCellWall"),body(id + "keeperRecess"));
        makeBox(context,id + "nutKeeper",vector(-23,-16,9)*mm,vector(-21,16,28)*mm);
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            makeCylinder(context,id + ("keeperHole"~t),vector(-24,side*11,24)*mm,vector(-20,side*11,24)*mm,1.7*mm);
            cut(context,id + ("keeperDrill"~t),body(id + "nutKeeper"),body(id + ("keeperHole"~t)));
            makeCylinder(context,id + ("keeperPilot"~t),vector(-23,side*11,24)*mm,vector(-15.8,side*11,24)*mm,1.7*mm);
            cut(context,id + ("keeperTap"~t),body(id + "loadCellWall"),body(id + ("keeperPilot"~t)));
            makeBox(context,id + ("keeperNutTrap"~t),vector(-18,side*11-2.85,21.15)*mm,vector(-15.8,side*11+2.85,26.85)*mm);
            cut(context,id + ("keeperNutTrapCut"~t),body(id + "loadCellWall"),body(id + ("keeperNutTrap"~t)));
            makeBox(context,id + ("keeperNut"~t),vector(-17.9,side*11-2.75,21.25)*mm,vector(-16.1,side*11+2.75,26.75)*mm);
            makeCylinder(context,id + ("keeperNutBore"~t),vector(-18.1,side*11,24)*mm,vector(-16,side*11,24)*mm,1.55*mm);
            cut(context,id + ("keeperNutThread"~t),body(id + ("keeperNut"~t)),body(id + ("keeperNutBore"~t)));
            makeCylinder(context,id + ("keeperScrew"~t),vector(-21.6,side*11,24)*mm,vector(-15,side*11,24)*mm,1.5*mm);
            fCone(context,id + ("keeperCountersink"~t),{"bottomCenter":vector(-23,side*11,24)*mm,"topCenter":vector(-21.5,side*11,24)*mm,"bottomRadius":3*mm,"topRadius":1.5*mm});
            cut(context,id + ("keeperCountersinkCut"~t),body(id + "nutKeeper"),body(id + ("keeperCountersink"~t)));
            fCone(context,id + ("keeperHead"~t),{"bottomCenter":vector(-23,side*11,24)*mm,"topCenter":vector(-21.5,side*11,24)*mm,"bottomRadius":3*mm,"topRadius":1.5*mm});
            join(context,id + ("keeperScrewJoin"~t),[body(id + ("keeperScrew"~t)),body(id + ("keeperHead"~t))]);
            nameBody(context,body(id + ("keeperScrew"~t)),"H16"~t~" M3 x 8 countersunk keeper screw - 90 deg max head diameter 6");
            nameBody(context,body(id + ("keeperNut"~t)),"H17"~t~" M3 square nut 5.5 x 5.5 x 1.8");
        }
        makeCylinder(context,id + "keeperCentre",vector(-24,0,18)*mm,vector(-20,0,18)*mm,3.2*mm);
        cut(context,id + "keeperShaftClearance",body(id + "nutKeeper"),body(id + "keeperCentre"));
        nameBody(context,body(id + "nutKeeper"),"H15 S355 steel keeper 32 x 19 x 2 - recessed and through bolted");
        // Recessed setting lock: M3x4 screw presses a brass pad onto M6.
        // Loosen before adjustment. Head remains below the 30 mm envelope.
        makeCylinder(context,id + "preloadLockHole",vector(-19,0,21)*mm,vector(-19,0,30)*mm,1.6*mm);
        cut(context,id + "preloadLockDrill",qUnion([body(id + "loadCellWall"),body(id + "preloadNut"),body(id + "nutKeeper")]),body(id + "preloadLockHole"));
        makeCylinder(context,id + "preloadLockCounterbore",vector(-19,0,26)*mm,vector(-19,0,30)*mm,2.9*mm);
        cut(context,id + "preloadLockHeadRelief",qUnion([body(id + "loadCellWall"),body(id + "nutKeeper")]),body(id + "preloadLockCounterbore"));
        makeCylinder(context,id + "preloadLockScrew",vector(-19,0,22)*mm,vector(-19,0,26.1)*mm,1.5*mm);
        makeCylinder(context,id + "preloadLockHead",vector(-19,0,26)*mm,vector(-19,0,29)*mm,2.75*mm);
        join(context,id + "preloadLockJoin",[body(id + "preloadLockScrew"),body(id + "preloadLockHead")]);
        makeCylinder(context,id + "preloadLockPad",vector(-19,0,21)*mm,vector(-19,0,22)*mm,1.25*mm);
        nameBody(context,body(id + "preloadLockScrew"),"H21 M3 x 4 recessed preload locking screw");
        nameBody(context,body(id + "preloadLockPad"),"H22 Brass preload lock pad dia2.5 x1");
        baseBodies=append(baseBodies,body(id + "loadCellWall"));
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const lo=side == -1 ? -17 : 14;
            makeBox(context,id + ("cassetteGuide"~t),vector(-16.2,lo,3.8)*mm,vector(-8,lo+3,29)*mm);
            baseBodies=append(baseBodies,body(id + ("cassetteGuide"~t)));
        }
        makeBox(context,id + "sensorCassette",vector(-12,-13.5,7.5)*mm,vector(-8,13.5,28.5)*mm);
        makeCylinder(context,id + "cellRearRelief",vector(-9.6,0,18)*mm,vector(-7.8,0,18)*mm,7.5*mm);
        cut(context,id + "cellSupportRelief",body(id + "sensorCassette"),body(id + "cellRearRelief"));
        // Side ears retain the cassette even with both springs removed.
        // OD4/ID3.2 x4 spacers prevent screw tightening from clamping the guides.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const lowY=side == -1 ? -13.5 : 10;
            makeBox(context,id + ("cassetteEar"~t),vector(-15.2,lowY,7.5)*mm,vector(-11.8,lowY+3.5,12.5)*mm);
            join(context,id + ("cassetteEarJoin"~t),[body(id + "sensorCassette"),body(id + ("cassetteEar"~t))]);
            makeCylinder(context,id + ("cassetteThread"~t),vector(-13,side*8.8,10)*mm,vector(-13,side*13.7,10)*mm,1.55*mm);
            cut(context,id + ("cassettePinTap"~t),body(id + "sensorCassette"),body(id + ("cassetteThread"~t)));
            // Slot overall X=-15..-9; OD4 spacer centres travel -13..-11.
            makeCylinder(context,id + ("captureSlotA"~t),vector(-12.8,side*13.8,10)*mm,vector(-12.8,side*17.2,10)*mm,2.2*mm);
            makeCylinder(context,id + ("captureSlotB"~t),vector(-11.2,side*13.8,10)*mm,vector(-11.2,side*17.2,10)*mm,2.2*mm);
            const slotLow=side == -1 ? -17.2 : 13.8;
            makeBox(context,id + ("captureSlotC"~t),vector(-12.8,slotLow,7.8)*mm,vector(-11.2,slotLow+3.4,12.2)*mm);
            cut(context,id + ("captureSlotCut"~t),body(id + ("cassetteGuide"~t)),qUnion([body(id + ("captureSlotA"~t)),body(id + ("captureSlotB"~t)),body(id + ("captureSlotC"~t))]));
            makeCylinder(context,id + ("captureSpacer"~t),vector(-13,side*13.5,10)*mm,vector(-13,side*17.5,10)*mm,2*mm);
            makeCylinder(context,id + ("captureSpacerBore"~t),vector(-13,side*13.4,10)*mm,vector(-13,side*17.6,10)*mm,1.6*mm);
            cut(context,id + ("captureSpacerCut"~t),body(id + ("captureSpacer"~t)),body(id + ("captureSpacerBore"~t)));
            makeCylinder(context,id + ("captureScrew"~t),vector(-13,side*9.5,10)*mm,vector(-13,side*17.6,10)*mm,1.5*mm);
            makeCylinder(context,id + ("captureHead"~t),vector(-13,side*17.5,10)*mm,vector(-13,side*20.5,10)*mm,2.75*mm);
            join(context,id + ("captureScrewJoin"~t),[body(id + ("captureScrew"~t)),body(id + ("captureHead"~t))]);
            nameBody(context,body(id + ("captureScrew"~t)),"H18"~t~" M3 x 8 cassette retention screw");
            nameBody(context,body(id + ("captureSpacer"~t)),"H19"~t~" Steel spacer 4 x 3.2 x 4 - preload travel limiter");
        }
        nameBody(context,body(id + "sensorCassette"),"H12 Machined steel translating sensor backing plate - relieved centre");
        makeCylinder(context,id + "preloadScrew",vector(-24,0,18)*mm,vector(-12,0,18)*mm,3*mm);
        makeCylinder(context,id + "preloadWheel",vector(-15.8,0,18)*mm,vector(-13,0,18)*mm,11*mm);
        join(context,id + "joinPreloadScrew",[body(id + "preloadScrew"),body(id + "preloadWheel")]);
        nameBody(context,body(id + "preloadScrew"),"H13 M6x1 flat-tip adjuster with 22 mm thumbwheel - 2 turns max");
        makeCylinder(context,id + "loadCell",vector(-8,0,18)*mm,vector(-2.55,0,18)*mm,9.875*mm);
        makeCylinder(context,id + "loadCellBoss",vector(-2.55,0,18)*mm,vector(-1.9,0,18)*mm,2.5*mm);
        makeBox(context,id + "loadCellOvermold",vector(-7,8,15.5)*mm,vector(-3.5,14,20.5)*mm);
        // Cable/connector preview rerouted inward. Retain real sensor-lead slack.
        makeCylinder(context,id + "loadCellCable",vector(-5.25,8.5,18)*mm,vector(-5.25,33,18)*mm,1.2*mm);
        makeBox(context,id + "loadCellConnector",vector(-8.25,30.5,15)*mm,vector(-2.25,38.5,21)*mm);
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
        nameBody(context,body(id + "loadCell"),"H01 TE FX1901-0001-0200-L compression cell");
        nameBody(context,body(id + "loadCellBoss"),"H01a Sensor force boss");
        nameBody(context,body(id + "loadCellOvermold"),"H01b Sensor cable overmold");
        nameBody(context,body(id + "loadCellCable"),"H01c Sensor cable");
        nameBody(context,body(id + "loadCellConnector"),"H01d Sensor connector");
        nameBody(context,body(id + "loadPusher"),"H02 Retained steel pusher: dia4 tip x1.9, dia8 shoulder x1, M3 tail x6.5");

        // Ordered pairs: DF2194 initial compression 1..3 mm; DF2185 4..6 mm; travel 30 mm.
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
                nameBody(context,body(id + ("isoSleeve"~s)),"H14"~s~" ISOMETRIC steel compression lock sleeve 16 x 8 x 86 mm");
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
            makeCylinder(context,id + ("rod"~s),vector(-16,y,18)*mm,vector(130,y,18)*mm,3*mm);
            nameBody(context,body(id + ("rod"~s)),"H04"~s~" Steel guide rod dia 6 x 146 mm");
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
            // Rear assembly sweep: P04 underside is Z5, so fixed feet stop at
            // Z4.5 (0.5 mm nominal clearance). Removable retainers extend down
            // to this seat, preserving their rod datum and screw head Z10.
            makeBox(context,id + ("rearFoot"~s),vector(124.5,y-12,3.8)*mm,vector(134,y+12,4.5)*mm);
            baseBodies=append(baseBodies,body(id + ("rearFoot"~s)));
            makeBox(context,id + ("rearBlock"~s),vector(125.5,y-12,4.5)*mm,vector(133.5,y+12,28)*mm);
            makeCylinder(context,id + ("rearSocket"~s),vector(125,y,18)*mm,vector(131.2,y,18)*mm,3.1*mm);
            cut(context,id + ("rearBore"~s),body(id + ("rearBlock"~s)),body(id + ("rearSocket"~s)));
            nameBody(context,body(id + ("rearBlock"~s)),"P06"~s~" PRINT - removable rear retainer - through holes RevC");
            for (var offset in [-8,8])
            {
                const t=offset == -8 ? "a" : "b";
                makeCylinder(context,id + ("rearHole"~s~t),vector(129.5,y+offset,4)*mm,vector(129.5,y+offset,29)*mm,1.7*mm);
                makeCylinder(context,id + ("rearHead"~s~t),vector(129.5,y+offset,10)*mm,vector(129.5,y+offset,29)*mm,3.2*mm);
                cut(context,id + ("rearMount"~s~t),body(id + ("rearBlock"~s)),
                    qUnion([body(id + ("rearHole"~s~t)),body(id + ("rearHead"~s~t))]));
                makeCylinder(context,id + ("rearInsert"~s~t),vector(129.5,y+offset,0.5)*mm,vector(129.5,y+offset,4.6)*mm,2.1*mm);
                insertTools=append(insertTools,body(id + ("rearInsert"~s~t)));
                const padY=y+(offset == -8 ? -7.5 : 7.5);
                makeBox(context,id + ("returnPad"~s~t),vector(124,padY-2.25,14)*mm,vector(125.5,padY+2.25,20)*mm);
                nameBody(context,body(id + ("returnPad"~s~t)),"P07"~s~t~" TPU PRINT - return bumper");
            }
        }

        // M4 stops meet the pocket deck front at X35 after30 mm travel.
        // Captive square M4 nuts sit in open-top 7.2 mm traps for assembly.
        for (var side in [-1,1])
        {
            const s = side == -1 ? "0" : "1";
            const y = side*24;
            makeBox(context,id + ("stopBlock"~s),vector(24,y-5,3.8)*mm,vector(31,y+5,25)*mm);
            makeCylinder(context,id + ("stopHole"~s),vector(23,y,18)*mm,vector(32,y,18)*mm,2.25*mm);
            makeBox(context,id + ("stopNutSlot"~s),vector(25.8,y-3.6,14.4)*mm,vector(29.2,y+3.6,26)*mm);
            cut(context,id + ("stopCut"~s),body(id + ("stopBlock"~s)),
                qUnion([body(id + ("stopHole"~s)),body(id + ("stopNutSlot"~s))]));
            baseBodies=append(baseBodies,body(id + ("stopBlock"~s)));
            makeCylinder(context,id + ("stopScrew"~s),vector(25,y,18)*mm,vector(35,y,18)*mm,2*mm);
            makeBox(context,id + ("stopNut"~s),vector(26,y-3.5,14.5)*mm,vector(29,y+3.5,21.5)*mm);
            makeCylinder(context,id + ("nutBore"~s),vector(25,y,18)*mm,vector(30,y,18)*mm,2*mm);
            cut(context,id + ("cutNut"~s),body(id + ("stopNut"~s)),body(id + ("nutBore"~s)));
            nameBody(context,body(id + ("stopScrew"~s)),"H07"~s~" M4 x 10 flat-tip stop screw");
            nameBody(context,body(id + ("stopNut"~s)),"H08"~s~" M4 square nut 7 x 7 x 3 mm");
        }

        // SS-01GL2 laid on its broad face: only 6.4 mm above the base. Actual
        // case and mounting dimensions; hinge is an illustrative approximation.
        // OP nominal X31 is 1 mm ahead of cam full-travel face X30.
        makeBox(context,id + "switchPedestal",vector(13,-18,3.8)*mm,vector(25,4,6)*mm);
        baseBodies=append(baseBodies,body(id + "switchPedestal"));
        makeBox(context,id + "switchBody",vector(14,-17,6)*mm,vector(24.2,2.8,12.4)*mm);
        for (var y in [-11.9,-2.4])
        {
            const s=y == -11.9 ? "0" : "1";
            makeCylinder(context,id + ("switchMountHole"~s),vector(16.5,y,5)*mm,vector(16.5,y,13)*mm,1.175*mm);
            cut(context,id + ("switchDrill"~s),body(id + "switchBody"),body(id + ("switchMountHole"~s)));
            makeCylinder(context,id + ("switchInsert"~s),vector(16.5,y,2)*mm,vector(16.5,y,6.2)*mm,1.6*mm);
            insertTools=append(insertTools,body(id + ("switchInsert"~s)));
        }
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(33.4*mm,60*mm-stroke-2.4*mm);
        const rollerY=-14.1*mm+sqrt(leverLength*leverLength-(rollerX-25.5*mm)*(rollerX-25.5*mm));
        makeCylinder(context,id + "switchLever",vector(25.5,-14.1,9.2)*mm,
            vector(rollerX,rollerY,9.2*mm),0.45*mm);
        makeCylinder(context,id + "switchRoller",vector(rollerX,rollerY,7.6*mm),
            vector(rollerX,rollerY,10.8*mm),2.4*mm);
        nameBody(context,body(id + "switchBody"),"H09 Omron SS-01GL2 - flat mounting");
        nameBody(context,body(id + "switchLever"),"H09a Switch lever preview");
        nameBody(context,body(id + "switchRoller"),"H09b Switch roller preview");

        // 13.10.2026: cord eyes removed to restore rear carriage assembly access.

        join(context,id + "integrateBase",baseBodies);
        join(context,id + "integratePalm",[body(id + "base"),body(id + "palmPad")]);
        cut(context,id + "baseInserts",body(id + "base"),qUnion(insertTools));
        var mountingTools=[];
        n=0;
        for (var x in [16,127])
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
        nameBody(context,body(id + "base"),"P01-P02 PRINT STUDY - Flat132 integral fixed frame and palm support, 6 mm floor");

        if (preload > 0*mm)
            opTransform(context,id + "synchronizedPreload",{
                "bodies":qUnion([body(id + "springAnchor"),body(id + "fixedSeat0"),body(id + "fixedSeat1"),
                    body(id + "sensorCassette"),body(id + "loadCell"),body(id + "loadCellBoss"),
                    body(id + "loadCellOvermold"),body(id + "loadCellCable"),body(id + "loadCellConnector"),
                    body(id + "loadPusher"),body(id + "preloadScrew"),
                    body(id + "captureSpacer0"),body(id + "captureSpacer1"),
                    body(id + "captureScrew0"),body(id + "captureScrew1"),body(id + "pusherNut")]),
                "transform":transform(vector(preload,0*mm,0*mm)) });
        println({"mode":definition.isometricLock ? "ISOMETRIC compression lock" : "DYNAMIC",
            "additionalPreload":preload,"actualStroke":stroke,
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
        // Neutral green frame, warm tan climbing surface, dark soft contact.
        finishBody(context,body(id + "base"),color(0.27,0.30,0.28));
        finishBody(context,body(id + "palmCushion"),color(0.15,0.20,0.17));
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
        for (var check in auditFingerworkerCollisions(context,id))
            println({ "pose":stroke,"pair":check.pair,"status":check.status,
                "gap":check.minimumSeparation,"interferences":check.interferenceCount,
                "contacts":check.exteriorContactCount,"unclassified":check.unclassifiedCount });
        if (definition.showElectronics)
        {
            for (var check in makeElectronicsStudy(context,id))
                println({ "pose":stroke,"pair":check.pair,"status":check.status,
                    "gap":check.minimumSeparation,"interferences":check.interferenceCount,
                    "contacts":check.exteriorContactCount,"unclassified":check.unclassifiedCount });
        }

    }, { "previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,
        "lightSprings":true,"isometricLock":false,"showHand":false,"showElectronics":false });
