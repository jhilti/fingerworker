FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

// The helper below uses the original Z59.5 datum. In the 30 mm model,
// call it and translate the resulting hand body by vector(0,0,-29.5)*millimeter,
// exactly as fingerworker_mvp.fs does. Do not omit that final transform.

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


