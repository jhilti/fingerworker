FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker MVP - production-oriented layout for a first 3D printed test.
 *
 * X = pull direction, Y = finger-bar width, Z = height above the base.
 * Purchased hardware is modeled at nominal catalogue size. Printed parts are
 * separated bodies so they can be exported and printed individually.
 * Revision 2026-09-04: clearance and contact-surface review.
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
}

/**
 * Hand reference helper block for Fingerworker. Paste above defineFeature in the
 * existing Feature Studio (geometry.fs is already imported there).
 *
 * Call makeHandReference(context, id + "handReference", displacement);
 * after positioning the machine, with displacement between 0 and 30 mm.
 *
 * Assumed interface: a rounded palm bolster is centered at x = 26.75 mm,
 * z = 49.25 mm with outer radius 10.25 mm. Its front is x = 37 mm and
 * its crown z = 59.5 mm, level with the recessed climbing grip. The grip is
 * x = 137..171 mm, y = +/-47 mm, floor z = 39.5 mm and top z = 59.5 mm at
 * rest. The pocket's loaded inner wall is x = 137 mm. The heel braces against the forward curved bolster face with a nominal
 * 0.1 mm visualization gap. It remains fixed while the fingertips pull the
 * pocket wall toward -X through a 30 mm stroke. Covers are omitted.
 * The pose is an illustrative adult-sized
 * reference, not anthropometric data or a fit/force/clearance certification.
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

    // A continuous palm with the heel braced against the rounded forward face.
    // At z49.25 the heel begins at x37.1, 0.1 mm in front of the bolster.
    // Flattening the heel vertically leaves 1.25 mm above the spring anchor;
    // a rising volume connects it to the metacarpal arch. The wrist passes
    // above the bolster crown rather than through the horizontal reaction face.
    const palmVolumes = [
        { "suffix" : "wrist", "center" : vector(-15, 0, 76),
          "radius" : vector(39, 23, 12) },
        { "suffix" : "heel", "center" : vector(51.5, 0, 49.25),
          "radius" : vector(14.4, 29, 9) },
        { "suffix" : "heelRise", "center" : vector(54, 0, 60),
          "radius" : vector(16, 29, 13) },
        { "suffix" : "palm", "center" : vector(58, 0, 74.5),
          "radius" : vector(45, 38, 14) },
        { "suffix" : "thenar", "center" : vector(46, -25, 72),
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
        { "name" : "index", "x" : 84, "y" : -28, "z" : 71,
          "proximal" : 43, "middle" : 29, "radius" : 8.5 },
        { "name" : "middle", "x" : 87, "y" : -8, "z" : 73,
          "proximal" : 44, "middle" : 27, "radius" : 9.0 },
        { "name" : "ring", "x" : 84, "y" : 13, "z" : 72,
          "proximal" : 43, "middle" : 30, "radius" : 8.4 },
        { "name" : "little", "x" : 79, "y" : 31, "z" : 70,
          "proximal" : 43, "middle" : 33, "radius" : 7.2 }
    ];
    for (var finger in fingers)
    {
        const root = vector(finger.x, finger.y, finger.z) * millimeter;
        const tipRadius = finger.radius * 0.74 * millimeter;
        const contactX = 137.1 * millimeter + tipRadius - stroke;
        const distalJointX = 137.1 * millimeter + finger.radius * 0.80 * millimeter - stroke;
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
            [vector(47, -30, 70) * millimeter,
             vector(64, -49, 70) * millimeter,
             vector(85, -68, 69) * millimeter,
             vector(101, -71, 68) * millimeter],
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
                "value" : "Illustrative adult-sized hand pulling a 20 mm climbing recess against the forward face of the rounded palm bolster. Fixed-length finger links follow the 0-30 mm stroke. Not anthropometric validation, a physical clearance guarantee, or a manufactured component."
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

export function auditFingerworkerCollisions(context is Context,
                                            modelFeatureId is Id) returns array
{
    const carriage = qCreatedBy(modelFeatureId + "carriageBridge", EntityType.BODY);
    const rods = qUnion([
                qCreatedBy(modelFeatureId + "springGuideLong1", EntityType.BODY),
                qCreatedBy(modelFeatureId + "springGuideLong2", EntityType.BODY)
            ]);
    const springs = qUnion([
                qCreatedBy(modelFeatureId + "springLong1" + "sweep", EntityType.BODY),
                qCreatedBy(modelFeatureId + "springLong2" + "sweep", EntityType.BODY)
            ]);
    const palmPad = qCreatedBy(modelFeatureId + "palmPad", EntityType.BODY);
    const base = qCreatedBy(modelFeatureId + "base", EntityType.BODY);
    const hand = qCreatedBy(modelFeatureId + "handReference", EntityType.BODY);
    const cushion = qCreatedBy(modelFeatureId + "palmCushion", EntityType.BODY);
    const remainingDevice = qSubtraction(
            qBodyType(qCreatedBy(modelFeatureId, EntityType.BODY), BodyType.SOLID),
            qUnion([hand, carriage, cushion]));

    // The climbing pocket is fused to the carriage. Test the full body,
    // including its lowered spring reaction pads and stop-plate recesses.
    return [
        auditSolidPair(context, "Carriage / integrated base", carriage, base, false),
        auditSolidPair(context, "Carriage / switch body and bracket", carriage,
            qUnion([qCreatedBy(modelFeatureId + "switchBracket", EntityType.BODY),
                    qCreatedBy(modelFeatureId + "switchBody", EntityType.BODY)]), false),
        auditSolidPair(context, "Carriage / switch actuator", carriage,
            qUnion([qCreatedBy(modelFeatureId + "switchLever", EntityType.BODY),
                    qCreatedBy(modelFeatureId + "switchRoller", EntityType.BODY)]), true),
        auditSolidPair(context, "Switch actuator / case and bracket",
            qUnion([qCreatedBy(modelFeatureId + "switchLever", EntityType.BODY),
                    qCreatedBy(modelFeatureId + "switchRoller", EntityType.BODY)]),
            qUnion([qCreatedBy(modelFeatureId + "switchBracket", EntityType.BODY),
                    qCreatedBy(modelFeatureId + "switchBody", EntityType.BODY)]), false),
        auditSolidPair(context, "Carriage / strike plates", carriage,
            qUnion([qCreatedBy(modelFeatureId + "strikePlateLeft", EntityType.BODY),
                    qCreatedBy(modelFeatureId + "strikePlateRight", EntityType.BODY)]), false),
        auditSolidPair(context, "Carriage / guide rods", carriage, rods, false),
        auditSolidPair(context, "Carriage / spring sweeps", carriage, springs, false),
        auditSolidPair(context, "Palm support / integrated base", palmPad, base, true),
        auditSolidPair(context, "Palm sleeve / rigid support", cushion, palmPad, true),
        auditSolidPair(context, "Hand / climbing pocket and carriage", hand, carriage, true),
        auditSolidPair(context, "Hand / palm cushion", hand, cushion, true),
        auditSolidPair(context, "Hand / remaining device", hand, remainingDevice, false)
    ];
}

annotation { "Feature Type Name" : "FingerworkerMVP", "Feature Name Template" : "Fingerworker MVP" }
export const fingerworkerMVP = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Base length" }
        isLength(definition.baseLength, LENGTH_BOUNDS);

        annotation { "Name" : "Base width" }
        isLength(definition.baseWidth, LENGTH_BOUNDS);

        annotation { "Name" : "Base thickness" }
        isLength(definition.baseThickness, LENGTH_BOUNDS);

        annotation { "Name" : "Working travel" }
        isLength(definition.travel, LENGTH_BOUNDS);

        annotation { "Name" : "Grip deck width" }
        isLength(definition.handleWidth, LENGTH_BOUNDS);

        annotation { "Name" : "Climbing lip wall" }
        isLength(definition.handleThickness, LENGTH_BOUNDS);

        annotation { "Name" : "Pocket depth" }
        isLength(definition.handleHeight, LENGTH_BOUNDS);

        annotation { "Name" : "Climbing lip radius" }
        isLength(definition.handleEdgeRadius, BLEND_BOUNDS);

        annotation { "Name" : "Guide spacing" }
        isLength(definition.guideSpacing, LENGTH_BOUNDS);

        annotation { "Name" : "Guide rail width" }
        isLength(definition.railWidth, LENGTH_BOUNDS);

        annotation { "Name" : "Guide rail height" }
        isLength(definition.railHeight, LENGTH_BOUNDS);

        annotation { "Name" : "Preview displacement (0 to working travel)" }
        isLength(definition.previewTravel, LENGTH_BOUNDS);

        annotation { "Name" : "Show hand reference (exclude from manufacturing)" }
        definition.showHand is boolean;
    }
    {
        const baseLength = definition.baseLength;
        const baseWidth = definition.baseWidth;
        const baseThickness = definition.baseThickness;
        const travel = definition.travel;
        const handleWidth = definition.handleWidth;
        const handleThickness = definition.handleThickness;
        const handleHeight = definition.handleHeight;
        const guideY = definition.guideSpacing / 2;
        const railWidth = definition.railWidth;
        const railHeight = definition.railHeight;
        const previewTravel = definition.previewTravel;
        if (previewTravel < 0 * millimeter || previewTravel > travel || travel > 30 * millimeter)
            throw regenError("Preview must be within the working travel; this hardware layout supports up to 30 mm.", ["previewTravel", "travel"]);

        const railStartX = 5 * millimeter;
        const railEndX = railStartX + 200 * millimeter;
        const blockStartX = 145 * millimeter;
        const blockEndX = blockStartX + 45.4 * millimeter;
        const bridgeStartX = 140 * millimeter;
        const bridgeEndX = 194 * millimeter;
        const bridgeBottomZ = baseThickness + railHeight + 5 * millimeter;
        const bridgeTopZ = bridgeBottomZ + 18 * millimeter;
        // The loaded inner wall remains x=137: 100 mm open from the palm
        // datum x=37, reducing to 70 mm at full travel.
        const gripContactX = 137 * millimeter;
        const deckFrontX = gripContactX - handleThickness;
        const deckRearX = 184 * millimeter;
        const pocketFloorZ = baseThickness + 27.5 * millimeter;
        const deckBottomZ = pocketFloorZ - 3 * millimeter;
        const gripTopZ = pocketFloorZ + handleHeight;
        const springStartX = 65 * millimeter;
        const springEndX = 166 * millimeter;
        const springZ = baseThickness + 13 * millimeter;
        const springY1 = -30 * millimeter;
        const springY2 = 30 * millimeter;
        const hardStopContactX = bridgeStartX - travel;
        const hardStopY = 50 * millimeter;

        // Main printed plate: 210 x 170 mm fits a 220 mm printer bed with margin.
        makeBox(context, id + "base",
                vector(0 * millimeter, -baseWidth / 2, 0 * millimeter),
                vector(baseLength, baseWidth / 2, baseThickness));
        opFillet(context, id + "exposedBaseRound", {
                    "entities" : qCreatedBy(id + "base", EntityType.EDGE),
                    "radius" : 3 * millimeter,
                    "tangentPropagation" : true
                });
        nameBody(context, qCreatedBy(id + "base", EntityType.BODY), "P01 Rounded exposed base plate 210x170x12");

        // Four M5 bench/clamp holes near the corners.
        var baseMountTools = [];
        var baseMountIndex = 0;
        for (var mountX in [10 * millimeter, baseLength - 10 * millimeter])
        {
            for (var mountY in [-75 * millimeter, 75 * millimeter])
            {
                const mountId = id + ("baseMount" ~ baseMountIndex);
                makeCylinder(context, mountId,
                        vector(mountX, mountY, -1 * millimeter),
                        vector(mountX, mountY, baseThickness + 1 * millimeter),
                        2.75 * millimeter);
                baseMountTools = append(baseMountTools, qCreatedBy(mountId, EntityType.BODY));
                baseMountIndex += 1;
            }
        }
        opBoolean(context, id + "cutBaseMounts", {
                    "targets" : qCreatedBy(id + "base", EntityType.BODY),
                    "tools" : qUnion(baseMountTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Adjustable palm support: two feet leave a center tunnel for the load cell.
        makeBox(context, id + "palmFootLeft",
                vector(12 * millimeter, -62 * millimeter, baseThickness - 0.2 * millimeter),
                vector(39 * millimeter, -40 * millimeter, baseThickness + 27 * millimeter));
        makeBox(context, id + "palmFootRight",
                vector(12 * millimeter, 40 * millimeter, baseThickness - 0.2 * millimeter),
                vector(39 * millimeter, 62 * millimeter, baseThickness + 27 * millimeter));
        nameBody(context, qCreatedBy(id + "palmFootLeft", EntityType.BODY), "P02 Palm stop left support");
        nameBody(context, qCreatedBy(id + "palmFootRight", EntityType.BODY), "P03 Palm stop right support");

        // A rounded transverse reaction bolster takes the pull into the palm.
        // Its finished front remains x37; its crown is level with the edge frame.
        const palmCenterX = 26.75 * millimeter;
        const palmCenterZ = gripTopZ - 10.25 * millimeter;
        const palmPlateTopZ = baseThickness + 32 * millimeter;
        makeBox(context, id + "palmPad",
                vector(10 * millimeter, -64 * millimeter, baseThickness + 27 * millimeter),
                vector(37 * millimeter, 64 * millimeter, palmPlateTopZ));
        opFillet(context, id + "palmPlateCorners", {
                    "entities" : qParallelEdges(qCreatedBy(id + "palmPad", EntityType.EDGE), vector(0, 0, 1)),
                    "radius" : 2 * millimeter,
                    "tangentPropagation" : true
                });
        makeCylinder(context, id + "palmBolsterCore",
                vector(palmCenterX, -58 * millimeter, palmCenterZ),
                vector(palmCenterX, 58 * millimeter, palmCenterZ), 7.75 * millimeter);
        opFillet(context, id + "palmCoreEndRound", {
                    "entities" : qCreatedBy(id + "palmBolsterCore", EntityType.EDGE),
                    "radius" : 2 * millimeter,
                    "tangentPropagation" : true
                });
        opBoolean(context, id + "joinPalmBolster", {
                    "tools" : qUnion([qCreatedBy(id + "palmPad", EntityType.BODY),
                                        qCreatedBy(id + "palmBolsterCore", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });
        nameBody(context, qCreatedBy(id + "palmPad", EntityType.BODY), "P04 Rounded palm reaction bolster - level with climbing edge");

        // Four M4 heat-set inserts in the supports and matching counterbored
        // clearance holes make the palm pad removable without hidden nuts.
        var palmInsertTools = [];
        var palmPadHoleTools = [];
        var palmPadCounterboreTools = [];
        var palmMountIndex = 0;
        for (var palmX in [20 * millimeter, 32 * millimeter])
        {
            for (var palmY in [-51 * millimeter, 51 * millimeter])
            {
                const palmInsertId = id + ("palmInsert" ~ palmMountIndex);
                makeCylinder(context, palmInsertId,
                        vector(palmX, palmY, baseThickness + 20 * millimeter),
                        vector(palmX, palmY, baseThickness + 28 * millimeter), 2.6 * millimeter);
                palmInsertTools = append(palmInsertTools, qCreatedBy(palmInsertId, EntityType.BODY));

                const palmHoleId = id + ("palmPadHole" ~ palmMountIndex);
                makeCylinder(context, palmHoleId,
                        vector(palmX, palmY, baseThickness + 26 * millimeter),
                        vector(palmX, palmY, gripTopZ + 1 * millimeter), 2.2 * millimeter);
                palmPadHoleTools = append(palmPadHoleTools, qCreatedBy(palmHoleId, EntityType.BODY));

                const palmCounterboreId = id + ("palmPadCounterbore" ~ palmMountIndex);
                makeCylinder(context, palmCounterboreId,
                        vector(palmX, palmY, baseThickness + 31 * millimeter),
                        vector(palmX, palmY, gripTopZ + 1 * millimeter), 4 * millimeter);
                palmPadCounterboreTools = append(palmPadCounterboreTools, qCreatedBy(palmCounterboreId, EntityType.BODY));
                palmMountIndex += 1;
            }
        }
        opBoolean(context, id + "cutPalmInserts", {
                    "targets" : qUnion([
                                qCreatedBy(id + "palmFootLeft", EntityType.BODY),
                                qCreatedBy(id + "palmFootRight", EntityType.BODY)
                            ]),
                    "tools" : qUnion(palmInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutPalmPadMounts", {
                    "targets" : qCreatedBy(id + "palmPad", EntityType.BODY),
                    "tools" : qUnion(palmPadHoleTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutPalmPadCounterbores", {
                    "targets" : qCreatedBy(id + "palmPad", EntityType.BODY),
                    "tools" : qUnion(palmPadCounterboreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Removable 2.5 mm C-shaped soft sleeve on the load-bearing front
        // and crown. The lower opening clears the mounting plate by 0.1 mm;
        // its ends stop inside the screw wells, keeping them accessible.
        makeCylinder(context, id + "palmCushion",
                vector(palmCenterX, -43 * millimeter, palmCenterZ),
                vector(palmCenterX, 43 * millimeter, palmCenterZ), 10.25 * millimeter);
        opFillet(context, id + "palmSleeveEndRound", {
                    "entities" : qCreatedBy(id + "palmCushion", EntityType.EDGE),
                    "radius" : 1.2 * millimeter,
                    "tangentPropagation" : true
                });
        makeCylinder(context, id + "palmSleeveCoreTool",
                vector(palmCenterX, -44 * millimeter, palmCenterZ),
                vector(palmCenterX, 44 * millimeter, palmCenterZ), 7.75 * millimeter);
        makeBox(context, id + "palmSleeveBottomTool",
                vector(0 * millimeter, -45 * millimeter, 0 * millimeter),
                vector(45 * millimeter, 45 * millimeter, palmPlateTopZ + 0.1 * millimeter));
        opBoolean(context, id + "hollowPalmSleeve", {
                    "targets" : qCreatedBy(id + "palmCushion", EntityType.BODY),
                    "tools" : qUnion([qCreatedBy(id + "palmSleeveCoreTool", EntityType.BODY),
                                        qCreatedBy(id + "palmSleeveBottomTool", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "palmCushion", EntityType.BODY), "P13 Rounded 2.5 mm palm reaction sleeve");

        // Dold MGN12R rails, nominal 200 mm.
        makeBox(context, id + "railLeft",
                vector(railStartX, -guideY - railWidth / 2, baseThickness),
                vector(railEndX, -guideY + railWidth / 2, baseThickness + railHeight));
        makeBox(context, id + "railRight",
                vector(railStartX, guideY - railWidth / 2, baseThickness),
                vector(railEndX, guideY + railWidth / 2, baseThickness + railHeight));
        nameBody(context, qCreatedBy(id + "railLeft", EntityType.BODY), "H01 Dold MGN12R-200 left");
        nameBody(context, qCreatedBy(id + "railRight", EntityType.BODY), "H02 Dold MGN12R-200 right");

        // Eight M3 rail holes at 25 mm pitch, 12.5 mm from each rail end.
        var railThroughTools = [];
        var railCounterboreTools = [];
        var railInsertTools = [];
        var railHoleCounter = 0;
        for (var holeIndex = 0; holeIndex < 8; holeIndex += 1)
        {
            const holeX = railStartX + (12.5 + holeIndex * 25) * millimeter;
            for (var railY in [-guideY, guideY])
            {
                const railHoleId = id + ("railHole" ~ railHoleCounter);
                makeCylinder(context, railHoleId,
                        vector(holeX, railY, -1 * millimeter),
                        vector(holeX, railY, baseThickness + railHeight + 1 * millimeter),
                        1.7 * millimeter);
                railThroughTools = append(railThroughTools, qCreatedBy(railHoleId, EntityType.BODY));

                const insertId = id + ("railInsert" ~ railHoleCounter);
                makeCylinder(context, insertId,
                        vector(holeX, railY, baseThickness - 6.5 * millimeter),
                        vector(holeX, railY, baseThickness + 1 * millimeter),
                        2.3 * millimeter);
                railInsertTools = append(railInsertTools, qCreatedBy(insertId, EntityType.BODY));

                const counterboreId = id + ("railCounterbore" ~ railHoleCounter);
                makeCylinder(context, counterboreId,
                        vector(holeX, railY, baseThickness + 3 * millimeter),
                        vector(holeX, railY, baseThickness + railHeight + 1 * millimeter),
                        3 * millimeter);
                railCounterboreTools = append(railCounterboreTools, qCreatedBy(counterboreId, EntityType.BODY));
                railHoleCounter += 1;
            }
        }
        opBoolean(context, id + "cutRailThroughHoles", {
                    "targets" : qUnion([
                                qCreatedBy(id + "railLeft", EntityType.BODY),
                                qCreatedBy(id + "railRight", EntityType.BODY)
                            ]),
                    "tools" : qUnion(railThroughTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutRailInsertPockets", {
                    "targets" : qCreatedBy(id + "base", EntityType.BODY),
                    "tools" : qUnion(railInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutRailCounterbores", {
                    "targets" : qUnion([
                                qCreatedBy(id + "railLeft", EntityType.BODY),
                                qCreatedBy(id + "railRight", EntityType.BODY)
                            ]),
                    "tools" : qUnion(railCounterboreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Two Dold MGN12H long blocks, 45.4 x 27 x 13 mm nominal envelope.
        makeBox(context, id + "blockLeft",
                vector(blockStartX, -guideY - 13.5 * millimeter, baseThickness + 3 * millimeter),
                vector(blockEndX, -guideY + 13.5 * millimeter, baseThickness + 13 * millimeter));
        makeBox(context, id + "blockRight",
                vector(blockStartX, guideY - 13.5 * millimeter, baseThickness + 3 * millimeter),
                vector(blockEndX, guideY + 13.5 * millimeter, baseThickness + 13 * millimeter));
        nameBody(context, qCreatedBy(id + "blockLeft", EntityType.BODY), "H03 Dold MGN12H left");
        nameBody(context, qCreatedBy(id + "blockRight", EntityType.BODY), "H04 Dold MGN12H right");

        // Printed moving bridge with the MGN12H 20 x 20 mm mounting pattern.
        makeBox(context, id + "carriageBridge",
                vector(bridgeStartX, -82.5 * millimeter, bridgeBottomZ),
                vector(bridgeEndX, 82.5 * millimeter, bridgeTopZ));
        nameBody(context, qCreatedBy(id + "carriageBridge", EntityType.BODY), "P05 Carriage bridge for 2x MGN12H");

        // Lower reaction pads support the complete washer annulus after
        // lowering the spring axis by 6 mm. Subsequent bores cut these too.
        var reactionBodies = [qCreatedBy(id + "carriageBridge", EntityType.BODY)];
        var reactionIndex = 0;
        for (var reactionY in [springY1, springY2])
        {
            const reactionId = id + ("reactionPad" ~ reactionIndex);
            makeBox(context, reactionId,
                    vector(165.5 * millimeter, reactionY - 12 * millimeter, baseThickness + 1 * millimeter),
                    vector(bridgeEndX, reactionY + 12 * millimeter, bridgeTopZ));
            reactionBodies = append(reactionBodies, qCreatedBy(reactionId, EntityType.BODY));
            reactionIndex += 1;
        }
        opBoolean(context, id + "joinReactionPads", {
                    "tools" : qUnion(reactionBodies),
                    "operationType" : BooleanOperationType.UNION
                });

        var bridgeHoleTools = [];
        var bridgeCounterboreTools = [];
        var bridgeHoleIndex = 0;
        const blockCenterX = (blockStartX + blockEndX) / 2;
        for (var blockCenterY in [-guideY, guideY])
        {
            for (var holeOffsetX in [-10 * millimeter, 10 * millimeter])
            {
                for (var holeOffsetY in [-10 * millimeter, 10 * millimeter])
                {
                    const bridgeHoleId = id + ("bridgeHole" ~ bridgeHoleIndex);
                    makeCylinder(context, bridgeHoleId,
                            vector(blockCenterX + holeOffsetX, blockCenterY + holeOffsetY, bridgeBottomZ - 1 * millimeter),
                            vector(blockCenterX + holeOffsetX, blockCenterY + holeOffsetY, bridgeTopZ + 1 * millimeter),
                            1.7 * millimeter);
                    bridgeHoleTools = append(bridgeHoleTools, qCreatedBy(bridgeHoleId, EntityType.BODY));

                    const bridgeCounterboreId = id + ("bridgeCounterbore" ~ bridgeHoleIndex);
                    makeCylinder(context, bridgeCounterboreId,
                            vector(blockCenterX + holeOffsetX, blockCenterY + holeOffsetY, bridgeBottomZ + 6 * millimeter),
                            vector(blockCenterX + holeOffsetX, blockCenterY + holeOffsetY, bridgeTopZ + 1 * millimeter),
                            3.2 * millimeter);
                    bridgeCounterboreTools = append(bridgeCounterboreTools, qCreatedBy(bridgeCounterboreId, EntityType.BODY));
                    bridgeHoleIndex += 1;
                }
            }
        }
        opBoolean(context, id + "cutBridgeHoles", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(bridgeHoleTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutBridgeCounterbores", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(bridgeCounterboreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Total-force path: floating spring anchor -> centered steel pusher ->
        // TE Connectivity FX1901 200 lbf compression cell -> fixed wall.
        // The 889.6 N full-scale range leaves useful headroom above the 500 N MVP limit.
        const loadCellBackX = 41 * millimeter;
        const loadCellFrontX = loadCellBackX + 5.45 * millimeter;
        const loadCellCenterZ = baseThickness + 13 * millimeter;

        makeBox(context, id + "loadCellWall",
                vector(29 * millimeter, -27 * millimeter, baseThickness - 0.2 * millimeter),
                vector(48.5 * millimeter, 27 * millimeter, baseThickness + 26 * millimeter));
        makeBox(context, id + "loadCellGussetNeg",
                vector(20 * millimeter, -29 * millimeter, baseThickness - 0.2 * millimeter),
                vector(loadCellBackX, -18 * millimeter, baseThickness + 25 * millimeter));
        makeBox(context, id + "loadCellGussetPos",
                vector(20 * millimeter, 18 * millimeter, baseThickness - 0.2 * millimeter),
                vector(loadCellBackX, 29 * millimeter, baseThickness + 25 * millimeter));

        // Leave a compact 25 x 25 mm front boss on the wall, then form a
        // Ø20.2 mm locating pocket with 0.225 mm nominal radial clearance.
        makeBox(context, id + "loadCellTrimYNeg",
                vector(loadCellBackX, -28 * millimeter, baseThickness - 1 * millimeter),
                vector(49 * millimeter, -12.5 * millimeter, baseThickness + 40 * millimeter));
        makeBox(context, id + "loadCellTrimYPos",
                vector(loadCellBackX, 12.5 * millimeter, baseThickness - 1 * millimeter),
                vector(49 * millimeter, 28 * millimeter, baseThickness + 40 * millimeter));
        makeBox(context, id + "loadCellTrimZLow",
                vector(loadCellBackX, -12.5 * millimeter, baseThickness - 1 * millimeter),
                vector(49 * millimeter, 12.5 * millimeter, loadCellCenterZ - 12.5 * millimeter));
        makeBox(context, id + "loadCellTrimZHigh",
                vector(loadCellBackX, -12.5 * millimeter, loadCellCenterZ + 12.5 * millimeter),
                vector(49 * millimeter, 12.5 * millimeter, baseThickness + 40 * millimeter));
        opBoolean(context, id + "shapeLoadCellPocketBoss", {
                    "targets" : qCreatedBy(id + "loadCellWall", EntityType.BODY),
                    "tools" : qUnion([
                                qCreatedBy(id + "loadCellTrimYNeg", EntityType.BODY),
                                qCreatedBy(id + "loadCellTrimYPos", EntityType.BODY),
                                qCreatedBy(id + "loadCellTrimZLow", EntityType.BODY),
                                qCreatedBy(id + "loadCellTrimZHigh", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        makeCylinder(context, id + "loadCellPocketCavity",
                vector(loadCellBackX, 0 * millimeter, loadCellCenterZ),
                vector(48.6 * millimeter, 0 * millimeter, loadCellCenterZ), 10.1 * millimeter);
        makeBox(context, id + "loadCellCableNotch",
                vector(loadCellBackX, 7.5 * millimeter, loadCellCenterZ - 3.5 * millimeter),
                vector(48.6 * millimeter, 28 * millimeter, loadCellCenterZ + 3.5 * millimeter));
        opBoolean(context, id + "cutLoadCellPocket", {
                    "targets" : qCreatedBy(id + "loadCellWall", EntityType.BODY),
                    "tools" : qUnion([
                                qCreatedBy(id + "loadCellPocketCavity", EntityType.BODY),
                                qCreatedBy(id + "loadCellCableNotch", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // TE specifies that the rear face may be supported only on the outer
        // force-support rim. This relief keeps the four delicate rear bumps free.
        makeCylinder(context, id + "loadCellBackRelief",
                vector(loadCellBackX - 1.6 * millimeter, 0 * millimeter, loadCellCenterZ),
                vector(loadCellBackX + 0.2 * millimeter, 0 * millimeter, loadCellCenterZ),
                7.5 * millimeter);
        opBoolean(context, id + "cutLoadCellBackRelief", {
                    "targets" : qCreatedBy(id + "loadCellWall", EntityType.BODY),
                    "tools" : qCreatedBy(id + "loadCellBackRelief", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "loadCellWall", EntityType.BODY), "P06 FX1901 reaction wall and locating pocket");

        // Catalogue geometry of FX1901-0001-0200-L, including the central
        // compression boss and a shortened representation of its 4-wire cable.
        makeCylinder(context, id + "loadCell",
                vector(loadCellBackX, 0 * millimeter, loadCellCenterZ),
                vector(loadCellFrontX, 0 * millimeter, loadCellCenterZ), 9.875 * millimeter);
        makeCylinder(context, id + "loadCellBoss",
                vector(loadCellFrontX, 0 * millimeter, loadCellCenterZ),
                vector(loadCellFrontX + 0.65 * millimeter, 0 * millimeter, loadCellCenterZ), 2.5 * millimeter);
        makeBox(context, id + "loadCellOvermold",
                vector(42 * millimeter, 8 * millimeter, loadCellCenterZ - 2.5 * millimeter),
                vector(45.5 * millimeter, 14 * millimeter, loadCellCenterZ + 2.5 * millimeter));
        makeCylinder(context, id + "loadCellCable",
                vector(43.75 * millimeter, 8.5 * millimeter, loadCellCenterZ),
                vector(43.75 * millimeter, 50 * millimeter, loadCellCenterZ), 1.2 * millimeter);
        makeBox(context, id + "loadCellConnector",
                vector(40.75 * millimeter, 47.5 * millimeter, loadCellCenterZ - 3 * millimeter),
                vector(46.75 * millimeter, 55.5 * millimeter, loadCellCenterZ + 3 * millimeter));
        nameBody(context, qCreatedBy(id + "loadCell", EntityType.BODY), "H05 TE FX1901-0001-0200-L 200 lbf load cell");
        nameBody(context, qCreatedBy(id + "loadCellBoss", EntityType.BODY), "H05a FX1901 center force boss");
        nameBody(context, qCreatedBy(id + "loadCellOvermold", EntityType.BODY), "H05b FX1901 cable overmold");
        nameBody(context, qCreatedBy(id + "loadCellCable", EntityType.BODY), "H05c FX1901 four-wire cable");
        nameBody(context, qCreatedBy(id + "loadCellConnector", EntityType.BODY), "H05d FX1901 Molex connector");

        makeCylinder(context, id + "loadPusher",
                vector(loadCellFrontX + 0.65 * millimeter, 0 * millimeter, loadCellCenterZ),
                vector(55 * millimeter, 0 * millimeter, loadCellCenterZ), 2 * millimeter);
        nameBody(context, qCreatedBy(id + "loadPusher", EntityType.BODY), "H06 Centered 4 mm steel load-cell pusher");

        makeBox(context, id + "springAnchor",
                vector(55 * millimeter, -48 * millimeter, baseThickness),
                vector(springStartX, 48 * millimeter, baseThickness + 27 * millimeter));
        nameBody(context, qCreatedBy(id + "springAnchor", EntityType.BODY), "P07 Shared spring anchor");

        // Two norelem 26000-1608102 ISO 10243 springs: 1 mm preload plus 30 mm
        // stroke at 7.8 N/mm each gives 483.6 N total (about 49.3 kgf).
        makeCompressionSpring(context, id + "springLong1", springStartX, springEndX - previewTravel, springY1, springZ);
        makeCompressionSpring(context, id + "springLong2", springStartX, springEndX - previewTravel, springY2, springZ);
        nameBody(context, qCreatedBy(id + "springLong1" + "sweep", EntityType.BODY), "H07 norelem 26000-1608102 spring left");
        nameBody(context, qCreatedBy(id + "springLong2" + "sweep", EntityType.BODY), "H08 norelem 26000-1608102 spring right");

        // Readily available Ø6 mm steel mandrels prevent spring buckling without
        // binding in the springs' nominal Ø8 mm bore. Ø6.6 mm printed bores give
        // 0.3 mm radial FDM clearance through anchor, seats and bridge.
        makeCylinder(context, id + "springGuideLong1",
                vector(49 * millimeter, springY1, springZ),
                vector(175 * millimeter, springY1, springZ), 3 * millimeter);
        makeCylinder(context, id + "springGuideLong2",
                vector(49 * millimeter, springY2, springZ),
                vector(175 * millimeter, springY2, springZ), 3 * millimeter);
        nameBody(context, qCreatedBy(id + "springGuideLong1", EntityType.BODY), "H09 Spring guide rod dia 6 x 126 left");
        nameBody(context, qCreatedBy(id + "springGuideLong2", EntityType.BODY), "H10 Spring guide rod dia 6 x 126 right");

        // Fixed printed rod sockets key into the base. The Ø6.2 mm bores provide
        // a light reamed/adhesive fit. A 1.5 mm axial gap to the floating anchor
        // prevents the sockets from bypassing the load-cell force path.
        makeBox(context, id + "springGuideSocket1",
                vector(48 * millimeter, springY1 - 8 * millimeter, baseThickness - 0.2 * millimeter),
                vector(53.5 * millimeter, springY1 + 8 * millimeter, springZ + 8 * millimeter));
        makeBox(context, id + "springGuideSocket2",
                vector(48 * millimeter, springY2 - 8 * millimeter, baseThickness - 0.2 * millimeter),
                vector(53.5 * millimeter, springY2 + 8 * millimeter, springZ + 8 * millimeter));
        var springSocketBoreTools = [];
        var springSocketBoreIndex = 0;
        for (var socketY in [springY1, springY2])
        {
            const socketBoreId = id + ("springSocketBore" ~ springSocketBoreIndex);
            makeCylinder(context, socketBoreId,
                    vector(47 * millimeter, socketY, springZ),
                    vector(54.5 * millimeter, socketY, springZ), 3.1 * millimeter);
            springSocketBoreTools = append(springSocketBoreTools, qCreatedBy(socketBoreId, EntityType.BODY));
            springSocketBoreIndex += 1;
        }
        opBoolean(context, id + "cutSpringSocketBores", {
                    "targets" : qUnion([
                                qCreatedBy(id + "springGuideSocket1", EntityType.BODY),
                                qCreatedBy(id + "springGuideSocket2", EntityType.BODY)
                            ]),
                    "tools" : qUnion(springSocketBoreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Replaceable steel spring seats / large washers.
        makeCylinder(context, id + "fixedSeat1", vector(62 * millimeter, springY1, springZ), vector(springStartX, springY1, springZ), 11 * millimeter);
        makeCylinder(context, id + "fixedSeat2", vector(62 * millimeter, springY2, springZ), vector(springStartX, springY2, springZ), 11 * millimeter);
        makeCylinder(context, id + "movingSeat1", vector(springEndX, springY1, springZ), vector(springEndX + 3 * millimeter, springY1, springZ), 11 * millimeter);
        makeCylinder(context, id + "movingSeat2", vector(springEndX, springY2, springZ), vector(springEndX + 3 * millimeter, springY2, springZ), 11 * millimeter);
        nameBody(context, qCreatedBy(id + "fixedSeat1", EntityType.BODY), "H11 Fixed spring seat left");
        nameBody(context, qCreatedBy(id + "fixedSeat2", EntityType.BODY), "H12 Fixed spring seat right");
        nameBody(context, qCreatedBy(id + "movingSeat1", EntityType.BODY), "H13 Moving spring seat left");
        nameBody(context, qCreatedBy(id + "movingSeat2", EntityType.BODY), "H14 Moving spring seat right");

        var fixedSeatPocketTools = [];
        var movingSeatPocketTools = [];
        var seatPocketIndex = 0;
        for (var seatPocketY in [springY1, springY2])
        {
            const fixedPocketId = id + ("fixedSeatPocket" ~ seatPocketIndex);
            makeCylinder(context, fixedPocketId,
                    vector(61.8 * millimeter, seatPocketY, springZ),
                    vector(65.2 * millimeter, seatPocketY, springZ), 11.2 * millimeter);
            fixedSeatPocketTools = append(fixedSeatPocketTools, qCreatedBy(fixedPocketId, EntityType.BODY));

            const movingPocketId = id + ("movingSeatPocket" ~ seatPocketIndex);
            makeCylinder(context, movingPocketId,
                    vector(springEndX - 0.2 * millimeter, seatPocketY, springZ),
                    vector(springEndX + 3.2 * millimeter, seatPocketY, springZ), 11.2 * millimeter);
            movingSeatPocketTools = append(movingSeatPocketTools, qCreatedBy(movingPocketId, EntityType.BODY));
            seatPocketIndex += 1;
        }
        opBoolean(context, id + "cutFixedSeatPockets", {
                    "targets" : qCreatedBy(id + "springAnchor", EntityType.BODY),
                    "tools" : qUnion(fixedSeatPocketTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutMovingSeatPockets", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(movingSeatPocketTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Spring envelopes need clearance through the bridge BEFORE the seat.
        // This forms two open-bottom tunnels; the rear shoulder still carries
        // the steel seats. Ø17.2 gives 0.6 mm radial clearance to the Ø16 spring.
        var springTunnelTools = [];
        var springTunnelIndex = 0;
        for (var tunnelY in [springY1, springY2])
        {
            const tunnelId = id + ("springTunnel" ~ springTunnelIndex);
            makeCylinder(context, tunnelId,
                    vector(bridgeStartX - 1 * millimeter, tunnelY, springZ),
                    vector(springEndX + 0.2 * millimeter, tunnelY, springZ), 8.6 * millimeter);
            springTunnelTools = append(springTunnelTools, qCreatedBy(tunnelId, EntityType.BODY));
            springTunnelIndex += 1;
        }
        opBoolean(context, id + "cutSpringTunnels", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(springTunnelTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        var springGuideBoreTools = [];
        var springGuideBoreIndex = 0;
        for (var guideBoreY in [springY1, springY2])
        {
            const guideBoreId = id + ("springGuideBore" ~ springGuideBoreIndex);
            makeCylinder(context, guideBoreId,
                    vector(51 * millimeter, guideBoreY, springZ),
                    vector(bridgeEndX + 1 * millimeter, guideBoreY, springZ), 3.3 * millimeter);
            springGuideBoreTools = append(springGuideBoreTools, qCreatedBy(guideBoreId, EntityType.BODY));
            springGuideBoreIndex += 1;
        }
        opBoolean(context, id + "cutSpringGuideBores", {
                    "targets" : qUnion([
                                qCreatedBy(id + "springAnchor", EntityType.BODY),
                                qCreatedBy(id + "fixedSeat1", EntityType.BODY),
                                qCreatedBy(id + "fixedSeat2", EntityType.BODY),
                                qCreatedBy(id + "movingSeat1", EntityType.BODY),
                                qCreatedBy(id + "movingSeat2", EntityType.BODY),
                                qCreatedBy(id + "carriageBridge", EntityType.BODY)
                            ]),
                    "tools" : qUnion(springGuideBoreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Four low side cheeks retain the nominal open position without
        // obstructing the rail or its last mounting screw. Replaceable 1 mm
        // elastomer faces soften contact with the rear of each guide block.
        var returnStopIndex = 0;
        var returnStopBodies = [];
        for (var returnRailY in [-guideY, guideY])
        {
            for (var returnOffsetY in [-10 * millimeter, 10 * millimeter])
            {
                const returnY = returnRailY + returnOffsetY;
                const returnStopId = id + ("returnStopEar" ~ returnStopIndex);
                makeBox(context, returnStopId,
                        vector(blockEndX + 1 * millimeter, returnY - 3 * millimeter, baseThickness - 0.2 * millimeter),
                        vector(204 * millimeter, returnY + 3 * millimeter, baseThickness + 12.5 * millimeter));

                returnStopBodies = append(returnStopBodies, qCreatedBy(returnStopId, EntityType.BODY));
                const returnBumperId = id + ("returnBumperPad" ~ returnStopIndex);
                makeBox(context, returnBumperId,
                        vector(blockEndX, returnY - 3 * millimeter, baseThickness + 3 * millimeter),
                        vector(blockEndX + 1 * millimeter, returnY + 3 * millimeter, baseThickness + 12.5 * millimeter));
                nameBody(context, qCreatedBy(returnBumperId, EntityType.BODY),
                        "H22 Return-stop elastomer bumper " ~ (returnStopIndex + 1));
                finishBody(context, qCreatedBy(returnBumperId, EntityType.BODY), color(0.18, 0.20, 0.21));
                returnStopIndex += 1;
            }
        }

        // Adjustable M6 hard stops define the 30 mm working stroke.
        makeBox(context, id + "hardStopLeft",
                vector(hardStopContactX - 15 * millimeter, -hardStopY - 8 * millimeter, baseThickness - 0.2 * millimeter),
                vector(hardStopContactX - 5 * millimeter, -hardStopY + 8 * millimeter, baseThickness + 30 * millimeter));
        makeBox(context, id + "hardStopRight",
                vector(hardStopContactX - 15 * millimeter, hardStopY - 8 * millimeter, baseThickness - 0.2 * millimeter),
                vector(hardStopContactX - 5 * millimeter, hardStopY + 8 * millimeter, baseThickness + 30 * millimeter));

        var stopInsertTools = [];
        var stopInsertIndex = 0;
        for (var stopInsertY in [-hardStopY, hardStopY])
        {
            const stopInsertId = id + ("stopInsert" ~ stopInsertIndex);
            makeCylinder(context, stopInsertId,
                    vector(hardStopContactX - 16 * millimeter, stopInsertY, baseThickness + 20 * millimeter),
                    vector(hardStopContactX - 4 * millimeter, stopInsertY, baseThickness + 20 * millimeter),
                    4.2 * millimeter);
            stopInsertTools = append(stopInsertTools, qCreatedBy(stopInsertId, EntityType.BODY));
            stopInsertIndex += 1;
        }
        opBoolean(context, id + "cutStopInsertPockets", {
                    "targets" : qUnion([
                                qCreatedBy(id + "hardStopLeft", EntityType.BODY),
                                qCreatedBy(id + "hardStopRight", EntityType.BODY)
                            ]),
                    "tools" : qUnion(stopInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        makeCylinder(context, id + "stopScrewLeft",
                vector(hardStopContactX - 5 * millimeter, -hardStopY, baseThickness + 20 * millimeter),
                vector(hardStopContactX, -hardStopY, baseThickness + 20 * millimeter), 3 * millimeter);
        makeCylinder(context, id + "stopScrewRight",
                vector(hardStopContactX - 5 * millimeter, hardStopY, baseThickness + 20 * millimeter),
                vector(hardStopContactX, hardStopY, baseThickness + 20 * millimeter), 3 * millimeter);
        nameBody(context, qCreatedBy(id + "hardStopLeft", EntityType.BODY), "P08 Left hard-stop bracket");
        nameBody(context, qCreatedBy(id + "hardStopRight", EntityType.BODY), "P09 Right hard-stop bracket");
        nameBody(context, qCreatedBy(id + "stopScrewLeft", EntityType.BODY), "H15 M6 adjustable stop left");
        nameBody(context, qCreatedBy(id + "stopScrewRight", EntityType.BODY), "H16 M6 adjustable stop right");

        // Two replaceable 2 mm steel strike plates protect the printed bridge.
        makeBox(context, id + "strikePlateLeft",
                vector(bridgeStartX, -hardStopY - 4 * millimeter, bridgeBottomZ),
                vector(bridgeStartX + 2 * millimeter, -hardStopY + 4 * millimeter, bridgeBottomZ + 13.5 * millimeter));
        makeBox(context, id + "strikePlateRight",
                vector(bridgeStartX, hardStopY - 4 * millimeter, bridgeBottomZ),
                vector(bridgeStartX + 2 * millimeter, hardStopY + 4 * millimeter, bridgeBottomZ + 13.5 * millimeter));
        nameBody(context, qCreatedBy(id + "strikePlateLeft", EntityType.BODY), "H20 Steel strike plate left");
        nameBody(context, qCreatedBy(id + "strikePlateRight", EntityType.BODY), "H21 Steel strike plate right");

        // Omron SS-01GL2 micro-load roller-lever switch. Its envelope and 9.5 mm
        // mounting pattern are identical to SS-5GL2, but its contacts are suited
        // to an electronic input. Two M3 slots provide +/-2 mm click adjustment.
        // Keep the manufacturer's free-to-operating motion: nominal click
        // is about 1 mm before the hard stop. Slots permit physical calibration.
        const switchBaseX = hardStopContactX - 16 * millimeter;
        const switchCenterY = 0 * millimeter;
        const switchBodyZ = baseThickness;

        // Printable right-angle bracket with exact M2.3 mounting-hole locations.
        makeBox(context, id + "switchBracket",
                vector(switchBaseX - 3 * millimeter, switchCenterY - 11 * millimeter, baseThickness),
                vector(switchBaseX + 11.7 * millimeter, switchCenterY + 4 * millimeter, switchBodyZ + 19.5 * millimeter));
        makeBox(context, id + "switchBracketCavity",
                vector(switchBaseX - 4 * millimeter, switchCenterY - 3.5 * millimeter, baseThickness + 3.5 * millimeter),
                vector(switchBaseX + 12.7 * millimeter, switchCenterY + 5 * millimeter, switchBodyZ + 20.5 * millimeter));
        opBoolean(context, id + "shapeSwitchBracket", {
                    "targets" : qCreatedBy(id + "switchBracket", EntityType.BODY),
                    "tools" : qCreatedBy(id + "switchBracketCavity", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Accessible mounting foot: slots sit beside the switch, not underneath it.
        makeBox(context, id + "switchAccessibleFoot",
                vector(switchBaseX - 5.2 * millimeter, -11 * millimeter, baseThickness),
                vector(switchBaseX + 17 * millimeter, 11 * millimeter, baseThickness + 3.5 * millimeter));
        opBoolean(context, id + "joinSwitchAccessibleFoot", {
                    "tools" : qUnion([qCreatedBy(id + "switchBracket", EntityType.BODY),
                                      qCreatedBy(id + "switchAccessibleFoot", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });
        // Seat the switch at base level while retaining full thickness under
        // the side mounting screws. The recess also clears the actuator root.
        makeBox(context, id + "switchCaseSeat",
                vector(switchBaseX - 0.2 * millimeter, -3.4 * millimeter, baseThickness - 0.2 * millimeter),
                vector(switchBaseX + 13.2 * millimeter, 3.4 * millimeter, baseThickness + 4 * millimeter));
        opBoolean(context, id + "cutSwitchCaseSeat", {
                    "targets" : qCreatedBy(id + "switchBracket", EntityType.BODY),
                    "tools" : qCreatedBy(id + "switchCaseSeat", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        const switchMountY = switchCenterY + 7.5 * millimeter;

        var switchBaseSlotTools = [];
        var switchBaseInsertTools = [];
        var switchBaseMountIndex = 0;
        for (var switchBaseMountX in [switchBaseX + 1 * millimeter, switchBaseX + 9.5 * millimeter])
        {
            const slotLeftId = id + ("switchBaseSlotLeft" ~ switchBaseMountIndex);
            const slotRightId = id + ("switchBaseSlotRight" ~ switchBaseMountIndex);
            const slotBridgeId = id + ("switchBaseSlotBridge" ~ switchBaseMountIndex);
            makeCylinder(context, slotLeftId,
                    vector(switchBaseMountX - 2 * millimeter, switchMountY, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX - 2 * millimeter, switchMountY, baseThickness + 5 * millimeter), 1.8 * millimeter);
            makeCylinder(context, slotRightId,
                    vector(switchBaseMountX + 2 * millimeter, switchMountY, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX + 2 * millimeter, switchMountY, baseThickness + 5 * millimeter), 1.8 * millimeter);
            makeBox(context, slotBridgeId,
                    vector(switchBaseMountX - 2 * millimeter, switchMountY - 1.8 * millimeter, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX + 2 * millimeter, switchMountY + 1.8 * millimeter, baseThickness + 5 * millimeter));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotLeftId, EntityType.BODY));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotRightId, EntityType.BODY));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotBridgeId, EntityType.BODY));

            const baseInsertId = id + ("switchBaseInsert" ~ switchBaseMountIndex);
            makeCylinder(context, baseInsertId,
                    vector(switchBaseMountX, switchMountY, baseThickness - 6.5 * millimeter),
                    vector(switchBaseMountX, switchMountY, baseThickness + 1 * millimeter), 2.3 * millimeter);
            switchBaseInsertTools = append(switchBaseInsertTools, qCreatedBy(baseInsertId, EntityType.BODY));
            switchBaseMountIndex += 1;
        }
        opBoolean(context, id + "cutSwitchBaseSlots", {
                    "targets" : qCreatedBy(id + "switchBracket", EntityType.BODY),
                    "tools" : qUnion(switchBaseSlotTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutSwitchBaseInserts", {
                    "targets" : qCreatedBy(id + "base", EntityType.BODY),
                    "tools" : qUnion(switchBaseInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        makeBox(context, id + "switchBody",
                vector(switchBaseX, switchCenterY - 3.2 * millimeter, switchBodyZ),
                vector(switchBaseX + 10.2 * millimeter, switchCenterY + 3.2 * millimeter, switchBodyZ + 19.8 * millimeter));

        var switchBracketMountTools = [];
        var switchBodyMountTools = [];
        var switchMountIndex = 0;
        for (var switchHoleZ in [switchBodyZ + 5.1 * millimeter, switchBodyZ + 14.6 * millimeter])
        {
            const switchBracketHoleId = id + ("switchBracketMountHole" ~ switchMountIndex);
            makeCylinder(context, switchBracketHoleId,
                    vector(switchBaseX + 2.5 * millimeter, switchCenterY - 12 * millimeter, switchHoleZ),
                    vector(switchBaseX + 2.5 * millimeter, switchCenterY - 2.5 * millimeter, switchHoleZ), 1.25 * millimeter);
            switchBracketMountTools = append(switchBracketMountTools, qCreatedBy(switchBracketHoleId, EntityType.BODY));

            const switchBodyHoleId = id + ("switchBodyMountHole" ~ switchMountIndex);
            makeCylinder(context, switchBodyHoleId,
                    vector(switchBaseX + 2.5 * millimeter, switchCenterY - 4 * millimeter, switchHoleZ),
                    vector(switchBaseX + 2.5 * millimeter, switchCenterY + 4 * millimeter, switchHoleZ), 1.175 * millimeter);
            switchBodyMountTools = append(switchBodyMountTools, qCreatedBy(switchBodyHoleId, EntityType.BODY));
            switchMountIndex += 1;
        }
        opBoolean(context, id + "cutSwitchBracketMounts", {
                    "targets" : qCreatedBy(id + "switchBracket", EntityType.BODY),
                    "tools" : qUnion(switchBracketMountTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutSwitchBodyMounts", {
                    "targets" : qCreatedBy(id + "switchBody", EntityType.BODY),
                    "tools" : qUnion(switchBodyMountTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Omron OP is measured from the mounting-hole datum, at baseX+2.5.
        // Nominal roller contact plane is x111 (1 mm before the hard stop).
        // OP roller center is z=bodyZ+5.1+14.5. The hinge location is an
        // approximate drawing-derived point, used only for a contact preview.
        const switchPivotX = switchBaseX + 11.5 * millimeter;
        const switchPivotZ = switchBodyZ + 2.9 * millimeter;
        const switchLeverLength = norm(vector(3.1, 0, 16.7)) * millimeter;
        const switchRollerX = min(switchBaseX + 19.4 * millimeter,
                bridgeStartX - previewTravel - 2.4 * millimeter);
        const switchLeverDX = switchRollerX - switchPivotX;
        const switchRollerZ = switchPivotZ + sqrt(switchLeverLength * switchLeverLength - switchLeverDX * switchLeverDX);
        makeCylinder(context, id + "switchLever",
                vector(switchPivotX, switchCenterY, switchPivotZ),
                vector(switchRollerX, switchCenterY, switchRollerZ), 0.45 * millimeter);
        makeCylinder(context, id + "switchRoller",
                vector(switchRollerX, switchCenterY - 1.6 * millimeter, switchRollerZ),
                vector(switchRollerX, switchCenterY + 1.6 * millimeter, switchRollerZ), 2.4 * millimeter);
        nameBody(context, qCreatedBy(id + "switchBracket", EntityType.BODY), "P10 Adjustable Omron SS-01GL2 mounting bracket");
        nameBody(context, qCreatedBy(id + "switchBody", EntityType.BODY), "H17 Omron SS-01GL2 micro-load switch");
        nameBody(context, qCreatedBy(id + "switchLever", EntityType.BODY), "H18 SS-01GL2 stainless roller lever");
        nameBody(context, qCreatedBy(id + "switchRoller", EntityType.BODY), "H19 SS-01GL2 polyacetal roller");

        // Recessed four-finger climbing pocket. Its continuous rounded lip
        // carries load directly into the bridge without elevated uprights.
        makeBox(context, id + "climbingDeck",
                vector(deckFrontX, -handleWidth / 2, deckBottomZ),
                vector(deckRearX, handleWidth / 2, gripTopZ));
        opFillet(context, id + "deckOuterRound", {
                    "entities" : qParallelEdges(qCreatedBy(id + "climbingDeck", EntityType.EDGE), vector(0, 0, 1)),
                    "radius" : 5 * millimeter,
                    "tangentPropagation" : true
                });
        opFillet(context, id + "deckTopSoftEdge", {
                    "entities" : qContainsPoint(qCreatedBy(id + "climbingDeck", EntityType.EDGE),
                            vector(deckFrontX, 0 * millimeter, gripTopZ)),
                    "radius" : 1 * millimeter,
                    "tangentPropagation" : true
                });
        opBoolean(context, id + "joinClimbingDeck", {
                    "tools" : qUnion([qCreatedBy(id + "carriageBridge", EntityType.BODY),
                                        qCreatedBy(id + "climbingDeck", EntityType.BODY)]),
                    "operationType" : BooleanOperationType.UNION
                });
        // Preserve strike-plate pockets after fusing the deck into the bridge.
        makeBox(context, id + "strikePocketLeft",
                vector(bridgeStartX - 0.2 * millimeter, -hardStopY - 4.2 * millimeter, bridgeBottomZ - 0.2 * millimeter),
                vector(bridgeStartX + 2.2 * millimeter, -hardStopY + 4.2 * millimeter, bridgeBottomZ + 13.7 * millimeter));
        makeBox(context, id + "strikePocketRight",
                vector(bridgeStartX - 0.2 * millimeter, hardStopY - 4.2 * millimeter, bridgeBottomZ - 0.2 * millimeter),
                vector(bridgeStartX + 2.2 * millimeter, hardStopY + 4.2 * millimeter, bridgeBottomZ + 13.7 * millimeter));
        opBoolean(context, id + "cutStrikePlatePockets", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion([
                                qCreatedBy(id + "strikePocketLeft", EntityType.BODY),
                                qCreatedBy(id + "strikePocketRight", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        makeBox(context, id + "climbingPocketTool",
                vector(gripContactX, -(handleWidth - 31 * millimeter) / 2, pocketFloorZ),
                vector(171 * millimeter, (handleWidth - 31 * millimeter) / 2, gripTopZ + 6 * millimeter));
        opFillet(context, id + "pocketPlanRound", {
                    "entities" : qParallelEdges(qCreatedBy(id + "climbingPocketTool", EntityType.EDGE), vector(0, 0, 1)),
                    "radius" : 8 * millimeter,
                    "tangentPropagation" : true
                });
        opBoolean(context, id + "cutClimbingPocket", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qCreatedBy(id + "climbingPocketTool", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opFillet(context, id + "climbingLipRound", {
                    "entities" : qCreatedBy(id + "cutClimbingPocket", EntityType.EDGE),
                    "radius" : definition.handleEdgeRadius,
                    "tangentPropagation" : true
                });

        // Bottom reliefs pass over the two fixed 30 mm hard-stop brackets.
        var deckStopTools = [];
        var deckStopIndex = 0;
        for (var stopY in [-hardStopY, hardStopY])
        {
            const stopReliefId = id + ("deckStopRelief" ~ deckStopIndex);
            makeBox(context, stopReliefId,
                    vector(124 * millimeter, stopY - 8.6 * millimeter, baseThickness),
                    vector(136 * millimeter, stopY + 8.6 * millimeter, 43 * millimeter));
            deckStopTools = append(deckStopTools, qCreatedBy(stopReliefId, EntityType.BODY));
            deckStopIndex += 1;
        }
        opBoolean(context, id + "cutDeckStopReliefs", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(deckStopTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Keep a screwdriver path to the four inner MGN12H mounting screws.
        var deckScrewTools = [];
        var deckScrewIndex = 0;
        for (var screwX in [blockCenterX - 10 * millimeter, blockCenterX + 10 * millimeter])
        {
            for (var screwY in [-guideY + 10 * millimeter, guideY - 10 * millimeter])
            {
                const screwId = id + ("deckScrewAccess" ~ deckScrewIndex);
                makeCylinder(context, screwId,
                        vector(screwX, screwY, bridgeBottomZ + 6 * millimeter),
                        vector(screwX, screwY, gripTopZ + 1 * millimeter), 3.2 * millimeter);
                deckScrewTools = append(deckScrewTools, qCreatedBy(screwId, EntityType.BODY));
                deckScrewIndex += 1;
            }
        }
        opBoolean(context, id + "cutDeckScrewAccess", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(deckScrewTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "carriageBridge", EntityType.BODY), "P05 Low climbing pocket carriage - 20 mm edge R4");

        // Join every load-bearing printed body that must be a single FDM part.
        // The rounded palm support and switch bracket remain removable.
        opBoolean(context, id + "joinBaseStructure", {
                    "tools" : qUnion([
                                qCreatedBy(id + "base", EntityType.BODY),
                                qCreatedBy(id + "palmFootLeft", EntityType.BODY),
                                qCreatedBy(id + "palmFootRight", EntityType.BODY),
                                qCreatedBy(id + "loadCellWall", EntityType.BODY),
                                qCreatedBy(id + "loadCellGussetNeg", EntityType.BODY),
                                qCreatedBy(id + "loadCellGussetPos", EntityType.BODY),
                                qCreatedBy(id + "springGuideSocket1", EntityType.BODY),
                                qCreatedBy(id + "springGuideSocket2", EntityType.BODY),
                                qUnion(returnStopBodies),
                                qCreatedBy(id + "hardStopLeft", EntityType.BODY),
                                qCreatedBy(id + "hardStopRight", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.UNION
                });
        nameBody(context, qCreatedBy(id + "base", EntityType.BODY), "P01 Integrated structural base, palm supports and hard stops");

        // Coordinated presentation pose: springs shorten and every moving body
        // follows the same displacement. This is a geometry preview, not an FEA.
        if (previewTravel > 0 * millimeter)
        {
            opTransform(context, id + "previewMotion", {
                        "bodies" : qUnion([
                                    qCreatedBy(id + "blockLeft", EntityType.BODY),
                                    qCreatedBy(id + "blockRight", EntityType.BODY),
                                    qCreatedBy(id + "carriageBridge", EntityType.BODY),
                                    qCreatedBy(id + "movingSeat1", EntityType.BODY),
                                    qCreatedBy(id + "movingSeat2", EntityType.BODY),
                                    qCreatedBy(id + "strikePlateLeft", EntityType.BODY),
                                    qCreatedBy(id + "strikePlateRight", EntityType.BODY)
                                ]),
                        "transform" : transform(vector(-previewTravel, 0 * millimeter, 0 * millimeter))
                    });
        }

        // Open mechanism, warm climbing edge and dark olive palm reaction sleeve.
        finishBody(context, qCreatedBy(id + "base", EntityType.BODY), color(0.27, 0.30, 0.28));
        finishBody(context, qCreatedBy(id + "palmPad", EntityType.BODY), color(0.27, 0.32, 0.28));
        finishBody(context, qCreatedBy(id + "palmCushion", EntityType.BODY), color(0.15, 0.20, 0.17));
        finishBody(context, qCreatedBy(id + "carriageBridge", EntityType.BODY), color(0.66, 0.46, 0.27));
        finishBody(context, qUnion([qCreatedBy(id + "springLong1" + "sweep", EntityType.BODY),
                                    qCreatedBy(id + "springLong2" + "sweep", EntityType.BODY)]), color(0.14, 0.40, 0.27));

        if (definition.showHand && handleHeight != 20 * millimeter)
            throw regenError("Hand reference is fitted to the 20 mm pocket; hide it for other depths.", ["showHand", "handleHeight"]);
        if (definition.showHand)
            makeHandReference(context, id + "handReference", previewTravel);

        // Exact-solid diagnostic for the current pose; results appear in
        // FeatureScript notices. No warnings are hidden and no geometry is altered.
        for (var check in auditFingerworkerCollisions(context, id))
            println({ "pose" : previewTravel, "pair" : check.pair,
                      "status" : check.status, "gap" : check.minimumSeparation,
                      "interferences" : check.interferenceCount,
                      "contacts" : check.exteriorContactCount,
                      "unclassified" : check.unclassifiedCount });
    }, {
        "baseLength" : 210 * millimeter,
        "baseWidth" : 170 * millimeter,
        "baseThickness" : 12 * millimeter,
        "travel" : 30 * millimeter,
        "handleWidth" : 125 * millimeter,
        "handleThickness" : 12 * millimeter,
        "handleHeight" : 20 * millimeter,
        "handleEdgeRadius" : 4 * millimeter,
        "guideSpacing" : 130 * millimeter,
        "railWidth" : 12 * millimeter,
        "railHeight" : 8 * millimeter,
        "previewTravel" : 0 * millimeter,
        "showHand" : false
    });
