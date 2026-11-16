---
name: as-structural-design
description: Structural member design and checking to Australian Standards - timber (AS 1720.1, AS 1684), reinforced concrete (AS 3600, AS 2870) and structural steel (AS 4100), with loads from AS/NZS 1170 and AS 4055. Use this whenever Scott asks to size, check, design or justify a beam, joist, rafter, lintel, bearer, post, column, slab, footing, bolt or weld, asks for a capacity, span, deflection, load combination, k-factor, phi factor, cover or lap length, wants a structural calc sheet or engineering notes for council/certifier documentation, or mentions any of those standards, MGP/F-grade/GL/LVL timber, UB/UC/PFC/SHS/RHS steel sections or N-bar/mesh reinforcement - even if they don't say "Australian Standards" or "structural design".
---

# Structural design to Australian Standards

For Scott at Absolute Drafting (NSW): residential and light commercial members in timber,
concrete and steel. Limit states design throughout. The output is a calc he can paste into a
report, a drawing note or a letter to council or a certifier.

## Where the numbers come from

Design values get copied into documents that people build from, so every factor and formula
needs a known source. Work down this list and say in the calc which one you used:

1. **Scott's Knowledge Vault** - `D:\Knowledge Vault 2026\` on his PC, read through Desktop
   Commander. Search it for the standard number (`AS 1720`, `AS 4100`, `AS 3600`, `1170`,
   `1684`, `2870`) and for span tables or manufacturer data before using anything else. His
   copies are the purchased standards and outrank this skill. If the vault can't be reached
   (cloud session, Desktop Commander not connected), say so in one line and carry on.
2. **This skill's `references/`** - formulas, factors and tables with clause numbers. Each
   value carries `[C]` (matched to a published source) or `[U]` (not matched - written from
   memory of the standard). A `[U]` value that the result depends on goes in the calc's
   Assumptions list with "confirm against the standard", and when the vault is reachable,
   check it there and tell Scott if the reference file is wrong so it can be corrected.
3. **Fetch** - manufacturer literature (section properties, LVL/I-joist data, proprietary
   connectors), WoodSolutions, ASI, SRIA, CCAA, the NCC. Standards themselves are paywalled;
   don't present a secondary source as the standard.

If a value can't be found in any of the three, say so and ask Scott for it, or carry a
clearly labelled assumption. Don't fill the gap from memory - a plausible-looking k-factor is
worse than a blank.

## Which file to read

| Task | Read |
|---|---|
| Any design - loads, combinations, psi factors, wind class, deflection limits | `references/loads.md` |
| Timber by calculation: joists, bearers, rafters, lintels, posts, studs, glulam, LVL | `references/timber.md` |
| House framing by span table, wall bracing, tie-down, framing schedule | `references/as1684.md` |
| Steel: UB/UC/PFC beams, SHS/RHS posts, lintels, bolts, welds | `references/steel.md` |
| Concrete: slabs, beams, columns, footings, cover, laps, site class | `references/concrete.md` |

Read `loads.md` plus the one file for the job. Don't load them all.

## Workflow

1. **Pin down the member.** Span and support conditions, what it carries (tributary width or
   area, what sits on it, point loads from above), restraint (what stops it buckling
   sideways), exposure, and the building's use and importance level. Ask for what's missing
   only if it changes the answer; otherwise assume, and list the assumption.
2. **Build the loads** from the layers actually present (roof, ceiling, floor, walls), not a
   lump guess. Show kPa x tributary width = kN/m. `references/loads.md`.
3. **Combine** to AS/NZS 1170.0. Timber needs every combination checked against its own k1 -
   the long-term case often governs over the bigger short-term load.
4. **Check strength** with `scripts/as_calc.py` (below) so the arithmetic is reproducible, then
   read the output critically: are the restraint and bearing assumptions the real ones?
5. **Check serviceability.** Deflection governs most domestic timber and many steel beams.
   Include creep (j2 for timber, long-term multiplier for concrete).
6. **Check what the member bears on and is fixed with** - bearing length, the post and footing
   under it, tie-down for uplift. A beam that works on paper but crushes its support hasn't
   been designed.
7. **Report** in the format below.

## The calculator

`scripts/as_calc.py` produces a markdown calc sheet with clause references and utilisation
ratios. Python 3, no dependencies. Run `python scripts/as_calc.py <command> -h` for inputs.

| Command | Covers |
|---|---|
| `combos` | AS/NZS 1170.0 strength and serviceability combinations |
| `timber-beam` | AS 1720.1 bending, shear, bearing, k9, k12, deflection with creep |
| `timber-column` | AS 1720.1 compression with slenderness |
| `steel-beam` | AS 4100 section class, phi Ms, phi Mb (alpha_m, alpha_s), shear, deflection |
| `steel-column` | AS 4100 phi Ns, phi Nc about both axes |
| `rc-beam` | AS 3600 flexure, ku, minimum steel, shear (simplified method); `--slab` for slab strips |
| `as1684-widths` | AS 1684.2 floor, roof and ceiling load widths for span-table lookup |
| `as1684-bracing` | AS 1684.2 racking force against bracing wall capacity, one wind direction |
| `as1684-tiedown` | AS 1684.2 uplift force at a tie-down connection |

```bash
# 240x45 MGP10 floor joists at 450 crs, 4.2 m span, 1.5 kPa imposed
python scripts/as_calc.py timber-beam --b 45 --d 240 --span 4200 --grade MGP10 \
  --G 0.4 --Q 0.68 --use floor --nmem 5 --spacing 450 --bearing 45

# 310UB40.4 Grade 300, 6 m span restrained at mid-span, UDL on top flange
python scripts/as_calc.py steel-beam --name 310UB40.4 --d 304 --bf 165 --tf 10.2 --tw 6.1 \
  --Zx 569e3 --Sx 633e3 --Ix 86.4e6 --Iy 7.65e6 --J 157e3 --Iw 165e9 --fyf 320 \
  --L 3000 --span 6000 --kl 1.4 --alpha_m 1.13 --w 25 --ws 14
```

The beam commands assume a simply supported span under UDL. For anything else (point loads,
cantilevers, continuous spans) work out M* and V* by hand, show that working, and pass
`--Mstar`/`--Vstar`. Steel section properties come from the manufacturer's tables (fetch them
or get them from the vault) - the script doesn't carry a section library, so nothing is
silently assumed.

The script is a tool, not the designer. It doesn't know that the lintel also takes a girder
truss, that the "continuous restraint" is plasterboard, or that the slab is on reactive clay.

## Report format

Use this structure so calcs read the same from job to job:

```
# [Job number] - [Member] - Structural check
Standards: [list with editions]        Source of values: [vault / skill reference / fetched]

## 1. Member and assumptions
## 2. Loads               (layer by layer, kPa -> kN/m)
## 3. Design actions      (combinations, M*, V*, N*)
## 4. Strength            (capacity, clause, utilisation)
## 5. Serviceability      (deflection vs stated limit)
## 6. Supports and connections
## 7. Result              (adopted size, grade, fixing; what still needs checking)
## Assumptions and limits (numbered)
```

Australian English, SI units, kN and mm. Give utilisation as a ratio and say plainly whether
it passes. If it fails, don't stop there - say what would make it work (next size, higher
grade, closer spacing, an added restraint) and re-run it.

Where a job number is given, save the calc into that job's `Claude` subfolder (create it if
needed), not loose in the job folder. Vault files are append-only.

## Being straight with Scott

He wants shaky thinking challenged, so:

- If the member fails or the request doesn't stack up, say so first, then give the fix.
- Name the two or three things most likely to be wrong in this particular calc (usually
  restraint, load path, and bearing/tie-down), not a generic disclaimer.
- Never quietly swap what was asked for - a different grade, size, standard or method gets
  flagged as a change, with the reason.
- If the problem is outside what can be checked reliably here, stop and say what's needed.

## Scope and sign-off

This skill covers member-level design of ordinary building elements. It gives preliminary
sizing and supporting calculations. It is not a substitute for a structural engineer's design
and certification where the job needs one - which in NSW is most structural work going to a
certifier, anything in a Class 2 building (Design and Building Practitioners Act), and
anything unusual. Say once, in the Result section, whether the element is one that normally
needs an engineer's certificate; don't repeat it through the calc.

Take particular care, and recommend an engineer rather than pressing on, with: transfer
structures, retaining walls over about 1 m or with surcharge, anything in bushfire-, flood-
or mine-subsidence-affected land where the structure is part of the response, lateral
stability and bracing of the whole building, earthquake design, post-tensioning, fatigue, and
fire-rated structure.

Deemed-to-satisfy span tables (AS 1684, manufacturers' tables) are often the right answer for
housing and are quicker and more defensible than a first-principles calc. Offer that route
when the member falls inside their limits; use first principles when it doesn't, or when
Scott wants the working. The AS 1684.2 span tables are not bundled: sizes are read from the
vault copy or a manufacturer's table, never recalled. For a whole-house framing job, fill in
`assets/as1684-framing-schedule.md` (member schedule, bracing, tie-down) rather than writing
separate calcs per member.
