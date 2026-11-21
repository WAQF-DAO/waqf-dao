#!/usr/bin/env python3
"""Zero-dependency pure Python 3.12 PNG rasterizer for WAQF DAO brand assets.

Uses analytical signed-distance geometry + box-filtered supersampling to render
crisp anti-aliased PNG icons, circle-safe GitHub/social profile avatars,
horizontal/stacked lockups, Odoo module graphics, favicons, and platform-exact
social media banners matching the canonical Medina Hisbah Vault Seal SVGs.
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
    arch_poly.extend(sample_cubic_bezier((184.0, 256.0), (184.0, 204.0), (218.0, 173.0), (256.0, 146.0), 22)[1:])
    arch_poly.extend(sample_cubic_bezier((256.0, 146.0), (294.0, 173.0), (328.0, 204.0), (328.0, 256.0), 22)[1:])
    arch_poly.append((328.0, 358.0))

    inner_arch_pts: list[tuple[float, float]] = [(196.0, 348.0), (196.0, 258.0)]
    inner_arch_pts.extend(sample_cubic_bezier((196.0, 258.0), (196.0, 213.0), (224.0, 185.0), (256.0, 161.0), 18)[1:])
    inner_arch_pts.extend(sample_cubic_bezier((256.0, 161.0), (288.0, 185.0), (316.0, 213.0), (316.0, 258.0), 18)[1:])
    inner_arch_pts.append((316.0, 348.0))

    left_wf = sample_cubic_bezier((241.0, 240.0), (223.0, 252.0), (216.0, 266.0), (216.0, 286.0), 16)
    left_wf.append((216.0, 340.0))

    right_wf = sample_cubic_bezier((271.0, 240.0), (289.0, 252.0), (296.0, 266.0), (296.0, 286.0), 16)
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

GOLD_HI = (245 / 255, 217 / 255, 147 / 255)
GOLD_MID = (212 / 255, 168 / 255, 79 / 255)
GOLD_LO = (155 / 255, 114 / 255, 34 / 255)
GOLD_DARK_HI = (212 / 255, 168 / 255, 79 / 255)
GOLD_DARK_MID = (176 / 255, 129 / 255, 36 / 255)
GOLD_DARK_LO = (138 / 255, 97 / 255, 20 / 255)
EMERALD_HI = (72 / 255, 229 / 255, 168 / 255)
EMERALD_MID = (30 / 255, 185 / 255, 128 / 255)
EMERALD_LO = (13 / 255, 110 / 255, 73 / 255)
PARCHMENT = (250 / 255, 247 / 255, 240 / 255)
INK_DARK = (17 / 255, 34 / 255, 29 / 255)


def eval_seal_pixel(
    nx: float,
    ny: float,
    px_scale: float,
    transparent_outer: bool = False,
    with_vault_glow: bool = True,
) -> tuple[float, float, float, float]:
    """Evaluate RGBA (0..1) at canonical seal coordinate (nx, ny) in [0, 512]."""
    def gold_color(x: float, y: float) -> tuple[float, float, float]:
        t = clamp((x + y) / 1024.0)
        return lerp_rgb(GOLD_HI, GOLD_MID, t * 2.0) if t < 0.45 else lerp_rgb(GOLD_MID, GOLD_LO, (t - 0.45) / 0.55)

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

            d_rim = abs(sd_round_rect(nx, ny, 256.0, 256.0, 238.0, 238.0, 106.0)) - 1.5
            col = alpha_over(col, gold_color(nx, ny), clamp(0.5 - d_rim / aa) * 0.45)

            d_inring = abs(sd_round_rect(nx, ny, 256.0, 256.0, 226.0, 226.0, 94.0)) - 0.65
            col = alpha_over(col, EMERALD_MID, clamp(0.5 - d_inring / aa) * 0.2)

    if with_vault_glow:
        r_vault = math.hypot(nx - 256.0, ny - 235.0)
        if r_vault < 176.0:
            g_t = 1.0 - r_vault / 176.0
            col = alpha_over(col, EMERALD_MID, 0.19 * (g_t**1.6))

    # Tight bounding-box cull for the Rub el Hizb octagonal seal (60..452)
    if 58.0 <= nx <= 454.0 and 58.0 <= ny <= 454.0:
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

        d_in1 = abs(sd_round_rect(nx, ny, 256.0, 256.0, 114.0, 114.0, 10.0)) - 0.85
        d_in2 = abs(sd_round_rect(rx, ry, 256.0, 256.0, 114.0, 114.0, 10.0)) - 0.85
        col = alpha_over(col, g_rgb, clamp(0.5 - d_in1 / aa) * 0.45)
        col = alpha_over(col, g_rgb, clamp(0.5 - d_in2 / aa) * 0.45)

        for ax, ay in SEAL_GEOM["anchors"]:  # type: ignore[attr-defined]
            if abs(nx - ax) < 8.5 and abs(ny - ay) < 8.5:
                d_dot = math.hypot(nx - ax, ny - ay) - 5.0
                col = alpha_over(col, (236 / 255, 199 / 255, 116 / 255), clamp(0.5 - d_dot / aa))

        # Tight bounding-box cull for inner Medina arch, keystone, and 3-channel waterfall
        if 162.0 <= nx <= 350.0 and 138.0 <= ny <= 382.0:
            arch_poly: list[tuple[float, float]] = SEAL_GEOM["arch_poly"]  # type: ignore[assignment]
            d_arch = sd_polygon(nx, ny, arch_poly)
            col = alpha_over(col, (5 / 255, 15 / 255, 12 / 255), clamp(0.5 - d_arch / aa))
            col = alpha_over(col, g_rgb, clamp(0.5 - (abs(d_arch) - 3.25) / aa))

            d_inarch = sd_polyline(nx, ny, SEAL_GEOM["inner_arch_pts"]) - 0.9  # type: ignore[arg-type]
            col = alpha_over(col, EMERALD_MID, clamp(0.5 - d_inarch / aa) * 0.35)

            if 220.0 <= nx <= 292.0 and 172.0 <= ny <= 244.0:
                d_odiam = sd_polygon(nx, ny, SEAL_GEOM["outer_diamond"])  # type: ignore[arg-type]
                col = alpha_over(col, g_rgb, clamp(0.5 - d_odiam / aa))
                d_idiam = sd_polygon(nx, ny, SEAL_GEOM["inner_diamond"])  # type: ignore[arg-type]
                t_em = clamp((ny - 190.0) / 36.0)
                col = alpha_over(col, lerp_rgb(EMERALD_HI, EMERALD_LO, t_em), clamp(0.5 - d_idiam / aa))
                d_spec = math.hypot(nx - 256.0, ny - 208.0) - 4.5
                col = alpha_over(col, PARCHMENT, clamp(0.5 - d_spec / aa))

            if 204.0 <= nx <= 308.0 and 232.0 <= ny <= 352.0:
                d_lwf = sd_polyline(nx, ny, SEAL_GEOM["left_wf"]) - 5.5  # type: ignore[arg-type]
                t_lwf = clamp((ny - 240.0) / 100.0)
                col = alpha_over(col, lerp_rgb(GOLD_MID, (16 / 255, 132 / 255, 88 / 255), t_lwf), clamp(0.5 - d_lwf / aa))

                d_cwf = sd_segment(nx, ny, 256.0, 246.0, 256.0, 342.0) - 7.0
                t_cwf = clamp((ny - 246.0) / 96.0)
                cwf_col = (
                    lerp_rgb(EMERALD_HI, EMERALD_MID, t_cwf * 2.0)
                    if t_cwf < 0.5
                    else lerp_rgb(EMERALD_MID, EMERALD_LO, (t_cwf - 0.5) * 2.0)
                )
                col = alpha_over(col, cwf_col, clamp(0.5 - d_cwf / aa))

                d_rwf = sd_polyline(nx, ny, SEAL_GEOM["right_wf"]) - 5.5  # type: ignore[arg-type]
                t_rwf = clamp((ny - 240.0) / 100.0)
                col = alpha_over(
                    col,
                    lerp_rgb((236 / 255, 199 / 255, 116 / 255), (182 / 255, 138 / 255, 50 / 255), t_rwf),
                    clamp(0.5 - d_rwf / aa),
                )

            d_p1 = sd_segment(nx, ny, 170.0, 358.0, 342.0, 358.0) - 3.25
            col = alpha_over(col, g_rgb, clamp(0.5 - d_p1 / aa))
            d_p2 = sd_segment(nx, ny, 204.0, 374.0, 308.0, 374.0) - 2.0
            col = alpha_over(col, EMERALD_MID, clamp(0.5 - d_p2 / aa) * 0.85)

    return col


def encode_png_rgba(width: int, height: int, rgba_bytes: bytes) -> bytes:
    """Write standard PNG RGBA image using pure zlib + struct."""
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(rgba_bytes[y * stride : (y + 1) * stride])

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        crc = zlib.crc32(body) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=6)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def render_seal_buffer(size: int, transparent_outer: bool = False) -> bytearray:
    buf = bytearray(size * size * 4)
    scale = 1.12 if transparent_outer else 1.0
    px_scale = (size / 512.0) * scale
    inv = 512.0 / size
    idx = 0
    for y in range(size):
        ny = 256.0 + ((y + 0.5) * inv - 256.0) / scale
        for x in range(size):
            nx = 256.0 + ((x + 0.5) * inv - 256.0) / scale
            r, g, b, a = eval_seal_pixel(nx, ny, px_scale, transparent_outer=transparent_outer)
            buf[idx] = int(clamp(r) * 255.0 + 0.5)
            buf[idx + 1] = int(clamp(g) * 255.0 + 0.5)
            buf[idx + 2] = int(clamp(b) * 255.0 + 0.5)
            buf[idx + 3] = int(clamp(a) * 255.0 + 0.5)
            idx += 4
    return buf


def render_profile_avatar_buffer(size: int = 1024) -> bytearray:
    """Render full-bleed opaque square avatar designed for GitHub/X circular crops."""
    buf = bytearray(size * size * 4)
    seal_scale = 0.88
    px_scale = (size / 512.0) * seal_scale
    inv = 512.0 / size
    aa = max(0.85, 1.15 / (size / 512.0))
    idx = 0
    for y in range(size):
        ny = (y + 0.5) * inv
        sny = 256.0 + (ny - 256.0) / seal_scale
        for x in range(size):
            nx = (x + 0.5) * inv
            snx = 256.0 + (nx - 256.0) / seal_scale

            # Full-bleed radial obsidian-emerald background (opaque alpha = 255 everywhere)
            dist_glow = math.hypot((nx - 179.2) / 380.0, (ny - 128.0) / 380.0)
            t_bg = clamp(dist_glow)
            if t_bg < 0.55:
                bg = lerp_rgb((19 / 255, 52 / 255, 43 / 255), (10 / 255, 27 / 255, 22 / 255), t_bg / 0.55)
            else:
                bg = lerp_rgb((10 / 255, 27 / 255, 22 / 255), (6 / 255, 17 / 255, 14 / 255), (t_bg - 0.55) / 0.45)

            col = (bg[0], bg[1], bg[2], 1.0)

            # Circular Sovereign Gold & Emerald safety frame inside circular crop margin
            r_center = math.hypot(nx - 256.0, ny - 256.0)
            if r_center < 240.0:
                d_gold_ring = abs(r_center - 230.0) - 1.85
                if d_gold_ring < 2.0:
                    t_g = clamp((nx + ny) / 1024.0)
                    grgb = lerp_rgb(GOLD_HI, GOLD_MID, t_g * 2.0) if t_g < 0.45 else lerp_rgb(GOLD_MID, GOLD_LO, (t_g - 0.45) / 0.55)
                    col = alpha_over(col, grgb, clamp(0.5 - d_gold_ring / aa) * 0.72)

                d_em_ring = abs(r_center - 216.0) - 0.75
                if d_em_ring < 2.0:
                    col = alpha_over(col, EMERALD_MID, clamp(0.5 - d_em_ring / aa) * 0.35)

                sr, sg, sb, sa = eval_seal_pixel(snx, sny, px_scale, transparent_outer=True, with_vault_glow=True)
                if sa > 0.0:
                    col = alpha_over(col, (sr, sg, sb), sa)

            buf[idx] = int(clamp(col[0]) * 255.0 + 0.5)
            buf[idx + 1] = int(clamp(col[1]) * 255.0 + 0.5)
            buf[idx + 2] = int(clamp(col[2]) * 255.0 + 0.5)
            buf[idx + 3] = 255
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
    [(0, 0), (14, 0), (29, 58), (43, 10), (53, 10), (67, 58), (82, 0), (96, 0), (74, 84), (61, 84), (48, 36), (35, 84), (22, 84)],
    [(304, 0), (366, 0), (366, 13), (318, 13), (318, 36), (358, 36), (358, 49), (318, 49), (318, 84), (304, 84)],
]
WAQF_A_OUTER = [(142, 0), (156, 0), (188, 84), (173, 84), (165, 62), (133, 62), (125, 84), (110, 84)]
WAQF_A_INNER = [(149, 18), (137, 50), (161, 50)]
WORDMARK_Q_TAIL = [(250, 56), (260, 48), (288, 86), (276, 93)]
WORDMARK_DIAMOND = [(388, 35), (395, 42), (388, 49), (381, 42)]


def build_ring_polys(cx: float, cy: float, r_out: float, r_in: float, segs: int = 44) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    outer = [(cx + r_out * math.cos(2 * math.pi * k / segs), cy + r_out * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    inner = [(cx + r_in * math.cos(2 * math.pi * k / segs), cy + r_in * math.sin(2 * math.pi * k / segs)) for k in range(segs)]
    return outer, inner


def build_d_polys(ox: float) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    outer = [(ox, 0.0), (ox + 36.0, 0.0)]
    outer.extend(sample_cubic_bezier((ox + 36.0, 0.0), (ox + 59.0, 0.0), (ox + 74.0, 17.0), (ox + 74.0, 42.0), 14)[1:])
    outer.extend(sample_cubic_bezier((ox + 74.0, 42.0), (ox + 74.0, 67.0), (ox + 59.0, 84.0), (ox + 36.0, 84.0), 14)[1:])
    outer.append((ox, 84.0))

    inner = [(ox + 14.0, 13.0), (ox + 35.0, 13.0)]
    inner.extend(sample_cubic_bezier((ox + 35.0, 13.0), (ox + 51.0, 13.0), (ox + 60.0, 25.0), (ox + 60.0, 42.0), 12)[1:])
    inner.extend(sample_cubic_bezier((ox + 60.0, 42.0), (ox + 60.0, 59.0), (ox + 51.0, 71.0), (ox + 35.0, 71.0), 12)[1:])
    inner.append((ox + 14.0, 71.0))
    return outer, inner


Q_OUTER, Q_INNER = build_ring_polys(244.0, 42.0, 42.0, 28.0)
O_OUTER, O_INNER = build_ring_polys(636.0, 42.0, 42.0, 28.0)
D_OUTER, D_INNER = build_d_polys(412.0)
DAO_A_OUTER = [(534, 0), (548, 0), (580, 84), (565, 84), (557, 62), (525, 62), (517, 84), (502, 84)]
DAO_A_INNER = [(541, 18), (529, 50), (553, 50)]


def eval_wordmark(
    wx: float,
    wy: float,
    out: tuple[float, float, float, float],
    light_mode: bool = False,
) -> tuple[float, float, float, float]:
    """Composite custom vector WAQF DAO wordmark in local [0..680, 0..95] space."""
    if wx < -2.0 or wx > 684.0 or wy < -2.0 or wy > 95.0:
        return out

    waqf_rgb = INK_DARK if light_mode else PARCHMENT

    # Left segment: WAQF (x in 0..370)
    if wx <= 372.0:
        d_w = 1e9
        if wx <= 100.0:
            d_w = min(d_w, sd_polygon(wx, wy, WORDMARK_WAQF_SOLID[0]))
        elif 106.0 <= wx <= 192.0:
            d_w = min(d_w, max(sd_polygon(wx, wy, WAQF_A_OUTER), -sd_polygon(wx, wy, WAQF_A_INNER)))
        elif 198.0 <= wx <= 292.0:
            d_w = min(d_w, max(sd_polygon(wx, wy, Q_OUTER), -sd_polygon(wx, wy, Q_INNER)))
        elif wx >= 300.0:
            d_w = min(d_w, sd_polygon(wx, wy, WORDMARK_WAQF_SOLID[1]))
        if d_w < 1.3:
            out = alpha_over(out, waqf_rgb, clamp(0.5 - d_w))

    # Accent Q tail + Right segment: DAO
    d_g = 1e9
    if 246.0 <= wx <= 292.0 and wy >= 44.0:
        d_g = min(d_g, sd_polygon(wx, wy, WORDMARK_Q_TAIL))
    elif 408.0 <= wx <= 490.0:
        d_g = min(d_g, max(sd_polygon(wx, wy, D_OUTER), -sd_polygon(wx, wy, D_INNER)))
    elif 498.0 <= wx <= 584.0:
        d_g = min(d_g, max(sd_polygon(wx, wy, DAO_A_OUTER), -sd_polygon(wx, wy, DAO_A_INNER)))
    elif wx >= 590.0:
        d_g = min(d_g, max(sd_polygon(wx, wy, O_OUTER), -sd_polygon(wx, wy, O_INNER)))

    if d_g < 1.3:
        if light_mode and wx >= 400.0:
            gt = clamp(wy / 84.0)
            gcol = lerp_rgb(EMERALD_MID, (11 / 255, 102 / 255, 67 / 255), gt)
        elif light_mode:
            gcol = GOLD_DARK_MID
        else:
            gt = clamp((wx - 250.0) / 420.0)
            gcol = lerp_rgb(GOLD_HI, GOLD_MID, gt) if gt < 0.6 else lerp_rgb(GOLD_MID, GOLD_LO, (gt - 0.6) / 0.4)
        out = alpha_over(out, gcol, clamp(0.5 - d_g))

    if 378.0 <= wx <= 398.0 and 32.0 <= wy <= 52.0:
        d_dia = sd_polygon(wx, wy, WORDMARK_DIAMOND)
        if d_dia < 1.3:
            dia_col = (16 / 255, 132 / 255, 88 / 255) if light_mode else EMERALD_MID
            out = alpha_over(out, dia_col, clamp(0.5 - d_dia))

    return out


# Crisp 5x7 uppercase glyph strokes for OpenGraph / banner metric & badge labels
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
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
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


def render_horizontal_lockup(light_mode: bool = False) -> bytes:
    width, height = 1200, 340
    buf = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            t = clamp((x / 1200.0 + y / 340.0) * 0.5)
            if light_mode:
                bg = lerp_rgb((250 / 255, 247 / 255, 240 / 255), (239 / 255, 231 / 255, 214 / 255), t)
                out = (bg[0], bg[1], bg[2], 1.0)
                d_frame = abs(sd_round_rect(x + 0.5, y + 0.5, 600.0, 170.0, 598.0, 168.0, 22.0)) - 1.2
                if d_frame < 1.5:
                    out = alpha_over(out, (216 / 255, 206 / 255, 184 / 255), clamp(0.5 - d_frame))
            else:
                bg = lerp_rgb((13 / 255, 38 / 255, 31 / 255), (5 / 255, 15 / 255, 12 / 255), t)
                out = (bg[0], bg[1], bg[2], 1.0)
                d_frame = abs(sd_round_rect(x + 0.5, y + 0.5, 600.0, 170.0, 598.0, 168.0, 22.0)) - 1.0
                if d_frame < 1.5:
                    out = alpha_over(out, GOLD_MID, clamp(0.5 - d_frame) * 0.35)

            if 44 <= x <= 304 and 40 <= y <= 300:
                snx = (x + 0.5 - 46.0) * 2.0
                sny = (y + 0.5 - 42.0) * 2.0
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 0.5)
                    out = alpha_over(out, (sr, sg, sb), sa)

            if 344 <= x <= 1075 and 82 <= y <= 190:
                out = eval_wordmark((x + 0.5 - 348.0) / 1.06, (y + 0.5 - 86.0) / 1.06, out, light_mode=light_mode)

            # Bottom governance pills (y=238..270)
            if 236 <= y <= 272:
                pill_specs = [
                    (433.0, 83.0, (16 / 255, 132 / 255, 88 / 255)),
                    (602.0, 72.0, GOLD_DARK_MID if light_mode else GOLD_MID),
                    (780.0, 92.0, INK_DARK if light_mode else PARCHMENT),
                    (984.0, 98.0, (16 / 255, 132 / 255, 88 / 255)),
                ]
                for pcx, phw, pcol in pill_specs:
                    dp = sd_round_rect(x + 0.5, y + 0.5, pcx, 254.0, phw, 16.0, 16.0)
                    if dp < 1.4:
                        fill_op = 0.12 if light_mode else 0.18
                        stroke_op = 0.38 if light_mode else 0.45
                        out = alpha_over(out, pcol, clamp(0.5 - dp) * fill_op)
                        out = alpha_over(out, pcol, clamp(0.5 - (abs(dp) - 0.6)) * stroke_op)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    sub_rgb = (138, 97, 20) if light_mode else (236, 199, 116)
    draw_mini_text(buf, width, height, "INSTITUTIONAL ON-CHAIN ENDOWMENT PROTOCOL", 350, 202, 3, sub_rgb)
    if light_mode:
        draw_mini_text(buf, width, height, "AAOIFI SS 60", 362, 247, 2, (11, 102, 67))
        draw_mini_text(buf, width, height, "PSAK 412", 554, 247, 2, (124, 86, 15))
        draw_mini_text(buf, width, height, "DIGITAL HISBAH", 697, 247, 2, (17, 34, 29))
        draw_mini_text(buf, width, height, "4X KAP WTP", 924, 247, 2, (11, 102, 67))
    else:
        draw_mini_text(buf, width, height, "AAOIFI SS 60", 362, 247, 2, (110, 231, 183))
        draw_mini_text(buf, width, height, "PSAK 412", 554, 247, 2, (245, 217, 147))
        draw_mini_text(buf, width, height, "DIGITAL HISBAH", 697, 247, 2, (230, 236, 233))
        draw_mini_text(buf, width, height, "4X KAP WTP", 924, 247, 2, (167, 243, 208))

    return encode_png_rgba(width, height, bytes(buf))


def render_stacked_crest() -> bytes:
    width, height = 800, 800
    buf = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            dist_glow = math.hypot((x - 400.0) / 600.0, (y - 256.0) / 600.0)
            t = clamp(dist_glow)
            bg = lerp_rgb((18 / 255, 50 / 255, 41 / 255), (6 / 255, 17 / 255, 14 / 255), t)
            out = (bg[0], bg[1], bg[2], 1.0)

            d_frame = abs(sd_round_rect(x + 0.5, y + 0.5, 400.0, 400.0, 382.0, 382.0, 36.0)) - 1.0
            if d_frame < 1.5:
                out = alpha_over(out, GOLD_MID, clamp(0.5 - d_frame) * 0.38)

            if 190 <= x <= 610 and 72 <= y <= 492:
                snx = (x + 0.5 - 195.0) / 0.8
                sny = (y + 0.5 - 76.0) / 0.8
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 0.8, transparent_outer=True)
                    out = alpha_over(out, (sr, sg, sb), sa)

            if 98 <= x <= 705 and 520 <= y <= 614:
                out = eval_wordmark((x + 0.5 - 102.0) / 0.88, (y + 0.5 - 524.0) / 0.88, out, light_mode=False)

            if 673 <= y <= 675 and 190 <= x <= 610:
                out = alpha_over(out, GOLD_MID, 0.35)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    draw_mini_text(buf, width, height, "TAHBISUL ASHLI WA TASBILUL MANFA AH", 192, 642, 2, (236, 199, 116))
    draw_mini_text(buf, width, height, "AAOIFI SS 60 · PSAK 412 · UU 41/2004", 184, 700, 2, (166, 186, 179))
    return encode_png_rgba(width, height, bytes(buf))


def render_og_banner(width: int = 1200, height: int = 630) -> bytes:
    buf = bytearray(width * height * 4)
    ox = (width - 1200) // 2
    oy = (height - 630) // 2

    for y in range(height):
        cy_l = y - oy
        for x in range(width):
            cx_l = x - ox
            dist_glow = math.hypot((cx_l - 280.0) / 860.0, (cy_l - 120.0) / 560.0)
            t = clamp(dist_glow)
            if t < 0.55:
                col = lerp_rgb((20 / 255, 55 / 255, 45 / 255), (10 / 255, 27 / 255, 22 / 255), t / 0.55)
            else:
                col = lerp_rgb((10 / 255, 27 / 255, 22 / 255), (6 / 255, 17 / 255, 14 / 255), (t - 0.55) / 0.45)

            out = (col[0], col[1], col[2], 1.0)

            d_frame = abs(sd_round_rect(x + 0.5, y + 0.5, width / 2.0, height / 2.0, width / 2.0 - 18.0, height / 2.0 - 18.0, 24.0)) - 1.0
            if d_frame < 1.2:
                out = alpha_over(out, GOLD_MID, clamp(0.5 - d_frame) * 0.34)

            if 50 <= cy_l <= 90:
                d_p1 = sd_round_rect(cx_l + 0.5, cy_l + 0.5, 255.0, 70.0, 191.0, 16.0, 16.0)
                if d_p1 < 1.5:
                    out = alpha_over(out, (16 / 255, 132 / 255, 88 / 255), clamp(0.5 - d_p1) * 0.22)
                    out = alpha_over(out, EMERALD_MID, clamp(0.5 - (abs(d_p1) - 0.7)) * 0.55)
                d_p2 = sd_round_rect(cx_l + 0.5, cy_l + 0.5, 682.0, 70.0, 214.0, 16.0, 16.0)
                if d_p2 < 1.5:
                    out = alpha_over(out, GOLD_MID, clamp(0.5 - d_p2) * 0.16)
                    out = alpha_over(out, GOLD_MID, clamp(0.5 - (abs(d_p2) - 0.7)) * 0.5)

            if 58 <= cx_l <= 290 and 120 <= cy_l <= 352:
                snx = (cx_l + 0.5 - 64.0) * (512.0 / 220.0)
                sny = (cy_l + 0.5 - 126.0) * (512.0 / 220.0)
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 220.0 / 512.0)
                    out = alpha_over(out, (sr, sg, sb), sa)

            if 316 <= cx_l <= 1040 and 148 <= cy_l <= 246:
                out = eval_wordmark((cx_l + 0.5 - 320.0) / 0.95, (cy_l + 0.5 - 152.0) / 0.95, out, light_mode=False)

            if 381 <= cy_l <= 383 and 64 <= cx_l <= 1136:
                out = alpha_over(out, GOLD_MID, 0.25)

            if 408 <= cy_l <= 536:
                for ci in range(4):
                    cx = 64.0 + ci * 272.0 + 126.0
                    dc = sd_round_rect(cx_l + 0.5, cy_l + 0.5, cx, 472.0, 126.0, 62.0, 16.0)
                    if dc < 1.5:
                        out = alpha_over(out, (16 / 255, 40 / 255, 34 / 255), clamp(0.5 - dc))
                        out = alpha_over(out, GOLD_MID, clamp(0.5 - (abs(dc) - 0.7)) * 0.35)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    draw_mini_text(buf, width, height, "AAOIFI SS 60 · PSAK 412 · UU 41", ox + 82, oy + 63, 2, (110, 231, 183))
    draw_mini_text(buf, width, height, "STBPN BWI 3.3.00386 · 4X KAP WTP", ox + 490, oy + 63, 2, (245, 217, 147))
    draw_mini_text(buf, width, height, "INSTITUTIONAL ON-CHAIN ENDOWMENT PROTOCOL", ox + 322, oy + 266, 3, (236, 199, 116))
    draw_mini_text(buf, width, height, "TAHBISUL ASHLI WA TASBILUL MANFA AH · DIGITAL HISBAH", ox + 322, oy + 304, 2, (166, 186, 179))

    cards = [
        ("GENESIS ASSETS FY26", "RP 1,404 M", "PSAK 412 DIFF = 0", (245, 217, 147), (110, 231, 183)),
        ("EXTERNAL AUDIT", "4X KAP WTP", "UNQUALIFIED 22-25", (245, 217, 147), (166, 186, 179)),
        ("NAUTERA RWA WPUD", "18.02% P.A.", "IJARAH+QARDH 0.42", (110, 231, 183), (166, 186, 179)),
        ("CLEAN WATER WPAIR", "SROI 4.11X", "41 CLUSTERS · 26K", (110, 231, 183), (166, 186, 179)),
    ]
    for ci, (lbl, val, sub, val_rgb, sub_rgb) in enumerate(cards):
        bx = ox + 64 + ci * 272 + 18
        draw_mini_text(buf, width, height, lbl, bx, oy + 428, 2, (166, 186, 179))
        draw_mini_text(buf, width, height, val, bx, oy + 460, 3, val_rgb)
        draw_mini_text(buf, width, height, sub, bx, oy + 502, 2, sub_rgb)

    draw_mini_text(buf, width, height, "YAYASAN AMAL PRODUKTIF INDONESIA · PT PIB · FWP · ANI", ox + 64, oy + 570, 2, (166, 186, 179))
    draw_mini_text(buf, width, height, "WAQF-DAO-EXPLORER.PAGES.DEV", ox + 808, oy + 570, 2, (236, 199, 116))
    return encode_png_rgba(width, height, bytes(buf))


def render_x_header(width: int = 1500, height: int = 500) -> bytes:
    """Render 1500x500 X / GitHub Organization Header with left safe zone."""
    buf = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            dist_glow = math.hypot((x - 975.0) / 1100.0, (y - 175.0) / 420.0)
            t = clamp(dist_glow)
            col = lerp_rgb((20 / 255, 55 / 255, 45 / 255), (6 / 255, 17 / 255, 14 / 255), t)
            out = (col[0], col[1], col[2], 1.0)

            if 356 <= x <= 640 and 110 <= y <= 394:
                snx = (x + 0.5 - 360.0) / 0.54
                sny = (y + 0.5 - 114.0) / 0.54
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 0.54)
                    out = alpha_over(out, (sr, sg, sb), sa)

            if 672 <= x <= 1410 and 134 <= y <= 242:
                out = eval_wordmark((x + 0.5 - 676.0) / 1.06, (y + 0.5 - 138.0) / 1.06, out, light_mode=False)

            if 342 <= y <= 380:
                for pcx, phw, pcol in [
                    (818.0, 140.0, EMERALD_MID),
                    (1118.0, 142.0, GOLD_MID),
                ]:
                    dp = sd_round_rect(x + 0.5, y + 0.5, pcx, 361.0, phw, 17.0, 17.0)
                    if dp < 1.5:
                        out = alpha_over(out, pcol, clamp(0.5 - dp) * 0.18)
                        out = alpha_over(out, pcol, clamp(0.5 - (abs(dp) - 0.7)) * 0.45)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    draw_mini_text(buf, width, height, "NEO-PASAR MADINAH · INSTITUTIONAL ON-CHAIN ENDOWMENT", 678, 258, 2, (236, 199, 116))
    draw_mini_text(buf, width, height, "OWNERLESS VAULTS (AAOIFI SS 60) · ODOO 20.0 MERKLE PROOFS", 678, 294, 2, (166, 186, 179))
    draw_mini_text(buf, width, height, "4X KAP WTP (2022-25)", 698, 354, 2, (110, 231, 183))
    draw_mini_text(buf, width, height, "STBPN BWI 3.3.00386", 1004, 354, 2, (245, 217, 147))
    return encode_png_rgba(width, height, bytes(buf))


def render_linkedin_cover(width: int = 1584, height: int = 396) -> bytes:
    """Render 1584x396 LinkedIn Institutional Cover with left profile safe zone."""
    buf = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            t = clamp((x / 1584.0 + y / 396.0) * 0.5)
            col = lerp_rgb((6 / 255, 17 / 255, 14 / 255), (13 / 255, 37 / 255, 30 / 255), t)
            out = (col[0], col[1], col[2], 1.0)

            if 339 <= x <= 341 and 54 <= y <= 342:
                out = alpha_over(out, GOLD_MID, 0.3)

            if 378 <= x <= 604 and 88 <= y <= 314:
                snx = (x + 0.5 - 382.0) / 0.42
                sny = (y + 0.5 - 92.0) / 0.42
                if 0.0 <= snx <= 512.0 and 0.0 <= sny <= 512.0:
                    sr, sg, sb, sa = eval_seal_pixel(snx, sny, 0.42)
                    out = alpha_over(out, (sr, sg, sb), sa)

            if 628 <= x <= 1290 and 88 <= y <= 186:
                out = eval_wordmark((x + 0.5 - 632.0) / 0.95, (y + 0.5 - 92.0) / 0.95, out, light_mode=False)

            idx = (y * width + x) * 4
            buf[idx] = int(clamp(out[0]) * 255 + 0.5)
            buf[idx + 1] = int(clamp(out[1]) * 255 + 0.5)
            buf[idx + 2] = int(clamp(out[2]) * 255 + 0.5)
            buf[idx + 3] = 255

    draw_mini_text(buf, width, height, "INSTITUTIONAL ON-CHAIN ENDOWMENT PROTOCOL · AAOIFI SS 60 & PSAK 412", 634, 204, 2, (250, 247, 240))
    draw_mini_text(buf, width, height, "YAYASAN AMAL PRODUKTIF INDONESIA (STBPN BWI 3.3.00386) · PT PIB · FWP · ANI", 634, 244, 2, (236, 199, 116))
    draw_mini_text(buf, width, height, "4X KAP WTP · RP 1.404M ASSETS · 18.02% P.A. NAUTERA · SROI 4.11X WPAIR", 634, 284, 2, (110, 231, 183))
    return encode_png_rgba(width, height, bytes(buf))


def main() -> None:
    ODOO_DESC.mkdir(parents=True, exist_ok=True)
    EXPLORER_PUBLIC.mkdir(parents=True, exist_ok=True)
    BRAND_LOGOS.mkdir(parents=True, exist_ok=True)
    BRAND_SOCIAL.mkdir(parents=True, exist_ok=True)

    # 1. App Seal Icons & Transparent Mark
    buf_1024 = render_seal_buffer(1024, transparent_outer=False)
    (BRAND_LOGOS / "waqf-dao-mark-1024.png").write_bytes(encode_png_rgba(1024, 1024, bytes(buf_1024)))
    buf_512 = downsample_box2(buf_1024, 1024)
    (BRAND_LOGOS / "waqf-dao-mark-512.png").write_bytes(encode_png_rgba(512, 512, bytes(buf_512)))
    buf_256 = downsample_box2(buf_512, 512)
    (ODOO_DESC / "icon.png").write_bytes(encode_png_rgba(256, 256, bytes(buf_256)))

    buf_180 = render_seal_buffer(180, transparent_outer=False)
    (EXPLORER_PUBLIC / "apple-touch-icon.png").write_bytes(encode_png_rgba(180, 180, bytes(buf_180)))
    buf_32 = downsample_box2(downsample_box2(downsample_box2(buf_256, 256), 128), 64)
    (EXPLORER_PUBLIC / "favicon-32x32.png").write_bytes(encode_png_rgba(32, 32, bytes(buf_32)))

    buf_trans_1024 = render_seal_buffer(1024, transparent_outer=True)
    (BRAND_LOGOS / "waqf-dao-mark-transparent-1024.png").write_bytes(encode_png_rgba(1024, 1024, bytes(buf_trans_1024)))

    # 2. Circle-Safe Full-Bleed GitHub / Social Profile Avatars (Opaque 1024 & 512)
    prof_1024 = render_profile_avatar_buffer(1024)
    (BRAND_LOGOS / "waqf-dao-profile-avatar-1024.png").write_bytes(encode_png_rgba(1024, 1024, bytes(prof_1024)))
    prof_512 = downsample_box2(prof_1024, 1024)
    (BRAND_LOGOS / "waqf-dao-profile-avatar-512.png").write_bytes(encode_png_rgba(512, 512, bytes(prof_512)))

    # 3. Horizontal & Stacked Logo Lockups (PNG)
    (BRAND_LOGOS / "waqf-dao-horizontal-dark.png").write_bytes(render_horizontal_lockup(light_mode=False))
    (BRAND_LOGOS / "waqf-dao-horizontal-light.png").write_bytes(render_horizontal_lockup(light_mode=True))
    (BRAND_LOGOS / "waqf-dao-stacked.png").write_bytes(render_stacked_crest())

    # 4. Copy canonical SVG icon into Odoo & Explorer public favicon
    shutil.copyfile(BRAND_LOGOS / "waqf-dao-mark.svg", ODOO_DESC / "icon.svg")
    shutil.copyfile(BRAND_LOGOS / "favicon.svg", EXPLORER_PUBLIC / "favicon.svg")

    # 5. OpenGraph & Platform-Exact Social Banners (PNG)
    og_png = render_og_banner(1200, 630)
    (BRAND_SOCIAL / "og-banner.png").write_bytes(og_png)
    (EXPLORER_PUBLIC / "og-banner.png").write_bytes(og_png)
    (BRAND_SOCIAL / "github-social-preview-1280x640.png").write_bytes(render_og_banner(1280, 640))
    (BRAND_SOCIAL / "x-header-banner.png").write_bytes(render_x_header(1500, 500))
    (BRAND_SOCIAL / "linkedin-cover.png").write_bytes(render_linkedin_cover(1584, 396))

    print("Generated all WAQF DAO raster PNG, circle-safe GitHub avatars, lockups, and social banners.")


if __name__ == "__main__":
    main()
