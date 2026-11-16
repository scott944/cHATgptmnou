# Structural steel - AS 4100:2020

**Status marks.** `[C]` = matched to a published secondary source on 2026-11-16. `[U]` = not
matched - confirm against the standard in the Knowledge Vault.

Editions: AS 4100:2020 incl. Amd 1 (2021), referenced by NCC 2022 `[C]`. Fabrication
AS/NZS 5131:2016 Amd 1 `[C]`; welding AS/NZS 1554.1:2014 `[C]`; cold-formed AS/NZS 4600:2018
(purlins, girts, light gauge - not covered here). Clause numbers in Section 9 moved between
the 1998 and 2020 editions; older guides cite the old ones.

Constants: E = 200 000 MPa, G = 80 000 MPa, density 7850 kg/m3.

## Contents
1. Capacity factors
2. Steel grades
3. Bending - section capacity
4. Bending - member capacity (lateral buckling)
5. Shear and bearing
6. Axial tension and compression
7. Combined actions
8. Bolts
9. Welds
10. Section properties and test values

## 1. Capacity factors - Table 3.4

| Element | phi | Status |
|---|---|---|
| Members (bending, shear, axial) | 0.90 | `[U]` (reproduces published phi Ms) |
| Bolts | 0.80 | `[C]` |
| Ply in bearing | 0.90 | `[C]` |
| Fillet welds, SP category | 0.80 | `[C]` |
| Fillet welds, GP category | 0.60 | `[C]` |
| Complete penetration butt weld, SP | 0.90 | `[U]` - sources conflict (0.80 also quoted) |

## 2. Steel grades - yield fy / tensile fu, MPa

| Product | Grade | fy by thickness | fu | Status |
|---|---|---|---|---|
| Hot-rolled UB, UC, PFC, angles (AS/NZS 3679.1) | 300 (300PLUS) | 320 (t < 11); 300 (11 to 17); 280 (t > 17) | 440 | `[U]`; boundary at 11 mm checked against a published phi Ns |
| | 350 | 360 (t <= 11); 340 (11 to 40) | 480 | `[U]` |
| Cold-formed SHS, RHS, CHS (AS/NZS 1163) | C350L0 | 350 | 430 | `[C]` |
| | C450L0 | 450 | 500 | `[U]` |
| | C250L0 | 250 | 320 | `[U]` |
| Plate (AS/NZS 3678) | 250 | 280 (t <= 8); 260 (8-12); 250 (12-50) | 410 | `[U]` |
| | 350 | 360 (t <= 12); 350 (12-20); 340 (20-80) | 450 | `[U]` |

Flange and web of a UB can have different fy (thickness-based) - use each where it applies.

## 3. Bending - section capacity, Cl 5.2

Ms = fy Ze; design capacity phi Ms.

Element slenderness lambda_e = (b/t) sqrt(fy/250). Limits, Table 5.2:

| Element | lambda_ep | lambda_ey | Status |
|---|---|---|---|
| Flange outstand, uniform compression, hot-rolled | 9 | 16 | `[U]` |
| Flange outstand, welded (HW) | 8 | 14 | `[C]` |
| Flange outstand, lightly welded / cold-formed | 8 | 15 | `[U]` |
| Plate supported both edges, uniform compression, hot-rolled | 30 | 45 | `[U]` |
| Same, cold-formed (RHS/SHS walls) | 30 | 40 | `[U]` |
| Web in bending, both edges supported | 82 | 115 | `[C]` |
| CHS, lambda = (do/t)(fy/250) | 50 | 120 | `[U]` |

The section slenderness is that of the element with the largest lambda_e / lambda_ey.
- Compact (lambda_s <= lambda_sp): Ze = lesser of S and 1.5Z
- Non-compact: Ze = Z + [(lambda_sy - lambda_s)/(lambda_sy - lambda_sp)] (Zc - Z), Zc = compact value
- Slender (flat plate in uniform compression): Ze = Z (lambda_sy / lambda_s)

Published tables list Zex directly - prefer that to calculating it.

## 4. Bending - member capacity, Cl 5.6 `[U]` (arithmetic cross-checked)

Mb = alpha_m alpha_s Ms, not more than Ms.

- alpha_s = 0.6 { sqrt[(Ms/Moa)^2 + 3] - Ms/Moa }
- Moa = Mo = sqrt{ (pi^2 E Iy / le^2) [ G J + pi^2 E Iw / le^2 ] }
- le = kt kl kr L, L = segment length between restraints

alpha_m = 1.7 M*m / sqrt(M*2^2 + M*3^2 + M*4^2), not more than 2.5 (moments at the quarter
points and mid-point of the segment), or from Table 5.6.1:

| Segment loading | alpha_m |
|---|---|
| Uniform moment | 1.00 `[C]` |
| UDL, simply supported, restrained at ends only | 1.13 |
| Central point load, restrained at ends only | 1.35 |
| Cantilever, tip load | 1.25 |
| Cantilever, UDL | 2.25 |

Effective length factors, Tables 5.6.3:

| Factor | Value |
|---|---|
| kt twist | 1.0 for FF, FL, LL, FU. For FP, PL, PU: 1 + [(d1/L)(tf/2tw)^3]/nw. For PP: 1 + [2(d1/L)(tf/2tw)^3]/nw |
| kl load height | 1.0 load at shear centre or below. Gravity load on top flange within the segment: 1.4 (2.0 for FU, PU) |
| kr lateral rotation | 1.0 none; 0.85 one end restrained; 0.70 both ends |

F = fully restrained end, P = partial, L = lateral only, U = unrestrained. A beam built into
a floor that restrains the compression flange continuously has le = 0 and Mb = Ms. A lintel
or a beam with joists hung off the side usually does not - the restraint has to hold the
compression flange.

## 5. Shear and bearing `[U]`

- Web shear, Cl 5.11: Vw = 0.6 fy Aw where dp/tw <= 82/sqrt(fy/250). Aw = d x tw for
  hot-rolled sections (full depth). Design capacity phi Vv.
- Non-uniform shear stress: Vv = 2Vu/(0.9 + f*vm/f*va), not more than Vu.
- Shear with bending, Cl 5.12.3: full Vv where M* <= 0.75 phi Ms; otherwise
  Vvm = Vv [2.2 - 1.6 M*/(phi Ms)].
- Web bearing yield, Cl 5.13.3: Rby = 1.25 bbf tw fy, bbf = stiff bearing length plus
  dispersion at 1:2.5 through the flange.
- Web bearing buckling, Cl 5.13.4: web treated as a strut of area tw x bb, slenderness
  le/r = 2.5 d1/tw, alpha_b = 0.5, kf = 1.0.

## 6. Axial

**Tension, Cl 7.2 `[U]`:** Nt = lesser of Ag fy and 0.85 kt An fu.

**Compression, Section 6 `[U]` (arithmetic cross-checked):**
- Section: Ns = kf An fy
- Member: Nc = alpha_c Ns, not more than Ns
- lambda_n = (le/r) sqrt(kf) sqrt(fy/250)
- alpha_a = 2100 (lambda_n - 13.5) / (lambda_n^2 - 15.3 lambda_n + 2050)
- lambda = lambda_n + alpha_a alpha_b
- eta = 0.00326 (lambda - 13.5), not less than 0
- xi = [(lambda/90)^2 + 1 + eta] / [2 (lambda/90)^2]
- alpha_c = xi { 1 - sqrt[ 1 - (90/(xi lambda))^2 ] }

alpha_b, Table 6.3.3 (kf = 1.0):

| Section | alpha_b |
|---|---|
| Hot-formed RHS, CHS | -1.0 |
| Cold-formed RHS, SHS, CHS (not stress relieved) | -0.5 |
| Hot-rolled UB, UC, flange up to 40 mm | 0 |
| Welded I/H from flame-cut plate | 0 |
| Tees, angles, channels; hot-rolled UB/UC flange over 40 mm | 0.5 |
| Welded I/H with flange over 40 mm | 1.0 |

Effective length le = ke L: pinned-pinned 1.0, fixed-pinned 0.85, fixed-fixed 0.7, cantilever
2.2 (Fig 4.6.3.2 `[U]`). A post on a bolted base plate with a beam sitting on top is
pinned-pinned unless the frame is shown to restrain it.

## 7. Combined actions - Section 8 `[U]`

- Section: N*/(phi Ns) + M*x/(phi Msx) + M*y/(phi Msy) <= 1
- In-plane member: Mi = Ms (1 - N*/(phi Nc))
- Out-of-plane member: Mox = Mbx (1 - N*/(phi Ncy))
- Biaxial: [M*x/(phi Mcx)]^1.4 + [M*y/(phi Miy)]^1.4 <= 1

A post carrying a beam on a cap plate should be checked for the reaction applied at an
eccentricity (commonly 100 mm from the column face for simple construction, Cl 4.3.4 `[U]`).

## 8. Bolts - Cl 9.2.2 (2020 numbering `[C]`; 9.3.2 in 1998)

- Shear: Vf = 0.62 fuf kr (nn Ac + nx Ao) (0.62 factor confirmed by back-calculating
  published capacities)
- Tension: Ntf = As fuf
- Combined: (V*/(phi Vf))^2 + (N*/(phi Ntf))^2 <= 1
- Ply bearing: Vb = 3.2 df tp fup; tear-out: Vb = ae tp fup (phi 0.9)
- fuf: Grade 4.6 = 400 MPa; Grade 8.8 = 830 MPa

Areas mm2 and design capacities kN (phi = 0.8), threads included (N) / excluded (X) `[U]`,
arithmetic consistent:

| Bolt | Ac core | Ao shank | As tensile | 4.6/S phi Vfn / Vfx / Ntf | 8.8/S phi Vfn / Vfx / Ntf |
|---|---|---|---|---|---|
| M12 | 76.2 | 113 | 84.3 | 15.1 / 22.4 / 27.0 | - |
| M16 | 144 | 201 | 157 | 28.6 / 39.9 / 50.2 | 59.3 / 82.7 / 104 |
| M20 | 225 | 314 | 245 | 44.6 / 62.3 / 78.4 | 92.6 / 129 / 163 |
| M24 | 324 | 452 | 353 | 64.3 / 89.7 / 113 | 133 / 186 / 234 |

Minimum edge distance and pitch: Cl 9.5 (about 1.5 df to a rolled edge, 2.5 df pitch `[U]`).

## 9. Fillet welds - Cl 9.6.3.10 (2020 `[C]`; 9.7.3.10 in 1998)

Capacity per unit length: phi vw = phi 0.6 fuw tt kr, tt = leg size / sqrt(2) `[C]`.

fuw for E48XX / W50X electrodes: 480 MPa in the 1998 edition; sources disagree on whether the
2020 table gives 480 or 490 `[U]`. Using 480 (conservative):

| Leg mm | SP (phi 0.8) kN/mm | GP (phi 0.6) kN/mm |
|---|---|---|
| 5 | 0.815 | 0.611 |
| 6 | 0.978 | 0.733 |
| 8 | 1.30 | 0.978 |
| 10 | 1.63 | 1.22 |

## 10. Section properties and test values

The calculator takes section properties as inputs. Get them from the manufacturer's current
tables (InfraBuild / Liberty for hot-rolled, Austube Mills for hollow sections) or ASI Design
Capacity Tables in the vault. Units in those tables are 10^6 mm4, 10^3 mm3, 10^9 mm6.

Values to test the calculator against:

| Section | Input | Result | Status |
|---|---|---|---|
| 310UB40.4 Gr 300: d 304, bf 165, tf 10.2, tw 6.1, Ix 86.4e6, Zx 569e3, Sx 633e3, Iy 7.65e6, J 157e3, Iw 165e9, fy 320 | section | phi Msx = 182 kNm | `[C]` published 182.2 |
| | shear | phi Vv = 320 kN | calculated |
| | le = 2 / 4 / 6 m, alpha_m = 1 | phi Mbx = 155.9 / 101.7 / 67.4 kNm | calculated two ways, not read from DCT |
| 89x89x5.0 SHS C350: Ag 1590, r 33.7 | le = 3 m, alpha_b -0.5 | phi Ns = 501, phi Nc = 281 kN | properties `[C]`, capacity calculated |
