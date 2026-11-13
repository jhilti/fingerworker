/**
 * Hand reference helper block for Fingerworker. Paste above defineFeature in the
 * existing Feature Studio (geometry.fs is already imported there).
 *
 * Call makeHandReference(context, id + "handReference", displacement);
 * after positioning the machine, with displacement between 0 and 30 mm.
 *
 * Assumed interface: padded palm surface z = 49.5 mm; recessed climbing grip
 * x = 137..171 mm, y = +/-47 mm, floor z = 39.5 mm and top z = 59.5 mm at
 * rest. The pocket's loaded inner wall is x = 137 mm. The heel remains fixed
 * while the fingertips pull this wall toward -X through a 30 mm stroke.
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

    // An understated, continuous palm volume with a narrower wrist, a soft heel
    // resting on the pad, and a wider metacarpal arch leading into four digits.
    // The forward arch clears the translating 59.5 mm enclosure roof.
    const palmVolumes = [
        { "suffix" : "wrist", "center" : vector(-15, 0, 65.5),
          "radius" : vector(39, 23, 12) },
        { "suffix" : "heel", "center" : vector(25, 0, 64),
          "radius" : vector(29, 29, 14.5) },
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

    // Thumb sweeps beside the housing, visibly separate from the four working
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
                "value" : "Illustrative adult-sized hand pulling a 20 mm climbing recess. Fixed-length finger links follow the 0-30 mm stroke. Not anthropometric validation, a physical clearance guarantee, or a manufactured component."
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
