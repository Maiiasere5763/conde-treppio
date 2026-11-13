#!/usr/bin/env python3
"""Gerador heraldico unificado do Brasao do Conde de Treppenia (V9.0):
- Vetor SVG puro (Site/PWA & WebView APK)
- Android VectorDrawable XML com gradientes aapt:attr API 24+ (Splash & Adaptive Icon)
- Bitmaps de alta resolucao (WinForms EXE & fallbacks quantizados API 24-25)
"""

import io
import math
import os
import struct
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT_DIR = r"D:\Conde_Treppio"
UI_DIR = os.path.join(ROOT_DIR, "sandbox", "ui_dicionario")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
LAUNCHER_DIR = os.path.join(ROOT_DIR, "sandbox", "launcher_exe")
ANDROID_RES = os.path.join(ROOT_DIR, "sandbox", "android_apk", "app", "src", "main", "res")
SCRATCH_PREVIEW = os.path.join(ROOT_DIR, "sandbox", "brasao_contact_sheet.png")


def _fmt_pt(x: float, y: float) -> str:
    return f"{x:.2f},{y:.2f}"


def circle_svg_path(cx: float, cy: float, r: float) -> str:
    return (
        f"M {cx - r:.2f},{cy:.2f} "
        f"A {r:.2f},{r:.2f} 0 1,0 {cx + r:.2f},{cy:.2f} "
        f"A {r:.2f},{r:.2f} 0 1,0 {cx - r:.2f},{cy:.2f} Z"
    )


def ellipse_svg_path(cx: float, cy: float, rx: float, ry: float) -> str:
    return (
        f"M {cx - rx:.2f},{cy:.2f} "
        f"A {rx:.2f},{ry:.2f} 0 1,0 {cx + rx:.2f},{cy:.2f} "
        f"A {rx:.2f},{ry:.2f} 0 1,0 {cx - rx:.2f},{cy:.2f} Z"
    )


def poly_svg_path(pts, closed: bool = True) -> str:
    parts = [f"M {_fmt_pt(pts[0][0], pts[0][1])}"]
    for x, y in pts[1:]:
        parts.append(f"L {_fmt_pt(x, y)}")
    if closed:
        parts.append("Z")
    return " ".join(parts)


def curve_band_svg_path(top_pts, bot_pts) -> str:
    pts = list(top_pts) + list(reversed(bot_pts))
    return poly_svg_path(pts, closed=True)


def open_line_svg_path(pts) -> str:
    return poly_svg_path(pts, closed=False)


def facet_hex(shade: float) -> str:
    t = max(0.0, min(1.0, 0.54 + 0.44 * shade))
    r = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [116, 198, 240, 255])))
    g = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [80, 150, 200, 242])))
    b = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [18, 42, 78, 178])))
    return f"#{r:02X}{g:02X}{b:02X}"


def build_vector_scene(vp: float = 512.0):
    """Constroi a geometria matematica unica do Brasao do Conde no viewport vp x vp."""
    cx = vp * 0.50
    shield_top = vp * 0.295
    shield_h = vp * 0.635
    shield_hw = vp * 0.345
    rim_t = vp * 0.025

    pts_outer = build_shield_polygon(cx, shield_top, shield_h, shield_hw, steps=44)
    pts_inner = build_shield_polygon(
        cx,
        shield_top + rim_t * 0.95,
        shield_h - rim_t * 2.05,
        shield_hw - rim_t,
        steps=44,
    )

    star_cy = shield_top + shield_h * 0.445
    star_rad = shield_hw * 0.69
    lx, ly = -0.64, -0.76
    inner_r = star_rad * 0.28

    star_facets = []
    star_ribs = []
    for i in range(8):
        angle_deg = -90.0 + i * 45.0
        rad = math.radians(angle_deg)
        is_card = (i % 2 == 0)
        tip_r = star_rad * (1.0 if is_card else 0.72)
        side_half_deg = 16.5 if is_card else 13.0

        p_c = (cx, star_cy)
        p_t = (cx + math.cos(rad) * tip_r, star_cy + math.sin(rad) * tip_r)
        p_l = (
            cx + math.cos(math.radians(angle_deg - side_half_deg)) * inner_r * 1.15,
            star_cy + math.sin(math.radians(angle_deg - side_half_deg)) * inner_r * 1.15,
        )
        p_r = (
            cx + math.cos(math.radians(angle_deg + side_half_deg)) * inner_r * 1.15,
            star_cy + math.sin(math.radians(angle_deg + side_half_deg)) * inner_r * 1.15,
        )
        s1 = math.cos(rad - 1.15) * lx + math.sin(rad - 1.15) * ly
        s2 = math.cos(rad + 1.15) * lx + math.sin(rad + 1.15) * ly
        star_facets.append(([p_c, p_l, p_t], facet_hex(s1)))
        star_facets.append(([p_c, p_t, p_r], facet_hex(s2)))
        if is_card:
            p0 = (cx + math.cos(rad) * (star_rad * 0.26), star_cy + math.sin(rad) * (star_rad * 0.26))
            p1 = (cx + math.cos(rad) * (star_rad * 0.98), star_cy + math.sin(rad) * (star_rad * 0.98))
            star_ribs.append((p0, p1))

    ring_r = star_rad * 0.255
    inner_disc = star_rad * 0.205
    flame_h = star_rad * 0.35
    flame_w = star_rad * 0.145
    f_top = (cx, star_cy - flame_h * 0.62)
    f_bot = (cx, star_cy + flame_h * 0.44)
    flame_l = [
        f_top,
        (cx - flame_w * 0.65, star_cy - flame_h * 0.12),
        (cx - flame_w * 0.92, star_cy + flame_h * 0.14),
        (cx - flame_w * 0.42, star_cy + flame_h * 0.38),
        f_bot,
    ]
    flame_r = [
        f_top,
        f_bot,
        (cx + flame_w * 0.42, star_cy + flame_h * 0.38),
        (cx + flame_w * 0.92, star_cy + flame_h * 0.14),
        (cx + flame_w * 0.65, star_cy - flame_h * 0.12),
    ]

    # Coronel de Conde (9 perolas)
    c_base_y = shield_top - vp * 0.008
    c_span_w = shield_hw * 1.48
    hoop_h = c_span_w * 0.175
    arch_lift = c_span_w * 0.048
    lw_half = c_span_w * 0.50

    pearls = []
    for k in range(9):
        u = -1.0 + 2.0 * (k / 8.0)
        px = cx + math.sin(u * 1.18) / math.sin(1.18) * (lw_half * 0.94)
        rim_y = c_base_y - hoop_h * 0.96 - arch_lift * (1.0 - u * u)
        stem_h = hoop_h * (0.98 - 0.22 * (u * u))
        pr = hoop_h * (0.37 - 0.05 * (u * u))
        py_top = rim_y - stem_h
        pearls.append({
            "u": u,
            "px": px,
            "rim_y": rim_y,
            "py_top": py_top,
            "pr": pr,
            "stem_l": [(px - pr * 0.85, rim_y + hoop_h * 0.12), (px, rim_y + hoop_h * 0.12), (px, py_top), (px - pr * 0.48, py_top)],
            "stem_r": [(px, rim_y + hoop_h * 0.12), (px + pr * 0.85, rim_y + hoop_h * 0.12), (px + pr * 0.48, py_top), (px, py_top)],
        })

    top_curve = []
    bot_curve = []
    for i in range(37):
        u = -1.0 + 2.0 * (i / 36.0)
        x = cx + u * lw_half
        yt = c_base_y - hoop_h - arch_lift * (1.0 - u * u) + hoop_h * 0.14 * (u * u)
        yb = c_base_y + arch_lift * 0.55 * (1.0 - u * u) - hoop_h * 0.08 * (u * u)
        top_curve.append((x, yt))
        bot_curve.append((x, yb))
    bot_hi = [(x, y - hoop_h * 0.08) for (x, y) in bot_curve]

    gems = []
    for idx_g, u in enumerate((-0.62, -0.31, 0.0, 0.31, 0.62)):
        gx = cx + u * lw_half * 0.92
        gy_top = c_base_y - hoop_h - arch_lift * (1.0 - u * u) + hoop_h * 0.14 * (u * u)
        gy_bot = c_base_y + arch_lift * 0.55 * (1.0 - u * u) - hoop_h * 0.08 * (u * u)
        gy = 0.5 * (gy_top + gy_bot)
        rx = hoop_h * (0.28 if abs(u) < 0.1 else 0.22 - 0.04 * abs(u))
        ry = hoop_h * 0.23
        gems.append({
            "gx": gx,
            "gy": gy,
            "rx": rx,
            "ry": ry,
            "is_ruby": (idx_g % 2 == 0),
        })

    return {
        "vp": vp,
        "cx": cx,
        "shield_top": shield_top,
        "shield_h": shield_h,
        "shield_hw": shield_hw,
        "pts_outer": pts_outer,
        "pts_inner": pts_inner,
        "star_cy": star_cy,
        "star_rad": star_rad,
        "star_facets": star_facets,
        "star_ribs": star_ribs,
        "ring_r": ring_r,
        "inner_disc": inner_disc,
        "flame_l": flame_l,
        "flame_r": flame_r,
        "c_base_y": c_base_y,
        "lw_half": lw_half,
        "hoop_h": hoop_h,
        "pearls": pearls,
        "top_curve": top_curve,
        "bot_curve": bot_curve,
        "bot_hi": bot_hi,
        "gems": gems,
    }


def export_brasao_svg(scene: dict, out_svg_path: str):
    """Exporta brasao_conde.svg vetorial puro (Cubic/Polyline + Gradientes)."""
    vp = scene["vp"]
    cx = scene["cx"]
    x_min = cx - scene["lw_half"]
    x_max = cx + scene["lw_half"]

    defs = [
        '<linearGradient id="goldRim" gradientUnits="userSpaceOnUse" x1="82" y1="140" x2="430" y2="480">',
        '  <stop offset="0%" stop-color="#FFF4B8"/>',
        '  <stop offset="28%" stop-color="#F6CE5E"/>',
        '  <stop offset="56%" stop-color="#D4AF37"/>',
        '  <stop offset="82%" stop-color="#9A6F1C"/>',
        '  <stop offset="100%" stop-color="#6E4B10"/>',
        '</linearGradient>',
        '<radialGradient id="sableField" gradientUnits="userSpaceOnUse" cx="220" cy="240" r="245">',
        '  <stop offset="0%" stop-color="#272D3D"/>',
        '  <stop offset="52%" stop-color="#141822"/>',
        '  <stop offset="100%" stop-color="#09090D"/>',
        '</radialGradient>',
        f'<linearGradient id="hoopGold" gradientUnits="userSpaceOnUse" x1="{x_min:.2f}" y1="{scene["c_base_y"] - scene["hoop_h"]:.2f}" x2="{x_max:.2f}" y2="{scene["c_base_y"]:.2f}">',
        '  <stop offset="0%" stop-color="#6E4C12"/>',
        '  <stop offset="18%" stop-color="#C8982E"/>',
        '  <stop offset="36%" stop-color="#FFF2B4"/>',
        '  <stop offset="58%" stop-color="#E4B844"/>',
        '  <stop offset="82%" stop-color="#A6781E"/>',
        '  <stop offset="100%" stop-color="#6E4C12"/>',
        '</linearGradient>',
        '<linearGradient id="rubyGem" gradientUnits="objectBoundingBox" x1="0" y1="0" x2="1" y2="1">',
        '  <stop offset="0%" stop-color="#FF4769"/>',
        '  <stop offset="55%" stop-color="#D41C3E"/>',
        '  <stop offset="100%" stop-color="#780C1F"/>',
        '</linearGradient>',
        '<linearGradient id="emeraldGem" gradientUnits="objectBoundingBox" x1="0" y1="0" x2="1" y2="1">',
        '  <stop offset="0%" stop-color="#34D38B"/>',
        '  <stop offset="55%" stop-color="#109056"/>',
        '  <stop offset="100%" stop-color="#084E2D"/>',
        '</linearGradient>',
    ]
    for i, p in enumerate(scene["pearls"]):
        pr = p["pr"]
        fx = p["px"] - pr * 0.34
        fy = p["py_top"] - pr * 0.36
        defs.append(
            f'<radialGradient id="pearl_{i}" gradientUnits="userSpaceOnUse" cx="{fx:.2f}" cy="{fy:.2f}" r="{pr * 1.42:.2f}">'
            '<stop offset="0%" stop-color="#FFFFFF"/>'
            '<stop offset="32%" stop-color="#F2F4FA"/>'
            '<stop offset="72%" stop-color="#AAB3C6"/>'
            '<stop offset="100%" stop-color="#7D7668"/>'
            '</radialGradient>'
        )

    outer_d = poly_svg_path(scene["pts_outer"])
    inner_d = poly_svg_path(scene["pts_inner"])
    hoop_d = curve_band_svg_path(scene["top_curve"], scene["bot_curve"])
    star_shadow_dx = vp * 0.010
    star_shadow_dy = vp * 0.012

    elems = [
        f'  <path d="{outer_d}" fill="url(#goldRim)" stroke="#8E6618" stroke-width="2.4" stroke-linejoin="round"/>',
        f'  <path d="{inner_d}" fill="url(#sableField)" stroke="#050508" stroke-opacity="0.72" stroke-width="3.6" stroke-linejoin="round"/>',
        f'  <ellipse cx="{cx:.2f}" cy="{scene["c_base_y"] + 6:.2f}" rx="{scene["lw_half"] * 0.96:.2f}" ry="9" fill="#000000" fill-opacity="0.48"/>',
        f'  <g transform="translate({star_shadow_dx:.2f},{star_shadow_dy:.2f})" opacity="0.46">',
    ]
    for pts, _ in scene["star_facets"]:
        elems.append(f'    <path d="{poly_svg_path(pts)}" fill="#000000"/>')
    elems.append('  </g>')

    for pts, col in scene["star_facets"]:
        elems.append(f'  <path d="{poly_svg_path(pts)}" fill="{col}"/>')
    for p0, p1 in scene["star_ribs"]:
        elems.append(f'  <path d="M {_fmt_pt(*p0)} L {_fmt_pt(*p1)}" stroke="#FFF6C6" stroke-opacity="0.88" stroke-width="1.8" stroke-linecap="round"/>')

    elems.append(f'  <path d="{circle_svg_path(cx, scene["star_cy"], scene["ring_r"])}" fill="#785416" stroke="#FFF4C2" stroke-opacity="0.55" stroke-width="1.4"/>')
    elems.append(f'  <path d="{circle_svg_path(cx, scene["star_cy"], scene["inner_disc"])}" fill="#181412"/>')
    elems.append(f'  <path d="{poly_svg_path(scene["flame_l"])}" fill="#FFF0A5"/>')
    elems.append(f'  <path d="{poly_svg_path(scene["flame_r"])}" fill="#D6A02C"/>')

    # Hastes do coronel
    for p in scene["pearls"]:
        elems.append(f'  <path d="{poly_svg_path(p["stem_l"])}" fill="#F8DA78"/>')
        elems.append(f'  <path d="{poly_svg_path(p["stem_r"])}" fill="#9E721C"/>')

    # Aro + molduras
    elems.append(f'  <path d="{hoop_d}" fill="url(#hoopGold)"/>')
    elems.append(f'  <path d="{open_line_svg_path(scene["top_curve"])}" fill="none" stroke="#FFF4C4" stroke-width="6.2" stroke-linecap="round"/>')
    elems.append(f'  <path d="{open_line_svg_path(scene["bot_hi"])}" fill="none" stroke="#FCE492" stroke-opacity="0.82" stroke-width="3.0" stroke-linecap="round"/>')
    elems.append(f'  <path d="{open_line_svg_path(scene["bot_curve"])}" fill="none" stroke="#8A5E14" stroke-width="6.8" stroke-linecap="round"/>')

    # Gemas
    for g in scene["gems"]:
        gx, gy, rx, ry = g["gx"], g["gy"], g["rx"], g["ry"]
        grad_id = "rubyGem" if g["is_ruby"] else "emeraldGem"
        elems.append(f'  <path d="{ellipse_svg_path(gx, gy, rx * 1.25, ry * 1.25)}" fill="#7A5614"/>')
        elems.append(f'  <path d="{ellipse_svg_path(gx, gy, rx, ry)}" fill="url(#{grad_id})"/>')
        sr = max(1.8, rx * 0.25)
        elems.append(f'  <path d="{circle_svg_path(gx - rx * 0.42, gy - ry * 0.42, sr)}" fill="#FFF5F5" fill-opacity="0.92"/>')

    # Colarinhos e 9 perolas
    for i, p in enumerate(scene["pearls"]):
        px, py_top, pr = p["px"], p["py_top"], p["pr"]
        elems.append(f'  <path d="{ellipse_svg_path(px, py_top + pr * 0.92, pr * 0.52, pr * 0.20)}" fill="#D6A838"/>')
        elems.append(f'  <path d="{circle_svg_path(px, py_top, pr)}" fill="url(#pearl_{i})"/>')

    svg_text = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {int(vp)} {int(vp)}" width="{int(vp)}" height="{int(vp)}" role="img" aria-label="Brasão do Conde de Treppênia">\n'
        '  <defs>\n    ' + '\n    '.join(defs) + '\n  </defs>\n'
        + '\n'.join(elems) + '\n'
        '</svg>\n'
    )
    with open(out_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_text)


def _vd_linear_grad(path_d: str, x0: float, y0: float, x1: float, y1: float, stops, stroke_color=None, stroke_w: float = 0.0, fill_alpha: float = 1.0) -> str:
    extra_stroke = ""
    if stroke_color and stroke_w > 0:
        extra_stroke = f' android:strokeColor="{stroke_color}" android:strokeWidth="{stroke_w:.2f}" android:strokeLineJoin="round"'
    alpha_attr = f' android:fillAlpha="{fill_alpha:.2f}"' if fill_alpha < 0.999 else ""
    items = "\n".join(f'          <item android:offset="{off}" android:color="{col}"/>' for off, col in stops)
    return (
        f'    <path android:pathData="{path_d}"{extra_stroke}{alpha_attr}>\n'
        '      <aapt:attr name="android:fillColor">\n'
        f'        <gradient android:type="linear" android:startX="{x0:.2f}" android:startY="{y0:.2f}" android:endX="{x1:.2f}" android:endY="{y1:.2f}">\n'
        f'{items}\n'
        '        </gradient>\n'
        '      </aapt:attr>\n'
        '    </path>'
    )


def _vd_radial_grad(path_d: str, cx: float, cy: float, radius: float, stops, stroke_color=None, stroke_w: float = 0.0) -> str:
    extra_stroke = ""
    if stroke_color and stroke_w > 0:
        extra_stroke = f' android:strokeColor="{stroke_color}" android:strokeWidth="{stroke_w:.2f}" android:strokeLineJoin="round"'
    items = "\n".join(f'          <item android:offset="{off}" android:color="{col}"/>' for off, col in stops)
    return (
        f'    <path android:pathData="{path_d}"{extra_stroke}>\n'
        '      <aapt:attr name="android:fillColor">\n'
        f'        <gradient android:type="radial" android:centerX="{cx:.2f}" android:centerY="{cy:.2f}" android:gradientRadius="{radius:.2f}">\n'
        f'{items}\n'
        '        </gradient>\n'
        '      </aapt:attr>\n'
        '    </path>'
    )


def build_vector_drawable_body(scene: dict) -> list:
    vp = scene["vp"]
    cx = scene["cx"]
    x_min = cx - scene["lw_half"]
    x_max = cx + scene["lw_half"]

    outer_d = poly_svg_path(scene["pts_outer"])
    inner_d = poly_svg_path(scene["pts_inner"])
    hoop_d = curve_band_svg_path(scene["top_curve"], scene["bot_curve"])

    nodes = [
        _vd_linear_grad(
            outer_d, 82, 140, 430, 480,
            [("0.0", "#FFF4B8"), ("0.28", "#F6CE5E"), ("0.56", "#D4AF37"), ("0.82", "#9A6F1C"), ("1.0", "#6E4B10")],
            stroke_color="#8E6618", stroke_w=2.4,
        ),
        _vd_radial_grad(
            inner_d, 220, 240, 245,
            [("0.0", "#272D3D"), ("0.52", "#141822"), ("1.0", "#09090D")],
            stroke_color="#B8050508", stroke_w=3.6,
        ),
        f'    <path android:pathData="{ellipse_svg_path(cx, scene["c_base_y"] + 6, scene["lw_half"] * 0.96, 9.0)}" android:fillColor="#7A000000"/>',
    ]

    dx = vp * 0.010
    dy = vp * 0.012
    nodes.append(f'    <group android:translateX="{dx:.2f}" android:translateY="{dy:.2f}">')
    for pts, _ in scene["star_facets"]:
        nodes.append(f'      <path android:pathData="{poly_svg_path(pts)}" android:fillColor="#75000000"/>')
    nodes.append('    </group>')

    for pts, col in scene["star_facets"]:
        nodes.append(f'    <path android:pathData="{poly_svg_path(pts)}" android:fillColor="{col}"/>')
    for p0, p1 in scene["star_ribs"]:
        nodes.append(f'    <path android:pathData="M {_fmt_pt(*p0)} L {_fmt_pt(*p1)}" android:strokeColor="#E0FFF6C6" android:strokeWidth="1.8" android:strokeLineCap="round"/>')

    nodes.append(f'    <path android:pathData="{circle_svg_path(cx, scene["star_cy"], scene["ring_r"])}" android:fillColor="#785416" android:strokeColor="#8CFFF4C2" android:strokeWidth="1.4"/>')
    nodes.append(f'    <path android:pathData="{circle_svg_path(cx, scene["star_cy"], scene["inner_disc"])}" android:fillColor="#181412"/>')
    nodes.append(f'    <path android:pathData="{poly_svg_path(scene["flame_l"])}" android:fillColor="#FFF0A5"/>')
    nodes.append(f'    <path android:pathData="{poly_svg_path(scene["flame_r"])}" android:fillColor="#D6A02C"/>')

    for p in scene["pearls"]:
        nodes.append(f'    <path android:pathData="{poly_svg_path(p["stem_l"])}" android:fillColor="#F8DA78"/>')
        nodes.append(f'    <path android:pathData="{poly_svg_path(p["stem_r"])}" android:fillColor="#9E721C"/>')

    nodes.append(
        _vd_linear_grad(
            hoop_d, x_min, scene["c_base_y"] - scene["hoop_h"], x_max, scene["c_base_y"],
            [("0.0", "#6E4C12"), ("0.18", "#C8982E"), ("0.36", "#FFF2B4"), ("0.58", "#E4B844"), ("0.82", "#A6781E"), ("1.0", "#6E4C12")],
        )
    )
    nodes.append(f'    <path android:pathData="{open_line_svg_path(scene["top_curve"])}" android:strokeColor="#FFF4C4" android:strokeWidth="6.2" android:strokeLineCap="round"/>')
    nodes.append(f'    <path android:pathData="{open_line_svg_path(scene["bot_hi"])}" android:strokeColor="#D1FCE492" android:strokeWidth="3.0" android:strokeLineCap="round"/>')
    nodes.append(f'    <path android:pathData="{open_line_svg_path(scene["bot_curve"])}" android:strokeColor="#8A5E14" android:strokeWidth="6.8" android:strokeLineCap="round"/>')

    for g in scene["gems"]:
        gx, gy, rx, ry = g["gx"], g["gy"], g["rx"], g["ry"]
        nodes.append(f'    <path android:pathData="{ellipse_svg_path(gx, gy, rx * 1.25, ry * 1.25)}" android:fillColor="#7A5614"/>')
        if g["is_ruby"]:
            nodes.append(_vd_linear_grad(ellipse_svg_path(gx, gy, rx, ry), gx - rx, gy - ry, gx + rx, gy + ry, [("0.0", "#FF4769"), ("0.55", "#D41C3E"), ("1.0", "#780C1F")]))
        else:
            nodes.append(_vd_linear_grad(ellipse_svg_path(gx, gy, rx, ry), gx - rx, gy - ry, gx + rx, gy + ry, [("0.0", "#34D38B"), ("0.55", "#109056"), ("1.0", "#084E2D")]))
        sr = max(1.8, rx * 0.25)
        nodes.append(f'    <path android:pathData="{circle_svg_path(gx - rx * 0.42, gy - ry * 0.42, sr)}" android:fillColor="#EBFFF5F5"/>')

    for p in scene["pearls"]:
        px, py_top, pr = p["px"], p["py_top"], p["pr"]
        nodes.append(f'    <path android:pathData="{ellipse_svg_path(px, py_top + pr * 0.92, pr * 0.52, pr * 0.20)}" android:fillColor="#D6A838"/>')
        nodes.append(
            _vd_radial_grad(
                circle_svg_path(px, py_top, pr),
                px - pr * 0.34, py_top - pr * 0.36, pr * 1.42,
                [("0.0", "#FFFFFF"), ("0.32", "#F2F4FA"), ("0.72", "#AAB3C6"), ("1.0", "#7D7668")],
            )
        )
    return nodes


def export_android_vector_drawable(scene: dict, out_xml_path: str, adaptive_safe_scale: float = 1.0):
    """Exporta VectorDrawable XML nativo Android minSdk 24+ com aapt:attr gradients."""
    vp = scene["vp"]
    body = build_vector_drawable_body(scene)
    if adaptive_safe_scale < 0.999:
        tx = vp * (1.0 - adaptive_safe_scale) * 0.5
        wrapped = [f'  <group android:translateX="{tx:.2f}" android:translateY="{tx:.2f}" android:scaleX="{adaptive_safe_scale:.4f}" android:scaleY="{adaptive_safe_scale:.4f}">']
        for line in body:
            wrapped.append("  " + line)
        wrapped.append("  </group>")
        body_text = "\n".join(wrapped)
    else:
        body_text = "\n".join(body)

    xml_text = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    xmlns:aapt="http://schemas.android.com/aapt"\n'
        f'    android:width="108dp"\n'
        f'    android:height="108dp"\n'
        f'    android:viewportWidth="{int(vp)}"\n'
        f'    android:viewportHeight="{int(vp)}">\n'
        f'{body_text}\n'
        '</vector>\n'
    )
    ET.fromstring(xml_text.encode("utf-8"))  # Valida XML estrito antes de gravar
    os.makedirs(os.path.dirname(out_xml_path), exist_ok=True)
    with open(out_xml_path, "w", encoding="utf-8") as f:
        f.write(xml_text)


def save_quantized_png(img: Image.Image, out_path: str, colors: int = 128):
    """Quantiza RGBA para paleta 8-bit com alfa preservado via FASTOCTREE para minSdk 24-25 enxuto."""
    q = img.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(out_path, "PNG", optimize=True)


def shield_half_width(yn: float) -> float:
    """Largura normalizada [0..1] do escudo classico luso-italiano para y normalizado [-0.22..1.0]."""
    if yn < 0.0:
        return 0.0
    if yn <= 0.42:
        # Lateral levemente afilada com leve elegancia no terco superior
        return 1.0 - 0.04 * (yn / 0.42) ** 1.3
    t = min(1.0, (yn - 0.42) / 0.58)
    # Curva ogival suave culminando na ponta do escudo em yn = 1.0
    return 0.96 * max(0.0, 1.0 - t ** 1.85) ** 0.58


def build_shield_polygon(cx: float, top_y: float, height: float, half_w: float, steps: int = 120):
    right_pts = []
    # Pequena ponta elegante nos cantos superiores
    right_pts.append((cx + half_w * 1.01, top_y - height * 0.015))
    for i in range(1, steps + 1):
        yn = i / float(steps)
        w = half_w * shield_half_width(yn)
        right_pts.append((cx + w, top_y + yn * height))
    left_pts = [(2 * cx - x, y) for (x, y) in reversed(right_pts[:-1])]
    # Topo levemente arqueado no centro (estilo clássico nobre)
    arch_pts = []
    for k in range(1, 16):
        u = -1.0 + 2.0 * (k / 16.0)
        x = cx + u * half_w * 0.98
        y = top_y - height * 0.022 * (1.0 - u * u) - height * 0.015 * (u * u)
        arch_pts.append((x, y))
    return arch_pts[:8] + right_pts + left_pts + arch_pts[8:]


def render_gold_gradient(light_map: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mapeia intensidade escalar [-1..1] em ouro 24k realista com specular metalico."""
    # Curva metalica não linear de ouro polido e escovado
    t = np.clip(0.50 + 0.50 * light_map, 0.0, 1.0)
    spec = np.power(np.clip((t - 0.72) / 0.28, 0.0, 1.0), 1.7)

    # Paleta ouro realista: sombra bronze escuro -> ouro medio -> ouro claro -> brilho champanhe
    r = np.interp(t, [0.0, 0.28, 0.55, 0.80, 1.0], [92, 168, 224, 248, 255])
    g = np.interp(t, [0.0, 0.28, 0.55, 0.80, 1.0], [64, 126, 180, 218, 246])
    b = np.interp(t, [0.0, 0.28, 0.55, 0.80, 1.0], [16, 36, 62, 114, 198])

    r = np.clip(r + spec * 24.0, 0, 255)
    g = np.clip(g + spec * 24.0, 0, 255)
    b = np.clip(b + spec * 42.0, 0, 255)

    out = np.zeros((light_map.shape[0], light_map.shape[1], 4), dtype=np.uint8)
    out[..., 0] = r.astype(np.uint8)
    out[..., 1] = g.astype(np.uint8)
    out[..., 2] = b.astype(np.uint8)
    out[..., 3] = np.clip(mask * 255.0, 0, 255).astype(np.uint8)
    return out


def composite_alpha(base_img: Image.Image, layer_arr: np.ndarray) -> Image.Image:
    layer = Image.fromarray(layer_arr, mode="RGBA")
    return Image.alpha_composite(base_img, layer)


def draw_bevel_poly(draw_mask, pts):
    draw_mask.polygon(pts, fill=255)


def faceted_star_flame_layer(size: int, cx: float, cy: float, radius: float) -> Image.Image:
    """Renderiza a Chama-Estrela central (Halvur/bellexe) em relevo facetado 3D realista."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    lx, ly = -0.64, -0.76  # Luz diagonal heraldica do cantao destro superior

    # 8 raios divididos em duas faces (facetas) por raio: cada face reflete a luz conforme sua normal!
    num_rays = 8
    inner_r = radius * 0.28
    # Raios cardinais mais longos (N/S/L/O) e diagonais medios para silhueta nobre limpa
    for i in range(num_rays):
        angle_deg = -90.0 + i * 45.0
        rad = math.radians(angle_deg)
        is_cardinal = (i % 2 == 0)
        tip_r = radius * (1.0 if is_cardinal else 0.72)
        side_half_deg = 16.5 if is_cardinal else 13.0

        p_center = (cx, cy)
        p_tip = (cx + math.cos(rad) * tip_r, cy + math.sin(rad) * tip_r)
        p_left = (
            cx + math.cos(math.radians(angle_deg - side_half_deg)) * inner_r * 1.15,
            cy + math.sin(math.radians(angle_deg - side_half_deg)) * inner_r * 1.15,
        )
        p_right = (
            cx + math.cos(math.radians(angle_deg + side_half_deg)) * inner_r * 1.15,
            cy + math.sin(math.radians(angle_deg + side_half_deg)) * inner_r * 1.15,
        )

        # Normais das duas facetas laterais da crista
        nx1, ny1 = math.cos(rad - 1.15), math.sin(rad - 1.15)
        nx2, ny2 = math.cos(rad + 1.15), math.sin(rad + 1.15)
        shade1 = nx1 * lx + ny1 * ly
        shade2 = nx2 * lx + ny2 * ly

        def facet_color(s: float):
            t = max(0.0, min(1.0, 0.54 + 0.44 * s))
            r = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [116, 198, 240, 255])))
            g = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [80, 150, 200, 242])))
            b = int(round(np.interp(t, [0.0, 0.35, 0.65, 1.0], [18, 42, 78, 178])))
            return (r, g, b, 255)

        d = ImageDraw.Draw(canvas)
        d.polygon([p_center, p_left, p_tip], fill=facet_color(shade1))
        d.polygon([p_center, p_tip, p_right], fill=facet_color(shade2))

    # Anel central lavrado ligando os raios
    d = ImageDraw.Draw(canvas)
    ring_r = radius * 0.255
    d.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], fill=(120, 84, 22, 255))
    inner_disc = radius * 0.205
    d.ellipse([cx - inner_disc, cy - inner_disc, cx + inner_disc, cy + inner_disc], fill=(24, 20, 18, 255))

    # Gota/Chama sagrada central (Halvur) em ouro claro e núcleo brilhante
    flame_h = radius * 0.35
    flame_w = radius * 0.145
    flame_top = (cx, cy - flame_h * 0.62)
    flame_bot = (cx, cy + flame_h * 0.44)
    flame_l = [
        flame_top,
        (cx - flame_w * 0.65, cy - flame_h * 0.12),
        (cx - flame_w * 0.92, cy + flame_h * 0.14),
        (cx - flame_w * 0.42, cy + flame_h * 0.38),
        flame_bot,
    ]
    flame_r = [
        flame_top,
        flame_bot,
        (cx + flame_w * 0.42, cy + flame_h * 0.38),
        (cx + flame_w * 0.92, cy + flame_h * 0.14),
        (cx + flame_w * 0.65, cy - flame_h * 0.12),
    ]
    d.polygon(flame_l, fill=(255, 240, 165, 255))
    d.polygon(flame_r, fill=(214, 160, 44, 255))

    # Chanfro interno luminoso em torno do anel
    d.arc([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 135, 315, fill=(255, 244, 194, 255), width=max(2, int(size * 0.004)))
    d.arc([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 315, 135, fill=(140, 96, 20, 255), width=max(2, int(size * 0.004)))

    # Realce da crista dos 4 raios principais
    for i in range(0, 8, 2):
        rad = math.radians(-90.0 + i * 45.0)
        p0 = (cx + math.cos(rad) * (ring_r * 1.02), cy + math.sin(rad) * (ring_r * 1.02))
        p1 = (cx + math.cos(rad) * (radius * 0.98), cy + math.sin(rad) * (radius * 0.98))
        d.line([p0, p1], fill=(255, 246, 198, 230), width=max(2, int(size * 0.003)))

    return canvas


def draw_count_coronet(size: int, cx: float, base_y: float, span_w: float) -> Image.Image:
    """Desenha o Coronel de Conde Luso-Italiano autentico: aro cravejado + 9 perolas visiveis."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    hoop_h = span_w * 0.175
    arch_lift = span_w * 0.048
    lw_half = span_w * 0.50

    # 1. 9 pontas/hastes (tradição portuguesa e italiana: 9 perolas visiveis no Coronel de Conde)
    # Distribuicao em arco perspectivo (-1.0 .. +1.0)
    num_pearls = 9
    pearl_positions = []
    for k in range(num_pearls):
        u = -1.0 + 2.0 * (k / float(num_pearls - 1))
        # Perspectiva cilindrica leve no posicionamento horizontal
        px = cx + math.sin(u * 1.18) / math.sin(1.18) * (lw_half * 0.94)
        rim_y = base_y - hoop_h * 0.96 - arch_lift * (1.0 - u * u)
        stem_h = hoop_h * (0.98 - 0.22 * (u * u))
        pearl_r = hoop_h * (0.37 - 0.05 * (u * u))
        py_top = rim_y - stem_h
        pearl_positions.append((u, px, rim_y, py_top, pearl_r))

    # Hastes metalicas atras das perolas
    for u, px, rim_y, py_top, pearl_r in pearl_positions:
        stem_w_bot = pearl_r * 0.85
        stem_w_top = pearl_r * 0.48
        # Lado esquerdo iluminado, lado direito sombreado
        d.polygon(
            [(px - stem_w_bot, rim_y + hoop_h * 0.12), (px, rim_y + hoop_h * 0.12), (px, py_top), (px - stem_w_top, py_top)],
            fill=(248, 218, 120, 255),
        )
        d.polygon(
            [(px, rim_y + hoop_h * 0.12), (px + stem_w_bot, rim_y + hoop_h * 0.12), (px + stem_w_top, py_top), (px, py_top)],
            fill=(158, 114, 28, 255),
        )

    # 2. Aro principal do Coronel de Conde com iluminacao cilindrica horizontal
    band_steps = 90
    top_curve = []
    bot_curve = []
    for i in range(band_steps + 1):
        u = -1.0 + 2.0 * (i / float(band_steps))
        x = cx + u * lw_half
        yt = base_y - hoop_h - arch_lift * (1.0 - u * u) + hoop_h * 0.14 * (u * u)
        yb = base_y + arch_lift * 0.55 * (1.0 - u * u) - hoop_h * 0.08 * (u * u)
        top_curve.append((x, yt))
        bot_curve.append((x, yb))

    # Preencher fatias verticais para brilho cilindrico realista no aro dourado
    for i in range(band_steps):
        u = -1.0 + 2.0 * ((i + 0.5) / float(band_steps))
        cyl = math.cos((u + 0.30) * 1.15)  # brilho deslocado p/ esquerda (luz 45°)
        t = max(0.0, min(1.0, 0.35 + 0.62 * cyl))
        r = int(round(np.interp(t, [0.0, 0.4, 0.75, 1.0], [110, 190, 240, 255])))
        g = int(round(np.interp(t, [0.0, 0.4, 0.75, 1.0], [76, 142, 198, 242])))
        b = int(round(np.interp(t, [0.0, 0.4, 0.75, 1.0], [18, 38, 76, 180])))
        quad = [top_curve[i], top_curve[i + 1], bot_curve[i + 1], bot_curve[i]]
        d.polygon(quad, fill=(r, g, b, 255))

    # Molduras superior e inferior em relevo no aro
    d.line(top_curve, fill=(255, 244, 196, 255), width=max(2, int(hoop_h * 0.14)))
    d.line(bot_curve, fill=(138, 94, 20, 255), width=max(2, int(hoop_h * 0.16)))
    bot_hi = [(x, y - hoop_h * 0.08) for (x, y) in bot_curve]
    d.line(bot_hi, fill=(252, 228, 146, 220), width=max(1, int(hoop_h * 0.07)))

    # 3. Gemas engastadas ao longo do aro (Rubi e Esmeralda alternados)
    gem_u = [-0.62, -0.31, 0.0, 0.31, 0.62]
    for idx_g, u in enumerate(gem_u):
        gx = cx + u * lw_half * 0.92
        gy_top = base_y - hoop_h - arch_lift * (1.0 - u * u) + hoop_h * 0.14 * (u * u)
        gy_bot = base_y + arch_lift * 0.55 * (1.0 - u * u) - hoop_h * 0.08 * (u * u)
        gy = 0.5 * (gy_top + gy_bot)
        rx = hoop_h * (0.28 if abs(u) < 0.1 else 0.22 - 0.04 * abs(u))
        ry = hoop_h * 0.23

        # Engaste em ouro escuro
        d.ellipse([gx - rx * 1.25, gy - ry * 1.25, gx + rx * 1.25, gy + ry * 1.25], fill=(122, 86, 20, 255))
        if idx_g % 2 == 0:
            # Rubi carmesim
            d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(150, 18, 38, 255))
            d.ellipse([gx - rx * 0.72, gy - ry * 0.72, gx + rx * 0.55, gy + ry * 0.55], fill=(224, 38, 72, 255))
        else:
            # Esmeralda imperial
            d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(14, 112, 68, 255))
            d.ellipse([gx - rx * 0.72, gy - ry * 0.72, gx + rx * 0.55, gy + ry * 0.55], fill=(32, 184, 116, 255))
        # Brilho especular da gema
        sr = max(2.0, rx * 0.26)
        d.ellipse([gx - rx * 0.45 - sr, gy - ry * 0.45 - sr, gx - rx * 0.45 + sr, gy - ry * 0.45 + sr], fill=(255, 245, 245, 240))

    # 4. 9 Perolas de Prata/Nacar com iluminacao esferica realista
    pearl_arr = np.zeros((size, size, 4), dtype=np.uint8)
    for u, px, _, py_top, pr in pearl_positions:
        x0 = max(0, int(math.floor(px - pr - 3)))
        x1 = min(size, int(math.ceil(px + pr + 3)))
        y0 = max(0, int(math.floor(py_top - pr - 3)))
        y1 = min(size, int(math.ceil(py_top + pr + 3)))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dx = (xx - px) / pr
        dy = (yy - py_top) / pr
        dist2 = dx * dx + dy * dy
        inside = dist2 <= 1.0
        nz = np.sqrt(np.clip(1.0 - dist2, 0.0, 1.0))

        # Luz ambiente nacarada + especular + reflexo quente de ouro por baixo
        ndotl = np.clip(dx * (-0.52) + dy * (-0.62) + nz * 0.59, 0.0, 1.0)
        hx, hy, hz = -0.34, -0.42, 0.84
        spec = np.power(np.clip(dx * hx + dy * hy + nz * hz, 0.0, 1.0), 16.0)
        gold_bounce = np.clip(dy * 0.65, 0.0, 1.0) * 0.22

        cr = np.clip(126 + 108 * ndotl + 115 * spec + 48 * gold_bounce, 0, 255)
        cg = np.clip(132 + 106 * ndotl + 112 * spec + 30 * gold_bounce, 0, 255)
        cb = np.clip(144 + 102 * ndotl + 106 * spec - 10 * gold_bounce, 0, 255)

        alpha = np.clip((1.0 - np.sqrt(dist2)) * pr * 1.35 + 0.5, 0.0, 1.0) * 255.0
        patch = pearl_arr[y0:y1, x0:x1]
        # Mescla simples considerando contorno
        m = alpha > 0
        patch[m, 0] = cr[m].astype(np.uint8)
        patch[m, 1] = cg[m].astype(np.uint8)
        patch[m, 2] = cb[m].astype(np.uint8)
        patch[m, 3] = np.maximum(patch[m, 3], alpha[m].astype(np.uint8))

        # Colarinho dourado minimo na base da perola
        d.ellipse([px - pr * 0.52, py_top + pr * 0.72, px + pr * 0.52, py_top + pr * 1.12], fill=(214, 168, 56, 255))

    return Image.alpha_composite(layer, Image.fromarray(pearl_arr, mode="RGBA"))


def generate_master_crest(size: int = 2048) -> Image.Image:
    """Gera o Brasao do Conde completo em altissima resolucao RGBA."""
    cx = size * 0.50
    shield_top = size * 0.295
    shield_h = size * 0.635
    shield_hw = size * 0.345

    # 1. Mascaras vetoriais anti-aliased do escudo (borda externa e campo interno Sable)
    pts_outer = build_shield_polygon(cx, shield_top, shield_h, shield_hw)
    rim_thickness = size * 0.025
    pts_inner = build_shield_polygon(
        cx,
        shield_top + rim_thickness * 0.95,
        shield_h - rim_thickness * 2.05,
        shield_hw - rim_thickness,
    )

    outer_mask_img = Image.new("L", (size, size), 0)
    ImageDraw.Draw(outer_mask_img).polygon(pts_outer, fill=255)
    outer_mask = np.asarray(outer_mask_img, dtype=np.float32) / 255.0

    inner_mask_img = Image.new("L", (size, size), 0)
    ImageDraw.Draw(inner_mask_img).polygon(pts_inner, fill=255)
    inner_mask = np.asarray(inner_mask_img, dtype=np.float32) / 255.0

    rim_mask = np.clip(outer_mask - inner_mask, 0.0, 1.0)

    # 2. Mapa de coordenadas normalizadas para relevo metalico PBR
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    nx_norm = (xx - cx) / max(1.0, shield_hw)
    ny_norm = (yy - (shield_top + shield_h * 0.38)) / max(1.0, shield_h * 0.55)

    # Curvatura convexa do escudo (altura esferica suave) + textura escovada sutil no Sable
    dome_l = np.clip(-0.55 * nx_norm - 0.58 * ny_norm + 0.42, -1.0, 1.0)
    rng = np.random.default_rng(42)
    grain = (rng.normal(0.0, 1.0, (size // 2, size // 2))).astype(np.float32)
    grain = np.repeat(np.repeat(grain, 2, axis=0), 2, axis=1)
    # Brushed steel effect along diagonal
    brushed = 0.6 * grain + 0.4 * np.roll(grain, 3, axis=1)

    # Campo Sable realista (obsidiana metalica escura com brilho controlado p/ contrastar em #09090b)
    sable_val = np.clip(16.0 + 18.0 * np.clip(dome_l + 0.3, 0.0, 1.0) + 2.2 * brushed, 8, 46)
    sable_arr = np.zeros((size, size, 4), dtype=np.uint8)
    sable_arr[..., 0] = np.clip(sable_val * 0.92, 0, 255).astype(np.uint8)
    sable_arr[..., 1] = np.clip(sable_val * 0.98, 0, 255).astype(np.uint8)
    sable_arr[..., 2] = np.clip(sable_val * 1.24 + 3.0, 0, 255).astype(np.uint8)
    sable_arr[..., 3] = (outer_mask * 255.0).astype(np.uint8)
    base_img = Image.fromarray(sable_arr, mode="RGBA")

    # Sombra interna sutil projetada pela moldura de ouro sobre o campo Sable
    rim_shadow_img = Image.fromarray((np.clip(1.0 - inner_mask, 0.0, 1.0) * 255.0).astype(np.uint8), mode="L")
    rim_shadow_blur = rim_shadow_img.filter(ImageFilter.GaussianBlur(radius=size * 0.012))
    rim_shadow_arr = np.asarray(rim_shadow_blur, dtype=np.float32) / 255.0
    dark_ring = np.zeros((size, size, 4), dtype=np.uint8)
    dark_ring[..., 3] = (np.clip(rim_shadow_arr * inner_mask * 0.85, 0.0, 1.0) * 210.0).astype(np.uint8)
    base_img = Image.alpha_composite(base_img, Image.fromarray(dark_ring, mode="RGBA"))

    # 3. Carga central (Chama-Estrela 8 raios Halvur/bellexe) com sombra de contato realista
    star_cy = shield_top + shield_h * 0.445
    star_rad = shield_hw * 0.69
    star_layer = faceted_star_flame_layer(size, cx, star_cy, star_rad)

    # Sombra projetada pelo ouro sobre o Sable (deslocada para baixo/direita)
    star_alpha = star_layer.split()[3]
    shadow_alpha = Image.new("L", (size, size), 0)
    shadow_alpha.paste(star_alpha, (int(size * 0.010), int(size * 0.012)))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(radius=size * 0.010))
    shadow_rgba = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_rgba.putalpha(Image.eval(shadow_alpha, lambda a: int(a * 0.65)))
    # Recortar sombra apenas para dentro do escudo
    s_arr = np.asarray(shadow_rgba, dtype=np.uint8).copy()
    s_arr[..., 3] = (s_arr[..., 3].astype(np.float32) * inner_mask).astype(np.uint8)
    base_img = Image.alpha_composite(base_img, Image.fromarray(s_arr, mode="RGBA"))
    base_img = Image.alpha_composite(base_img, star_layer)

    # 4. Borda / Orla em Ouro 24k brunido
    rim_light = np.clip(-0.68 * nx_norm - 0.65 * ny_norm + 0.14 + 0.06 * np.sin(nx_norm * 5.0), -1.0, 1.0)
    # Chanfro interno brilhante dentro da borda
    rim_inner_hi = Image.fromarray((outer_mask * 255.0).astype(np.uint8), mode="L").filter(ImageFilter.GaussianBlur(radius=size * 0.004))
    rim_hi_arr = np.asarray(rim_inner_hi, dtype=np.float32) / 255.0
    rim_light = np.clip(rim_light + (rim_hi_arr - inner_mask) * 0.35, -1.0, 1.0)
    rim_arr = render_gold_gradient(rim_light, rim_mask)
    base_img = composite_alpha(base_img, rim_arr)

    # Filete dourado externo em bronze/ouro antigo p/ contraste nitido ate no fundo branco
    d_outer = ImageDraw.Draw(base_img)
    d_outer.line(pts_outer + [pts_outer[0]], fill=(142, 102, 24, 245), width=max(3, int(size * 0.0045)))

    # 5. Coronel de Conde (9 perolas visiveis + aro cravejado) com sombra de contato no topo do escudo
    coronet = draw_count_coronet(size, cx, shield_top - size * 0.008, shield_hw * 1.48)
    c_alpha = coronet.split()[3]
    c_shadow = Image.new("L", (size, size), 0)
    c_shadow.paste(c_alpha, (int(size * 0.004), int(size * 0.015)))
    c_shadow = c_shadow.filter(ImageFilter.GaussianBlur(radius=size * 0.014))
    cs_rgba = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cs_rgba.putalpha(Image.eval(c_shadow, lambda a: int(a * 0.72)))
    base_img = Image.alpha_composite(base_img, cs_rgba)
    base_img = Image.alpha_composite(base_img, coronet)

    return base_img


def fit_square_with_padding(img: Image.Image, target_px: int, content_ratio: float, bg_rgba=(0, 0, 0, 0)) -> Image.Image:
    bbox = img.getbbox()
    cropped = img.crop(bbox) if bbox else img
    cw, ch = cropped.size
    max_side = max(cw, ch)
    scale = (target_px * content_ratio) / float(max_side)
    nw = max(1, int(round(cw * scale)))
    nh = max(1, int(round(ch * scale)))
    resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
    if target_px <= 64:
        # Nitidez sutil p/ micro-tamanhos (16px..48px)
        resized = resized.filter(ImageFilter.UnsharpMask(radius=0.8, percent=95, threshold=2))
    out = Image.new("RGBA", (target_px, target_px), bg_rgba)
    ox = (target_px - nw) // 2
    oy = (target_px - nh) // 2
    out.alpha_composite(resized, (ox, oy))
    return out


def save_win32_classic_ico(master: Image.Image, out_ico: str, include_256_png: bool = True):
    """Salva ICO multi-resolucao; inclui frames classic DIB sem compressao ate 128px e 256px opcional."""
    sizes = [16, 24, 32, 48, 64, 128] + ([256] if include_256_png else [])
    entries = []
    for sz in sizes:
        frame = fit_square_with_padding(master, sz, content_ratio=0.90)
        if sz == 256 and include_256_png:
            import io
            buf = io.BytesIO()
            frame.save(buf, format="PNG", optimize=True)
            data = buf.getvalue()
            w_b, h_b = 0, 0
        else:
            # Classic ICO BGRA bottom-up bitmap + 1bpp AND mask -> 100% compativel GDI+ .NET 4.x e Win32
            w_b, h_b = (sz if sz < 256 else 0), (sz if sz < 256 else 0)
            rgba = np.asarray(frame, dtype=np.uint8)
            # Inverter verticalmente (bottom-up DIB) e converter RGBA -> BGRA
            bgra = rgba[::-1, :, [2, 1, 0, 3]].copy()
            bmi = struct.pack("<IiiHHIIiiII", 40, sz, sz * 2, 1, 32, 0, bgra.nbytes, 0, 0, 0, 0)
            # AND mask 1bpp padded para multiplo de 4 bytes por linha
            row_bytes = ((sz + 31) // 32) * 4
            and_mask = b"\x00" * (row_bytes * sz)
            data = bmi + bgra.tobytes() + and_mask
        entries.append((w_b, h_b, sz, data))

    header = struct.pack("<HHH", 0, 1, len(entries))
    offset = 6 + 16 * len(entries)
    dirs = []
    blobs = []
    for w_b, h_b, sz, data in entries:
        dirs.append(struct.pack("<BBBBHHII", w_b, h_b, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
        blobs.append(data)

    with open(out_ico, "wb") as f:
        f.write(header)
        for d_rec in dirs:
            f.write(d_rec)
        for blob in blobs:
            f.write(blob)


def build_contact_sheet(master: Image.Image, out_path: str):
    sizes = [512, 192, 64, 48, 32, 24, 16]
    cols = len(sizes)
    w, h = 1120, 420
    sheet = Image.new("RGBA", (w, h), (18, 20, 26, 255))
    d = ImageDraw.Draw(sheet)
    # Metade superior escura (#09090b), metade inferior clara (#ffffff)
    d.rectangle([0, 0, w, h // 2], fill=(9, 9, 11, 255))
    d.rectangle([0, h // 2, w, h], fill=(255, 255, 255, 255))

    x_cursor = 24
    for sz in sizes:
        draw_sz = min(sz, 160)
        icon_real = fit_square_with_padding(master, sz, 0.90)
        disp = icon_real if sz <= 160 else icon_real.resize((160, 160), Image.Resampling.LANCZOS)
        sheet.alpha_composite(disp, (x_cursor, (h // 2 - disp.height) // 2))
        sheet.alpha_composite(disp, (x_cursor, h // 2 + (h // 2 - disp.height) // 2))
        d.text((x_cursor, 8), f"{sz}px", fill=(230, 200, 110, 255))
        x_cursor += max(draw_sz + 22, 68)
    sheet.save(out_path, "PNG")


def main():
    os.makedirs(UI_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(LAUNCHER_DIR, exist_ok=True)

    # 1. Vetor matematico unico (SVG para Web/PWA + VectorDrawable API 24+ para Android)
    scene = build_vector_scene(512.0)
    ui_svg = os.path.join(UI_DIR, "brasao_conde.svg")
    docs_svg = os.path.join(DOCS_DIR, "brasao_conde.svg")
    export_brasao_svg(scene, ui_svg)
    export_brasao_svg(scene, docs_svg)

    drawable_dir = os.path.join(ANDROID_RES, "drawable")
    os.makedirs(drawable_dir, exist_ok=True)
    export_android_vector_drawable(scene, os.path.join(drawable_dir, "brasao_conde_vector.xml"), adaptive_safe_scale=1.0)
    export_android_vector_drawable(scene, os.path.join(drawable_dir, "ic_launcher_foreground.xml"), adaptive_safe_scale=0.62)

    # 2. Renderizacao master 2048px para ICO/Header WinForms (Decisao A4) e fallbacks legados API 24-25
    master = generate_master_crest(2048)

    icon_512 = fit_square_with_padding(master, 512, 0.90)
    icon_192 = fit_square_with_padding(master, 192, 0.90)
    icon_maskable_512 = fit_square_with_padding(master, 512, 0.72, bg_rgba=(9, 9, 11, 255))

    for out_dir in (UI_DIR, DOCS_DIR):
        save_quantized_png(icon_512, os.path.join(out_dir, "icon-512.png"), colors=128)
        save_quantized_png(icon_192, os.path.join(out_dir, "icon-192.png"), colors=128)
        save_quantized_png(icon_maskable_512, os.path.join(out_dir, "icon-maskable-512.png"), colors=128)
        save_win32_classic_ico(master, os.path.join(out_dir, "favicon.ico"), include_256_png=False)

    # Windows Launcher (.ico Win32 + GDI + bitmap de alta resolucao p/ PictureBox)
    save_win32_classic_ico(master, os.path.join(LAUNCHER_DIR, "conde_brasao.ico"), include_256_png=True)
    save_win32_classic_ico(master, os.path.join(LAUNCHER_DIR, "conde_form_gdi.ico"), include_256_png=False)
    fit_square_with_padding(master, 256, 0.90).save(os.path.join(LAUNCHER_DIR, "conde_crest_header.png"), "PNG", optimize=True)

    # Remover splash raster antigo (168 KB) e foregrounds raster redundantes (141 KB)
    for obsolete in (
        os.path.join(ANDROID_RES, "drawable", "ic_launcher.xml"),
        os.path.join(ANDROID_RES, "drawable-nodpi", "brasao_conde_splash.png"),
    ):
        if os.path.exists(obsolete):
            os.remove(obsolete)
    nodpi_dir = os.path.join(ANDROID_RES, "drawable-nodpi")
    if os.path.isdir(nodpi_dir) and not os.listdir(nodpi_dir):
        try:
            os.rmdir(nodpi_dir)
        except OSError:
            pass

    densities = {
        "mdpi": 48,
        "hdpi": 72,
        "xhdpi": 96,
        "xxhdpi": 144,
        "xxxhdpi": 192,
    }
    for dpi, leg_px in densities.items():
        mdir = os.path.join(ANDROID_RES, f"mipmap-{dpi}")
        os.makedirs(mdir, exist_ok=True)
        # Remover raster foreground antigo substituido pelo VectorDrawable
        fg_old = os.path.join(mdir, "ic_launcher_foreground.png")
        if os.path.exists(fg_old):
            os.remove(fg_old)

        # Legacy launcher icon quantizado 8-bit (minSdk 24-25)
        legacy = fit_square_with_padding(master, leg_px, 0.78, bg_rgba=(9, 9, 11, 255))
        save_quantized_png(legacy, os.path.join(mdir, "ic_launcher.png"), colors=96)

        r_mask = Image.new("L", (leg_px, leg_px), 0)
        ImageDraw.Draw(r_mask).ellipse([1, 1, leg_px - 2, leg_px - 2], fill=255)
        round_icon = Image.new("RGBA", (leg_px, leg_px), (0, 0, 0, 0))
        round_icon.paste(legacy, (0, 0), r_mask)
        ImageDraw.Draw(round_icon).ellipse([1, 1, leg_px - 2, leg_px - 2], outline=(212, 175, 55, 180), width=max(1, leg_px // 48))
        save_quantized_png(round_icon, os.path.join(mdir, "ic_launcher_round.png"), colors=96)

    anydpi = os.path.join(ANDROID_RES, "mipmap-anydpi-v26")
    os.makedirs(anydpi, exist_ok=True)
    adaptive_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/obsidian" />\n'
        '    <foreground android:drawable="@drawable/ic_launcher_foreground" />\n'
        '</adaptive-icon>\n'
    )
    for fname in ("ic_launcher.xml", "ic_launcher_round.xml"):
        with open(os.path.join(anydpi, fname), "w", encoding="utf-8") as f:
            f.write(adaptive_xml)

    build_contact_sheet(master, SCRATCH_PREVIEW)
    res_total = sum(
        os.path.getsize(os.path.join(dp, fn))
        for dp, _, fns in os.walk(ANDROID_RES)
        for fn in fns
    )
    print(f"Brasao vetorizado gerado! SVG={os.path.getsize(ui_svg)}B Android_res_total={res_total}B Contact={SCRATCH_PREVIEW}")


if __name__ == "__main__":
    main()
