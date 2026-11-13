FeatureScript 3070;
import(path : "onshape/std/geometry.fs", version : "3070.0");

/**
 * Fingerworker MVP - production-oriented layout for a first 3D printed test.
 *
 * X = pull direction, Y = finger-bar width, Z = height above the base.
 * Purchased hardware is modeled at nominal catalogue size. Printed parts are
 * separated bodies so they can be exported and printed individually.
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

        annotation { "Name" : "Finger bar width" }
        isLength(definition.handleWidth, LENGTH_BOUNDS);

        annotation { "Name" : "Finger bar thickness" }
        isLength(definition.handleThickness, LENGTH_BOUNDS);

        annotation { "Name" : "Finger bar height" }
        isLength(definition.handleHeight, LENGTH_BOUNDS);

        annotation { "Name" : "Finger bar edge radius" }
        isLength(definition.handleEdgeRadius, BLEND_BOUNDS);

        annotation { "Name" : "Guide spacing" }
        isLength(definition.guideSpacing, LENGTH_BOUNDS);

        annotation { "Name" : "Guide rail width" }
        isLength(definition.railWidth, LENGTH_BOUNDS);

        annotation { "Name" : "Guide rail height" }
        isLength(definition.railHeight, LENGTH_BOUNDS);
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

        const railStartX = 5 * millimeter;
        const railEndX = railStartX + 200 * millimeter;
        const blockStartX = 145 * millimeter;
        const blockEndX = blockStartX + 45.4 * millimeter;
        const bridgeStartX = 140 * millimeter;
        const bridgeEndX = 194 * millimeter;
        const bridgeBottomZ = baseThickness + railHeight + 5 * millimeter;
        const bridgeTopZ = bridgeBottomZ + 18 * millimeter;
        // With a 10 mm bar, x = 142 mm places its near face at x = 137 mm.
        // The palm pad ends at x = 37 mm: 100 mm open and 70 mm after 30 mm travel.
        const handleX = 142 * millimeter;
        const handleZ = baseThickness + 48 * millimeter;
        const springStartX = 65 * millimeter;
        const springEndX = 166 * millimeter;
        const springZ = baseThickness + 19 * millimeter;
        const springY1 = -30 * millimeter;
        const springY2 = 30 * millimeter;
        const hardStopContactX = bridgeStartX - travel;
        const hardStopY = 50 * millimeter;

        // Main printed plate: 210 x 170 mm fits a 220 mm printer bed with margin.
        makeBox(context, id + "base",
                vector(0 * millimeter, -baseWidth / 2, 0 * millimeter),
                vector(baseLength, baseWidth / 2, baseThickness));
        nameBody(context, qCreatedBy(id + "base", EntityType.BODY), "P01 Base plate 210x170x12");

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
                vector(42 * millimeter, -40 * millimeter, baseThickness + 21 * millimeter));
        makeBox(context, id + "palmFootRight",
                vector(12 * millimeter, 40 * millimeter, baseThickness - 0.2 * millimeter),
                vector(42 * millimeter, 62 * millimeter, baseThickness + 21 * millimeter));
        nameBody(context, qCreatedBy(id + "palmFootLeft", EntityType.BODY), "P02 Palm stop left support");
        nameBody(context, qCreatedBy(id + "palmFootRight", EntityType.BODY), "P03 Palm stop right support");

        makeBox(context, id + "palmPad",
                vector(10 * millimeter, -64 * millimeter, baseThickness + 21 * millimeter),
                vector(37 * millimeter, 64 * millimeter, baseThickness + 37 * millimeter));
        opFillet(context, id + "palmPadFillet", {
                    "entities" : qCreatedBy(id + "palmPad", EntityType.EDGE),
                    "radius" : 4 * millimeter,
                    "tangentPropagation" : true
                });
        nameBody(context, qCreatedBy(id + "palmPad", EntityType.BODY), "P04 Rounded palm pad");

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
                        vector(palmX, palmY, baseThickness + 14 * millimeter),
                        vector(palmX, palmY, baseThickness + 22 * millimeter), 2.6 * millimeter);
                palmInsertTools = append(palmInsertTools, qCreatedBy(palmInsertId, EntityType.BODY));

                const palmHoleId = id + ("palmPadHole" ~ palmMountIndex);
                makeCylinder(context, palmHoleId,
                        vector(palmX, palmY, baseThickness + 20 * millimeter),
                        vector(palmX, palmY, baseThickness + 39 * millimeter), 2.2 * millimeter);
                palmPadHoleTools = append(palmPadHoleTools, qCreatedBy(palmHoleId, EntityType.BODY));

                const palmCounterboreId = id + ("palmPadCounterbore" ~ palmMountIndex);
                makeCylinder(context, palmCounterboreId,
                        vector(palmX, palmY, baseThickness + 32.5 * millimeter),
                        vector(palmX, palmY, baseThickness + 39 * millimeter), 4 * millimeter);
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
        const loadCellCenterZ = baseThickness + 19 * millimeter;

        makeBox(context, id + "loadCellWall",
                vector(29 * millimeter, -27 * millimeter, baseThickness - 0.2 * millimeter),
                vector(48.5 * millimeter, 27 * millimeter, baseThickness + 39 * millimeter));
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
                vector(springStartX, 48 * millimeter, baseThickness + 38 * millimeter));
        nameBody(context, qCreatedBy(id + "springAnchor", EntityType.BODY), "P07 Shared spring anchor");

        // Two norelem 26000-1608102 ISO 10243 springs: 1 mm preload plus 30 mm
        // stroke at 7.8 N/mm each gives 483.6 N total (about 49.3 kgf).
        makeCompressionSpring(context, id + "springLong1", springStartX, springEndX, springY1, springZ);
        makeCompressionSpring(context, id + "springLong2", springStartX, springEndX, springY2, springZ);
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

        var springGuideBoreTools = [];
        var springGuideBoreIndex = 0;
        for (var guideBoreY in [springY1, springY2])
        {
            const guideBoreId = id + ("springGuideBore" ~ springGuideBoreIndex);
            makeCylinder(context, guideBoreId,
                    vector(51 * millimeter, guideBoreY, springZ),
                    vector(176 * millimeter, guideBoreY, springZ), 3.3 * millimeter);
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
                vector(bridgeStartX + 2 * millimeter, -hardStopY + 4 * millimeter, bridgeBottomZ + 16 * millimeter));
        makeBox(context, id + "strikePlateRight",
                vector(bridgeStartX, hardStopY - 4 * millimeter, bridgeBottomZ),
                vector(bridgeStartX + 2 * millimeter, hardStopY + 4 * millimeter, bridgeBottomZ + 16 * millimeter));
        makeBox(context, id + "strikePocketLeft",
                vector(bridgeStartX - 0.2 * millimeter, -hardStopY - 4.2 * millimeter, bridgeBottomZ - 0.2 * millimeter),
                vector(bridgeStartX + 2.2 * millimeter, -hardStopY + 4.2 * millimeter, bridgeBottomZ + 16.2 * millimeter));
        makeBox(context, id + "strikePocketRight",
                vector(bridgeStartX - 0.2 * millimeter, hardStopY - 4.2 * millimeter, bridgeBottomZ - 0.2 * millimeter),
                vector(bridgeStartX + 2.2 * millimeter, hardStopY + 4.2 * millimeter, bridgeBottomZ + 16.2 * millimeter));
        opBoolean(context, id + "cutStrikePlatePockets", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion([
                                qCreatedBy(id + "strikePocketLeft", EntityType.BODY),
                                qCreatedBy(id + "strikePocketRight", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "strikePlateLeft", EntityType.BODY), "H20 Steel strike plate left");
        nameBody(context, qCreatedBy(id + "strikePlateRight", EntityType.BODY), "H21 Steel strike plate right");

        // Omron SS-01GL2 micro-load roller-lever switch. Its envelope and 9.5 mm
        // mounting pattern are identical to SS-5GL2, but its contacts are suited
        // to an electronic input. Two M3 slots provide +/-2 mm click adjustment.
        const switchBaseX = hardStopContactX - 13.5 * millimeter;
        const switchCenterY = 0 * millimeter;
        const switchBodyZ = baseThickness + 4 * millimeter;

        // Printable right-angle bracket with exact M2.3 mounting-hole locations.
        makeBox(context, id + "switchBracket",
                vector(switchBaseX - 3 * millimeter, switchCenterY - 11 * millimeter, baseThickness),
                vector(switchBaseX + 11.7 * millimeter, switchCenterY + 4 * millimeter, switchBodyZ + 22.5 * millimeter));
        makeBox(context, id + "switchBracketCavity",
                vector(switchBaseX - 4 * millimeter, switchCenterY - 3.5 * millimeter, baseThickness + 3.5 * millimeter),
                vector(switchBaseX + 12.7 * millimeter, switchCenterY + 5 * millimeter, switchBodyZ + 23.5 * millimeter));
        opBoolean(context, id + "shapeSwitchBracket", {
                    "targets" : qCreatedBy(id + "switchBracket", EntityType.BODY),
                    "tools" : qCreatedBy(id + "switchBracketCavity", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        var switchBaseSlotTools = [];
        var switchBaseInsertTools = [];
        var switchBaseMountIndex = 0;
        for (var switchBaseMountX in [switchBaseX + 1 * millimeter, switchBaseX + 9.5 * millimeter])
        {
            const slotLeftId = id + ("switchBaseSlotLeft" ~ switchBaseMountIndex);
            const slotRightId = id + ("switchBaseSlotRight" ~ switchBaseMountIndex);
            const slotBridgeId = id + ("switchBaseSlotBridge" ~ switchBaseMountIndex);
            makeCylinder(context, slotLeftId,
                    vector(switchBaseMountX - 2 * millimeter, switchCenterY, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX - 2 * millimeter, switchCenterY, baseThickness + 5 * millimeter), 1.8 * millimeter);
            makeCylinder(context, slotRightId,
                    vector(switchBaseMountX + 2 * millimeter, switchCenterY, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX + 2 * millimeter, switchCenterY, baseThickness + 5 * millimeter), 1.8 * millimeter);
            makeBox(context, slotBridgeId,
                    vector(switchBaseMountX - 2 * millimeter, switchCenterY - 1.8 * millimeter, baseThickness - 1 * millimeter),
                    vector(switchBaseMountX + 2 * millimeter, switchCenterY + 1.8 * millimeter, baseThickness + 5 * millimeter));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotLeftId, EntityType.BODY));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotRightId, EntityType.BODY));
            switchBaseSlotTools = append(switchBaseSlotTools, qCreatedBy(slotBridgeId, EntityType.BODY));

            const baseInsertId = id + ("switchBaseInsert" ~ switchBaseMountIndex);
            makeCylinder(context, baseInsertId,
                    vector(switchBaseMountX, switchCenterY, baseThickness - 6.5 * millimeter),
                    vector(switchBaseMountX, switchCenterY, baseThickness + 1 * millimeter), 2.3 * millimeter);
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

        makeCylinder(context, id + "switchLever",
                vector(switchBaseX + 10.2 * millimeter, switchCenterY, switchBodyZ + 0.5 * millimeter),
                vector(switchBaseX + 16.9 * millimeter, switchCenterY, switchBodyZ + 15 * millimeter), 0.45 * millimeter);
        makeCylinder(context, id + "switchRoller",
                vector(switchBaseX + 16.9 * millimeter, switchCenterY - 1.6 * millimeter, switchBodyZ + 15 * millimeter),
                vector(switchBaseX + 16.9 * millimeter, switchCenterY + 1.6 * millimeter, switchBodyZ + 15 * millimeter), 2.4 * millimeter);
        nameBody(context, qCreatedBy(id + "switchBracket", EntityType.BODY), "P10 Adjustable Omron SS-01GL2 mounting bracket");
        nameBody(context, qCreatedBy(id + "switchBody", EntityType.BODY), "H17 Omron SS-01GL2 micro-load switch");
        nameBody(context, qCreatedBy(id + "switchLever", EntityType.BODY), "H18 SS-01GL2 stainless roller lever");
        nameBody(context, qCreatedBy(id + "switchRoller", EntityType.BODY), "H19 SS-01GL2 polyacetal roller");

        // Two side uprights and the shared four-finger pull bar. Keeping the
        // supports outside y = +/-55 mm leaves spring and strike-plate corridors unobstructed.
        // These bodies are
        // fused to the bridge at the end of the feature so the 500 N load never
        // relies on glue or a face-only contact.
        makeBox(context, id + "handleSupportLeft",
                vector(handleX - 6 * millimeter, -handleWidth / 2, baseThickness + 24 * millimeter),
                vector(handleX + 6 * millimeter, -55 * millimeter, handleZ + handleHeight / 2));
        makeBox(context, id + "handleSupportRight",
                vector(handleX - 6 * millimeter, 55 * millimeter, baseThickness + 24 * millimeter),
                vector(handleX + 6 * millimeter, handleWidth / 2, handleZ + handleHeight / 2));
        nameBody(context, qCreatedBy(id + "handleSupportLeft", EntityType.BODY), "P11 Left finger-bar support");
        nameBody(context, qCreatedBy(id + "handleSupportRight", EntityType.BODY), "P11 Right finger-bar support");

        makeBox(context, id + "fingerBar",
                vector(handleX - handleThickness / 2, -handleWidth / 2, handleZ - handleHeight / 2),
                vector(handleX + handleThickness / 2, handleWidth / 2, handleZ + handleHeight / 2));
        opFillet(context, id + "fingerBarFillet", {
                    "entities" : qCreatedBy(id + "fingerBar", EntityType.EDGE),
                    "radius" : definition.handleEdgeRadius,
                    "tangentPropagation" : true
                });
        nameBody(context, qCreatedBy(id + "fingerBar", EntityType.BODY), "P12 Rounded 10 mm four-finger pull bar");

        // --------------------------------------------------------------------
        // Product enclosure. Three printable shells turn the exposed mechanism
        // into a compact device while preserving access to palm pad and handle.

        // Rounded lower tray: 0.6 mm per-side FDM assembly clearance around the
        // printed base, 4 mm bottom and roughly 3 mm perimeter wall.
        makeBox(context, id + "lowerShell",
                vector(-3.6 * millimeter, -89.6 * millimeter, -4 * millimeter),
                vector(baseLength + 3.6 * millimeter, 89.6 * millimeter, baseThickness + 1 * millimeter));
        opFillet(context, id + "lowerShellFillet", {
                    "entities" : qCreatedBy(id + "lowerShell", EntityType.EDGE),
                    "radius" : 4 * millimeter,
                    "tangentPropagation" : true
                });
        makeBox(context, id + "lowerShellCavity",
                vector(-0.6 * millimeter, -85.6 * millimeter, -0.1 * millimeter),
                vector(baseLength + 0.6 * millimeter, 85.6 * millimeter, baseThickness + 2 * millimeter));
        opBoolean(context, id + "hollowLowerShell", {
                    "targets" : qCreatedBy(id + "lowerShell", EntityType.BODY),
                    "tools" : qCreatedBy(id + "lowerShellCavity", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        var trayHoleTools = [];
        var trayHoleIndex = 0;
        for (var trayX in [10 * millimeter, baseLength - 10 * millimeter])
        {
            for (var trayY in [-75 * millimeter, 75 * millimeter])
            {
                const trayHoleId = id + ("trayHole" ~ trayHoleIndex);
                makeCylinder(context, trayHoleId,
                        vector(trayX, trayY, -5 * millimeter),
                        vector(trayX, trayY, 1 * millimeter), 2.75 * millimeter);
                trayHoleTools = append(trayHoleTools, qCreatedBy(trayHoleId, EntityType.BODY));
                trayHoleIndex += 1;
            }
        }
        opBoolean(context, id + "cutTrayMounts", {
                    "targets" : qCreatedBy(id + "lowerShell", EntityType.BODY),
                    "tools" : qUnion(trayHoleTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "lowerShell", EntityType.BODY), "C01 Rounded lower housing tray");

        // Fixed inner hood over load cell and springs. It is open at the bottom
        // and both X ends so the moving components can pass through it.
        makeBox(context, id + "fixedHood",
                vector(43 * millimeter, -58 * millimeter, baseThickness),
                vector(105 * millimeter, 58 * millimeter, 56 * millimeter));
        opFillet(context, id + "fixedHoodFillet", {
                    "entities" : qCreatedBy(id + "fixedHood", EntityType.EDGE),
                    "radius" : 7 * millimeter,
                    "tangentPropagation" : true
                });
        makeBox(context, id + "fixedHoodCavity",
                vector(42 * millimeter, -55 * millimeter, baseThickness - 1 * millimeter),
                vector(108 * millimeter, 55 * millimeter, 53 * millimeter));
        opBoolean(context, id + "hollowFixedHood", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "fixedHoodCavity", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Two-level window opening: a through opening plus a shallow 0.3 mm
        // clearance recess leaves a positive ledge for a 1.5 mm clear panel.
        makeBox(context, id + "fixedWindowThrough",
                vector(52 * millimeter, -38 * millimeter, 52 * millimeter),
                vector(96 * millimeter, 38 * millimeter, 58 * millimeter));
        opFillet(context, id + "fixedWindowThroughFillet", {
                    "entities" : qCreatedBy(id + "fixedWindowThrough", EntityType.EDGE),
                    "radius" : 2.5 * millimeter,
                    "tangentPropagation" : true
                });
        makeBox(context, id + "fixedWindowRecess",
                vector(45.7 * millimeter, -46.3 * millimeter, 54.2 * millimeter),
                vector(103.3 * millimeter, 46.3 * millimeter, 58 * millimeter));
        opFillet(context, id + "fixedWindowRecessFillet", {
                    "entities" : qCreatedBy(id + "fixedWindowRecess", EntityType.EDGE),
                    "radius" : 1.5 * millimeter,
                    "tangentPropagation" : true
                });
        opBoolean(context, id + "cutFixedWindowThrough", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "fixedWindowThrough", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutFixedWindowRecess", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "fixedWindowRecess", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Side slot lets the FX1901's factory cable and Molex connector leave
        // the sealed spring bay without being pinched by the fixed hood.
        makeBox(context, id + "sensorCableSlot",
                vector(39.5 * millimeter, 54 * millimeter, loadCellCenterZ - 4 * millimeter),
                vector(48 * millimeter, 60 * millimeter, loadCellCenterZ + 4 * millimeter));
        opBoolean(context, id + "cutSensorCableSlot", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "sensorCableSlot", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Local side openings clear the two inward-shifted hard-stop brackets.
        // Their y = +/-50 mm positions sit between springs and linear rails.
        makeBox(context, id + "hardStopHoodNotchNeg",
                vector(hardStopContactX - 17 * millimeter, -60 * millimeter, baseThickness - 1 * millimeter),
                vector(hardStopContactX + 2 * millimeter, -54 * millimeter, baseThickness + 34 * millimeter));
        makeBox(context, id + "hardStopHoodNotchPos",
                vector(hardStopContactX - 17 * millimeter, 54 * millimeter, baseThickness - 1 * millimeter),
                vector(hardStopContactX + 2 * millimeter, 60 * millimeter, baseThickness + 34 * millimeter));
        opBoolean(context, id + "cutHardStopHoodNotches", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qUnion([
                                qCreatedBy(id + "hardStopHoodNotchNeg", EntityType.BODY),
                                qCreatedBy(id + "hardStopHoodNotchPos", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        makeBox(context, id + "springWindow",
                vector(46 * millimeter, -46 * millimeter, 54.3 * millimeter),
                vector(103 * millimeter, 46 * millimeter, 55.8 * millimeter));
        opFillet(context, id + "springWindowFillet", {
                    "entities" : qCreatedBy(id + "springWindow", EntityType.EDGE),
                    "radius" : 0.5 * millimeter,
                    "tangentPropagation" : true
                });
        nameBody(context, qCreatedBy(id + "springWindow", EntityType.BODY), "C03 Clear spring inspection window");

        // Four integral side flanges overlap the shell wall and use M4 heat-set
        // inserts in the base. The shell holes remain normal M4 clearance holes.
        var fixedFlangeTools = [qCreatedBy(id + "fixedHood", EntityType.BODY)];
        var fixedMountHoleTools = [];
        var fixedBaseInsertTools = [];
        var fixedMountIndex = 0;
        for (var flangeX in [52.5 * millimeter, 82.5 * millimeter])
        {
            for (var flangeY in [-53 * millimeter, 53 * millimeter])
            {
                const flangeId = id + ("fixedFlange" ~ fixedMountIndex);
                makeBox(context, flangeId,
                        vector(flangeX - 7.5 * millimeter, flangeY - 5 * millimeter, baseThickness),
                        vector(flangeX + 7.5 * millimeter, flangeY + 5 * millimeter, baseThickness + 4 * millimeter));
                fixedFlangeTools = append(fixedFlangeTools, qCreatedBy(flangeId, EntityType.BODY));

                const mountHoleId = id + ("fixedMountHole" ~ fixedMountIndex);
                makeCylinder(context, mountHoleId,
                        vector(flangeX, flangeY, baseThickness - 1 * millimeter),
                        vector(flangeX, flangeY, baseThickness + 6 * millimeter), 2.25 * millimeter);
                fixedMountHoleTools = append(fixedMountHoleTools, qCreatedBy(mountHoleId, EntityType.BODY));

                const baseInsertId = id + ("fixedBaseInsert" ~ fixedMountIndex);
                makeCylinder(context, baseInsertId,
                        vector(flangeX, flangeY, baseThickness - 6.5 * millimeter),
                        vector(flangeX, flangeY, baseThickness + 1 * millimeter), 2.8 * millimeter);
                fixedBaseInsertTools = append(fixedBaseInsertTools, qCreatedBy(baseInsertId, EntityType.BODY));
                fixedMountIndex += 1;
            }
        }
        opBoolean(context, id + "joinFixedFlanges", {
                    "tools" : qUnion(fixedFlangeTools),
                    "operationType" : BooleanOperationType.UNION
                });
        opBoolean(context, id + "cutFixedMountHoles", {
                    "targets" : qCreatedBy(id + "fixedHood", EntityType.BODY),
                    "tools" : qUnion(fixedMountHoleTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutFixedBaseInserts", {
                    "targets" : qCreatedBy(id + "base", EntityType.BODY),
                    "tools" : qUnion(fixedBaseInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "fixedHood", EntityType.BODY), "C02 Fixed spring and sensor hood");

        // Larger moving hood telescopes over the fixed hood. It is attached to
        // the carriage, moves with the finger bar, and stays open at the left.
        makeBox(context, id + "movingHood",
                vector(112 * millimeter, -86 * millimeter, baseThickness + 1 * millimeter),
                vector(198 * millimeter, 86 * millimeter, 60 * millimeter));
        opFillet(context, id + "movingHoodFillet", {
                    "entities" : qCreatedBy(id + "movingHood", EntityType.EDGE),
                    "radius" : 8 * millimeter,
                    "tangentPropagation" : true
                });
        makeBox(context, id + "movingHoodCavity",
                vector(108 * millimeter, -83 * millimeter, baseThickness),
                vector(195 * millimeter, 83 * millimeter, 57 * millimeter));
        opBoolean(context, id + "hollowMovingHood", {
                    "targets" : qCreatedBy(id + "movingHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "movingHoodCavity", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        makeBox(context, id + "fingerAccessSlot",
                vector(handleX - 10 * millimeter, -65 * millimeter, baseThickness + 22 * millimeter),
                vector(handleX + 10 * millimeter, 65 * millimeter, 72 * millimeter));
        opBoolean(context, id + "cutFingerAccessSlot", {
                    "targets" : qCreatedBy(id + "movingHood", EntityType.BODY),
                    "tools" : qCreatedBy(id + "fingerAccessSlot", EntityType.BODY),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // At full 30 mm travel the fixed guide rods pass through the moving
        // hood's rear wall. Two clearance holes prevent an otherwise hidden jam.
        var movingGuideClearanceTools = [];
        var movingGuideClearanceIndex = 0;
        for (var movingGuideY in [springY1, springY2])
        {
            const movingGuideClearanceId = id + ("movingGuideClearance" ~ movingGuideClearanceIndex);
            makeCylinder(context, movingGuideClearanceId,
                    vector(190 * millimeter, movingGuideY, springZ),
                    vector(201 * millimeter, movingGuideY, springZ), 3.6 * millimeter);
            movingGuideClearanceTools = append(movingGuideClearanceTools, qCreatedBy(movingGuideClearanceId, EntityType.BODY));
            movingGuideClearanceIndex += 1;
        }
        opBoolean(context, id + "cutMovingGuideClearances", {
                    "targets" : qCreatedBy(id + "movingHood", EntityType.BODY),
                    "tools" : qUnion(movingGuideClearanceTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });

        // Four internal bosses and M4 through holes secure the moving hood to the
        // carriage bridge without glue. The 14 mm boss height clears the hardware.
        var movingBossTools = [qCreatedBy(id + "movingHood", EntityType.BODY)];
        var movingMountHoleTools = [];
        var movingMountCounterboreTools = [];
        var movingBridgeInsertTools = [];
        var movingMountIndex = 0;
        for (var bossX in [166 * millimeter, 184 * millimeter])
        {
            for (var bossY in [-45 * millimeter, 45 * millimeter])
            {
                const bossId = id + ("movingBoss" ~ movingMountIndex);
                makeCylinder(context, bossId,
                        vector(bossX, bossY, bridgeTopZ),
                        vector(bossX, bossY, 60 * millimeter), 6 * millimeter);
                movingBossTools = append(movingBossTools, qCreatedBy(bossId, EntityType.BODY));

                const movingHoleId = id + ("movingMountHole" ~ movingMountIndex);
                makeCylinder(context, movingHoleId,
                        vector(bossX, bossY, bridgeTopZ - 1 * millimeter),
                        vector(bossX, bossY, 61 * millimeter), 2.25 * millimeter);
                movingMountHoleTools = append(movingMountHoleTools, qCreatedBy(movingHoleId, EntityType.BODY));

                const movingCounterboreId = id + ("movingMountCounterbore" ~ movingMountIndex);
                makeCylinder(context, movingCounterboreId,
                        vector(bossX, bossY, 56 * millimeter),
                        vector(bossX, bossY, 61 * millimeter), 4 * millimeter);
                movingMountCounterboreTools = append(movingMountCounterboreTools, qCreatedBy(movingCounterboreId, EntityType.BODY));

                const bridgeInsertId = id + ("movingBridgeInsert" ~ movingMountIndex);
                makeCylinder(context, bridgeInsertId,
                        vector(bossX, bossY, bridgeTopZ - 6.5 * millimeter),
                        vector(bossX, bossY, bridgeTopZ + 1 * millimeter), 2.8 * millimeter);
                movingBridgeInsertTools = append(movingBridgeInsertTools, qCreatedBy(bridgeInsertId, EntityType.BODY));
                movingMountIndex += 1;
            }
        }
        opBoolean(context, id + "joinMovingBosses", {
                    "tools" : qUnion(movingBossTools),
                    "operationType" : BooleanOperationType.UNION
                });
        opBoolean(context, id + "cutMovingMountHoles", {
                    "targets" : qCreatedBy(id + "movingHood", EntityType.BODY),
                    "tools" : qUnion(movingMountHoleTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutMovingMountCounterbores", {
                    "targets" : qCreatedBy(id + "movingHood", EntityType.BODY),
                    "tools" : qUnion(movingMountCounterboreTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        opBoolean(context, id + "cutMovingBridgeInserts", {
                    "targets" : qCreatedBy(id + "carriageBridge", EntityType.BODY),
                    "tools" : qUnion(movingBridgeInsertTools),
                    "operationType" : BooleanOperationType.SUBTRACTION
                });
        nameBody(context, qCreatedBy(id + "movingHood", EntityType.BODY), "C04 Telescoping moving carriage hood");

        // Join every load-bearing printed body that must be a single FDM part.
        // The palm pad, switch bracket and enclosure shells remain removable.
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
                                qCreatedBy(id + "hardStopLeft", EntityType.BODY),
                                qCreatedBy(id + "hardStopRight", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.UNION
                });
        nameBody(context, qCreatedBy(id + "base", EntityType.BODY), "P01 Integrated structural base, palm supports and hard stops");

        opBoolean(context, id + "joinCarriageAndHandle", {
                    "tools" : qUnion([
                                qCreatedBy(id + "carriageBridge", EntityType.BODY),
                                qCreatedBy(id + "handleSupportLeft", EntityType.BODY),
                                qCreatedBy(id + "handleSupportRight", EntityType.BODY),
                                qCreatedBy(id + "fingerBar", EntityType.BODY)
                            ]),
                    "operationType" : BooleanOperationType.UNION
                });
        nameBody(context, qCreatedBy(id + "carriageBridge", EntityType.BODY), "P05 Integrated carriage bridge and 10 mm finger bar");
    }, {
        "baseLength" : 210 * millimeter,
        "baseWidth" : 170 * millimeter,
        "baseThickness" : 12 * millimeter,
        "travel" : 30 * millimeter,
        "handleWidth" : 125 * millimeter,
        "handleThickness" : 10 * millimeter,
        "handleHeight" : 20 * millimeter,
        "handleEdgeRadius" : 2 * millimeter,
        "guideSpacing" : 130 * millimeter,
        "railWidth" : 12 * millimeter,
        "railHeight" : 8 * millimeter
    });
