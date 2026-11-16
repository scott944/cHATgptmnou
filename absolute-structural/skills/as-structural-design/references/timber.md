# Timber - AS 1720.1-2010 (Amd 1-3) and AS 1684

**Status marks.** `[C]` = matched to a published secondary source on 2026-11-16. `[U]` = not
matched - confirm against the standard in the Knowledge Vault. Where sources could not settle
a value, the more conservative figure is used here and in `scripts/as_calc.py`.

Editions: AS 1720.1-2010 with Amendment 3 (2015) `[C]`. AS 1684.2-2021 referenced by NCC 2022
`[C]`. Watch for 1988-edition values in free copies online - k7 and k12 differ.

## Contents
1. Design capacities
2. Capacity factor phi
3. Modification factors k1, k4, k6, k7, k9, k12
4. Characteristic values - MGP, F-grades, glulam, LVL
5. Deflection and creep
6. Combined actions
7. When to use AS 1684 instead

## 1. Design capacities

| Action | Capacity | Clause |
|---|---|---|
| Bending | Md = phi k1 k4 k6 k9 k12 f'b Z | 3.2.1.1 |
| Shear | Vd = phi k1 k4 k6 f's As, As = (2/3) b d | 3.2.5 |
| Bearing perpendicular to grain | Nd,p = phi k1 k4 k6 k7 f'p Ap | 3.2.6.1 |
| Bearing parallel to grain | Nd,l = phi k1 k4 k6 f'l Al | 3.2.6.2 |
| Compression | Nd,c = phi k1 k4 k6 k12 f'c Ac `[C]` | 3.3.1.1 |
| Tension | Nd,t = phi k1 k4 k6 f't At | 3.4.1 |

Forms other than compression are `[U]` but standard. Rectangular section: Z = bd^2/6,
I = bd^3/12. Notches reduce shear capacity sharply (Cl 3.2.5) - avoid at supports or check.

## 2. Capacity factor phi - Table 2.1

Category 1 = house, secondary members (joists, rafters, studs). Category 2 = house primary
members (bearers, lintels, girders, posts) and secondary members in other buildings.
Category 3 = primary members in other buildings and post-disaster structures.

| Material | Cat 1 | Cat 2 | Cat 3 | Status |
|---|---|---|---|---|
| Sawn: MGP15 and higher, A17, F17 and higher | 0.95 | 0.85 | 0.75 | `[U]` |
| Sawn: MGP12 and lower, F14 and lower | 0.90 | 0.70 | 0.60 | `[U]` - conservative row; some sources use 0.90/0.85/0.75. Confirm, and override with `--phi` if the vault copy says otherwise |
| Glulam | 0.95 | 0.85 | 0.75 | Cat 1 `[C]`, others `[U]` |
| LVL | 0.95 | 0.90 | 0.80 | `[C]` |
| Structural plywood | 0.95 | 0.85 | 0.75 | `[C]` single source |

Joints have their own factors in Table 2.2.

## 3. Modification factors

**k1 duration of load - Table 2.3**

| Duration | Timber strength | Connections `[U]` |
|---|---|---|
| 5 seconds (wind gust) | 1.00 `[C]` | 1.14 |
| 5 minutes | 1.00 `[U]` | 1.00 |
| 5 hours | 0.97 `[U]` | 0.86 |
| 5 days (roof imposed, floor point load) | 0.94 `[C]` | 0.77 |
| 5 months (floor imposed) | 0.80 `[C]` | 0.69 |
| 50+ years (permanent) | 0.57 `[C]` | 0.57 |

Use the k1 of the shortest-duration action in each combination, and check every combination:
1.35G with 0.57 `[C]`; 1.2G + 1.5Q floor with 0.80; 1.2G + 1.5 psi_l Q with 0.57; roof
imposed with 0.94; any wind combination with 1.00. The governing case is the largest
action / k1.

**k4 moisture.** Seasoned timber staying dry: 1.0. Seasoned timber in service above 15% EMC:
1 - 0.3(EMC - 15)/10, not less than 0.7 `[U]`. Unseasoned timber that will dry under load,
by least dimension: 38 mm 1.15, 50 mm 1.10, 75 mm 1.05, 100 mm and over 1.00 `[U]`.

**k6 temperature.** 0.9 for seasoned timber in coastal Queensland north of 25 deg S and all
areas north of 16 deg S; otherwise 1.0 `[U]`. NSW: 1.0.

**k7 bearing length - Table 2.6 `[C]`.** Only where the bearing is 75 mm or more from the end
of the member; otherwise 1.0.

| Bearing length mm | 12 | 25 | 50 | 75 | 125 | 150+ |
|---|---|---|---|---|---|---|
| k7 | 1.75 | 1.40 | 1.20 | 1.15 | 1.10 | 1.00 |

**k9 strength sharing - Cl 2.4.5 `[U]`.** Sawn timber only (1.0 for glulam and LVL).
k9 = g31 + (g32 - g31)(1 - 2s/L), not less than 1.0. g31 is read for ncom (members fixed
together to act as one), g32 for ncom x nmem (parallel members sharing load through decking
or battens), s = spacing, L = span.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10+ |
|---|---|---|---|---|---|---|---|---|---|---|
| g31, g32 | 1.00 | 1.14 | 1.20 | 1.24 | 1.26 | 1.28 | 1.30 | 1.31 | 1.32 | 1.33 |

**k12 stability - Cl 3.2.4 (beams), 3.3.3 (columns) `[C]`**

| rho x S | k12 |
|---|---|
| up to 10 | 1.0 |
| 10 to 20 | 1.5 - 0.05 rho S |
| 20 and over | 200 / (rho S)^2 |

Beam slenderness S1, Cl 3.2.3.2 `[U]`:
- compression edge restrained at spacing Lay: S1 = 1.25 (d/b) (Lay/d)^0.5
- tension edge restrained at spacing Lay: S1 = (d/b)^1.35 (Lay/d)^0.25
- compression edge continuously restrained: S1 = 0
- tension edge continuously restrained: S1 = 2.25 d/b

Flooring or roof battens nailed to the compression edge count as restraint. Plasterboard
does not. Under wind uplift the bottom edge is the compression edge.

Column slenderness, Cl 3.3.2 `[U]`: S3 = lesser of Lax/d and g13 L/d (major axis);
S4 = lesser of Lay/b and g13 L/b (minor axis). g13: both ends fixed in position and direction
0.7; each end held by two bolts 0.75; one end fixed, other pinned 0.85; studs in light framing
0.9; pinned both ends 1.0; free-standing flagpole 2.0. Keep S to 50 or less.

Material constants, Appendix E, seasoned timber (r = temporary load / total load, 0.25 is a
common assumption):
- rho_b = 14.71 (E/f'b)^-0.480 r^-0.061 (coefficient and first exponent `[C]`, r term `[U]`)
- rho_c = 11.39 (E/f'c)^-0.408 r^-0.074 `[U]`

Glulam takes rho from Tables 7.2(A)/(B) and LVL from its own section - use those where
available rather than the formulas above.

## 4. Characteristic values (MPa)

**MGP seasoned pine - Table H3.1.** f'b, E, G for the small sizes `[C]`; everything else,
including the reductions for deeper sections, `[U]`.

| Grade | Depth mm | f'b | f't | f's | f'c | E | G |
|---|---|---|---|---|---|---|---|
| MGP10 | 70-140 | 17 | 7.7 | 2.6 | 18 | 10 000 | 670 |
| | 190 | 16 | 7.1 | 2.5 | 18 | | |
| | 240 | 15 | 6.6 | 2.4 | 17 | | |
| | 290 | 14 | 6.1 | 2.3 | 16 | | |
| MGP12 | 70-140 | 28 | 12 | 3.5 | 24 | 12 700 | 850 |
| | 190 | 25 | 12 | 3.3 | 23 | | |
| | 240 | 24 | 11 | 3.2 | 22 | | |
| | 290 | 22 | 9.9 | 3.1 | 22 | | |
| MGP15 | 70-140 | 39 | 18 | 4.3 | 30 | 15 200 | 1010 |
| | 190 | 36 | 17 | 4.1 | 29 | | |
| | 240 | 33 | 16 | 4.0 | 28 | | |
| | 290 | 31 | 14 | 3.8 | 27 | | |

f'p = 10 MPa, joint group JD5 (MGP10) / JD4 (MGP12, MGP15), density about 500/540/570 kg/m3
`[U]`.

**F-grades - Table H2.1.** F8 and F17 partly `[C]`; the rest `[U]`. f't given as
hardwood / softwood.

| Grade | f'b | f't | f's | f'c | E | G |
|---|---|---|---|---|---|---|
| F5 | 14 | 8.4 / 7.3 | 1.8 | 11 | 6 900 | 460 |
| F7 | 18 | 11 / 8.9 | 2.1 | 13 | 7 900 | 530 |
| F8 | 22 | 13 / 11 | 2.2 | 18 | 9 100 | 610 |
| F11 | 31 | 18 / 15 | 2.8 | 22 | 10 500 | 700 |
| F14 | 36 | 22 / 19 | 3.3 | 27 | 12 000 | 800 |
| F17 | 42 | 25 / 22 | 3.6 | 34 | 14 000 | 930 |
| F22 | 55 | 34 / 29 | 4.2 | 42 | 16 000 | 1070 |
| F27 | 67 | 42 / 34 | 5.1 | 51 | 18 500 | 1230 |

Bearing f'p for F-graded timber depends on the species strength group (Table H2.2), not the
F-grade - get it from the vault or the supplier. Plywood F-grades are a different table
(Table 5.1); don't mix them with these.

**Glulam - Table 7.1 `[C]`** (2010 edition values; GLTAA and some supplier sheets quote an
older, higher set - don't mix them).

| Grade | f'b | f't | f's | f'c | E | G |
|---|---|---|---|---|---|---|
| GL8 | 19 | 6 | 3.7 | 14 | 8 000 | 530 |
| GL10 | 22 | 8 | 3.7 | 18 | 10 000 | 670 |
| GL12 | 25 | 11 | 4.2 | 22 | 11 500 | 770 |
| GL13 | 33 | 16 | 4.2 | 26 | 13 300 | 900 |
| GL17 | 40 | 20 | 4.2 | 33 | 16 700 | 1110 |
| GL18 | 45 | 25 | 5.0 | 45 | 18 500 | 1230 |

Bending values for members deeper than 300 mm take a size reduction - check the clause.

**LVL, I-joists, proprietary products.** No generic grades: every manufacturer publishes its
own characteristic values and span tables. Fetch the current product guide (or find it in
the vault) and pass the values with `--fb --fs --fc --fp --E --phi`.

## 5. Deflection and creep

Long-term deflection = j2 x short-term deflection of the sustained load. Table 2.4 `[C]`:

| Initial moisture | Load under 1 day | Load 1 year or more |
|---|---|---|
| Seasoned (15% or less) | 1.0 | 2.0 |
| Unseasoned (25% or more) | 1.0 | 3.0 |

Tension members: j3 = 1.0 seasoned, 1.5 unseasoned long term `[C]`.

Total long-term = j2 x deflection(G + psi_l Q) + deflection((psi_s - psi_l) Q). Use the
lower-bound E where a single member is critical. Limits: `loads.md`.

## 6. Combined actions - Cl 3.5 `[U]`

Bending and compression, both to hold:
- (M*x / Md,x)^2 + N*c / Nd,cy <= 1
- M*x / Md,x + N*c / Nd,cx <= 1

Bending and tension: k12 M*x / Md,x + N*t / Nd,t <= 1.

## 7. When to use AS 1684 instead

For houses within AS 1684's limits (wind class to N4 in Part 2, roof pitch to 35 degrees,
spans and loads in the tables), the span tables are deemed-to-satisfy and are what a
certifier expects. Use first principles for: members outside the tables, concentrated loads
from girder trusses or upper-storey posts, steel-timber combinations, and when checking why
a tabulated size was chosen. AS 1684 also covers what a member calc does not: bracing,
tie-down and nailing schedules.
