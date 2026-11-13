# Flat layouts with a 72 mm clear finger opening

19 October 2026. **72 mm is the user's new clear-opening requirement.** It replaces the earlier 92 mm requirement for this study. The old scan-derived width budget is not used to reject this instruction.

**A roughly 138 mm-wide flat layout is the more conservative candidate with the existing spring hardware. About 132 mm is a more aggressive packaging target.** Both need new palm attachments and coordinated switch/mounting changes; neither is a validated assembly. The nominal height target remains approximately 32 mm.

## Width budget

The grip deck becomes **84 mm**: 72 mm opening plus two 6 mm side walls. The existing spring seats are Ø22 mm, the rod supports 24 mm wide, and the outside floor border 3 mm.

| Flat arrangement | Nominal width | What it requires |
|---|---:|---|
| Existing palm-attachment sections and four-bolt pattern retained | About 152 mm | The attachment corridor, rather than the smaller finger opening, limits width. Still a concept requiring a coordinated narrow grip and switch layout. |
| Seats fully beside the grip, existing seat/support sizes | **138 mm** | Spring axes Y±54. New palm support/attachment; switch/cam, bench-mount and connector-route changes. No rear-seat relief needed. |
| Seats locally recessed behind the grip | **132 mm** | Spring axes Y±51. The same attachment changes plus new rear grip reliefs. The matching relief geometry has an approximately 3.1 mm local roof concern from the earlier study. |
| New compact side supports and revised seat/retention construction | Smaller widths may be possible | Needs new fastening and structural design. No narrower equivalent-function model has been established; the present palm and enclosure also set 128 and 124 mm envelope limits. |
| Separate longitudinal spring bay and a long return carriage | Around 100 mm is an architecture possibility | New palm/enclosure, guides and force path; substantially more length. It is not the compact current arrangement. |

The unrelieved calculation is:

`72 + 2×6 + 2×(11 + 1 + 12 + 3) = 138 mm`

Here 11 is the seat radius, 1 the seat/deck gap, 12 the half-width of the rod support, and 3 the outside border. Recessing the moving seats permits the axes to move another 3 mm inward per side, giving the nominal 132 mm envelope. The Ø16 isometric sleeve then retains 1 mm nominal lateral gap to the 84 mm deck.

## Changes that a width formula misses

The current 128 mm palm plate and 124 mm enclosure fit inside a 132/138 mm overall width. Their attachments do not simply follow the spring rows inward: the original 21 mm palm ears would overlap the sensor wall and the moving cassette-capture heads. Full-mesh probes confirm capture-head interference when those ears are merely translated. A new wristward support, an integrated fixed bracket with deliberate hardware clearance, or another qualified attachment is required.

The negative spring row also enters the current switch envelope at the proposed axes. Moving the switch inward introduces stop/guide and bench-mount constraints. Its cam and mounting pedestal must be redesigned together. Existing rear bench holes are also close to the relocated support inserts. The sensor lead/connector needs a checked route around the relocated front support.

A simplified 72 mm pocket tool slightly overlaps the existing cam through-hole tool. Actual fillets may prevent a physical opening, so this is a regeneration concern rather than an established failure. The screw itself ends at X75; shortening the unnecessary through-tool extension is one candidate correction.

Thus **138 mm is a target for a new flat variant**, not a claim that changing two width parameters produces a working device. The nominal 30 mm travel, existing spring choices, 20 mm pocket depth and direct force measurement can remain design requirements. Strength, clearance through motion, assembly access, friction, calibration and the user's intended finger contact still need validation.

## What about 100 mm while staying flat?

With the springs and isometric sleeves alongside the full-length finger pocket, the current hardware cannot simply fit into a 100 mm envelope. Even deleting the side-wall thickness would not preserve a 72 mm opening, Ø16 sleeves, current 24 mm supports and normal outer margins at that width.

One different flat architecture moves the springs into a separate bay **along the length** of the device. The grip connects rigidly to the far spring seat using a return cage. Its seat separation can remain `101 − stroke − preload`, so closing the grip still compresses the springs without a reversing pulley. The near-seat reaction must pass through the load cell. A direct connection to the frame would bypass measurement.

This is kinematic feasibility, not a constructed 100 mm model. Keeping the current 101 mm installed spring length in a separate non-overlapping bay uses considerable additional length, before supports, sensor mounts and travel clearance. New cage/guides and smaller palm/enclosure geometry are essential. A width close to 100 mm can therefore be studied while staying flat, but it trades away the current compact length. Different springs or a different resistance mechanism are further redesign options; equivalent force range, stroke and accuracy would have to be established.

For scale, the existing assembly including its enclosure is about 180.1 mm long. Appending only a 101 mm spring gap, two 3 mm seats and 1 mm separation gives **288.1 mm before the omitted support/sensor/end allowances**. Translating the complete current module so that its front wall starts at X125, beyond the present carriage end X124, gives an overall envelope about **327.1 mm** long. Thus **roughly 300–330 mm** is a paper estimate for this particular separate-bay approach, not a minimum for every possible flat mechanism. The 32 mm height is a design target, not a checked complete assembly envelope.

## Decision

For a compact flat device using the existing spring hardware, **start with 138 mm and keep 132 mm as the aggressive alternative**. For a width close to 100 mm, study a longer separate-bay architecture or new resistance hardware. No production CAD, previous feasibility study, electronics package or print package was changed.

The [constraint audit](layout-constraints.json) records the calculations and current-layout conflicts. This study contains no newly regenerated native CAD, complete motion check or structural qualification.
