# Concrete - AS 3600:2018 (Amd 1 2018, Amd 2 2021) and AS 2870-2011

**Status marks.** `[C]` = matched to a published secondary source on 2026-11-16. `[U]` = not
matched - confirm against the standard in the Knowledge Vault.

Amendment 2 (May 2021) changed the shear rules and the column phi. Whether NCC 2022
references Amd 2 was not confirmed - check NCC Schedule 2. The shear items marked "Amd 2"
below need reading from the amendment itself before a tight shear design is relied on.

## Contents
1. Capacity reduction factors
2. Material properties, bars and mesh
3. Durability and cover
4. Flexure
5. Shear
6. Slabs - minimum steel, shrinkage, punching, deflection
7. Columns
8. Anchorage and laps
9. Residential slabs and footings - AS 2870

## 1. Capacity reduction factors - Table 2.2.2

| Action | phi | Status |
|---|---|---|
| Bending, Class N steel | 0.85 where kuo <= 0.36; otherwise 1.24 - 13kuo/12, between 0.65 and 0.85 | `[U]` |
| Bending, Class L mesh as main steel | 0.65 | `[U]` |
| Shear and torsion | 0.75 (0.7 in 2009) | `[U]` |
| Axial compression | 0.65 (0.6 in 2009); Amd 2 applies a modifier k_phi that reduces it for slender columns or Q/G <= 0.25 | `[C]` |
| Bearing | 0.60 | `[U]` |
| Axial tension | 0.85 | `[U]` |
| Plain concrete | 0.60 | `[U]` |

## 2. Materials

- f'ct.f = 0.6 sqrt(f'c) (flexural tensile); f'ct = 0.36 sqrt(f'c) `[U]`
- Density 2400 kg/m3 plain; 25 kN/m3 reinforced for loads
- Reinforcement: D500N bars and D500L mesh, fsy = 500 MPa, Es = 200 000 MPa

Ec, Table 3.1.2 (25 and 32 MPa `[C]`, others `[U]`):

| f'c MPa | 20 | 25 | 32 | 40 | 50 | 65 |
|---|---|---|---|---|---|---|
| Ec MPa | 24 000 | 26 700 | 30 100 | 32 800 | 34 800 | 37 400 |

Bar areas mm2 `[U]` (design tables round to the bracketed values):

| N10 | N12 | N16 | N20 | N24 | N28 | N32 | N36 |
|---|---|---|---|---|---|---|---|
| 78 | 113 (110) | 201 (200) | 314 (310) | 452 (450) | 616 (620) | 804 (800) | 1020 |

Mesh, mm2 per metre width `[U]`:

| SL62 | SL72 | SL82 | SL92 | SL102 | SL81 |
|---|---|---|---|---|---|
| 141 | 179 | 227 | 290 | 354 | 454 |

| RL718 | RL818 | RL918 | RL1018 | RL1118 | RL1218 |
|---|---|---|---|---|---|
| 358 | 454 | 574 | 709 | 899 | 1112 |

RL mesh cross wires give 227 mm2/m. Mesh is Class L (low ductility): phi = 0.65 when it is
the main flexural steel and no moment redistribution.

## 3. Durability and cover - Section 4

| Class | Typical exposure | Min f'c |
|---|---|---|
| A1 | Interior, residential; in non-aggressive soil with membrane | 20 |
| A2 | Interior non-residential; exterior inland, non-industrial, temperate | 25 |
| B1 | Exterior near-coastal (1-50 km from the coast); industrial | 32 |
| B2 | Coastal (within 1 km, not tidal or splash) | 40 |
| C1, C2 | Spray zone; tidal and splash zone | 50 |

Cover mm for standard formwork and compaction, Table 4.10.3.2. Bracketed values and A2 at
40 MPa `[C]`; rest `[U]`.

| Class | f'c 20 | 25 | 32 | 40 | 50 |
|---|---|---|---|---|---|
| A1 | 20 | 20 | 20 | 20 | 20 |
| A2 | (50) | 30 | 25 | 20 | 20 |
| B1 | - | (60) | 40 | 30 | 25 |
| B2 | - | - | (65) | 45 | 35 |
| C1 | - | - | - | (70) | 50 |
| C2 | - | - | - | - | 65 |

Bracketed = only where the concession for that lower strength applies. Cast against ground:
add 10 mm with a damp-proof membrane, 20 mm without `[U]`. Cover must also satisfy bar
diameter (not less than db) and fire (Section 5). Most of coastal NSW is B1; within 1 km of
surf is B2.

## 4. Flexure - Cl 8.1

Rectangular stress block `[U]`:
- alpha2 = 0.85 - 0.0015 f'c, not less than 0.67
- gamma = 0.97 - 0.0025 f'c, not less than 0.67
- Neutral axis: dn = ku d = Ast fsy / (alpha2 f'c gamma b)
- Mu = Ast fsy (d - gamma ku d / 2)
- Ductility: kuo <= 0.36, otherwise compression steel is needed (Cl 8.1.5)

Quick sizing: Ast ~ M* / (phi fsy 0.9 d), then check properly.

Minimum tension steel, Cl 8.1.6.1 `[U]`: Ast,min = 0.20 (D/d)^2 (f'ct.f / fsy) bw d.

Crack control in beams: bar spacing not more than 300 mm, and keep steel stress within the
Cl 8.6 limits for the bar size.

## 5. Shear - Cl 8.2 (2018 method)

V* <= phi Vu, Vu = Vuc + Vus, not more than Vu.max.

- Vuc = kv bv dv sqrt(f'c), with sqrt(f'c) not more than 8 MPa `[C]`
- dv = greater of 0.72D and 0.9d `[U]`
- Vus = (Asv fsy.f dv / s) cot(theta_v) `[U]`
- Vu.max = 0.55 f'c bv dv cot(theta_v) / (1 + cot^2(theta_v)) for vertical ligatures; **Amd 2
  reduced this limit by 10%** `[C]` - the calculator uses 0.9 x 0.55; read the exact
  expression from Amd 2

Simplified method, Cl 8.2.4.3 `[C]`: theta_v = 36 degrees; kv = 0.15 where at least minimum
ligatures are provided, otherwise kv = 200/(1000 + 1.3 dv), not more than 0.15 (the cap was
0.10 before Amd 2). Valid for f'c up to 65 MPa, fsy up to 500 MPa, no prestress, axial
tension or torsion.

Minimum ligatures: Asv.min / s = 0.08 sqrt(f'c) bv / fsy.f `[C]` (weak source).

When ligatures are required, Cl 8.2.1.6: where V* > phi Vuc, and in any beam with D > 750
`[C]`. The 0.5 phi Vuc trigger is the 2009 rule. **Amd 2** added a factor ks reducing the
no-ligature limit and requires ligatures in beams deeper than 300 mm even where V* is below
phi Vuc `[C]` - wording not seen. Practical rule: every beam gets at least minimum ligatures.

Spacing: not more than 0.5D or 300 mm (0.75D or 500 mm in low-shear regions) `[U]`. The
critical section is at dv from the face of a support for loads applied to the top.

## 6. Slabs

- Minimum flexural steel, Cl 9.1.1 `[U]`: 0.19 (D/d)^2 f'ct.f / fsy x b d for slabs on
  beams or walls; 0.24 for flat slabs on columns.
- Bar spacing for crack control: lesser of 2.0D and 300 mm `[U]`.
- Shrinkage and temperature steel, Cl 9.5.3 `[U]`, area = coefficient x b D x 10^-3:

  | Condition | Coefficient |
  |---|---|
  | Unrestrained direction | 1.75 |
  | Restrained, A1/A2, minor / moderate / strong crack control | 1.75 / 3.5 / 6.0 |
  | Restrained, B1 and worse, moderate / strong | 3.5 / 6.0 |

- Shear in one-way slabs: as Section 5 without ligatures; no minimum ligature rule in slabs
  of ordinary thickness.
- Punching shear at columns and point loads, Cl 9.3 `[U]`: Vuo = u dom fcv,
  fcv = 0.17 (1 + 2/beta_h) sqrt(f'c), not more than 0.34 sqrt(f'c); u = perimeter at dom/2
  from the loaded area.
- Deflection limits, Table 2.3.2 `[U]`: total span/250; span/500 where masonry partitions
  have movement provision, span/1000 where they don't; cantilevers span/125.
- Deemed-to-comply span/depth, Cl 9.4.4: Lef/d <= k3 k4 [ (Delta/Lef) Ec / Fd.ef ]^(1/3).
  k4 = 1.4 simply supported, 1.75 end span, 2.1 interior span `[C]`; k3 = 1.0 one-way `[U]`,
  0.95 flat slab without drop panels, 1.05 with `[C]`. Fd.ef = (1.0 + kcs) g + (psi_s +
  kcs psi_l) q; kcs = 2 - 1.2 Asc/Ast, not less than 0.8 `[U]`.

## 7. Columns - Section 10

- Squash load: Nuo = alpha1 f'c Ag + As fsy, alpha1 = 1.0 - 0.003 f'c within 0.72 to 0.85 `[U]`
- Minimum design moment: N* x 0.05D about each axis, Cl 10.1.2 `[C]`
- Longitudinal steel between 1% and 4% of Ag `[U]`
- Short column, Cl 10.3.1: braced Le/r <= greater of 25 and alpha_c (38 - f'c/15)(1 +
  M1*/M2*); unbraced Le/r <= 22 `[U]` (form partly `[C]`). Le/r never more than 120.
- Anything beyond a short, braced, lightly loaded column needs an interaction diagram - use
  design software or refer to an engineer.

## 8. Anchorage and laps - Section 13 `[C]`

Basic development length in tension:
Lsy.tb = 0.5 k1 k3 fsy db / (k2 sqrt(f'c)), not less than 0.058 fsy k1 db

- k1 = 1.3 for horizontal bars with more than 300 mm of concrete cast below; otherwise 1.0
- k2 = (132 - db)/100
- k3 = 1.0 - 0.15 (cd - db)/db, between 0.7 and 1.0 (cd = lesser of cover and half the clear spacing)

Lap = k7 Lsy.t, k7 = 1.25 (1.0 where steel provided is at least twice that required and no
more than half is spliced at one section) - confirmed for the 2009 edition.

Rough values for N12 / N16 / N20 bottom bars, f'c 32, k3 = 1.0: Lsy.tb about 440 / 610 / 790
mm; laps about 550 / 760 / 990 mm. Calculate for the actual case.

## 9. Residential slabs and footings - AS 2870-2011

Site classification by characteristic surface movement ys `[U]`:

| Class | Foundation | ys mm |
|---|---|---|
| A | Sand and rock, little or no movement | 0 |
| S | Slightly reactive clay | 0-20 |
| M | Moderately reactive | 20-40 |
| H1 | Highly reactive | 40-60 |
| H2 | Highly reactive | 60-75 |
| E | Extremely reactive | over 75 |
| P | Problem site: soft or collapsing soil, fill, landslip, mine subsidence, abnormal moisture | - |

A "-D" suffix (M-D, H1-D) marks deep-seated moisture change. The class comes from the
geotechnical report, not from a guess. AS 2870 Section 3 gives deemed-to-comply stiffened
raft, waffle raft, footing slab and strip footing details by class and construction type
(clad frame, articulated masonry veneer, masonry veneer, full masonry) - read the beam
depths, mesh and trench mesh from the standard's figures, they are not reproduced here.

Class P, H2 and E sites, slabs with heavy point loads, and anything on fill need an
engineer's design. Typical house slab concrete: N20 minimum (N25 or N32 where the exposure
class or a termite/durability requirement calls for it), 0.2 mm polyethylene membrane, mesh
with 20 mm top cover internal, 40 mm to unprotected ground.
