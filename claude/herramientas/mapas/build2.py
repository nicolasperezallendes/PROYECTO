"""Láminas 90 x 60 cm a 200 ppp: (1) SLEP Puerto Cordillera y (2) comuna completa."""
import os, sys
import build as B
from data2 import registros, numerar, SECTORES, DEP_COLOR, DEP_CORTA

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W, H = B.W, B.H
T, halo, wrap, esc = B.T, B.halo, B.wrap, B.esc
NAVY, TEAL, GREY, LGREY, LINE, BG = B.NAVY, B.TEAL, B.GREY, B.LGREY, B.LINE, B.BG

FUENTE = ('Fuente: base de establecimientos con enseñanza media de Coquimbo (corte 23.10.2026), sobre Directorio Oficial MINEDUC 2025, '
          'SLEP Puerto Cordillera (act. 07.05.2026) y Ficha MINEDUC. Sectores según PLADECO 2024-2028.')
FUENTE2 = 'Ubicación según coordenadas MINEDUC. Mapa base © colaboradores de OpenStreetMap. Matrícula 2025: total del establecimiento, todos los niveles.'

def doc(body, title_svg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<g id="Fondo"><rect width="{W}" height="{H}" fill="{BG}"/></g>\n<g id="Titulo">{title_svg}</g>\n{body}\n'
            f'<g id="Fuente">{T(80, H - 64, FUENTE, 22, 500, LGREY)}{T(80, H - 32, FUENTE2, 22, 500, LGREY)}</g>\n</svg>')

def header(kicker, title, right):
    return (T(80, 104, kicker, 30, 700, TEAL, extra='letter-spacing="4"') + T(80, 186, title, 72, 800)
            + T(3760, 186, right, 32, 600, GREY, 'end'))

def miles(n): return f'{n:,}'.replace(',', '.')

# ---------- ficha (variante con color propio) ----------
def card(s, x, y, w, scale=1.0):
    f_name = int(34 * scale); f_meta = int(23 * scale); f_lab = int(22 * scale); f_val = int(27 * scale)
    pad = int(30 * scale); badge = int(30 * scale); color = s['color']
    out, cy = [], y + pad
    name_x = x + pad + badge * 2 + int(20 * scale)
    lines = wrap(s['nombre'], f_name, 700, x + w - pad - name_x)
    for i, ln in enumerate(lines):
        out.append(T(name_x, cy + f_name * 0.85 + i * f_name * 1.22, ln, f_name, 700))
    name_h = len(lines) * f_name * 1.22
    bc = cy + max(name_h, badge * 2) / 2
    out.append(f'<circle cx="{x + pad + badge}" cy="{bc:.1f}" r="{badge}" fill="{color}"/>')
    out.append(T(x + pad + badge, bc + badge * 0.36, s['id'], badge, 800, '#FFFFFF', 'middle'))
    cy += max(name_h, badge * 2) + int(10 * scale)
    meta = f"{s['sector']} · {s['niveles']} · Matrícula 2025: {miles(s['mat'])}"
    for ln in wrap(meta, f_meta, 500, x + w - pad - name_x):
        out.append(T(name_x, cy + f_meta * 0.8, ln, f_meta, 500, LGREY)); cy += f_meta * 1.3
    cy += f_meta * 0.35
    labw = int(170 * scale)
    for lab, val in (('Director/a', s['director']), ('Fono', s['fono']), ('E-mail', s['email']), ('Dirección', s['dir'])):
        vl = wrap(val, f_val, 500, x + w - pad - (name_x + labw))
        out.append(T(name_x, cy + f_val * 0.82, lab.upper(), f_lab, 700, color, extra='letter-spacing="1.5"'))
        for i, ln in enumerate(vl):
            out.append(T(name_x + labw, cy + f_val * 0.82 + i * f_val * 1.25, ln, f_val, 500, NAVY))
        cy += len(vl) * f_val * 1.25 + int(10 * scale)
    h = cy - y + pad - int(10 * scale)
    return (f'<g id="Ficha {s["id"]}"><rect x="{x}" y="{y}" width="{w}" height="{h:.1f}" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{x}" y="{y + 16}" width="8" height="{h - 32:.1f}" fill="{color}"/>' + '\n'.join(out) + '</g>'), h

def cards_two(items, x, y, w, maxh, gap=24, cgap=30):
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    cw = (w - cgap) / 2
    for sc in [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65]:
        if all(sum(card(s, 0, 0, cw, sc)[1] for s in col) + gap * (len(col) - 1) <= maxh for col in cols): break
    svg, yend = [], y
    for k, col in enumerate(cols):
        cy = y
        for s in col:
            c, h = card(s, x + k * (cw + cgap), cy, cw, sc); svg.append(c); cy += h + gap
        yend = max(yend, cy)
    return '\n'.join(svg), yend

# ---------- capas de mapa ----------
def draw_points(P, items, r, labels=None, lsize=30, gap=10):
    """Marcadores con separación automática y línea a la ubicación real."""
    out = []
    pos = B.repel({s['id']: list(P(s['lat'], s['lon'])) for s in items}, r + 5, gap)
    for s in items:
        tx, ty = P(s['lat'], s['lon']); out.append(B.leader(tx, ty, *pos[s['id']]))
    for s in items:
        x, y = pos[s['id']]
        if labels is not None:
            side, dy = labels.get(s['id'], ('right', 0))
            out.append(B.marker(x, y, s['id'], s['color'], r=r, label=s['short'], side=side, lsize=lsize, dy=dy))
        else:
            out.append(B.marker(x, y, s['id'], s['color'], r=r))
    return '\n'.join(out)

def box(P, pts, pad_lat, pad_lon, label, anchor='end', below=True, size=26):
    la = [p[0] for p in pts]; lo = [p[1] for p in pts]
    (x0, y0), (x1, y1) = P(max(la) + pad_lat, min(lo) - pad_lon), P(min(la) - pad_lat, max(lo) + pad_lon)
    s = (f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1-x0:.0f}" height="{y1-y0:.0f}" fill="{NAVY}" fill-opacity="0.05" '
         f'stroke="{NAVY}" stroke-width="3" stroke-dasharray="12 8"/>')
    tx = x1 if anchor == 'end' else x0
    ty = y1 + size + 10 if below else y0 - 14
    return s + halo(tx, ty, label, size, 700, NAVY, anchor)

def commune_inset(gid, x, y, w, h, items, urban_pts, title, show_labels=True, sides=None):
    allp = [(s['lat'], s['lon']) for s in items] + urban_pts + [(-30.1977, -71.4220)]
    z, a, o = B.fit_zoom(allp, w, h, pad=0.1, zmax=12)
    mp, P = B.map_block(gid, x, y, w, h, a, o, z, None)
    g = [mp]
    g.append(box(P, urban_pts, 0.012, 0.02, 'Área urbana', 'start', False, 24))
    for s in items:
        px, py = P(s['lat'], s['lon'])
        g.append(B.marker(px, py, s['id'], s['color'], r=24,
                          label=s['short'] if show_labels else None, side=(sides or {}).get(s['id'], 'right'), lsize=24))
    g.append(halo(x + 28, y + 52, title, 32, 800))
    return '\n'.join(g)

# ======================================================================
def lamina_slep(labels_det, labels_urb):
    rs = [r for r in registros() if r['dep'].startswith('Pública')]
    numerar(rs)
    pen = [r for r in rs if r['sector'] == 'Península']
    urb = [r for r in rs if r['sector'] not in ('Rural Cordillera', 'Tongoy')]
    rur = [r for r in rs if r['sector'] in ('Rural Cordillera', 'Tongoy')]
    body = []
    # A. Área urbana
    AX, AY, AW, AH = 80, 250, 1840, 860
    z, a, o = B.fit_zoom([(r['lat'], r['lon']) for r in urb], AW, AH, pad=0.1, zmax=15)
    mp, P = B.map_block('urbano', AX, AY, AW, AH, a, o, z, 'Área urbana')
    body += ['<g id="Mapa urbano">', mp,
             box(P, [(r['lat'], r['lon']) for r in pen], 0.0025, 0.003, 'Península: ver detalle', 'start', False),
             draw_points(P, [r for r in urb if r not in pen], 28, labels_urb, 28),
             draw_points(P, pen, 20), '</g>']
    # B. Detalle Península
    DX, DY, DW, DH = 80, 1140, 1220, 1290
    z2, a2, o2 = B.fit_zoom([(r['lat'], r['lon']) for r in pen], DW, DH, pad=0.16, zmax=17)
    mp2, P2 = B.map_block('peninsula', DX, DY, DW, DH, a2, o2, z2, 'Detalle Península')
    body += ['<g id="Mapa Peninsula">', mp2, draw_points(P2, pen, 30, labels_det, 28), '</g>']
    # C. Comuna
    body += ['<g id="Mapa comunal">', commune_inset('comuna', 1330, 1140, 590, 1290, rur,
             [(r['lat'], r['lon']) for r in urb], 'Comuna', sides={9: 'left', 10: 'right'}), '</g>']
    # Panel
    PX, PW = 1960, 1800
    tot = sum(r['mat'] for r in rs)
    panel = ['<g id="Panel">',
             T(PX, 290, 'SERVICIO LOCAL DE EDUCACIÓN PÚBLICA PUERTO CORDILLERA', 24, 700, TEAL, extra='letter-spacing="3"')]
    for i, ln in enumerate(wrap(f'{len(rs)} establecimientos públicos con enseñanza media en la comuna de Coquimbo, '
                                f'con {miles(tot)} estudiantes matriculados en 2025 (todos los niveles).', 30, 600, PW)):
        panel.append(T(PX, 334 + i * 40, ln, 30, 600, NAVY))
    c, _ = cards_two(rs, PX, 430, PW, H - 130 - 430)
    panel += [c, '</g>']
    return doc('\n'.join(body + panel),
               header('SLEP PUERTO CORDILLERA · ESTABLECIMIENTOS CON ENSEÑANZA MEDIA',
                      'Liceos públicos con enseñanza media en Coquimbo', f'{len(rs)} establecimientos')), rs

# ======================================================================
def tabla(rs, x, y, w, maxh):
    cols = [('N°', 64), ('Establecimiento', 640), ('Director/a', 470), ('Fono', 270), ('E-mail', 540), ('Dirección', 456)]
    assert sum(c[1] for c in cols) == w
    for fs in (21, 20, 19, 18, 17):
        lh = fs * 1.22
        hs = []
        for r in rs:
            vals = [r['nombre'], r['director'], r['fono'], r['email'], r['dir']]
            nl = max(len(wrap(v, fs, 700 if j == 0 else 500, cols[j + 1][1] - 20)) for j, v in enumerate(vals))
            hs.append(14 + nl * lh + 6)
        if sum(hs) + 52 <= maxh: break
    g = ['<g id="Tabla">']
    cx = x
    for name, cw in cols:
        g.append(T(cx + 10, y + 30, name.upper(), 21, 700, TEAL, extra='letter-spacing="2"')); cx += cw
    g.append(f'<line x1="{x}" y1="{y+46}" x2="{x+w}" y2="{y+46}" stroke="{NAVY}" stroke-width="2"/>')
    cy = y + 48
    prev = None
    for i, (r, rh) in enumerate(zip(rs, hs)):
        if i % 2 == 0:
            g.append(f'<rect x="{x}" y="{cy:.1f}" width="{w}" height="{rh:.1f}" fill="#FFFFFF"/>')
        if prev and r['sector'] != prev:
            g.append(f'<line x1="{x}" y1="{cy:.1f}" x2="{x+w}" y2="{cy:.1f}" stroke="{NAVY}" stroke-width="1.5" opacity="0.5"/>')
        prev = r['sector']
        g.append(f'<circle cx="{x+30}" cy="{cy + 8 + fs*0.6:.1f}" r="{fs*0.95:.1f}" fill="{r["color"]}"/>')
        g.append(T(x + 30, cy + 8 + fs * 0.6 + fs * 0.33, r['id'], int(fs * 0.9), 800, '#FFFFFF', 'middle'))
        cx = x + cols[0][1]
        for j, v in enumerate([r['nombre'], r['director'], r['fono'], r['email'], r['dir']]):
            for k, ln in enumerate(wrap(v, fs, 700 if j == 0 else 500, cols[j + 1][1] - 20)):
                g.append(T(cx + 10, cy + 10 + fs * 0.92 + k * fs * 1.22, ln, fs, 700 if j == 0 else 500, NAVY))
            cx += cols[j + 1][1]
        cy += rh
    g.append(f'<line x1="{x}" y1="{cy:.1f}" x2="{x+w}" y2="{cy:.1f}" stroke="{LINE}" stroke-width="2"/></g>')
    print('tabla: fuente', fs, 'termina en', round(cy))
    return '\n'.join(g)

def lamina_comuna():
    rs = numerar(registros())
    pen = [r for r in rs if r['sector'] == 'Península']
    urb = [r for r in rs if r['sector'] not in ('Rural Cordillera', 'Tongoy')]
    rur = [r for r in rs if r['sector'] in ('Rural Cordillera', 'Tongoy')]
    body = []
    AX, AY, AW, AH = 80, 250, 1200, 820
    z, a, o = B.fit_zoom([(r['lat'], r['lon']) for r in urb], AW, AH, pad=0.06, zmax=15)
    mp, P = B.map_block('urbano', AX, AY, AW, AH, a, o, z, None)
    body += ['<g id="Mapa urbano">', mp,
             box(P, [(r['lat'], r['lon']) for r in pen], 0.002, 0.0025, 'Península: ver detalle', 'start', False, 24),
             draw_points(P, [r for r in urb if r not in pen], 20, gap=6),
             halo(AX + 36, AY + 66, 'Área urbana', 40, 800, NAVY, 'start'), '</g>']
    # Recuadro comunal dentro del mapa urbano (sobre la bahía)
    body += ['<g id="Mapa comunal">', commune_inset('comuna', 900, 1100, 380, 1050, rur,
             [(r['lat'], r['lon']) for r in urb], 'Comuna', show_labels=False), '</g>']
    DX, DY, DW, DH = 80, 1100, 790, 1050
    z2, a2, o2 = B.fit_zoom([(r['lat'], r['lon']) for r in pen], DW, DH, pad=0.07, zmax=17)
    mp2, P2 = B.map_block('peninsula', DX, DY, DW, DH, a2, o2, z2, 'Detalle Península')
    body += ['<g id="Mapa Peninsula">', mp2, draw_points(P2, pen, 24, gap=6), '</g>']
    # Leyendas
    LY = 2190
    lg = ['<g id="Leyenda">', T(80, LY, 'DEPENDENCIA', 22, 700, TEAL, extra='letter-spacing="3"')]
    yy = LY + 44
    for dep, col in DEP_COLOR.items():
        n = sum(1 for r in rs if r['dep'] == dep)
        lg.append(f'<circle cx="{96}" cy="{yy-8}" r="14" fill="{col}"/>')
        lg.append(T(124, yy, f'{DEP_CORTA[dep]}: {n}', 22, 600, NAVY)); yy += 40
    lg.append(T(560, LY, 'NUMERACIÓN POR SECTOR (PLADECO)', 22, 700, TEAL, extra='letter-spacing="3"'))
    yy = LY + 44; xx = 560
    for i, sec in enumerate(SECTORES):
        ids = [r['id'] for r in rs if r['sector'] == sec]
        rng = f'{ids[0]}–{ids[-1]}' if len(ids) > 1 else f'{ids[0]}'
        lab = sec.replace('Tierras Blancas y Peñuelas Alto', 'Tierras Blancas y P. Alto')
        lg.append(T(xx, yy, f'{rng}  {lab}', 20, 500, NAVY))
        yy += 32
        if i == 3: xx, yy = 930, LY + 44
    lg.append('</g>')
    body += lg
    body.append(tabla(rs, 1320, 250, 2440, H - 130 - 250))
    nd = {d: sum(1 for r in rs if r['dep'] == d) for d in DEP_COLOR}
    return doc('\n'.join(body), header('MUNICIPALIDAD DE COQUIMBO · ESTABLECIMIENTOS CON ENSEÑANZA MEDIA',
                                       'Establecimientos con enseñanza media en la comuna de Coquimbo',
                                       f'{len(rs)} establecimientos')), rs

if __name__ == '__main__':
    import labels2 as L
    s1, r1 = lamina_slep(L.SLEP_DET, L.SLEP_URB)
    open(os.path.join(OUT, 'MAPA SLEP PUERTO CORDILLERA ENSEÑANZA MEDIA.svg'), 'w').write(s1)
    s2, r2 = lamina_comuna()
    open(os.path.join(OUT, 'MAPA COMUNAL ENSEÑANZA MEDIA.svg'), 'w').write(s2)
    for r in r1: print('SLEP', r['id'], r['nombre'], '|', r['sector'])
