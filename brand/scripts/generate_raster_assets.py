#!/usr/bin/env python3
"""Zero-dependency pure Python 3.12 PNG rasterizer for WAQF DAO brand assets.

Uses analytical signed-distance geometry + box-filtered supersampling to render
crisp anti-aliased PNG icons, Odoo module graphics, favicons, and OpenGraph cards
matching the canonical Medina Hisbah Vault Seal SVG specification.
"""

from __future__ import annotations

import math
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRAND_LOGOS = ROOT / "brand" / "logos"
BRAND_SOCIAL = ROOT / "brand" / "social"
ODOO_DESC = ROOT / "odoo-addons" / "waqf_dao_oracle" / "static" / "description"
EXPLORER_PUBLIC = ROOT / "apps" / "explorer" / "public"


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if v < lo else (hi if v > hi else v)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_rgb(c1: tuple[float, float, float], c2: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    t = clamp(t)
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def alpha_over(
    dst: tuple[float, float, float, float],
    src_rgb: tuple[float, float, float],
    src_a: float,
) -> tuple[float, float, float, float]:
    a = clamp(src_a)
    if a <= 0.0:
        return dst
    dr, dg, db, da = dst
    sr, sg, sb = src_rgb
    out_a = a + da * (1.0 - a)
    if out_a <= 1e-9:
        return (0.0, 0.0, 0.0, 0.0)
    out_r = (sr * a + dr * da * (1.0 - a)) / out_a
    out_g = (sg * a + dg * da * (1.0 - a)) / out_a
    out_b = (sb * a + db * da * (1.0 - a)) / out_a
    return (out_r, out_g, out_b, out_a)


def sd_round_rect(px: float, py: float, cx: float, cy: float, hw: float, hh: float, r: float) -> float:
    qx = abs(px - cx) - (hw - r)
    qy = abs(py - cy) - (hh - r)
    ox = max(qx, 0.0)
    oy = max(qy, 0.0)
    return math.hypot(ox, oy) + min(max(qx, qy), 0.0) - r


def sd_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    pax = px - ax
    pay = py - ay
    bax = bx - ax
    bay = by - ay
    denom = bax * bax + bay * bay
    h = clamp((pax * bax + pay * bay) / denom) if denom > 1e-12 else 0.0
    return math.hypot(pax - bax * h, pay - bay * h)


def sd_polyline(px: float, py: float, pts: list[tuple[float, float]]) -> float:
    best = 1e9
    for i in range(len(pts) - 1):
        d = sd_segment(px, py, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
        if d < best:
            best = d
    return best


def point_in_polygon(px: float, py: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / ((yj - yi) + 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def sd_polygon(px: float, py: float, poly: list[tuple[float, float]]) -> float:
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        d = sd_segment(px, py, ax, ay, bx, by)
        if d < best:
            best = d
    return -best if point_in_polygon(px, py, poly) else best


def sample_cubic_bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 24,
) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for k in range(steps + 1):
        t = k / steps
        u = 1.0 - t
        x = (u**3) * p0[0] + 3 * (u**2) * t * p1[0] + 3 * u * (t**2) * p2[0] + (t**3) * p3[0]
        y = (u**3) * p0[1] + 3 * (u**2) * t * p1[1] + 3 * u * (t**2) * p2[1] + (t**3) * p3[1]
        pts.append((x, y))
    return pts


def build_seal_geometry() -> dict[str, object]:
    arch_poly: list[tuple[float, float]] = [(184.0, 358.0), (184.0, 256.0)]
    arch_poly.extend(sample_cubic_bezier((184.0, 256.0), (184.0, 204.0), (218.0, 173.0), (256.0, 146.0), 28)[1:])
    arch_poly.extend(sample_cubic_bezier((256.0, 146.0), (294.0, 173.0), (328.0, 204.0), (328.0, 256.0), 28)[1:])
    arch_poly.append((328.0, 358.0))

    inner_arch_pts: list[tuple[float, float]] = [(196.0, 348.0), (196.0, 258.0)]
    inner_arch_pts.extend(sample_cubic_bezier((196.0, 258.0), (196.0, 213.0), (224.0, 185.0), (256.0, 161.0), 24)[1:])
    inner_arch_pts.extend(sample_cubic_bezier((256.0, 161.0), (288.0, 185.0), (316.0, 213.0), (316.0, 258.0), 24)[1:])
    inner_arch_pts.append((316.0, 348.0))

    left_wf = sample_cubic_bezier((241.0, 240.0), (223.0, 252.0), (216.0, 266.0), (216.0, 286.0), 20)
    left_wf.append((216.0, 340.0))

    right_wf = sample_cubic_bezier((271.0, 240.0), (289.0, 252.0), (296.0, 266.0), (296.0, 286.0), 20)
    right_wf.append((296.0, 340.0))

    outer_diamond = [(256.0, 178.0), (286.0, 208.0), (256.0, 238.0), (226.0, 208.0)]
    inner_diamond = [(256.0, 190.0), (274.0, 208.0), (256.0, 226.0), (238.0, 208.0)]
    anchors = [
        (256.0, 69.0),
        (388.0, 124.0),
        (443.0, 256.0),
        (388.0, 388.0),
        (256.0, 443.0),
        (124.0, 388.0),
        (69.0, 256.0),
        (124.0, 124.0),
    ]
    return {
        "arch_poly": arch_poly,
        "inner_arch_pts": inner_arch_pts,
        "left_wf": left_wf,
        "right_wf": right_wf,
        "outer_diamond": outer_diamond,
        "inner_diamond": inner_diamond,
        "anchors": anchors,
    }


SEAL_GEOM = build_seal_geometry()
COS45 = math.cos(math.pi / 4.0)
SIN45 = math.sin(math.pi / 4.0)


def eval_seal_pixel(nx: float, ny: float, px_scale: float, transparent_outer: bool = False) -> tuple[float, float, float, float]:
    """Evaluate RGBA (0..1) at canonical seal coordinate (nx, ny) in [0, 512]."""
    gold_hi = (245 / 255, 217 / 255, 147 / 255)
    gold_mid = (212 / 255, 168 / 255, 79 / 255)
    gold_lo = (155 / 255, 114 / 255, 34 / 255)
    emerald_hi = (72 / 255, 229 / 255, 168 / 255)
    emerald_mid = (30 / 255, 185 / 255, 128 / 255)
    emerald_lo = (13 / 255, 110 / 255, 73 / 255)
    parchment = (250 / 255, 247 / 255, 240 / 255)

    def gold_color(x: float, y: float) -> tuple[float, float, float]:
        t = clamp((x + y) / 1024.0)
        return lerp_rgb(gold_hi, gold_mid, t * 2.0) if t < 0.45 else lerp_rgb(gold_mid, gold_lo, (t - 0.45) / 0.55)

    col: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    aa = max(0.9, 1.15 / px_scale)

    if not transparent_outer:
        d_shield = sd_round_rect(nx, ny, 256.0, 256.0, 240.0, 240.0, 108.0)
        cov_shield = clamp(0.5 - d_shield / aa)
        if cov_shield > 0.0:
            dist_glow = math.hypot((nx - 179.2) / 380.0, (ny - 128.0) / 380.0)
            t_bg = clamp(dist_glow)
            if t_bg < 0.55:
                bg_rgb = lerp_rgb((19 / 255, 52 / 255, 43 / 255), (10 / 255, 27 / 255, 22 / 255), t_bg / 0.55)
            else:
                bg_rgb = lerp_rgb((10 / 255, 27 / 255, 22 / 255), (6 / 255, 17 / 255, 14 / 255), (t_bg - 0.55) / 0.45)
            col = alpha_over(col, bg_rgb, cov_shield)

            # Outer gold shield rim (radius 238, stroke 3)
            d_rim = abs(sd_round_rect(nx, ny, 256.0, 256.0, 238.0, 238.0, 106.0)) - 1.5
            col = alpha_over(col, gold_color(nx, ny), clamp(0.5 - d_rim / aa) * 0.45)

            # Inner emerald ring (radius 226, stroke 1)
            d_inring = abs(sd_round_rect(nx, ny, 256.0, 256.0, 226.0, 226.0, 94.0)) - 0.65
            col = alpha_over(col, emerald_mid, clamp(0.5 - d_inring / aa) * 0.2)

    # Ambient central vault glow
    r_vault = math.hypot(nx - 256.0, ny - 235.0)
    if r_vault < 176.0:
        g_t = 1.0 - r_vault / 176.0
        col = alpha_over(col, emerald_mid, 0.19 * (g_t**1.6))

    # Outer Rub el Hizb squares (half-side 132, rx 14, stroke 7)
    dx = nx - 256.0
    dy = ny - 256.0
    rx = dx * COS45 + dy * SIN45 + 256.0
    ry = -dx * SIN45 + dy * COS45 + 256.0

    d_sq1 = sd_round_rect(nx, ny, 256.0, 256.0, 132.0, 132.0, 14.0)
    d_sq2 = sd_round_rect(rx, ry, 256.0, 256.0, 132.0, 132.0, 14.0)

    col = alpha_over(col, (8 / 255, 23 / 255, 19 / 255), clamp(0.5 - d_sq1 / aa) * 0.72)
    col = alpha_over(col, (8 / 255, 23 / 255, 19 / 255), clamp(0.5 - d_sq2 / aa) * 0.65)

    g_rgb = gold_color(nx, ny)
    col = alpha_over(col, g_rgb, clamp(0.5 - (abs(d_sq1) - 3.5) / aa))
    col = alpha_over(col, g_rgb, clamp(0.5 - (abs(d_sq2) - 3.5) / aa))

    # Inner hairlines (half-side 114, rx 10)
    d_in1 = abs(sd_round_rect(nx, ny, 256.0, 256.0, 114.0, 114.0, 10.0)) - 0.85
    d_in2 = abs(sd_round_rect(rx, ry, 256.0, 256.0, 114.0, 114.0, 10.0)) - 0.85
    col = alpha_over(col, g_rgb, clamp(0.5 - d_in1 / aa) * 0.45)
    col = alpha_over(col, g_rgb, clamp(0.5 - d_in2 / aa) * 0.45)

    # 8 Anchor Nodes
    for ax, ay in SEAL_GEOM["anchors"]:  # type: ignore[attr-defined]
        d_dot = math.hypot(nx - ax, ny - ay) - 5.0
        col = alpha_over(col, (236 / 255, 199 / 255, 116 / 255), clamp(0.5 - d_dot / aa))

    # Inner Pointed Medina Arch
    arch_poly: list[tuple[float, float]] = SEAL_GEOM["arch_poly"]  # type: ignore[assignment]
    d_arch = sd_polygon(nx, ny, arch_poly)
    col = alpha_over(col, (5 / 255, 15 / 255, 12 / 255), clamp(0.5 - d_arch / aa))
    col = alpha_over(col, g_rgb, clamp(0.5 - (abs(d_arch) - 3.25) / aa))

    d_inarch = sd_polyline(nx, ny, SEAL_GEOM["inner_arch_pts"]) - 0.9  # type: ignore[arg-type]
    col = alpha_over(col, emerald_mid, clamp(0.5 - d_inarch / aa) * 0.35)

    # Merkle Keystone Diamond
    d_odiam = sd_polygon(nx, ny, SEAL_GEOM["outer_diamond"])  # type: ignore[arg-type]
    col = alpha_over(col, g_rgb, clamp(0.5 - d_odiam / aa))

    d_idiam = sd_polygon(nx, ny, SEAL_GEOM["inner_diamond"])  # type: ignore[arg-type]
    t_em = clamp((ny - 190.0) / 36.0)
    col = alpha_over(col, lerp_rgb(emerald_hi, emerald_lo, t_em), clamp(0.5 - d_idiam / aa))

    d_spec = math.hypot(nx - 256.0, ny - 208.0) - 4.5
    col = alpha_over(col, parchment, clamp(0.5 - d_spec / aa))

    # 3-Channel PSAK 412 Waterfall
    d_lwf = sd_polyline(nx, ny, SEAL_GEOM["left_wf"]) - 5.5  # type: ignore[arg-type]
    t_lwf = clamp((ny - 240.0) / 100.0)
    col = alpha_over(col, lerp_rgb(gold_mid, (16 / 255, 132 / 255, 88 / 255), t_lwf), clamp(0.5 - d_lwf / aa))

    d_cwf = sd_segment(nx, ny, 256.0, 246.0, 256.0, 342.0) - 7.0
    t_cwf = clamp((ny - 246.0) / 96.0)
    col = alpha_over(
        col,
        lerp_rgb(emerald_hi, emerald_mid, t_cwf * 2.0) if t_cwf < 0.5 else lerp_rgb(emerald_mid, emerald_lo, (t_cwf - 0.5) * 2.0),
        clamp(0.5 - d_cwf / aa),
    )

    d_rwf = sd_polyline(nx, ny, SEAL_GEOM["right_wf"]) - 5.5  # type: ignore[arg-type]
    t_rwf = clamp((ny - 240.0) / 100.0)
    col = alpha_over(
        col,
        lerp_rgb((236 / 255, 199 / 255, 116 / 255), (182 / 255, 138 / 255, 50 / 255), t_rwf),
        clamp(0.5 - d_rwf / aa),
    )

    # Zero-Diff Ledger Plinth Bars
    d_p1 = sd_segment(nx, ny, 170.0, 358.0, 342.0, 358.0) - 3.25
    col = alpha_over(col, g_rgb, clamp(0.5 - d_p1 / aa))

    d_p2 = sd_segment(nx, ny, 204.0, 374.0, 308.0, 374.0) - 2.0
    col = alpha_over(col, emerald_mid, clamp(0.5 - d_p2 / aa) * 0.85)

    return col


def encode_png_rgba(width: int, height: int, rgba_bytes: bytes) -> bytes:
    """Write standard PNG RGBA image using pure zlib + struct."""
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)  # Filter type 0 (None)
        raw.extend(rgba_bytes[y * stride : (y + 1) * stride])

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        crc = zlib.crc32(body) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=6)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def render_seal_buffer(size: int) -> bytearray:
    buf = bytearray(size * size * 4)
    px_scale = size / 512.0
    inv = 512.0 / size
    idx = 0
    for y in range(size):
        ny = (y + 0.5) * inv
        for x in range(size):
            nx = (x + 0.5) * inv
            r, g, b, a = eval_seal_pixel(nx, ny, px_scale)
            buf[idx] = int(clamp(r) * 255.0 + 0.5)
            buf[idx + 1] = int(clamp(g) * 255.0 + 0.5)
            buf[idx + 2] = int(clamp(b) * 255.0 + 0.5)
            buf[idx + 3] = int(clamp(a) * 255.0 + 0.5)
            idx += 4
    return buf


def downsample_box2(src: bytearray, src_size: int) -> bytearray:
    dst_size = src_size // 2
    dst = bytearray(dst_size * dst_size * 4)
    for y in range(dst_size):
        sy = y * 2
        row0 = sy * src_size * 4
        row1 = (sy + 1) * src_size * 4
        for x in range(dst_size):
            sx4 = x * 8
            i00 = row0 + sx4
            i01 = row0 + sx4 + 4
            i10 = row1 + sx4
            i11 = row1 + sx4 + 4
            di = (y * dst_size + x) * 4
            for c in range(4):
                dst[di + c] = (src[i00 + c] + src[i01 + c] + src[i10 + c] + src[i11 + c] + 2) >> 2
    return dst


# Exact vector glyph polygons matching our SVG custom wordmark (84px cap height)
WORDMARK_WAQF_SOLID: list[list[tuple[float, float]]] = [
    # W
    [(0, 0), (14, 0), (29, 58), (43, 10), (53, 10), (67, 58), (82, 0), (96, 0), (74, 84), (61, 84), (48, 36), (35, 84), (22, 84)],
    # F
    [(304, 0), (366, 0), (366, 13), (318, 13), (318, 36), (358, 36), (358, 49), (318, 49), (318, 84), (304, 84)],
]
WAQF_A_OUTER = [(142, 0), (156, 0), (188, 84), (173, 84), (165, 62), (133, 62), (125, 84), (110, 84)]
WAQF_A_INNER = [(149, 18), (137, 50), (161, 50)]
WORDMARK_Q_TAIL = [(250, 56), (260, 48), (288, 86), (276, 93)]
WORDMARK_DIAMOND = [(388, 35), (395, 42), (388, 49), (381, 42)]


def build_ring_polys(cx: float, cy: float, r_out: float, r_in: float, segs: int = 48) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    outer = [(cx + r_out * math.cos(2 * math.pi * k / segs), cy + r_out * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    inner = [(cx + r_in * math.cos(2 * math.pi * k / segs), cy + r_in * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    return outer, inner


def build_d_polys(ox: float) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    outer = [(ox, 0.0), (ox + 36.0, 0.0)]
    outer.extend(sample_cubic_bezier((ox + 36.0, 0.0), (ox + 59.0, 0.0), (ox + 74.0, 17.0), (ox + 74.0, 42.0), 16)[1:])
    outer.extend(sample_cubic_bezier((ox + 74.0, 42.0), (ox + 74.0, 67.0), (ox + 59.0, 84.0), (ox + 36.0, 84.0), 16)[1:])
    outer.append((ox, 84.0))

    inner = [(ox + 14.0, 13.0), (ox + 35.0, 13.0)]
    inner.extend(sample_cubic_bezier((ox + 35.0, 13.0), (ox + 51.0, 13.0), (ox + 60.0, 25.0), (ox + 60.0, 42.0), 14)[1:])
    inner.extend(sample_cubic_bezier((ox + 60.0, 42.0), (ox + 60.0, 59.0), (ox + 51.0, 71.0), (ox + 35.0, 71.0), 14)[1:])
    inner.append((ox + 14.0, 71.0))
    return outer, inner


Q_OUTER, Q_INNER = build_ring_polys(244.0, 42.0, 42.0, 28.0)
O_OUTER, O_INNER = build_ring_polys(636.0, 42.0, 42.0, 28.0)
D_OUTER, D_INNER = build_d_polys(412.0)
DAO_A_OUTER = [(534, 0), (548, 0), (580, 84), (565, 84), (557, 62), (525, 62), (517, 84), (502, 84)]
DAO_A_INNER = [(541, 18), (529, 50), (553, 50)]


# Crisp 5x7 uppercase glyph strokes for OpenGraph metric & badge labels
MINI_FONT: dict[str, list[str]] = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "·": ["00000", "00000", "00100", "01110", "00100", "00000", "00000"],
}


def draw_mini_text(buf: bytearray, w: int, h: int, text: str, x0: int, y0: int, scale: int, rgb: tuple[int, int, int]) -> None:
    cx = x0
    for ch in text.upper():
        rows = MINI_FONT.get(ch, MINI_FONT[" "])
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "1":
                    for dy in range(scale):
                        py = y0 + ry * scale + dy
                        if 0 <= py < h:
                            for dx in range(scale):
                                px = cx + rx * scale + dx
                                if 0 <= px < w:
                                    idx = (py * w + px) * 4
                                    buf[idx], buf[idx + 1], buf[idx + 2], buf[idx + 3] = rgb[0], rgb[1], rgb[2], 255
        cx += 6 * scale


def render_og_banner(width: int = 1200, height: int = 630) -> bytes:
    buf = bytearray(width * height * 4)
    gold_hi = (246 / 255, 220 / 255, 151 / 255)
    gold_mid = (212 / 255, 168 / 255, 79 / 255)
    gold_lo = (155 / 255, 114 / 255, 34 / 255)
    emerald_mid = (30 / 255, 185 / 255, 128 / 255)
    parchment = (250 / 255, 247 / 255, 240 / 255)

    for y in range(height):
        for x in range(width):
            dist_glow = math.hypot((x - 280.0) / 860.0, (y - 120.0) / 560.0)
            t = clamp(dist_glow)
            if t < 0.55:
                col = lerp_rgb((20 / 255, 55 / 255, 45 / 255), (10 / 255, 27 / 255, 22 / 255), t / 0.55)
            else:
                col = lerp_rgb((10 / 255, 27 / 255, 22 / 255), (6 / 255, 17 / 255, 14 / 255), (t - 0.55) / 0.45)

            out = (col[0], col[1], col[2], 1.0)

            # Outer hairline frame
            d_frame = abs(sd_round_rect(x + 0.5, y + 0.5, 600.0, 315.0, 582.0, 297.0, 24.0)) - 1.0
            if d_frame < 1.2:
                out = alpha_over(out, gold_mid, clamp(0.5 - d_frame) * 0.34)

            # Top pills (spaced cleanly with zero overlap and generous right padding)
            if 50 <= y <= 90:
                d_p1 = sd_round_rect(x + 0.5, y + 0.5, 255.0, 70.0, 191.0, 16.0, 16.0)
                if d_p1 < 1.5:
                    out = alpha_over(out, (16 / 255, 132 / 255, 88 / 255), clamp(0.5 - d_p1) * 0.22)
                    out = alpha_over(out, emerald_mid, clamp(0.5 - (abs(d_p1) - 0.7)) * 0.55)
                d_p2 = sd_round_rect(x + 0.5, y + 0.5, 682.0, 70.0, 214.0, 16.0, 16.0)
                if d_p2 < 1.5:
                    out = alpha_over(out, gold_mid, clamp(0.5 - d_p2) * 0.16)
                    out = alpha_over(out, gold_mid, clamp(0.5 - (abs(d_p2) - 0.7)) * 0.5)

            # Embedded Medina Hisbah Seal (x=64..284, y=126..346 -> scale=220/512)
            if 58 <= x <= 290 and 120 <= y <= 352:
                snx = (x + 0.5 - 64.0) * (512.0 / 220.0)
                sny = (y + 0.5 - 126.0) * (512.0 / 220.0)
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 220.0 / 512.0)
                    out = alpha_over(out, (sr, sg, sb), sa)

            # Vector Wordmark WAQF DAO at (320, 152) scale=0.95
            if 316 <= x <= 1040 and 148 <= y <= 246:
                wx = (x + 0.5 - 320.0) / 0.95
                wy = (y + 0.5 - 152.0) / 0.95
                # WAQF white glyphs
                d_w = 1e9
                for poly in WORDMARK_WAQF_SOLID:
                    d_w = min(d_w, sd_polygon(wx, wy, poly))
                d_a = max(sd_polygon(wx, wy, WAQF_A_OUTER), -sd_polygon(wx, wy, WAQF_A_INNER))
                d_w = min(d_w, d_a)
                d_q = max(sd_polygon(wx, wy, Q_OUTER), -sd_polygon(wx, wy, Q_INNER))
                d_w = min(d_w, d_q)
                if d_w < 1.2:
                    out = alpha_over(out, parchment, clamp(0.5 - d_w))

                # Q Tail & DAO in Sovereign Gold
                d_g = sd_polygon(wx, wy, WORDMARK_Q_TAIL)
                d_g = min(d_g, max(sd_polygon(wx, wy, D_OUTER), -sd_polygon(wx, wy, D_INNER)))
                d_g = min(d_g, max(sd_polygon(wx, wy, DAO_A_OUTER), -sd_polygon(wx, wy, DAO_A_INNER)))
                d_g = min(d_g, max(sd_polygon(wx, wy, O_OUTER), -sd_polygon(wx, wy, O_INNER)))
                if d_g < 1.2:
                    gt = clamp((wx - 250.0) / 420.0)
                    gcol = lerp_rgb(gold_hi, gold_mid, gt) if gt < 0.6 else lerp_rgb(gold_mid, gold_lo, (gt - 0.6) / 0.4)
                    out = alpha_over(out, gcol, clamp(0.5 - d_g))

                # Diamond dot
                d_dia = sd_polygon(wx, wy, WORDMARK_DIAMOND)
                if d_dia < 1.2:
                    out = alpha_over(out, emerald_mid, clamp(0.5 - d_dia))

            # Horizontal separator y=382
            if 381 <= y <= 383 and 64 <= x <= 1136:
                out = alpha_over(out, gold_mid, 0.25)

            # 4 Bottom Metric Cards (y=410..532)
            if 408 <= y <= 536:
                for ci in range(4):
                    cx = 64.0 + ci * 272.0 + 126.0
                    dc = sd_round_rect(x + 0.5, y + 0.5, cx, 472.0, 126.0, 62.0, 16.0)
                    if dc < 1.5:
                        out = alpha_over(out, (16 / 255, 40 / 255, 34 / 255), clamp(0.5 - dc))
                        out = alpha_over(out, gold_mid, clamp(0.5 - (abs(dc) - 0.7)) * 0.35)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    # Crisp UI text overlays (all verified inside box bounds)
    draw_mini_text(buf, width, height, "AAOIFI SS 60 · PSAK 412 · UU 41", 82, 63, 2, (110, 231, 183))
    draw_mini_text(buf, width, height, "STBPN BWI 3.3.00386 · 4X KAP WTP", 490, 63, 2, (245, 217, 147))
    draw_mini_text(buf, width, height, "INSTITUTIONAL ON-CHAIN ENDOWMENT PROTOCOL", 322, 266, 3, (236, 199, 116))
    draw_mini_text(buf, width, height, "TAHBISUL ASHLI WA TASBILUL MANFA AH · DIGITAL HISBAH", 322, 304, 2, (166, 186, 179))

    cards = [
        ("GENESIS ASSETS FY26", "RP 1,404 M", "PSAK 412 DIFF = 0", (245, 217, 147), (110, 231, 183)),
        ("EXTERNAL AUDIT", "4X KAP WTP", "UNQUALIFIED 22-25", (245, 217, 147), (166, 186, 179)),
        ("NAUTERA RWA WPUD", "18.02% P.A.", "IJARAH+QARDH 0.42", (110, 231, 183), (166, 186, 179)),
        ("CLEAN WATER WPAIR", "SROI 4.11X", "41 CLUSTERS · 26K", (110, 231, 183), (166, 186, 179)),
    ]
    for ci, (lbl, val, sub, val_rgb, sub_rgb) in enumerate(cards):
        bx = 64 + ci * 272 + 18
        draw_mini_text(buf, width, height, lbl, bx, 428, 2, (166, 186, 179))
        draw_mini_text(buf, width, height, val, bx, 460, 3, val_rgb)
        draw_mini_text(buf, width, height, sub, bx, 502, 2, sub_rgb)

    draw_mini_text(buf, width, height, "YAYASAN AMAL PRODUKTIF INDONESIA · PT PIB · FWP · ANI", 64, 570, 2, (166, 186, 179))
    draw_mini_text(buf, width, height, "WAQF-DAO-EXPLORER.PAGES.DEV", 808, 570, 2, (236, 199, 116))

    return encode_png_rgba(width, height, bytes(buf))


def main() -> None:
    ODOO_DESC.mkdir(parents=True, exist_ok=True)
    EXPLORER_PUBLIC.mkdir(parents=True, exist_ok=True)
    BRAND_LOGOS.mkdir(parents=True, exist_ok=True)
    BRAND_SOCIAL.mkdir(parents=True, exist_ok=True)

    # Render supersampled 1024x1024 master mark and derive crisp box-filtered mipmaps
    buf_1024 = render_seal_buffer(1024)
    (BRAND_LOGOS / "waqf-dao-mark-1024.png").write_bytes(encode_png_rgba(1024, 1024, bytes(buf_1024)))

    buf_512 = downsample_box2(buf_1024, 1024)
    (BRAND_LOGOS / "waqf-dao-mark-512.png").write_bytes(encode_png_rgba(512, 512, bytes(buf_512)))

    buf_256 = downsample_box2(buf_512, 512)
    (ODOO_DESC / "icon.png").write_bytes(encode_png_rgba(256, 256, bytes(buf_256)))

    buf_180 = render_seal_buffer(180)
    (EXPLORER_PUBLIC / "apple-touch-icon.png").write_bytes(encode_png_rgba(180, 180, bytes(buf_180)))

    buf_64 = downsample_box2(downsample_box2(buf_256, 256), 128)
    buf_32 = downsample_box2(buf_64, 64)
    (EXPLORER_PUBLIC / "favicon-32x32.png").write_bytes(encode_png_rgba(32, 32, bytes(buf_32)))

    # Copy canonical SVG icon into Odoo static description & Explorer public favicon
    shutil.copyfile(BRAND_LOGOS / "waqf-dao-mark.svg", ODOO_DESC / "icon.svg")
    shutil.copyfile(BRAND_LOGOS / "favicon.svg", EXPLORER_PUBLIC / "favicon.svg")

    # Render crisp 1200x630 OpenGraph social preview card
    og_png = render_og_banner(1200, 630)
    (BRAND_SOCIAL / "og-banner.png").write_bytes(og_png)
    (EXPLORER_PUBLIC / "og-banner.png").write_bytes(og_png)

    print("Generated all WAQF DAO raster PNG & copied SVG assets successfully.")


if __name__ == "__main__":
    main()
