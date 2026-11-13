FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

// Audit queries for the 30 mm outboard-spring design, 20 September 2026, exterior palm.
function body(id is Id) returns Query
{
    return qCreatedBy(id, EntityType.BODY);
}

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

