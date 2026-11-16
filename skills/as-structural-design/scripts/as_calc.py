#!/usr/bin/env python3
"""
as_calc.py - member checks to Australian Standards (limit states).

  timber-beam / timber-column   AS 1720.1-2010
  steel-beam  / steel-column    AS 4100:2020
  rc-beam (also slabs, b=1000)  AS 3600:2018
  combos                        AS/NZS 1170.0:2002
  as1684-widths / -bracing / -tiedown   AS 1684.2 house framing

Units: mm, MPa, kN, kNm, kN/m (line loads), kPa only where stated.
Output is a markdown calc sheet with clause references and utilisation ratios.
Run `python as_calc.py <command> -h` for the inputs of each command.

Scope: single simply supported spans (or supply --Mstar/--Vstar yourself).
Every table value in here is listed in references/ with its source status;
check anything critical against the current published standard.
"""
import argparse
import math
import sys

# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

# AS 1720.1 characteristic values (MPa). kind: sawn | glulam | lvl
# phi = capacity factor for application category 1, 2, 3 (Table 2.1)
# fp = bearing perpendicular to grain; taken from strength group / supplier data.
TIMBER = {
    # MGP: Table H3.1 values for depths up to 140 mm; see SIZE_MGP for deeper sections
    "MGP10": dict(fb=17, ft=7.7, fs=2.6, fc=18, fp=10, E=10000, G=670, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "MGP12": dict(fb=28, ft=12, fs=3.5, fc=24, fp=10, E=12700, G=850, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "MGP15": dict(fb=39, ft=18, fs=4.3, fc=30, fp=10, E=15200, G=1010, kind="sawn", phi=(0.95, 0.85, 0.75)),
    # F-grades: Table H2.1 (ft shown is the softwood value - conservative for hardwood)
    "F5": dict(fb=14, ft=7.3, fs=1.8, fc=11, fp=None, E=6900, G=460, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "F7": dict(fb=18, ft=8.9, fs=2.1, fc=13, fp=None, E=7900, G=530, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "F8": dict(fb=22, ft=11, fs=2.2, fc=18, fp=None, E=9100, G=610, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "F11": dict(fb=31, ft=15, fs=2.8, fc=22, fp=None, E=10500, G=700, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "F14": dict(fb=36, ft=19, fs=3.3, fc=27, fp=None, E=12000, G=800, kind="sawn", phi=(0.90, 0.70, 0.60)),
    "F17": dict(fb=42, ft=22, fs=3.6, fc=34, fp=None, E=14000, G=930, kind="sawn", phi=(0.95, 0.85, 0.75)),
    "F22": dict(fb=55, ft=29, fs=4.2, fc=42, fp=None, E=16000, G=1070, kind="sawn", phi=(0.95, 0.85, 0.75)),
    "F27": dict(fb=67, ft=34, fs=5.1, fc=51, fp=None, E=18500, G=1230, kind="sawn", phi=(0.95, 0.85, 0.75)),
    # Glulam: Table 7.1
    "GL8": dict(fb=19, ft=6, fs=3.7, fc=14, fp=None, E=8000, G=530, kind="glulam", phi=(0.95, 0.85, 0.75)),
    "GL10": dict(fb=22, ft=8, fs=3.7, fc=18, fp=None, E=10000, G=670, kind="glulam", phi=(0.95, 0.85, 0.75)),
    "GL12": dict(fb=25, ft=11, fs=4.2, fc=22, fp=None, E=11500, G=770, kind="glulam", phi=(0.95, 0.85, 0.75)),
    "GL13": dict(fb=33, ft=16, fs=4.2, fc=26, fp=None, E=13300, G=900, kind="glulam", phi=(0.95, 0.85, 0.75)),
    "GL17": dict(fb=40, ft=20, fs=4.2, fc=33, fp=None, E=16700, G=1110, kind="glulam", phi=(0.95, 0.85, 0.75)),
    "GL18": dict(fb=45, ft=25, fs=5.0, fc=45, fp=None, E=18500, G=1230, kind="glulam", phi=(0.95, 0.85, 0.75)),
}

# MGP size effect, Table H3.1: {grade: [(max depth, fb, ft, fs, fc)]}
SIZE_MGP = {
    "MGP10": [(140, 17, 7.7, 2.6, 18), (190, 16, 7.1, 2.5, 18), (240, 15, 6.6, 2.4, 17), (290, 14, 6.1, 2.3, 16)],
    "MGP12": [(140, 28, 12, 3.5, 24), (190, 25, 12, 3.3, 23), (240, 24, 11, 3.2, 22), (290, 22, 9.9, 3.1, 22)],
    "MGP15": [(140, 39, 18, 4.3, 30), (190, 36, 17, 4.1, 29), (240, 33, 16, 4.0, 28), (290, 31, 14, 3.8, 27)],
}

# k1 duration of load, AS 1720.1 Table 2.3 (strength of timber)
K1 = {"5s": 1.00, "5min": 1.00, "5h": 0.97, "5d": 0.94, "5mo": 0.80, "50y": 0.57}

# k7 length of bearing, Table 2.6: (bearing length mm, k7)
K7 = [(12, 1.75), (25, 1.40), (50, 1.20), (75, 1.15), (125, 1.10), (150, 1.00)]

# g31 / g32 strength sharing, Table 2.7
G3X = {1: 1.00, 2: 1.14, 3: 1.20, 4: 1.24, 5: 1.26, 6: 1.28, 7: 1.30, 8: 1.31, 9: 1.32, 10: 1.33}

# AS/NZS 1170.0 Table 4.1: (psi_s, psi_l, psi_c, psi_E)
PSI = {
    "floor": (0.7, 0.4, 0.4, 0.3),      # residential, office, parking, retail floors
    "storage": (1.0, 0.6, 0.6, 0.6),    # storage and "other"
    "roof": (0.7, 0.0, 0.0, 0.0),       # roofs not used for floor-type activities
}

# AS 3600 Table 3.1.2 mean Ec (MPa)
EC = {20: 24000, 25: 26700, 32: 30100, 40: 32800, 50: 34800, 65: 37400, 80: 39600, 100: 42200}

OUT = []


def p(line=""):
    OUT.append(line)


def row(*cells):
    p("| " + " | ".join(str(c) for c in cells) + " |")


def table(head):
    row(*head)
    row(*["---"] * len(head))


def f(x, n=2):
    if x is None:
        return "-"
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    return f"{x:.{n}f}"


def verdict(u):
    return "OK" if u <= 1.0 else "FAILS"


def interp(tab, x):
    """Linear interpolation in a sorted (x, y) table, clamped at the ends."""
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


def header(title, std):
    p(f"## {title}")
    p(f"*Design standard: {std}. Limit states design. Preliminary calculation - "
      "check inputs, restraint assumptions and table values against the current standard.*")
    p()


# --------------------------------------------------------------------------
# AS/NZS 1170.0 combinations for a line load / axial load
# --------------------------------------------------------------------------

def combos(G, Q, use, Wdown=0.0, Wup=0.0):
    """Return list of (label, value, duration key) for strength, per Cl 4.2.2.
    Wup is entered as a positive number acting upward."""
    ps, pl, pc, pe = PSI[use]
    q_dur = "5d" if use == "roof" else "5mo"
    out = [("1.35G", 1.35 * G, "50y"),
           ("1.2G + 1.5Q", 1.2 * G + 1.5 * Q, q_dur)]
    if pl > 0:
        out.append((f"1.2G + 1.5({pl})Q long-term", 1.2 * G + 1.5 * pl * Q, "50y"))
    if Wdown:
        out.append((f"1.2G + Wu + {pc}Q", 1.2 * G + Wdown + pc * Q, "5s"))
    if Wup:
        out.append(("0.9G + Wu (uplift)", 0.9 * G - Wup, "5s"))
    return out


def cmd_combos(a):
    header("Load combinations", "AS/NZS 1170.0:2002 Cl 4.2.2 (strength), Cl 4.3 (serviceability)")
    ps, pl, pc, pe = PSI[a.use]
    p(f"G = {a.G}, Q = {a.Q}, Wu down = {a.Wdown}, Wu up = {a.Wup} (same units throughout); "
      f"use = {a.use}: psi_s {ps}, psi_l {pl}, psi_c {pc}, psi_E {pe}")
    p()
    table(["Strength combination", "Design action", "AS 1720.1 k1"])
    cs = combos(a.G, a.Q, a.use, a.Wdown, a.Wup)
    for lab, v, d in cs:
        row(lab, f(v), f"{K1[d]} ({d})")
    p()
    gov = max(cs, key=lambda c: abs(c[1]))
    p(f"Largest magnitude: **{gov[0]} = {f(gov[1])}**. For timber the governing case is the "
      "largest (action / k1), not the largest action - the timber commands check every case.")
    p()
    table(["Serviceability", "Value"])
    row(f"Short-term G + {ps}Q", f(a.G + ps * a.Q))
    row(f"Long-term G + {pl}Q", f(a.G + pl * a.Q))
    p()


# --------------------------------------------------------------------------
# AS 1720.1 timber
# --------------------------------------------------------------------------

def timber_props(a, depth):
    if a.grade not in TIMBER:
        sys.exit(f"Unknown grade {a.grade}. Known: {', '.join(TIMBER)}")
    t = dict(TIMBER[a.grade])
    for dmax, fb, ft, fs, fc in SIZE_MGP.get(a.grade, []):
        if depth <= dmax:
            t.update(fb=fb, ft=ft, fs=fs, fc=fc)
            break
    for k in ("fb", "fs", "fc", "fp", "E"):
        v = getattr(a, k, None)
        if v is not None:
            t[k] = v
    return t


def k12_from(rhoS):
    """AS 1720.1 Cl 3.2.4 / 3.3.3 stability factor."""
    if rhoS <= 10:
        return 1.0
    if rhoS <= 20:
        return 1.5 - 0.05 * rhoS
    return 200.0 / rhoS ** 2


def k9_from(ncom, nmem, s, L, kind):
    """Cl 2.4.5 strength sharing - sawn timber only."""
    if kind != "sawn" or (ncom == 1 and nmem == 1):
        return 1.0
    g31 = G3X[min(ncom, 10)]
    g32 = G3X[min(ncom * nmem, 10)]
    if nmem == 1 or not s:
        return max(g31, 1.0)
    return max(g31 + (g32 - g31) * (1 - 2 * s / L), 1.0)


def cmd_timber_beam(a):
    b, d, L = a.b, a.d, a.span
    t = timber_props(a, d)
    phi = a.phi if a.phi else t["phi"][a.category - 1]
    k4, k6 = a.k4, a.k6
    A, Z, I = b * d, b * d ** 2 / 6, b * d ** 3 / 12
    header(f"Timber beam {b:g} x {d:g} {a.grade}, span {L:g} mm", "AS 1720.1-2010")

    p("**Inputs**")
    p(f"- Section b = {b:g} mm, d = {d:g} mm: A = {f(A,0)} mm2, Z = {f(Z,0)} mm3, I = {I:.3e} mm4")
    p(f"- f'b = {t['fb']}, f's = {t['fs']}, f'p = {t['fp']}, E = {t['E']} MPa")
    p(f"- phi = {phi} (category {a.category}, Table 2.1), k4 = {k4}, k6 = {k6}")
    p(f"- Loads: G = {a.G} kN/m, Q = {a.Q} kN/m, wind down = {a.Wdown} kN/m, wind up = {a.Wup} kN/m; use = {a.use}")

    # stability
    if a.lay <= 0:
        S1 = 0.0
        note = "compression edge continuously restrained, S1 = 0"
    elif a.edge == "compression":
        S1 = 1.25 * (d / b) * (a.lay / d) ** 0.5
        note = f"Cl 3.2.3.2(a): S1 = 1.25 (d/b)(Lay/d)^0.5, Lay = {a.lay:g}"
    else:
        S1 = (d / b) ** 1.35 * (a.lay / d) ** 0.25
        note = f"Cl 3.2.3.2(b): S1 = (d/b)^1.35 (Lay/d)^0.25, Lay = {a.lay:g}"
    rho_b = a.rho_b if a.rho_b else 14.71 * (t["E"] / t["fb"]) ** -0.480 * a.r ** -0.061
    k12 = k12_from(rho_b * S1)
    k9 = k9_from(a.ncom, a.nmem, a.spacing, L, t["kind"])
    p(f"- Stability: {note}; S1 = {f(S1)}, rho_b = {f(rho_b)}, rho_b.S1 = {f(rho_b*S1)} -> **k12 = {f(k12,3)}** (Cl 3.2.4)")
    p(f"- Strength sharing k9 = {f(k9,3)} (Cl 2.4.5; ncom = {a.ncom}, nmem = {a.nmem})")
    p()

    cs = combos(a.G, a.Q, a.use, a.Wdown, a.Wup)
    Lm = L / 1000.0
    worst = 0.0
    p("**Strength** - Md = phi k1 k4 k6 k9 k12 f'b Z (Cl 3.2.1.1); Vd = phi k1 k4 k6 f's (2/3)bd (Cl 3.2.5)")
    p()
    table(["Combination", "w* kN/m", "k1", "M* kNm", "Md kNm", "M*/Md", "V* kN", "Vd kN", "V*/Vd", ""])
    Rmax = 0.0
    for lab, w, dur in cs:
        k1 = K1[dur]
        M = abs(w) * Lm ** 2 / 8 if a.Mstar is None else a.Mstar
        V = abs(w) * Lm / 2 if a.Vstar is None else a.Vstar
        # under net uplift the bottom edge is in compression: flag rather than guess restraint
        Md = phi * k1 * k4 * k6 * k9 * k12 * t["fb"] * Z / 1e6
        Vd = phi * k1 * k4 * k6 * t["fs"] * (2 / 3) * A / 1e3
        um, uv = M / Md, V / Vd
        worst = max(worst, um, uv)
        Rmax = max(Rmax, V / k1)
        row(lab, f(w), k1, f(M), f(Md), f(um), f(V), f(Vd), f(uv), verdict(max(um, uv)))
    p()
    if a.Wup and 0.9 * a.G - a.Wup < 0:
        p("> Net uplift occurs: the *bottom* edge goes into compression. The k12 above assumes the "
          "restraint entered applies to whichever edge is in compression - confirm that for the uplift case.")
        p()

    # bearing
    if a.bearing and t["fp"]:
        k7 = interp(K7, a.bearing) if a.bearing_inboard else 1.0
        p("**Bearing at support** - Nd,p = phi k1 k4 k6 k7 f'p Ap (Cl 3.2.6.1)")
        p()
        table(["Combination", "R* kN", "k1", "k7", "Nd,p kN", "R*/Nd,p", ""])
        for lab, w, dur in cs:
            k1 = K1[dur]
            R = abs(w) * Lm / 2 if a.Vstar is None else a.Vstar
            Nd = phi * k1 * k4 * k6 * k7 * t["fp"] * b * a.bearing / 1e3
            u = R / Nd
            worst = max(worst, u)
            row(lab, f(R), k1, f(k7), f(Nd), f(u), verdict(u))
        p()
    elif a.bearing:
        p("> Bearing not checked: no f'p stored for this grade - pass --fp from the strength group "
          "(Table H2.2) or the supplier's data.")
        p()

    # deflection
    ps, pl, pc, pe = PSI[a.use]
    j2 = a.j2
    k = 5 * Lm ** 4 * 1e12 / (384 * t["E"] * I)  # mm per (kN/m): w in N/mm = kN/m
    d_G = k * a.G
    d_Qs = k * ps * a.Q
    d_long = j2 * k * (a.G + pl * a.Q)
    d_total = d_long + k * (ps - pl) * a.Q
    p(f"**Serviceability** - 5wL^4/384EI, E = {t['E']} MPa, j2 = {j2} (Table 2.4), psi_s = {ps}, psi_l = {pl}")
    p()
    table(["Case", "Deflection mm", "Span/x", "Limit", ""])
    def drow(lab, dd, lim):
        ratio = L / dd if dd > 0 else float("inf")
        row(lab, f(dd, 1), f"L/{ratio:.0f}", f"L/{lim:g} = {f(L/lim,1)} mm", "OK" if dd <= L / lim else "FAILS")
        return dd / (L / lim)
    u1 = drow(f"Imposed short-term, {ps}Q", d_Qs, a.limit_live)
    u2 = drow(f"Long-term total, j2(G + {pl}Q) + {f(ps-pl,1)}Q", d_total, a.limit_total)
    p()
    p(f"Instantaneous dead-load deflection {f(d_G,1)} mm. Limits are the designer's choice "
      "(AS/NZS 1170.0 Table C1 guidance; AS 1684 uses its own criteria) - state them in the report.")
    p()
    us = max(u1, u2)
    p(f"**Result: strength utilisation {f(worst)} ({verdict(worst)}); serviceability {f(us)} ({verdict(us)}).**")
    p()


def cmd_timber_column(a):
    b, d, L = a.b, a.d, a.L          # d = larger dimension, b = smaller
    if b > d:
        b, d = d, b
    t = timber_props(a, d)
    phi = a.phi if a.phi else t["phi"][a.category - 1]
    A = b * d
    header(f"Timber column {b:g} x {d:g} {a.grade}, L = {L:g} mm", "AS 1720.1-2010")
    lax = a.lax if a.lax is not None else L
    lay = a.lay if a.lay is not None else L
    S3 = min(lax / d, a.g13 * L / d)
    S4 = min(lay / b, a.g13 * L / b)
    rho_c = a.rho_c if a.rho_c else 11.39 * (t["E"] / t["fc"]) ** -0.408 * a.r ** -0.074
    S = max(S3, S4)
    k12 = k12_from(rho_c * S)
    p("**Inputs**")
    p(f"- A = {f(A,0)} mm2; f'c = {t['fc']} MPa, E = {t['E']} MPa; phi = {phi}; k4 = {a.k4}, k6 = {a.k6}")
    p(f"- Slenderness (Cl 3.3.2): S3 = {f(S3)} (major axis, Lax = {lax:g}), S4 = {f(S4)} (minor axis, Lay = {lay:g}), g13 = {a.g13}")
    p(f"- rho_c = {f(rho_c)}; rho_c.S = {f(rho_c*S)} -> **k12 = {f(k12,3)}** (Cl 3.3.3)")
    if S > 50:
        p("- **Slenderness exceeds 50 - outside the usual limit for columns; resize.**")
    p()
    p("**Compression** - Nd,c = phi k1 k4 k6 k12 f'c Ac (Cl 3.3.1.1)")
    p()
    table(["Combination", "N* kN", "k1", "Nd,c kN", "N*/Nd,c", ""])
    worst = 0
    for lab, n, dur in combos(a.G, a.Q, a.use, a.Wdown, 0):
        k1 = K1[dur]
        Nd = phi * k1 * a.k4 * a.k6 * k12 * t["fc"] * A / 1e3
        u = n / Nd
        worst = max(worst, u)
        row(lab, f(n), k1, f(Nd), f(u), verdict(u))
    p()
    p(f"**Result: utilisation {f(worst)} ({verdict(worst)}).** Check bearing on plates (Cl 3.2.6) "
      "and combined bending if the load is eccentric or the column takes wind (Cl 3.5).")
    p()


# --------------------------------------------------------------------------
# AS 4100 steel
# --------------------------------------------------------------------------

E_S, G_S = 200000.0, 80000.0


def alpha_c(lam_n, alpha_b):
    """AS 4100 Cl 6.3.3 member slenderness reduction factor."""
    aa = 2100 * (lam_n - 13.5) / (lam_n ** 2 - 15.3 * lam_n + 2050)
    lam = lam_n + aa * alpha_b
    eta = max(0.00326 * (lam - 13.5), 0.0)
    xi = ((lam / 90) ** 2 + 1 + eta) / (2 * (lam / 90) ** 2)
    return min(xi * (1 - math.sqrt(1 - (90 / (xi * lam)) ** 2)), 1.0)


def cmd_steel_beam(a):
    phi = 0.9
    fyf = a.fyf
    fyw = a.fyw if a.fyw else a.fyf
    header(f"Steel beam {a.name}, segment L = {a.L:g} mm", "AS 4100:2020")
    # --- section classification, Cl 5.2.2, Table 5.2 (hot-rolled limits by default)
    lam_f = ((a.bf - a.tw) / 2) / a.tf * math.sqrt(fyf / 250)
    lam_w = (a.d - 2 * a.tf) / a.tw * math.sqrt(fyw / 250)
    fp_, fy_ = a.flange_limits
    wp_, wy_ = 82.0, 115.0
    # governing element = largest lambda_e / lambda_ey
    if lam_f / fy_ >= lam_w / wy_:
        ls, lsp, lsy, el = lam_f, fp_, fy_, "flange"
    else:
        ls, lsp, lsy, el = lam_w, wp_, wy_, "web"
    Zc = min(a.Sx, 1.5 * a.Zx)
    if ls <= lsp:
        Ze, cls = Zc, "compact"
    elif ls <= lsy:
        Ze, cls = a.Zx + (lsy - ls) / (lsy - lsp) * (Zc - a.Zx), "non-compact"
    else:
        Ze, cls = a.Zx * (lsy / ls), "slender"
    if a.Zex:
        Ze = a.Zex
    Ms = fyf * Ze / 1e6
    p("**Section** (Cl 5.2)")
    p(f"- Flange lambda_e = {f(lam_f)} (limits {fp_:g}/{fy_:g}); web lambda_e = {f(lam_w)} (limits 82/115); governing: {el} -> **{cls}**")
    p(f"- Zex = {f(Ze/1e3,0)} x10^3 mm3{' (as supplied)' if a.Zex else ''}; fy flange = {fyf}, web = {fyw} MPa")
    p(f"- Ms = fy Ze = {f(Ms,1)} kNm; **phi Ms = {f(phi*Ms,1)} kNm**")
    p()
    # --- member capacity, Cl 5.6.1
    le = a.kt * a.kl * a.kr * a.L
    if le <= 0:
        Mb, alpha_s, Mo = Ms, 1.0, float("inf")
        p("**Member** - full lateral restraint assumed (le = 0): phi Mb = phi Ms")
    else:
        Mo = math.sqrt((math.pi ** 2 * E_S * a.Iy / le ** 2) *
                       (G_S * a.J + math.pi ** 2 * E_S * a.Iw / le ** 2)) / 1e6
        alpha_s = 0.6 * (math.sqrt((Ms / Mo) ** 2 + 3) - Ms / Mo)
        Mb = min(a.alpha_m * alpha_s * Ms, Ms)
        p("**Member** (Cl 5.6.1)")
        p(f"- le = kt kl kr L = {a.kt} x {a.kl} x {a.kr} x {a.L:g} = {f(le,0)} mm")
        p(f"- Mo = {f(Mo,1)} kNm (Cl 5.6.1.1(3)); alpha_s = {f(alpha_s,3)}; alpha_m = {a.alpha_m}")
        p(f"- Mb = alpha_m alpha_s Ms <= Ms = {f(Mb,1)} kNm; **phi Mb = {f(phi*Mb,1)} kNm**")
    p()
    # --- shear, Cl 5.11
    Aw = a.d * a.tw
    web_ok = (a.d - 2 * a.tf) / a.tw <= 82 / math.sqrt(fyw / 250)
    Vv = 0.6 * fyw * Aw / 1e3
    p("**Shear** (Cl 5.11)")
    p(f"- Vw = 0.6 fy Aw = 0.6 x {fyw} x {a.d:g} x {a.tw:g} = {f(Vv,0)} kN; **phi Vv = {f(phi*Vv,0)} kN**"
      + ("" if web_ok else " - **web exceeds 82/sqrt(fy/250): shear buckling governs (Cl 5.11.5), not covered here**"))
    p()
    # --- actions
    Lm = (a.span or a.L) / 1000.0
    w = a.w
    M = a.Mstar if a.Mstar is not None else (w * Lm ** 2 / 8 if w else None)
    V = a.Vstar if a.Vstar is not None else (w * Lm / 2 if w else None)
    worst = None
    if M is not None:
        table(["Check", "Action", "Capacity", "Utilisation", ""])
        um = M / (phi * Mb)
        row("Bending M* <= phi Mb", f"{f(M,1)} kNm", f"{f(phi*Mb,1)} kNm", f(um), verdict(um))
        worst = um
        if V is not None:
            # Cl 5.12.3 shear-bending interaction
            if M <= 0.75 * phi * Ms:
                Vvm, note = Vv, ""
            else:
                Vvm, note = Vv * (2.2 - 1.6 * M / (phi * Ms)), " (reduced, Cl 5.12.3)"
            uv = V / (phi * Vvm)
            row("Shear V* <= phi Vvm" + note, f"{f(V,1)} kN", f"{f(phi*Vvm,0)} kN", f(uv), verdict(uv))
            worst = max(worst, uv)
        p()
    if a.ws and a.Ix:
        dlt = 5 * a.ws * Lm ** 4 * 1e12 / (384 * E_S * a.Ix)
        lim = (a.span or a.L) / a.limit
        p(f"**Deflection** under ws = {a.ws} kN/m: {f(dlt,1)} mm = L/{(a.span or a.L)/dlt:.0f} "
          f"(limit L/{a.limit:g} = {f(lim,1)} mm) -> {'OK' if dlt <= lim else 'FAILS'}")
        p()
        worst = max(worst or 0, dlt / lim)
    if worst is not None:
        p(f"**Result: utilisation {f(worst)} ({verdict(worst)}).** Also check web bearing at supports and "
          "point loads (Cl 5.13) and the connection design (Section 9).")
        p()


def cmd_steel_column(a):
    phi = 0.9
    header(f"Steel column {a.name}", "AS 4100:2020 Section 6")
    Ns = a.kf * a.An * a.fy / 1e3
    p(f"- Ns = kf An fy = {a.kf} x {a.An:g} x {a.fy:g} = {f(Ns,0)} kN; **phi Ns = {f(phi*Ns,0)} kN** (Cl 6.2)")
    worst_cap = phi * Ns
    table(["Axis", "le mm", "r mm", "lambda_n", "alpha_c", "phi Nc kN"])
    for ax, le, r in (("x", a.lex, a.rx), ("y", a.ley, a.ry)):
        if not le or not r:
            continue
        lam_n = (le / r) * math.sqrt(a.kf) * math.sqrt(a.fy / 250)
        ac = alpha_c(lam_n, a.alpha_b) if lam_n > 0 else 1.0
        Nc = ac * Ns
        worst_cap = min(worst_cap, phi * Nc)
        row(ax, f(le, 0), f(r, 1), f(lam_n, 1), f(ac, 3), f(phi * Nc, 0))
    p()
    p(f"alpha_b = {a.alpha_b} (Table 6.3.3). **Design capacity phi Nc = {f(worst_cap,0)} kN.**")
    if a.Nstar is not None:
        u = a.Nstar / worst_cap
        p(f"N* = {f(a.Nstar,1)} kN -> **utilisation {f(u)} ({verdict(u)})**. Add combined actions "
          "(Section 8) for any moment, including minimum eccentricity from the connection.")
    p()


# --------------------------------------------------------------------------
# AS 3600 concrete
# --------------------------------------------------------------------------

def cmd_rc_beam(a):
    fc, fsy = a.fc, a.fsy
    b, D = a.b, a.D
    d = a.d if a.d else D - a.cover - a.tie - a.bar / 2
    header(f"Reinforced concrete {'slab strip' if a.slab else 'beam'} {b:g} x {D:g}, f'c = {fc:g} MPa",
           "AS 3600:2018")
    alpha2 = max(0.85 - 0.0015 * fc, 0.67)
    gamma = max(0.97 - 0.0025 * fc, 0.67)
    fctf = 0.6 * math.sqrt(fc)
    p("**Inputs**")
    p(f"- b = {b:g}, D = {D:g}, d = {f(d,0)} mm; Ast = {a.Ast:g} mm2; fsy = {fsy:g} MPa")
    p(f"- alpha2 = {f(alpha2,3)}, gamma = {f(gamma,3)} (Cl 8.1.3); f'ct.f = 0.6 sqrt(f'c) = {f(fctf)} MPa")
    p()
    # flexure
    dn = a.Ast * fsy / (alpha2 * fc * gamma * b)
    ku = dn / d
    Mu = a.Ast * fsy * (d - gamma * dn / 2) / 1e6
    phi_b = min(max(1.24 - 13 * ku / 12, 0.65), 0.85)
    if a.class_L:
        phi_b = 0.65
    coef = {None: 0.20, "supported": 0.19, "flat": 0.24}[a.slab]
    Ast_min = coef * (D / d) ** 2 * (fctf / fsy) * b * d
    p("**Flexure** (Cl 8.1)")
    p(f"- Neutral axis dn = Ast fsy / (alpha2 f'c gamma b) = {f(dn,1)} mm; **ku = {f(ku,3)}** "
      + ("(<= 0.36, ductile)" if ku <= 0.36 else "(**> 0.36 - not permitted without compression steel, Cl 8.1.5**)"))
    p(f"- Mu = Ast fsy (d - gamma dn/2) = {f(Mu,1)} kNm; phi = {f(phi_b)} -> **phi Mu = {f(phi_b*Mu,1)} kNm**")
    p(f"- Minimum steel: {coef} (D/d)^2 (f'ct.f/fsy) b d = {f(Ast_min,0)} mm2 -> "
      + ("OK" if a.Ast >= Ast_min else "**Ast is below minimum**")
      + (" (Cl 9.1.1)" if a.slab else " (Cl 8.1.6.1)"))
    worst = None
    if a.Mstar is not None:
        um = a.Mstar / (phi_b * Mu)
        worst = um
        p(f"- M* = {f(a.Mstar,1)} kNm -> utilisation {f(um)} ({verdict(um)})")
    p()
    # shear - simplified method Cl 8.2.4.3
    phi_v = 0.75
    dv = max(0.72 * D, 0.9 * d)
    rt = min(math.sqrt(fc), 8.0)
    Asv_min_s = 0.08 * math.sqrt(fc) * b / a.fsyf
    Asv_s = a.Asv / a.s if (a.Asv and a.s) else 0.0
    if Asv_s >= Asv_min_s:
        kv = 0.15
    else:
        kv = min(200.0 / (1000 + 1.3 * dv), 0.15)   # cap 0.15 per Amd 2 (0.10 before)
    cot = 1 / math.tan(math.radians(36))
    Vuc = kv * b * dv * rt / 1e3
    Vus = Asv_s * a.fsyf * dv * cot / 1e3
    Vumax = 0.9 * 0.55 * fc * b * dv * cot / (1 + cot ** 2) / 1e3
    Vu = min(Vuc + Vus, Vumax)
    p("**Shear** - simplified method, theta_v = 36 deg (Cl 8.2.4.3); valid for f'c <= 65 MPa, "
      "fsy <= 500 MPa, no prestress, axial tension or torsion. Vu.max taken as 0.9 x 0.55 f'c bv dv "
      "cot/(1+cot^2) (Amd 2 reduction - confirm coefficient)")
    p(f"- dv = max(0.72D, 0.9d) = {f(dv,0)} mm; Asv/s = {f(Asv_s,3)} vs minimum {f(Asv_min_s,3)} mm2/mm -> kv = {f(kv,3)}")
    p(f"- Vuc = kv bv dv sqrt(f'c) = {f(Vuc,1)} kN; Vus = (Asv fsy.f dv / s) cot 36 = {f(Vus,1)} kN; Vu.max = {f(Vumax,0)} kN")
    p(f"- **phi Vu = {f(phi_v*Vu,1)} kN** (phi = 0.75); phi Vuc = {f(phi_v*Vuc,1)} kN")
    if a.Vstar is not None:
        uv = a.Vstar / (phi_v * Vu)
        worst = max(worst or 0, uv)
        p(f"- V* = {f(a.Vstar,1)} kN -> utilisation {f(uv)} ({verdict(uv)})")
    if not a.slab and Asv_s < Asv_min_s:
        p("- **Ligatures are below the minimum Asv.min/s.** Cl 8.2.1.6 requires at least minimum shear "
          "reinforcement where V* > phi Vuc or D > 750, and Amendment 2 tightened this for beams deeper "
          "than 300 mm - provide minimum ligatures in beams as a matter of course.")
    p()
    if worst is not None:
        p(f"**Result: utilisation {f(worst)} ({verdict(worst)}).** Still to check: deflection (Cl 8.5 / 9.4), "
          "crack control bar spacing (Cl 8.6 / 9.5), cover for exposure and fire (Sections 4, 5), anchorage (Section 13).")
        p()



# --------------------------------------------------------------------------
# AS 1684.2 house framing helpers
# --------------------------------------------------------------------------

# Structural wall bracing capacity kN/m, AS 1684.2 Table 8.18 (see references/as1684.md)
BRACE = {
    "a": (0.8, "two diagonally opposed timber or metal angle braces"),
    "b": (1.5, "tensioned metal straps"),
    "c": (1.5, "timber and metal angle braces"),
    "d": (3.0, "tensioned metal straps with stud straps"),
    "e": (2.1, "diagonal timber wall lining or cladding"),
    "g": (3.4, "structural plywood"),
    "h-A": (6.0, "structural plywood, method A (M12 rods)"),
    "h-B": (6.4, "structural plywood, method B (close nailing)"),
}
NOMINAL = {1: 0.45, 2: 0.75}   # kN/m, sheeted one side / two sides (Cl 8.3.6.2)


def cmd_as1684_widths(a):
    header("Load widths for span-table lookup", "AS 1684.2 Section 2.6")
    table(["Quantity", "Working", "Value mm"])
    if a.joist_spans:
        flw = sum(x / 2 for x in a.joist_spans) + a.joist_cantilever
        row("Floor load width FLW",
            " + ".join(f"{x:g}/2" for x in a.joist_spans)
            + (f" + {a.joist_cantilever:g} cantilever" if a.joist_cantilever else ""), f(flw, 0))
    if a.rafter_span:
        c = math.cos(math.radians(a.pitch))
        slope_half = a.rafter_span / 2 / c
        slope_oh = a.overhang / c
        row("Roof load width RLW (along the slope)",
            f"({a.rafter_span:g}/2 + {a.overhang:g}) / cos {a.pitch:g}", f(slope_half + slope_oh, 0))
        row("Uplift load width ULW (same lengths; check Fig 9.5)",
            "as RLW", f(slope_half + slope_oh, 0))
    if a.ceiling_spans:
        clw = sum(x / 2 for x in a.ceiling_spans)
        row("Ceiling load width CLW", " + ".join(f"{x:g}/2" for x in a.ceiling_spans), f(clw, 0))
    p()
    p("Half-span each side is the simple-span case. Where joists or rafters are continuous over the "
      "member, or struts/underpurlins change the load path, use the Section 2.6 figure for that "
      "arrangement - the load width is larger at the internal support.")
    p()


def cmd_as1684_bracing(a):
    header(f"Wall bracing check - wind direction {a.direction}", "AS 1684.2 Section 8")
    if a.force is not None:
        F = a.force
        p(f"- Racking force supplied: **{f(F,1)} kN**")
    else:
        if a.area is None or a.pressure is None:
            sys.exit("Give --force, or both --area and --pressure")
        F = a.area * a.pressure
        p(f"- Racking force = area of elevation x pressure = {a.area:g} m2 x {a.pressure:g} kPa "
          f"= **{f(F,1)} kN** (Cl 8.3.4; pressure from Tables 8.1-8.5)")
    hf = min(2700.0 / a.height, 1.0)
    if hf < 1:
        p(f"- Wall height {a.height:g} mm: structural capacities x 2700/{a.height:g} = {f(hf,3)}")
    p()
    table(["Wall", "Type", "Length m", "kN/m", "Capacity kN"])
    struct = 0.0
    for i, w in enumerate(a.wall or [], 1):
        parts = w.split(":")
        t, length = parts[0], float(parts[1])
        if t in BRACE:
            cap, desc = BRACE[t]
        else:
            try:
                cap, desc = float(t), "capacity supplied (manufacturer / table)"
            except ValueError:
                sys.exit(f"Unknown bracing type '{t}'. Use one of {', '.join(BRACE)} or a kN/m number.")
        c = cap * hf * length
        struct += c
        row(f"B{i}", f"({t}) {desc}", f(length), f(cap * hf), f(c, 1))
    p()
    nom_raw = NOMINAL[1] * a.nominal1 + NOMINAL[2] * a.nominal2
    nom = min(nom_raw, 0.5 * F)
    p(f"- Structural bracing: {f(struct,1)} kN")
    p(f"- Nominal bracing: {a.nominal1:g} m x 0.45 + {a.nominal2:g} m x 0.75 = {f(nom_raw,1)} kN, "
      f"counted up to 50% of the racking force -> {f(nom,1)} kN (Cl 8.3.6.2)")
    total = struct + nom
    u = F / total if total else float("inf")
    p(f"- **Total {f(total,1)} kN vs {f(F,1)} kN required -> utilisation {f(u)} ({verdict(u)})**")
    if u > 1:
        p(f"- Shortfall {f(F-total,1)} kN: about {f((F-total)/(BRACE['g'][0]*hf),1)} m more type (g) plywood, "
          f"or {f((F-total)/(BRACE['h-B'][0]*hf),1)} m of type (h) method B.")
    p()
    p("Capacity alone is not compliance. Also check: bracing spread evenly and placed at corners; "
      "maximum spacing between bracing walls at right angles to the wind (Cl 8.3.6.7); minimum panel "
      "lengths; fixing of the top of each bracing wall to the ceiling/roof diaphragm and the bottom "
      "to the floor (Tables 8.22-8.24); and subfloor bracing where the floor is on stumps or piers. "
      "Run the other wind direction separately.")
    p()


def cmd_as1684_tiedown(a):
    header("Tie-down uplift at a connection", "AS 1684.2 Section 9")
    area = a.ulw / 1000.0 * a.spacing / 1000.0
    U = a.pressure * area
    p(f"- Net uplift pressure {a.pressure:g} kPa (Table 9.5 for the wind class and roof type)")
    p(f"- Area held down = ULW x spacing = {a.ulw:g} x {a.spacing:g} mm = {f(area)} m2")
    p(f"- **Uplift force per fixing = {f(U)} kN**")
    if a.capacity:
        u = U / a.capacity
        p(f"- Connector design capacity {a.capacity:g} kN -> utilisation {f(u)} ({verdict(u)})")
    p()
    p("Carry the force down: rafter/truss to top plate, top plate to stud, stud to bottom plate, "
      "bottom plate to floor frame or slab, and into the footing. Each joint needs a fixing with "
      "at least this capacity for the joint group of the timber (Tables 9.16-9.25), and the "
      "force grows at openings where the lintel collects several rafters.")
    p()

# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def add_loads(sp, axial=False):
    u = "kN" if axial else "kN/m"
    sp.add_argument("--G", type=float, default=0.0, help=f"permanent action, {u}")
    sp.add_argument("--Q", type=float, default=0.0, help=f"imposed action, {u}")
    sp.add_argument("--Wdown", type=float, default=0.0, help=f"ultimate wind acting downward, {u}")
    sp.add_argument("--Wup", type=float, default=0.0, help=f"ultimate wind uplift (positive number), {u}")
    sp.add_argument("--use", choices=list(PSI), default="floor", help="sets psi factors and timber k1 for Q")


def add_timber(sp):
    sp.add_argument("--grade", required=True, help="e.g. MGP10, F17, GL17")
    sp.add_argument("--category", type=int, choices=[1, 2, 3], default=2,
                    help="application category for phi (1 house secondary, 2 house primary, 3 other primary)")
    sp.add_argument("--phi", type=float, help="override capacity factor (e.g. LVL from manufacturer)")
    sp.add_argument("--k4", type=float, default=1.0, help="moisture factor")
    sp.add_argument("--k6", type=float, default=1.0, help="temperature factor (0.9 tropical north)")
    sp.add_argument("--r", type=float, default=0.25, help="temporary/total load ratio for rho")
    for k in ("fb", "fs", "fc", "fp", "E"):
        sp.add_argument(f"--{k}", type=float, help=f"override characteristic {k} (MPa), e.g. LVL data")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("combos", help="AS/NZS 1170.0 combinations")
    add_loads(sp)
    sp.set_defaults(fn=cmd_combos)

    sp = sub.add_parser("timber-beam", help="AS 1720.1 simply supported beam/joist/rafter/lintel")
    sp.add_argument("--b", type=float, required=True, help="breadth mm (total, for nailed multiples use combined)")
    sp.add_argument("--d", type=float, required=True, help="depth mm")
    sp.add_argument("--span", type=float, required=True, help="span mm")
    add_timber(sp)
    add_loads(sp)
    sp.add_argument("--lay", type=float, default=0.0,
                    help="spacing of lateral restraints mm (0 = compression edge continuously restrained)")
    sp.add_argument("--edge", choices=["compression", "tension"], default="compression",
                    help="which edge the discrete restraints hold")
    sp.add_argument("--rho_b", type=float, help="override material constant")
    sp.add_argument("--ncom", type=int, default=1, help="members combined into one (e.g. 2 for 2/90x45)")
    sp.add_argument("--nmem", type=int, default=1, help="parallel members sharing load (e.g. 5 joists)")
    sp.add_argument("--spacing", type=float, default=0.0, help="member spacing mm (for k9)")
    sp.add_argument("--bearing", type=float, default=0.0, help="bearing length at support mm")
    sp.add_argument("--bearing_inboard", action="store_true",
                    help="bearing is >= 75 mm from the member end, so k7 applies")
    sp.add_argument("--j2", type=float, default=2.0, help="creep factor (2.0 seasoned, 3.0 unseasoned)")
    sp.add_argument("--limit_live", type=float, default=360, help="imposed deflection limit span/x")
    sp.add_argument("--limit_total", type=float, default=300, help="long-term total deflection limit span/x")
    sp.add_argument("--Mstar", type=float, help="supply M* kNm instead of wL2/8 (applied to every combination)")
    sp.add_argument("--Vstar", type=float, help="supply V* kN")
    sp.set_defaults(fn=cmd_timber_beam)

    sp = sub.add_parser("timber-column", help="AS 1720.1 axially loaded post/stud")
    sp.add_argument("--b", type=float, required=True)
    sp.add_argument("--d", type=float, required=True)
    sp.add_argument("--L", type=float, required=True, help="length mm")
    sp.add_argument("--lax", type=float, help="restraint spacing against buckling about major axis mm")
    sp.add_argument("--lay", type=float, help="restraint spacing against buckling about minor axis mm")
    sp.add_argument("--g13", type=float, default=1.0, help="effective length factor Table 3.2")
    sp.add_argument("--rho_c", type=float)
    add_timber(sp)
    add_loads(sp, axial=True)
    sp.set_defaults(fn=cmd_timber_column)

    sp = sub.add_parser("steel-beam", help="AS 4100 doubly symmetric I-section beam segment")
    sp.add_argument("--name", default="I-section")
    for k, h in (("d", "depth"), ("bf", "flange width"), ("tf", "flange thickness"), ("tw", "web thickness")):
        sp.add_argument(f"--{k}", type=float, required=True, help=f"{h} mm")
    sp.add_argument("--Zx", type=float, required=True, help="elastic modulus mm3")
    sp.add_argument("--Sx", type=float, required=True, help="plastic modulus mm3")
    sp.add_argument("--Zex", type=float, help="effective modulus mm3 from tables (else calculated)")
    sp.add_argument("--Ix", type=float, help="mm4 (for deflection)")
    sp.add_argument("--Iy", type=float, required=True, help="mm4")
    sp.add_argument("--J", type=float, required=True, help="torsion constant mm4")
    sp.add_argument("--Iw", type=float, required=True, help="warping constant mm6")
    sp.add_argument("--fyf", type=float, required=True, help="flange yield stress MPa")
    sp.add_argument("--fyw", type=float, help="web yield stress MPa (default = flange)")
    sp.add_argument("--flange_limits", type=float, nargs=2, default=(9.0, 16.0),
                    help="flange outstand plasticity/yield limits (HR 9 16; welded HW 8 14)")
    sp.add_argument("--L", type=float, required=True, help="segment length between restraints mm (0 = fully restrained)")
    sp.add_argument("--kt", type=float, default=1.0)
    sp.add_argument("--kl", type=float, default=1.0, help="1.4 for top-flange gravity load within segment")
    sp.add_argument("--kr", type=float, default=1.0)
    sp.add_argument("--alpha_m", type=float, default=1.0, help="moment modification factor (1.13 UDL, 1.35 central point load)")
    sp.add_argument("--span", type=float, help="beam span mm if different from segment length")
    sp.add_argument("--w", type=float, default=0.0, help="design UDL w* kN/m (strength)")
    sp.add_argument("--ws", type=float, default=0.0, help="serviceability UDL kN/m")
    sp.add_argument("--limit", type=float, default=250, help="deflection limit span/x")
    sp.add_argument("--Mstar", type=float)
    sp.add_argument("--Vstar", type=float)
    sp.set_defaults(fn=cmd_steel_beam)

    sp = sub.add_parser("steel-column", help="AS 4100 concentrically loaded compression member")
    sp.add_argument("--name", default="column")
    sp.add_argument("--An", type=float, required=True, help="net area mm2")
    sp.add_argument("--fy", type=float, required=True)
    sp.add_argument("--kf", type=float, default=1.0, help="form factor")
    sp.add_argument("--rx", type=float)
    sp.add_argument("--ry", type=float)
    sp.add_argument("--lex", type=float, help="effective length about x mm")
    sp.add_argument("--ley", type=float, help="effective length about y mm")
    sp.add_argument("--alpha_b", type=float, default=0.0,
                    help="section constant: 0 hot-rolled UB/UC, -0.5 cold-formed RHS/SHS/CHS, 0.5 angles/channels/tees")
    sp.add_argument("--Nstar", type=float)
    sp.set_defaults(fn=cmd_steel_column)

    sp = sub.add_parser("rc-beam", help="AS 3600 singly reinforced rectangular section (use --slab for slabs, b=1000)")
    sp.add_argument("--b", type=float, required=True)
    sp.add_argument("--D", type=float, required=True)
    sp.add_argument("--d", type=float, help="effective depth mm (else D - cover - tie - bar/2)")
    sp.add_argument("--cover", type=float, default=30)
    sp.add_argument("--tie", type=float, default=10)
    sp.add_argument("--bar", type=float, default=16)
    sp.add_argument("--fc", type=float, required=True)
    sp.add_argument("--fsy", type=float, default=500)
    sp.add_argument("--Ast", type=float, required=True, help="tension steel area mm2")
    sp.add_argument("--class_L", action="store_true", help="Class L mesh as main reinforcement (phi = 0.65)")
    sp.add_argument("--slab", choices=["supported", "flat"], help="slab minimum-steel rule")
    sp.add_argument("--Asv", type=float, default=0.0, help="area of one set of ligature legs mm2")
    sp.add_argument("--s", type=float, default=0.0, help="ligature spacing mm")
    sp.add_argument("--fsyf", type=float, default=500)
    sp.add_argument("--Mstar", type=float)
    sp.add_argument("--Vstar", type=float)
    sp.set_defaults(fn=cmd_rc_beam)

    sp = sub.add_parser("as1684-widths", help="AS 1684.2 floor / roof / ceiling load widths for table lookup")
    sp.add_argument("--joist_spans", type=float, nargs="*", help="joist spans either side of the bearer, mm")
    sp.add_argument("--joist_cantilever", type=float, default=0.0)
    sp.add_argument("--rafter_span", type=float, help="horizontal rafter or truss span supported, mm")
    sp.add_argument("--overhang", type=float, default=0.0, help="horizontal eaves overhang mm")
    sp.add_argument("--pitch", type=float, default=0.0, help="roof pitch degrees")
    sp.add_argument("--ceiling_spans", type=float, nargs="*", help="ceiling joist spans either side, mm")
    sp.set_defaults(fn=cmd_as1684_widths)

    sp = sub.add_parser("as1684-bracing", help="AS 1684.2 wall bracing: racking force vs capacity, one direction")
    sp.add_argument("--direction", default="1", help="label, e.g. 'wind on long side'")
    sp.add_argument("--area", type=float, help="projected area of elevation m2")
    sp.add_argument("--pressure", type=float, help="lateral wind pressure kPa from Tables 8.1-8.5")
    sp.add_argument("--force", type=float, help="racking force kN if already known")
    sp.add_argument("--wall", action="append",
                    help="TYPE:LENGTH_m, repeatable. TYPE = a, b, c, d, e, g, h-A, h-B or a kN/m number")
    sp.add_argument("--nominal1", type=float, default=0.0, help="m of wall sheeted one side (nominal bracing)")
    sp.add_argument("--nominal2", type=float, default=0.0, help="m of wall sheeted both sides")
    sp.add_argument("--height", type=float, default=2700, help="wall height mm")
    sp.set_defaults(fn=cmd_as1684_bracing)

    sp = sub.add_parser("as1684-tiedown", help="AS 1684.2 uplift force at a tie-down connection")
    sp.add_argument("--pressure", type=float, required=True, help="net uplift pressure kPa (Table 9.5)")
    sp.add_argument("--ulw", type=float, required=True, help="uplift load width mm")
    sp.add_argument("--spacing", type=float, required=True, help="fixing spacing mm")
    sp.add_argument("--capacity", type=float, help="connector design capacity kN")
    sp.set_defaults(fn=cmd_as1684_tiedown)

    a = ap.parse_args()
    a.fn(a)
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
