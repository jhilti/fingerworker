FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

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

