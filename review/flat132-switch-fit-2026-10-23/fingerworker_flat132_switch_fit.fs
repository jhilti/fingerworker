FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker MVP - R4 switch-fit drawing-based prototype; load rating unverified.
 * R4 2026-10-23: SS-01GL2 manufacturer DRAWING clearance reference.
 * Main body, three solder-tab boxes and a conservative lower-lug strip
 * share H09. Lever motion remains approximate; no factory STEP claim.
 * Switch moves +4 X / +1 Y / +1.5 Z mm; manual cam is M3x8.
 * Preserve the R3 palm fit and the R2 sensor-force path and travel limits.
 * Native regeneration and full validation are required before release.
 *
 * X = pull direction, Y = finger-bar width, Z = height above the base.
 * Purchased hardware is modeled at nominal catalogue size. Printed parts are
 * separated bodies so they can be exported and printed individually.
 * SEPARATE BRANCH STUDY 2026-10-19: flat 132 mm frame, 72 mm clear pocket,
 * 84 mm deck, 102 mm spring-axis spacing, 6 mm base, 35 mm nominal sensor-retainer envelope.
 * P02 is detachable on two M4 bolts and positive locating keys. This NEW joint
 * has unqualified stiffness/strength. Palm contact geometry, 86 mm sleeve and
 * electronics enclosure are retained. Remove both M4 bolts and lift the palm
 * and case module vertically before keeper/cassette assembly or service.
 * Lower forward clamps provide0.75 mm nominal capture-head withdrawal gap.
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

export function auditFingerworkerCollisions(context is Context, id is Id, sensor is Query) returns array
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
    const springs = qUnion([body(id + "spring0" + "sweep"), body(id + "spring1" + "sweep"),
        body(id + "isoSleeve0"), body(id + "isoSleeve1")]);
    const actuator = qUnion([body(id + "switchLever"), body(id + "switchRoller")]);
    const rear = qUnion([body(id + "rearBlock0"), body(id + "rearBlock1")]);
    const pads = qUnion([body(id + "returnPad0a"),body(id + "returnPad0b"),
                        body(id + "returnPad1a"),body(id + "returnPad1b")]);
    const stops = yoke; // Integral printed sensing-stop faces are part of P05.
    const keeperHardware=qUnion([body(id + "keeperScrew0"),body(id + "keeperScrew1"),body(id + "keeperNut0"),body(id + "keeperNut1"),body(id + "preloadLockScrew"),body(id + "preloadLockPad")]);
    const captureHardware=qUnion([body(id + "captureScrew0"),body(id + "captureScrew1"),body(id + "captureSpacer0"),body(id + "captureSpacer1")]);
    const device = qBodyType(qUnion([body(id),sensor]), BodyType.SOLID);
    return [
        auditSolidPair(context,"Keeper hardware / fixed wall and keeper",keeperHardware,qUnion([base,body(id + "nutKeeper")]),true),
        auditSolidPair(context,"Keeper hardware / moving stack and palm",keeperHardware,qUnion([body(id + "sensorCassette"),yoke,palm,sleeve]),false),
        auditSolidPair(context,"Cassette retainers / guides",captureHardware,base,true),
        auditSolidPair(context,"Cassette retainers / cassette",captureHardware,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette retainers / mechanism",captureHardware,qUnion([palm,sleeve,yoke,carriage,rods,sensor,body(id + "preloadScrew"),keeperHardware]),false),
        auditSolidPair(context,"Preload lock / adjusting screw",qUnion([body(id + "preloadLockScrew"),body(id + "preloadLockPad")]),body(id + "preloadScrew"),true),
        auditSolidPair(context,"Pusher / sensor and yoke",qUnion([body(id + "loadPusher"),body(id + "pusherNut")]),qUnion([sensor,yoke]),true),
        auditSolidPair(context,"Springs or lock sleeves / seats",springs,seats,true),
        auditSolidPair(context,"Adjustment hardware / base",qUnion([body(id + "preloadScrew"),
            body(id + "preloadNut"),body(id + "nutKeeper")]),base,true),
        auditSolidPair(context,"Adjustment hardware / yoke carriage palm",qUnion([body(id + "preloadScrew"),
            body(id + "preloadNut"),body(id + "nutKeeper"),body(id + "sensorCassette")]),qUnion([yoke,carriage,palm]),false),
        auditSolidPair(context,"Sensor / translating cassette",sensor,body(id + "sensorCassette"),true),
        auditSolidPair(context,"Cassette / fixed guide",body(id + "sensorCassette"),base,false),
        auditSolidPair(context,"Cassette / yoke",body(id + "sensorCassette"),yoke,false),
        auditSolidPair(context,"Preload screw / cassette",body(id + "preloadScrew"),body(id + "sensorCassette"),true),
        auditSolidPair(context,"Preload screw / palm",body(id + "preloadScrew"),palm,false),
        auditSolidPair(context,"Carriage / open frame and central guide",carriage,base,false),
        auditSolidPair(context,"Carriage / spring mandrels",carriage,rods,false),
        auditSolidPair(context,"Carriage / springs",carriage,springs,false),
        auditSolidPair(context,"Carriage / rear retainers",carriage,rear,false),
        auditSolidPair(context,"Carriage / return pads",carriage,pads,true),
        auditSolidPair(context,"Carriage / integral sensing-stop yoke",carriage,stops,true),
        auditSolidPair(context,"Carriage / switch case",carriage,body(id + "switchBody"),false),
        auditSolidPair(context,"Carriage / switch actuator",carriage,actuator,true),
        auditSolidPair(context,"Adjustable cam / switch actuator",body(id + "camScrew"),actuator,true),
        auditSolidPair(context,"Switch actuator / case",actuator,body(id + "switchBody"),false),
        auditSolidPair(context,"Switch case and actuator / fixed frame",qUnion([body(id + "switchBody"),actuator]),base,true),
        auditSolidPair(context,"Springs / surrounding structure",springs,qUnion([base,yoke,carriage,rear,rods,palm,sleeve]),false),
        auditSolidPair(context,"Spring seats / structure",seats,qUnion([base,yoke,carriage,rear,rods,palm,sleeve]),true),
        auditSolidPair(context,"Yoke / base rods and palm",yoke,qUnion([base,rods,palm,sleeve]),false),
        auditSolidPair(context,"Yoke / sensor",yoke,sensor,false),
        auditSolidPair(context,"Sensor / base",sensor,base,false),
        auditSolidPair(context,"Palm support / base",palm,base,true),
        auditSolidPair(context,"Palm / carriage and switch",qUnion([palm,sleeve]),qUnion([carriage,body(id + "switchBody"),actuator]),false),
        auditSolidPair(context,"Palm sleeve / rigid support",sleeve,palm,true),
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

annotation { "Feature Type Name" : "FingerworkerFlat132ActualSensor", "Feature Name Template" : "Flat132 actual sensor - 30 mm travel" }
export const fingerworkerMVP = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Aligned official TE FX1901 solid (derive before this feature)",
            "Filter" : EntityType.BODY && BodyType.SOLID, "MaxNumberOfPicks" : 1 }
        definition.actualSensor is Query;
        annotation { "Name" : "Frame travel (0 to 30 mm minus preload; reset click cam after preload)" }
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
        if (size(evaluateQuery(context,definition.actualSensor)) != 1)
            throw regenError("Select the aligned, unmodified official TE FX1901 manufacturer solid.",["actualSensor"]);
        const sensorBox = evBox3d(context,{"topology":definition.actualSensor,"tight":true});
        if (norm(sensorBox.minCorner-vector(-9.85,-12.5,5.5)*mm)>0.05*mm ||
            norm(sensorBox.maxCorner-vector(-1.9,27,30.5)*mm)>0.05*mm)
            throw regenError("Use the apex-aligned official STEP at its base origin; do not rescale or offset it.",["actualSensor"]);
        nameBody(context,definition.actualSensor,"H01 ACTUAL TE FX1901-0001-0200-L manufacturer STEP rev F");
        finishBody(context,definition.actualSensor,color(0.75,0.76,0.77));
        const preload = definition.preloadAdjustment;
        if (preload < 0 * mm || preload > 2 * mm)
            throw regenError("Additional preload must be between 0 and 2 mm.", ["preloadAdjustment"]);
        // Fixed-length compression locks set the grip position geometrically.
        const maxDynamicTravel = 30 * mm - preload;
        if (!definition.isometricLock && definition.previewTravel > maxDynamicTravel + 1e-6*mm)
            throw regenError("Integral sensing stops limit frame travel to30 mm minus preload. Use28 mm at2 mm preload; manually reset the click cam after changing preload.", ["previewTravel", "preloadAdjustment"]);
        const stroke = definition.isometricLock ? 15 * mm - preload : definition.previewTravel;
        if (stroke < 0 * mm || stroke > 30 * mm)
            throw regenError("Preview must be between 0 and 30 mm.", ["previewTravel"]);

        // Fixed dimensions form a coordinated prototype, not independent knobs.
        // Envelope180.1 x132 x35 including enclosure and captive sensor; base156 x132, floor6 (Z-2 to Z4); pocket20 deep, floor2.7 above guide.
        const baseThickness = 6 * mm;
        const gripTopZ = 30 * mm;
        const palmCenterX = -27 * mm;
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

        // Flat132 detachable palm: two narrow feet remain outside sensor wall
        // |Y|24 and inside rod blocks |Y|39, with2 mm nominal gaps each side.
        // Positive keys supplement two M4 bolts; joint strength is unqualified.
        // Case front X-23.6 clears foot wrist edge X-23 by0.6 mm.
        makeBox(context,id + "palmFootLeft",vector(-23,-37,3.8)*mm,vector(-9,-26,6.5)*mm);
        makeBox(context,id + "palmFootRight",vector(-23,26,3.8)*mm,vector(-9,37,6.5)*mm);
        baseBodies=append(baseBodies,body(id + "palmFootLeft"));
        baseBodies=append(baseBodies,body(id + "palmFootRight"));
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const y=side*31.5;
            makeBox(context,id + ("palmKey"~s),vector(-22,y-3,6.3)*mm,
                vector(-20,y+3,8)*mm);
            baseBodies=append(baseBodies,body(id + ("palmKey"~s)));
        }
        makeBox(context,id + "palmPad",vector(-37.25,-64,9.5)*mm,vector(-23.25,64,14.5)*mm);
        opFillet(context,id + "palmCorners",{
            "entities":qParallelEdges(qCreatedBy(id + "palmPad",EntityType.EDGE),vector(0,0,1)),
            "radius":2*mm,"tangentPropagation":true });
        makeBox(context,id + "palmEarLeft",vector(-30,-37,9.5)*mm,vector(-9.5,-26,14.5)*mm);
        makeBox(context,id + "palmEarRight",vector(-30,26,9.5)*mm,vector(-9.5,37,14.5)*mm);
        // Only the forward clamp drops belowZ9.5, retaining0.6 mm case gap
        // atX-23. The original upper root stays above the unchanged case.
        makeBox(context,id + "palmClampDropLeft",vector(-23,-37,6.5)*mm,vector(-9.5,-26,9.6)*mm);
        makeBox(context,id + "palmClampDropRight",vector(-23,26,6.5)*mm,vector(-9.5,37,9.6)*mm);
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
        var insertTools=[];
        var palmTools=[];
        var n=0;
        // Two M4 bolts are retained from the existing hardware set. Each wing
        // has one locating key with0.25 mm side and0.3 mm roof clearance.
        // Tab front X-9.5 clears connector X-8.25 by1.25 mm for vertical lift.
        for (var side in [-1,1])
        {
            const s=side == -1 ? "0" : "1";
            const y=side*31.5;
            makeBox(context,id + ("palmKeySlot"~s),vector(-22.25,y-3.25,6.4)*mm,
                vector(-19.75,y+3.25,8.3)*mm);
            cut(context,id + ("palmKeySlotCut"~s),body(id + "palmPad"),
                body(id + ("palmKeySlot"~s)));
        }
        for (var x in [-16])
        {
            for (var y in [-31.5,31.5])
            {
                // Six-mm inserts install flushZ6.5 and endZ0.5, leaving
                // Pilot floorZ0.2 leaves2.2 mm bottom wall above baseZ-2.
                // M4x10 fromZ10.5 ends0.5, with0.3 mm nominal tip clearance.
                makeCylinder(context,id + ("palmInsert"~n),vector(x,y,0.2)*mm,vector(x,y,7.5)*mm,2.6*mm);
                insertTools=append(insertTools,body(id + ("palmInsert"~n)));
                makeCylinder(context,id + ("palmHole"~n),vector(x,y,5.5)*mm,vector(x,y,31)*mm,2.2*mm);
                palmTools=append(palmTools,body(id + ("palmHole"~n)));
                makeCylinder(context,id + ("palmHead"~n),vector(x,y,10.5)*mm,vector(x,y,31)*mm,4*mm);
                palmTools=append(palmTools,body(id + ("palmHead"~n)));
                n+=1;
            }
        }
        cut(context,id + "palmMountHoles",body(id + "palmPad"),qUnion(palmTools));
        makeCylinder(context,id + "palmCushion",vector(-27,-43,19.75)*mm,vector(-27,43,19.75)*mm,10.25*mm);
        opFillet(context,id + "sleeveEnds",{
            "entities":qCreatedBy(id + "palmCushion",EntityType.EDGE),
            "radius":1.2*mm,"tangentPropagation":true });
        makeCylinder(context,id + "sleeveCoreTool",vector(-27,-44,19.75)*mm,vector(-27,44,19.75)*mm,7.75*mm);
        makeBox(context,id + "sleeveBottomTool",vector(-50,-45,0)*mm,vector(-18,45,14.6)*mm);
        makeBox(context,id + "palmSleeveForwardHalfTool",vector(-27,-45,0)*mm,vector(0,45,40)*mm);
        cut(context,id + "openSleeve",body(id + "palmCushion"),qUnion([body(id + "sleeveCoreTool"),body(id + "sleeveBottomTool"),body(id + "palmSleeveForwardHalfTool")]));
        // A plain half-shell loses the original over-centre radial capture.
        // Two integral end returns cover the flat D-core face while leaving
        // the central mechanism and contact surface clear. Pull-off retention
        // and real fit remain prototype qualifications; no added cam/hardware.
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const loY=side == -1 ? -43 : 39;
            makeBox(context,id + ("palmSleeveReturn"~t),vector(-27,loY,14.6)*mm,
                vector(-24.5,loY+4,30)*mm);
            join(context,id + ("palmSleeveReturnJoin"~t),
                [body(id + "palmCushion"),body(id + ("palmSleeveReturn"~t))]);
        }
        nameBody(context,body(id + "palmPad"),"P02 PRINT STUDY - plus7 mm wrist half-round palm, retained R2 keyed mounts");
        nameBody(context,body(id + "palmCushion"),"P03 TPU PRINT - plus7 mm half-round palm cap, two front returns");

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
        nameBody(context,body(id + "carriageBridge"),"P04 PRINT STUDY - Flat132 72 mm clear pocket, R12 seat reliefs");
        // MANUAL click-cam setup: after changing preload, back out the M3x8
        // screw by the same axial distance as that preload. This model shows
        // the required configured position X64-preload; there is no automatic
        // physical coupling. Check switch operation and re-lock before use.
        // The shifted switch and cam retain one-mm NOMINAL trip lead only.
        // OP tolerance and actual total travel require physical calibration.
        makeCylinder(context,id + "camScrew",vector(64,3.5,11.5)*mm,vector(67,3.5,11.5)*mm,2.75*mm);
        makeCylinder(context,id + "camScrewShank",vector(66.9,3.5,11.5)*mm,vector(75,3.5,11.5)*mm,1.5*mm);
        join(context,id + "joinCamScrew",[body(id + "camScrew"),body(id + "camScrewShank")]);
        // Diameter5.8 head recess leaves1.3 mm above female guide roofZ7.3.
        // Nominal L4 M3 insert is flush atX68 and endsX72; pilot endsX73.
        // Pilot fit and the setting lock remain dependent on actual hardware.
        makeCylinder(context,id + "camHeadReliefTool",vector(63.8,3.5,11.5)*mm,vector(68,3.5,11.5)*mm,2.9*mm);
        makeCylinder(context,id + "camInsertTool",vector(67.8,3.5,11.5)*mm,vector(73,3.5,11.5)*mm,2.1*mm);
        makeCylinder(context,id + "camThroughTool",vector(63,3.5,11.5)*mm,vector(76.5,3.5,11.5)*mm,1.7*mm);
        cut(context,id + "camMount",body(id + "carriageBridge"),qUnion([body(id + "camHeadReliefTool"),body(id + "camInsertTool"),body(id + "camThroughTool")]));
        movingBodies=append(movingBodies,body(id + "camScrew"));
        nameBody(context,body(id + "camScrew"),"H10 M3 x8 recessed manual click cam - reset by preload amount");
        if (preload > 0*mm)
            opTransform(context,id + "configuredManualClickCam",{
                "bodies":body(id + "camScrew"),
                "transform":transform(vector(-preload,0*mm,0*mm)) });

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
        makeBox(context,id + "reactionTopBridge",vector(-16.2,-25.4,30)*mm,
            vector(-12.5,25.4,33)*mm);
        join(context,id + "reactionTopBridgeJoin",[body(id + "loadCellWall"),body(id + "reactionTopBridge")]);
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
        makeBox(context,id + "keeperRecess",vector(-23.1,-16.2,8.8)*mm,vector(-20.9,16.2,28.2)*mm);
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
        // P01-only upper driver access; original H15/H11 hardware holes remain exact.
        makeCylinder(context,id + "reactionLockAccess",vector(-19,0,29.2)*mm,
            vector(-19,0,34)*mm,3.1*mm);
        cut(context,id + "reactionLockAccessCut",body(id + "loadCellWall"),body(id + "reactionLockAccess"));
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
            // Slot X=-14.8..-8.8; OD4 spacer centres travel -12.8..-10.8.
            makeCylinder(context,id + ("captureSlotA"~t),vector(-12.6,side*15.3,8.5)*mm,vector(-12.6,side*20.7,8.5)*mm,2.2*mm);
            makeCylinder(context,id + ("captureSlotB"~t),vector(-11,side*15.3,8.5)*mm,vector(-11,side*20.7,8.5)*mm,2.2*mm);
            const slotLow=side == -1 ? -20.7 : 15.3;
            makeBox(context,id + ("captureSlotC"~t),vector(-12.6,slotLow,6.3)*mm,vector(-11,slotLow+5.4,10.7)*mm);
            cut(context,id + ("captureSlotCut"~t),body(id + ("cassetteGuide"~t)),qUnion([body(id + ("captureSlotA"~t)),body(id + ("captureSlotB"~t)),body(id + ("captureSlotC"~t))]));
            makeCylinder(context,id + ("captureSpacer"~t),vector(-12.8,side*15,8.5)*mm,vector(-12.8,side*21,8.5)*mm,2*mm);
            makeCylinder(context,id + ("captureSpacerBore"~t),vector(-12.8,side*14.9,8.5)*mm,vector(-12.8,side*21.1,8.5)*mm,1.6*mm);
            cut(context,id + ("captureSpacerCut"~t),body(id + ("captureSpacer"~t)),body(id + ("captureSpacerBore"~t)));
            makeCylinder(context,id + ("captureScrew"~t),vector(-12.8,side*13,8.5)*mm,vector(-12.8,side*21.1,8.5)*mm,1.5*mm);
            makeCylinder(context,id + ("captureHead"~t),vector(-12.8,side*21,8.5)*mm,vector(-12.8,side*24,8.5)*mm,2.75*mm);
            join(context,id + ("captureScrewJoin"~t),[body(id + ("captureScrew"~t)),body(id + ("captureHead"~t))]);
            nameBody(context,body(id + ("captureScrew"~t)),"H18"~t~" M3 x 8 cassette retention screw");
            nameBody(context,body(id + ("captureSpacer"~t)),"H19"~t~" Steel spacer 4 x 3.2 x 6 - preload travel limiter");
        }
        nameBody(context,body(id + "sensorCassette"),"H12 S355 steel planar sensor backing plate 30 x30 x2.15 with locating collar");
        makeCylinder(context,id + "preloadScrew",vector(-24,0,18)*mm,vector(-12,0,18)*mm,3*mm);
        makeCylinder(context,id + "preloadWheel",vector(-15.8,0,18)*mm,vector(-13,0,18)*mm,11*mm);
        join(context,id + "joinPreloadScrew",[body(id + "preloadScrew"),body(id + "preloadWheel")]);
        nameBody(context,body(id + "preloadScrew"),"H13 M6x1 flat-tip adjuster with 22 mm thumbwheel - 2 turns max");
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

        // Broad integral PRINTED sensing stops replace both M4 screws/nuts.
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
            // R2 flare X24.7 is retained; the shifted R4 case overlaps in X
            // and clears the negative stop by1 mm in Y (case-16, stop-17).
            makeBox(context,id + ("sensingStopFace"~t),vector(24.7,y-7,7)*mm,
                vector(35,y+7,29)*mm);
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
        // Cam faceX64-preload-stroke reachesX34 at the integral stop:
        // one-mm nominal trip lead only; calibrate and check actual overtravel.
        const leverLength=sqrt(3.1*3.1+16.7*16.7)*mm;
        const rollerX=min(37.4*mm,64*mm-stroke-preload-2.4*mm);
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
        // Lower edges of backing and keeper sweep through this shallow pocket.
        // Z2.7 floor retains 4.7 mm solid frame thickness above Z-2.
        makeBox(context,id + "realSensorFloorPocket",vector(-12.3,-15.3,2.7)*mm,vector(2.9,15.3,4.2)*mm);
        cut(context,id + "realSensorFloorRelief",body(id + "base"),body(id + "realSensorFloorPocket"));
        nameBody(context,body(id + "base"),"P01 PRINT STUDY - Flat132 reinforced reaction portal, 5 mm cassette guides, 6 mm floor");

        if (preload > 0*mm)
            opTransform(context,id + "synchronizedPreload",{
                "bodies":qUnion([body(id + "springAnchor"),body(id + "fixedSeat0"),body(id + "fixedSeat1"),
                    body(id + "sensorCassette"),definition.actualSensor,
                    body(id + "loadPusher"),body(id + "preloadScrew"),
                    body(id + "captureSpacer0"),body(id + "captureSpacer1"),
                    body(id + "captureScrew0"),body(id + "captureScrew1"),body(id + "pusherNut"),
                    body(id + "cellFrontKeeper"),body(id + "cellRetainerSpacer0"),body(id + "cellRetainerSpacer1"),
                    body(id + "cellRetainerSpacer2"),body(id + "cellRetainerSpacer3"),body(id + "cellRetainerScrew0"),
                    body(id + "cellRetainerScrew1"),body(id + "cellRetainerScrew2"),body(id + "cellRetainerScrew3")]),
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
        finishBody(context,body(id + "palmPad"),color(0.27,0.32,0.28));
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

    }, { "previewTravel":0*millimeter,"preloadAdjustment":0*millimeter,
        "lightSprings":true,"isometricLock":false,"showHand":false,"showElectronics":false });
