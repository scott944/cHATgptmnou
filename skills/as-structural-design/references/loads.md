# Loads and combinations - AS/NZS 1170 series, AS 4055, NCC

**Status marks.** `[C]` = matched to a published secondary source (design guide, supplier
table, NCC page) on 2026-11-16. `[U]` = not matched to a source in that check - confirm
against Scott's copy of the standard in the Knowledge Vault before it goes into a document
that matters. When a `[U]` value is used in a calc, list it under Assumptions.

## Editions

| Standard | Edition | Note |
|---|---|---|
| NCC | 2022 in force in NSW (from 1 May 2023) `[C]` | NCC 2025 is published; NSW adoption reported as 1 May 2027 `[C]` - check before relying on it |
| AS/NZS 1170.0 | 2002 + amendments `[U]` | combinations |
| AS/NZS 1170.1 | 2002 + amendments `[U]` | permanent and imposed |
| AS/NZS 1170.2 | 2021 `[C]` | wind; referenced by NCC 2022 |
| AS 1170.4 | 2007 + amendments `[U]` | earthquake |
| AS 4055 | 2021 `[C]` | wind loads for housing |

## Strength combinations - AS/NZS 1170.0 Cl 4.2.2

| Combination | Use |
|---|---|
| 1.35G `[U]` | permanent only |
| 1.2G + 1.5Q `[C]` | permanent + imposed |
| 1.2G + 1.5 psi_l Q `[U]` | long-term imposed |
| 1.2G + Wu + psi_c Q `[U]` | wind downward |
| 0.9G + Wu `[U]` | wind uplift / overturning |
| G + Eu + psi_E Q `[U]` | earthquake |

Stability: destabilising 1.35G, 1.2G + 1.5Q or 1.2G + Wu + psi_c Q against stabilising 0.9G.

## Combination factors - Table 4.1

| Use | psi_s | psi_l | psi_c | psi_E |
|---|---|---|---|---|
| Residential, office, parking, retail floors `[C]` (psi_E `[U]`) | 0.7 | 0.4 | 0.4 | 0.3 |
| Storage and other `[C]` (psi_E `[U]`) | 1.0 | 0.6 | 0.6 | 0.6 |
| Roofs not used as floors `[C]` | 0.7 | 0.0 | 0.0 | 0.0 |

Serviceability: short-term G + psi_s Q; long-term G + psi_l Q; wind Ws.

## Imposed actions - AS/NZS 1170.1 Table 3.1

| Area | kPa | Point load kN | Status |
|---|---|---|---|
| Dwellings, general floors | 1.5 | 1.8 | `[U]` |
| Dwelling balconies | 2.0 | 1.8 (plus 1.5 kN/m at the edge) | `[U]` |
| Dwelling stairs and landings | 2.0 | 2.7 | `[U]` |
| Offices, general | 3.0 | 2.7 | kPa `[C]`, kN `[U]` |
| Retail / shopping | 4.0 | 3.6 | `[C]` |
| Light vehicle garages, car parks | 2.5 | 13 | `[U]` |
| Non-trafficable roof (R2) | 1.8/A + 0.12, not less than 0.25 (A = plan area supported, m2) | 1.4 (1.1 on cladding) | `[U]` |

## Typical permanent actions `[U]`

Build G from the actual layers. Starting values (confirm with product data):

| Item | Value |
|---|---|
| Reinforced concrete | 24-25 kN/m3 (25 used for design) |
| Steel | 77 kN/m3 (7850 kg/m3) |
| Seasoned softwood / hardwood | about 5.5 / 8-11 kN/m3 |
| Sheet metal roof incl. battens | about 0.1 kPa |
| Concrete or terracotta tiles incl. battens | about 0.6 kPa |
| 13 mm plasterboard ceiling incl. battens | about 0.1-0.15 kPa |
| Timber floor: joists + 19-22 mm sheet flooring | about 0.3-0.4 kPa (add tiles/screed if present) |
| Timber stud wall, lined both sides | about 0.3-0.5 kPa of wall area |
| 110 mm brick leaf | about 1.9-2.1 kPa of wall area |

AS 1684 treats sheet roof as 10 kg/m2 class and tile roof as 60 kg/m2 class plus ceiling.

## Wind

**Housing - AS 4055** design gust speeds at ridge height, m/s (table values matched to the
2012 edition `[C]`; confirm unchanged in 2021):

| Class | N1 | N2 | N3 | N4 | N5 | N6 |
|---|---|---|---|---|---|---|
| Vh,u ultimate | 34 | 40 | 50 | 61 | 74 | 86 |
| Vh,s serviceability | 26 | 26 | 32 | 39 | 47 | 55 |

Cyclonic C1/C2/C3/C4 ultimate = 50/61/74/86 `[U]`. AS 4055 only applies inside its geometric
limits (roughly: houses to 8.5 m high, 16 m wide, roof pitch to 35 degrees) `[U]`.

**General - AS/NZS 1170.2:2021**

- Vsit,b = VR Mc Md (Mz,cat Ms Mt); p = 0.5 rho_air Vdes^2 Cshp Cdyn, rho_air = 1.2 kg/m3 `[U]`
- The 2021 edition split the regions (A0-A5, B1, B2, C, D) and added the climate change
  multiplier Mc (1.05 in cyclonic regions) `[C]`
- Regional V500: A 45, B 57, C 66, D 80 m/s `[U]`
- NSW is mostly Region A2, alpine A3, far north coast B1 `[U]` - read Figure 3.1(A)

## Importance level and annual probability - NCC Table B1D3b

| IL | Wind (non-cyclonic) | Earthquake | Status |
|---|---|---|---|
| 1 | 1:100 (cyclonic 1:200) | 1:250 | `[C]` |
| 2 (houses, ordinary buildings) | 1:500 | 1:500 | `[C]` |
| 3 | 1:1000 | 1:1000 | `[U]` |
| 4 | 1:2000 | 1:1500 | `[U]` |

## Deflection limits

Limits are a design decision; state the one used. Common practice:

| Element | Limit | Source |
|---|---|---|
| Floor beams/joists, total long-term | span/300 (span/250 where nothing brittle) | AS/NZS 1170.0 Table C1 guidance `[U]` |
| Floors supporting masonry or brittle finishes | span/500 | `[U]` |
| Imposed load on floors | span/360, and 1.0 kN point load deflection of about 2 mm for floor dynamics | `[U]` |
| Roof members | span/300 dead, span/250 imposed, span/150 wind | `[U]` |
| Lintels over openings | span/300, max about 9-10 mm; span/500 under masonry | `[U]` |
| Cantilevers | span/125 to span/150 | `[U]` |
| Steel beams (AS 4100 App B), concrete (AS 3600 Table 2.3.2) | span/250 total; span/500 with masonry partitions; cantilever span/125 | `[U]` |

## Line load from area load

w (kN/m) = pressure (kPa) x tributary width (m). For a member carrying another member, take
the reaction, not an area guess. Simply supported under UDL: M* = wL^2/8, V* = wL/2,
deflection = 5wL^4/(384EI). Central point load P: M* = PL/4, deflection = PL^3/(48EI).
Cantilever UDL: M* = wL^2/2, deflection = wL^4/(8EI).
