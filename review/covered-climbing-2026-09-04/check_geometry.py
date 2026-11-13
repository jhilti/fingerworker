#!/usr/bin/env python3
"""Independent nominal geometry ledger for the Fingerworker design review.

Units are millimetres. This is intentionally separate from FeatureScript: it
documents the reviewed design targets, detects the previously identified box /
radial-envelope clashes, and samples the intended movement. It does not prove
that an Onshape regeneration matches those targets, verify freeform fillets,
replace a CAD interference check, or establish strength / human fit.
"""

from dataclasses import dataclass
from math import hypot, sqrt
from pathlib import Path
import re


@dataclass(frozen=True)
class Interval:
    low: float
    high: float

    def shifted(self, distance: float) -> "Interval":
        return Interval(self.low + distance, self.high + distance)

    def overlap(self, other: "Interval") -> float:
        return max(0.0, min(self.high, other.high) - max(self.low, other.low))


def close(actual: float, expected: float) -> None:
    assert abs(actual - expected) < 1e-8, (actual, expected)


def run() -> None:
    samples = (0.0, 15.0, 30.0)
    bridge = Interval(140.0, 194.0)
    rod = Interval(49.0, 175.0)
    palm_contact_x = 37.0
    finger_contact_x = 137.0
    spring_radius = 8.0
    tunnel_radius = 8.6
    rod_radius = 3.0
    guide_bore_radius = 3.3

    # The previous guide passage ended inside the bridge at x176. The new
    # drilling tool exits the rear of the bridge at x195 (one mm overrun).
    old_blind_material = Interval(176.0, bridge.high)
    through_bore_end = 195.0
    close(through_bore_end - bridge.high, 1.0)
    assert through_bore_end > bridge.high
    close(tunnel_radius - spring_radius, 0.6)
    close(guide_bore_radius - rod_radius, 0.3)

    # Spring channels now cover the whole bridge region ahead of the seats.
    # Their trailing 0.4mm overlap with the seat pockets prevents an annular
    # sliver between the two subtractive tools.
    spring_tunnel = Interval(139.0, 166.2)
    seat_pocket = Interval(165.8, 169.2)
    close(spring_tunnel.overlap(seat_pocket), 0.4)

    print("NOMINAL GEOMETRY LEDGER — millimetres")
    print("Stroke  Span  Old rod/bridge clash  New clash  Hood overlap  Rod protrusion")
    old_rod_clashes = []
    new_spans = []
    hood_overlaps = []
    full_roof_overlaps = []
    for stroke in samples:
        moved_bridge = bridge.shifted(-stroke)
        span = finger_contact_x - stroke - palm_contact_x
        old_rod_clash = rod.overlap(old_blind_material.shifted(-stroke))
        old_rod_clashes.append(old_rod_clash)
        new_spans.append(span)

        # The bore is through: there is no unbored bridge material at its end.
        new_rod_clash = 0.0 if through_bore_end >= bridge.high else None
        assert new_rod_clash == 0.0
        spring = Interval(65.0, 166.0 - stroke)
        old_spring_solid = Interval(bridge.low - stroke, 165.8 - stroke)
        close(spring.overlap(old_spring_solid), 25.8)
        tunnel = spring_tunnel.shifted(-stroke)
        assert tunnel.low < moved_bridge.low
        assert tunnel.high >= spring.high

        fixed_hood = Interval(43.0, 93.0)
        moving_hood = Interval(84.0 - stroke, 198.0 - stroke)
        overlap = fixed_hood.overlap(moving_hood)
        hood_overlaps.append(overlap)
        # With an 8mm front corner fillet, the full-height flat roof begins
        # 8mm after the hood envelope. This is a conservative roof-overlap
        # measure; actual curved surfaces still require CAD inspection.
        full_roof = Interval(92.0 - stroke, 190.0 - stroke)
        full_roof_overlaps.append(fixed_hood.overlap(full_roof))
        assert overlap > 0.0
        assert full_roof_overlaps[-1] > 0.0

        # The moving cover's 7.2mm rod holes also span its rear wall at every
        # position. At full stroke the fixed rods protrude beyond that wall.
        hood_rear_wall = Interval(195.0 - stroke, 198.0 - stroke)
        hood_rod_hole = Interval(190.0 - stroke, 201.0 - stroke)
        assert hood_rod_hole.low < hood_rear_wall.low
        assert hood_rod_hole.high > hood_rear_wall.high
        protrusion = max(0.0, rod.high - moved_bridge.high)
        print(f"{stroke:6.1f} {span:5.1f} {old_rod_clash:21.1f}"
              f" {new_rod_clash:10.1f} {overlap:13.1f} {protrusion:15.1f}")

    assert old_rod_clashes == [0.0, 14.0, 18.0]
    assert new_spans == [100.0, 85.0, 70.0]
    assert hood_overlaps == [9.0, 24.0, 39.0]

    # Palm pad and cable: old components occupied intersecting volumes.
    old_pad_z = Interval(33.0, 49.0)
    old_wall_z = Interval(12.0, 51.0)
    close(old_pad_z.overlap(old_wall_z), 16.0)
    new_pad_bottom = 39.0
    new_wall_top = 38.0
    close(new_pad_bottom - new_wall_top, 1.0)
    connector_x = Interval(40.75, 46.75)
    close(connector_x.overlap(Interval(12.0, 42.0)), 1.25)
    close(connector_x.low - 39.0, 1.75)

    # Straight-wall clearances; corner fillets / print tolerances are not
    # represented by this deliberately simple interval ledger.
    clearances = {
        "Spring / bridge tunnel radial": tunnel_radius - spring_radius,
        "Guide rod / carriage bore radial": guide_bore_radius - rod_radius,
        "Guide rod / cover hole radial": 3.6 - rod_radius,
        "Pad underside / reaction wall": new_pad_bottom - new_wall_top,
        "Connector / palm-foot rear": connector_x.low - 39.0,
        "Moving cavity roof / fixed hood": 56.5 - 44.0,
        "Moving cavity side / fixed hood": 83.0 - 58.0,
        "Moving cavity side / carriage": 83.0 - 82.5,
        "Deck / hood aperture each side": 63.1 - 62.5,
        "Deck / hood aperture front and rear": 0.6,
        "Full-stroke deck / fixed hood": 125.0 - 30.0 - 93.0,
        "Deck underside / switch body": 36.5 - 31.8,
        "Deck underside / switch bracket": 36.5 - 31.5,
        "Pocket floor / spring tunnel": 39.5 - (25.0 + 8.6),
        "Pocket floor / seat recess": 39.5 - (25.0 + 11.2),
        "Pocket wall / inner MGN screw port": 55.0 - 3.2 - 47.0,
        "R4 pocket mouth / inner MGN screw port": 55.0 - 3.2 - (47.0 + 4.0),
        "Reaction pad / base": 13.0 - 12.0,
        "Spring outer envelope / base": 25.0 - 8.0 - 12.0,
        "Spring seat envelope / base": 25.0 - 11.0 - 12.0,
        "Load-cell envelope / base": 25.0 - 9.875 - 12.0,
        "Full-height roof overlap at open": min(full_roof_overlaps),
        "Return cheek / rail each side": (10.0 - 3.0) - 6.0,
        "Return cheek / carriage underside": 25.0 - 24.5,
        "Return cheek / cover notch roof": 25.1 - 24.5,
        "Return cheek / cover notch each side": 14.0 - (10.0 + 3.0),
    }
    assert all(value > 0.0 for value in clearances.values())
    print("\nMinimum nominal clearances")
    for label, value in clearances.items():
        print(f"  {label:45s} {value:5.2f}")

    # The climbing deck passes the fixed stops only after 20 mm of movement.
    # A local underside cut, not an elevation of the complete grip, preserves
    # the stop geometry. This checks the entire 0..30 mm stroke at 0.5 mm steps.
    fixed_stop_x = Interval(95.0, 105.0)
    for index in range(61):
        stroke = index * 0.5
        deck_front_x = 125.0 - stroke
        stop_relief_x = Interval(124.0 - stroke, 136.0 - stroke)
        if deck_front_x < fixed_stop_x.high:
            assert stop_relief_x.low <= max(deck_front_x, fixed_stop_x.low)
            assert stop_relief_x.high > fixed_stop_x.high
    close(43.0 - 42.0, 1.0)  # relief ceiling above the fixed stop
    close(39.5 + 20.0 - (-4.0), 63.5)
    close(92.0 - 63.5, 28.5)
    print("\nFlat climbing layout: 94 mm wide / 20 mm deep pocket, 63.5 mm overall height;")
    print("28.5 mm (31.0%) lower than the previous 92 mm raised-bar layout.")

    # Read only the reviewed fastener and relief dimensions from FeatureScript
    # so this check cannot silently retain an obsolete boss position while
    # the live model is refined. Other values above are independent nominal
    # targets, not an interpreter or proof of FeatureScript regeneration.
    source_path = Path(__file__).resolve().parents[1] / "fingerworker_mvp.fs"
    source = source_path.read_text()
    boss_x_match = re.search(r"for \(var bossX in \[(.*?)\]\)", source)
    boss_y_match = re.search(r"for \(var bossY in \[(.*?)\]\)", source)
    relief_match = re.search(r"stopY - ([\d.]+) \* millimeter", source)
    assert boss_x_match and boss_y_match and relief_match
    extract = lambda text: [float(value) for value in re.findall(r"(-?[\d.]+) \* millimeter", text)]
    bosses = [(x, y) for x in extract(boss_x_match.group(1))
              for y in extract(boss_y_match.group(1))]
    screw_ports = [(x, y) for x in (157.7, 177.7)
                   for y in (-75.0, -55.0, 55.0, 75.0)]
    min_boss_gap = min(hypot(bx - sx, by - sy) - 6.0 - 3.2
                       for bx, by in bosses for sx, sy in screw_ports)
    stop_side_clearance = float(relief_match.group(1)) - 8.0
    print(f"Hood boss / MGN port footprint gap: {min_boss_gap:.3f} mm")
    print(f"Deck stop-relief side clearance: {stop_side_clearance:.3f} mm")
    assert min_boss_gap > 0.0, "A hood boss overhangs a carriage screw-port mouth"
    assert stop_side_clearance > 0.0, "Stop relief matches the bracket without side clearance"

    # A deck union can refill an earlier strike-plate recess. Check both the
    # actual nominal dimensions and feature order: the shortened plates and
    # their 0.2 mm assembly clearance must remain below the climbing floor.
    def box_definition(part: str) -> str:
        match = re.search(r'makeBox\(context, id \+ "' + re.escape(part)
                          + r'",\s*(.*?)\);', source, re.S)
        assert match, f"Missing {part} box"
        return match.group(1)

    for side in ("Left", "Right"):
        plate = box_definition("strikePlate" + side)
        lower = re.search(r'vector\(bridgeStartX, -?hardStopY - ([\d.]+) '
                          r'\* millimeter, bridgeBottomZ\)', plate)
        upper = re.search(r'vector\(bridgeStartX \+ ([\d.]+) \* millimeter, '
                          r'-?hardStopY \+ ([\d.]+) \* millimeter, '
                          r'bridgeBottomZ \+ ([\d.]+) \* millimeter\)', plate)
        assert lower and upper
        thickness, positive_half_width, height = map(float, upper.groups())
        width = float(lower.group(1)) + positive_half_width
        close(thickness, 2.0)
        close(width, 8.0)
        close(height, 13.5)

        recess = box_definition("strikePocket" + side)
        recess_lower = re.search(r'vector\(bridgeStartX - ([\d.]+) \* millimeter, '
                                 r'-?hardStopY - ([\d.]+) \* millimeter, '
                                 r'bridgeBottomZ - ([\d.]+) \* millimeter\)', recess)
        recess_upper = re.search(r'vector\(bridgeStartX \+ ([\d.]+) \* millimeter, '
                                 r'-?hardStopY \+ ([\d.]+) \* millimeter, '
                                 r'bridgeBottomZ \+ ([\d.]+) \* millimeter\)', recess)
        assert recess_lower and recess_upper
        low_x, low_y, low_z = map(float, recess_lower.groups())
        high_x, high_y, high_z = map(float, recess_upper.groups())
        for clearance in (low_x, low_y - width / 2, low_z,
                          high_x - thickness, high_y - width / 2, high_z - height):
            close(clearance, 0.2)
        recess_top = 25.0 + high_z
        close(recess_top, 38.7)
        close(39.5 - recess_top, 0.8)
        assert recess_top < 39.5

    deck_union = source.index('opBoolean(context, id + "joinClimbingDeck"')
    strike_cut = source.index('opBoolean(context, id + "cutStrikePlatePockets"')
    pocket_cut = source.index('opBoolean(context, id + "cutClimbingPocket"')
    assert source.count('opBoolean(context, id + "cutStrikePlatePockets"') == 1
    assert deck_union < strike_cut < pocket_cut, "Strike recesses must follow the deck union"
    print("Strike plates: two 8 x 13.5 x 2 mm plates with 0.2 mm recess clearance;")
    print("recess tops at 38.7 lie 0.8 mm below pocket floor 39.5; cuts follow deck union.")

    # The case now sits at base level. Side screws retain the full 3.5 mm foot
    # while a local recess clears both the case and the estimated hinge root.
    # Verify the source locations to reject the obsolete elevated switch pose.
    base_offset = re.search(r'const switchBaseX = hardStopContactX - ([\d.]+) '
                            r'\* millimeter;', source)
    assert base_offset
    close(float(base_offset.group(1)), 16.0)
    assert re.search(r'const switchBodyZ = baseThickness;', source)
    switch_base_x = 110.0 - float(base_offset.group(1))
    switch_case_z = 12.0
    close(switch_base_x, 94.0)
    switch_foot_x = Interval(switch_base_x - 5.2, switch_base_x + 17.0)
    slot_centres_x = (switch_base_x + 1.0, switch_base_x + 9.5)
    slot_half_length = 3.8
    switch_body_y_max = 3.2
    screw_head_radius = 2.75  # nominal M3 socket-head envelope
    switch_screw_y = 7.5
    for centre in slot_centres_x:
        assert centre - slot_half_length > switch_foot_x.low
        assert centre + slot_half_length < switch_foot_x.high
    close(switch_screw_y - screw_head_radius - switch_body_y_max, 1.55)
    case_recess = box_definition("switchCaseSeat")
    assert re.search(r'vector\(switchBaseX - 0\.2 \* millimeter, '
                     r'-3\.4 \* millimeter, baseThickness - 0\.2 \* millimeter\)',
                     case_recess)
    recess_upper = re.search(r'vector\(switchBaseX \+ ([\d.]+) \* millimeter, '
                             r'3\.4 \* millimeter, baseThickness \+ 4 \* millimeter\)',
                             case_recess)
    assert recess_upper
    recess_right_x = switch_base_x + float(recess_upper.group(1))
    close(recess_right_x, 107.2)
    close(3.4 - switch_body_y_max, 0.2)
    close(switch_screw_y - screw_head_radius - 3.4, 1.35)
    close(switch_screw_y - 1.8 - 3.4, 2.3)  # slot edge to recess
    close(16.0 - 15.5, 0.5)  # cutter exits the full foot thickness
    assert source.index('opBoolean(context, id + "joinSwitchAccessibleFoot"') < \
        source.index('opBoolean(context, id + "cutSwitchCaseSeat"')

    # Drawing-derived contact preview only: the hinge is estimated, so these
    # checks establish the chosen rigid envelopes and constant lever length,
    # not the manufacturer's exact internal kinematics or click repeatability.
    pivot_x, pivot_z = 105.5, 14.9
    lever_radius = 0.45
    lever_length = hypot(3.1, 16.7)
    roller_radius = 2.4
    case_rear_x = switch_base_x + 10.2
    free_roller_x = 113.4
    first_contact_stroke = 140.0 - (free_roller_x + roller_radius)
    close(first_contact_stroke, 24.2)
    nominal_op_stroke = 29.0
    close((113.4 + roller_radius) - (108.6 + roller_radius), 4.8)
    close(30.0 - nominal_op_stroke, 1.0)
    close(pivot_x - lever_radius - case_rear_x, 0.85)
    print("\nEstimated switch contact preview (not exact manufacturer kinematics)")
    print("Stroke  Roller X  Roller Z  Deck gap  Roller/case X gap")
    for stroke in (0.0, 15.0, first_contact_stroke, nominal_op_stroke, 30.0):
        bridge_front_x = 140.0 - stroke
        roller_x = min(free_roller_x, bridge_front_x - roller_radius)
        roller_z = pivot_z + sqrt(lever_length ** 2 - (roller_x - pivot_x) ** 2)
        close(hypot(roller_x - pivot_x, roller_z - pivot_z), lever_length)
        assert roller_x + roller_radius <= bridge_front_x + 1e-8
        deck_gap = 36.5 - (roller_z + roller_radius)
        roller_case_gap = roller_x - roller_radius - case_rear_x
        assert deck_gap > 0.0 and roller_case_gap > 0.0
        # Conservative radius-expanded axis envelope for the lever portion
        # near the foot. The widened case-seat recess contains this portion.
        root_axis_x = pivot_x + (roller_x - pivot_x) * \
            (16.0 + lever_radius - pivot_z) / (roller_z - pivot_z)
        root_corridor_gap = recess_right_x - (root_axis_x + lever_radius)
        assert root_corridor_gap > 0.0
        assert 3.4 > lever_radius
        assert 11.8 < pivot_z - lever_radius
        if stroke == nominal_op_stroke:
            close(roller_x, 108.6)
            close(roller_z, 31.6)
        if stroke == 30.0:
            close(roller_x, 107.6)
            close(roller_z, 31.75496959356498)
            close(deck_gap, 2.34503040643502)
            close(roller_case_gap, 1.0)
        print(f"{stroke:6.1f} {roller_x:9.3f} {roller_z:9.3f}"
              f" {deck_gap:9.3f} {roller_case_gap:18.3f}")
    print("Switch foot: 0.2 mm case side clearance; 1.35 mm head/recess clearance;")
    print("hinge corridor contains the conservative R0.45 lever-root envelope.")

    # Four separate bumper faces meet the block rear at x190.4 at rest.
    # Cheeks straddle (rather than bridge) each rail, preserving access to its
    # last screw. The cover notch travels with the cover and contains every
    # portion of its rear wall that could meet these stationary cheeks.
    block_rear_open = 190.4
    bumper = Interval(190.4, 191.4)
    cheek = Interval(191.4, 204.0)
    close(bumper.low - block_rear_open, 0.0)
    close(bumper.high - bumper.low, 1.0)
    close(cheek.low - bumper.high, 0.0)
    for stroke in (0.0, 2.0, 5.0, 7.6, 15.0, 30.0):
        close(bumper.low - (block_rear_open - stroke), stroke)
        cover_wall = Interval(195.0 - stroke, 198.0 - stroke)
        cover_notch = Interval(190.0 - stroke, 201.0 - stroke)
        if cover_wall.overlap(Interval(bumper.low, cheek.high)) > 0.0:
            assert cover_notch.low < cover_wall.low
            assert cover_notch.high > cover_wall.high
    print("\nReturn stops: four 1mm bumper faces; rest contact at x190.4;")
    print("rear-cover clearances checked at 0, 2, 5, 7.6, 15 and 30mm travel.")
    print("\nPASS: reviewed envelope targets and all three intended poses.")
    print("Limits: nominal geometry only; CAD solids, fillets, retention, strength,")
    print("manufacturing tolerances and a physical hand-fit test remain separate.")


if __name__ == "__main__":
    run()
