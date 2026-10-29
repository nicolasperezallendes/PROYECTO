import base64, io, math, os, sys
from PIL import Image, ImageEnhance, ImageFont
from tiles import mosaic, ll2px
from data import SEL, DELEG, DCOLOR, DNAME, GUANAQUEROS, TONGOY

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)

W, H = 3840, 2560
K = 7087 / W   # px de salida por unidad (90 x 60 cm a 200 ppp)
BG = '#F6F4EF'; NAVY = '#0B2545'; TEAL = '#007C99'; GREY = '#4A5568'; LGREY = '#718096'; LINE = '#D5D0C4'
FF = 'Montserrat, Arial, sans-serif'
FONTS = {w: os.path.expanduser(f'~/.fonts/Montserrat-{w}.ttf') for w in (400, 500, 600, 700, 800)}
_fc = {}
def tw(text, size, weight=400):
    k = (size, weight)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONTS[weight], size)
    return _fc[k].getlength(text)

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def wrap(text, size, weight, maxw):
    words = []
    for w_ in str(text).split():
        # un correo sin espacios que no cabe se corta antes de la @
        if '@' in w_ and tw(w_, size, weight) > maxw:
            u, dom = w_.split('@', 1); words += [u, '@' + dom]
        else:
            words.append(w_)
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if tw(t, size, weight) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def T(x, y, s, size, weight=400, fill=NAVY, anchor='start', extra=''):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FF}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')

def halo(x, y, s, size, weight=700, fill=NAVY, anchor='start'):
    return T(x, y, s, size, weight, fill, anchor,
             'stroke="#FFFFFF" stroke-width="8" stroke-linejoin="round" paint-order="stroke"')

# ---------- mapa base ----------
SCALE = 1.5
def fit_zoom(pts, bw, bh, pad=0.22, zmax=17, min_span_km=1.2):
    lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
    clat = (max(lats) + min(lats)) / 2; clon = (max(lons) + min(lons)) / 2
    for z in range(zmax, 5, -1):
        xs, ys = zip(*[ll2px(a, b, z) for a, b in pts])
        sw = (max(xs) - min(xs)) * SCALE; sh = (max(ys) - min(ys)) * SCALE
        # extensión mínima en metros por píxel
        mpp = 156543.03 * math.cos(math.radians(clat)) / 2 ** z / SCALE
        if sw <= bw * (1 - 2 * pad) and sh <= bh * (1 - 2 * pad) and min(bw, bh) * mpp >= min_span_km * 1000:
            return z, clat, clon
    return 6, clat, clon

def basemap(clat, clon, z, bw, bh):
    # Teselas un nivel más cerca (z+1) para que el mapa base tenga 200 ppp reales en la lámina
    img, proj = mosaic(clat, clon, z + 1, bw / SCALE * 2 + 4, bh / SCALE * 2 + 4)
    img = img.resize((round(bw * K), round(bh * K)), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(0.30)
    img = Image.blend(img, Image.new('RGB', img.size, (246, 244, 239)), 0.28)
    buf = io.BytesIO(); img.save(buf, 'JPEG', quality=90, dpi=(200, 200))
    href = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    def P(lat, lon):
        x, y = proj(lat, lon); return x * SCALE / 2, y * SCALE / 2
    return href, P

def map_block(gid, x, y, bw, bh, clat, clon, z, title=None):
    href, P = basemap(clat, clon, z, bw, bh)
    cid = 'clip_' + gid.replace(' ', '_')
    s = [f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="18"/></clipPath></defs>',
         f'<g id="Mapa base {esc(gid)}" clip-path="url(#{cid})"><image x="{x}" y="{y}" width="{bw}" height="{bh}" '
         f'preserveAspectRatio="none" xlink:href="{href}"/></g>',
         f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="18" fill="none" stroke="{LINE}" stroke-width="2"/>']
    if title:
        s.append(halo(x + 36, y + 66, title, 40, 800))
    return '\n'.join(s), (lambda lat, lon: (x + P(lat, lon)[0], y + P(lat, lon)[1]))

def marker(px, py, num, color, r=30, label=None, side='right', lsize=30, dy=0):
    g = [f'<g id="Marcador {num}">',
         f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r+5}" fill="#FFFFFF" opacity="0.95"/>',
         f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{color}"/>',
         T(px, py + r * 0.36, num, int(r * 1.0), 800, '#FFFFFF', 'middle')]
    if label:
        if side == 'right': g.append(halo(px + r + 14, py + lsize * 0.36 + dy, label, lsize))
        elif side == 'left': g.append(halo(px - r - 14, py + lsize * 0.36 + dy, label, lsize, anchor='end'))
        elif side == 'top': g.append(halo(px, py - r - 16 + dy, label, lsize, anchor='middle'))
        else: g.append(halo(px, py + r + lsize + 8 + dy, label, lsize, anchor='middle'))
    g.append('</g>')
    return '\n'.join(g)

def repel(pos, R, gap=10):
    for _ in range(300):
        moved = False
        ks = list(pos)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, c = pos[ks[i]], pos[ks[j]]
                dx, dy_ = c[0] - a[0], c[1] - a[1]; dd = math.hypot(dx, dy_) or 0.01
                if dd < 2 * R + gap:
                    push = (2 * R + gap - dd) / 2 + 0.5
                    a[0] -= dx / dd * push; a[1] -= dy_ / dd * push; c[0] += dx / dd * push; c[1] += dy_ / dd * push
                    moved = True
        if not moved: break
    return pos

def leader(tx, ty, x, y):
    if math.hypot(x - tx, y - ty) <= 4: return ''
    return (f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{NAVY}" stroke-width="2.5"/>'
            f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="6" fill="{NAVY}"/>')

# ---------- fichas ----------
def card(s, x, y, w, scale=1.0, draw=True):
    """Devuelve (svg, alto). Ficha con nombre, dependencia y los cuatro datos pedidos."""
    f_name = int(34 * scale); f_meta = int(23 * scale); f_lab = int(22 * scale); f_val = int(27 * scale)
    pad = int(30 * scale); badge = int(30 * scale)
    color = DCOLOR[s['d']]
    out = []
    cy = y + pad
    name_x = x + pad + badge * 2 + int(20 * scale)
    lines = wrap(s['nombre'], f_name, 700, x + w - pad - name_x)
    for i, ln in enumerate(lines):
        out.append(T(name_x, cy + f_name * 0.85 + i * f_name * 1.22, ln, f_name, 700))
    name_h = len(lines) * f_name * 1.22
    out.append(f'<circle cx="{x + pad + badge}" cy="{cy + max(name_h, badge*2)/2:.1f}" r="{badge}" fill="{color}"/>')
    out.append(T(x + pad + badge, cy + max(name_h, badge*2)/2 + badge * 0.36, s['id'], badge, 800, '#FFFFFF', 'middle'))
    cy += max(name_h, badge * 2) + int(10 * scale)
    mat = f"{s['mat']:,}".replace(',', '.')
    meta = f"{s['dep']} · {s['niveles']} · Matrícula 2025: {mat}"
    for i, ln in enumerate(wrap(meta, f_meta, 500, x + w - pad - name_x)):
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
    bgr = f'<rect x="{x}" y="{y}" width="{w}" height="{h:.1f}" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>'
    bar = f'<rect x="{x}" y="{y + 16}" width="8" height="{h - 32:.1f}" fill="{color}"/>'
    return f'<g id="Ficha {s["id"]}">' + bgr + bar + '\n'.join(out) + '</g>', h

def cards_two(items, x, y, w, maxh, gap=24, cgap=30):
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    cw = (w - cgap) / 2
    for sc in [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65]:
        ok = all(sum(card(s, 0, 0, cw, sc)[1] for s in col) + gap * (len(col) - 1) <= maxh for col in cols)
        if ok: break
    svg, yend = [], y
    for k, col in enumerate(cols):
        cy = y
        for s in col:
            c, h = card(s, x + k * (cw + cgap), cy, cw, sc); svg.append(c); cy += h + gap
        yend = max(yend, cy)
    return '\n'.join(svg), yend

def cards_column(items, x, y, w, maxh, gap=24):
    for sc in [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7]:
        hs = [card(s, x, 0, w, sc)[1] for s in items]
        if sum(hs) + gap * (len(items) - 1) <= maxh: break
    svg, cy = [], y
    for s in items:
        c, h = card(s, x, cy, w, sc); svg.append(c); cy += h + gap
    return '\n'.join(svg), cy

# ---------- piezas ----------
KICKER = 'MUNICIPALIDAD DE COQUIMBO · ESTABLECIMIENTOS CON ENSEÑANZA MEDIA'
FUENTE = ('Fuente: base de establecimientos con enseñanza media de Coquimbo (corte 23.10.2026), sobre Directorio Oficial MINEDUC 2025, '
          'SLEP Puerto Cordillera (act. 07.05.2026) y Ficha MINEDUC. Delegaciones según subsectores del PLADECO 2024-2028.')
FUENTE2 = 'Ubicación según coordenadas MINEDUC. Mapa base © colaboradores de OpenStreetMap.'

def doc(body, title_svg):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<g id="Fondo"><rect width="{W}" height="{H}" fill="{BG}"/></g>\n'
            f'<g id="Titulo">{title_svg}</g>\n{body}\n'
            f'<g id="Fuente">{T(80, H - 64, FUENTE, 22, 500, LGREY)}{T(80, H - 32, FUENTE2, 22, 500, LGREY)}</g>\n</svg>')

def header(title, right=None):
    s = T(80, 104, KICKER, 30, 700, TEAL, extra='letter-spacing="4"') + T(80, 186, title, 72, 800)
    if right:
        s += T(3760, 186, right, 32, 600, GREY, 'end')
    return s

REFS = {
    'RU': [('El Peñón', -30.1369, -71.2186), ('Tambillos', -30.1973, -71.2240),
           ('Las Barrancas', -30.2060, -71.2569), ('Las Cardas', -30.2817, -71.2546)],
    'TO': [('El Tangue', -30.3034, -71.5551)],
}
NOTES = {
    'RU': ('CONTEXTO', 'Es el único establecimiento con enseñanza media del sector Rural Cordillera. Atiende desde parvularia hasta 4° medio, en las modalidades científico-humanista y técnico-profesional, y su origen se remonta a 1891. En El Peñón, Tambillos, Las Barrancas y Las Cardas la base no registra enseñanza media.'),
    'TO': ('CONTEXTO', 'Es el único liceo de la costa sur de la comuna. Imparte enseñanza media científico-humanista y técnico-profesional, y educación de adultos. También es la opción más cercana para los estudiantes de Guanaqueros, a unos 10 km.'),
    'PA': ('CRITERIO', 'El PLADECO separa Parte Alta de los subsectores El Llano, Centro y Guayacán. Por eso no se incluyen aquí el Liceo Industrial José Tomás de Urmeneta, el Instituto Superior de Comercio, el Liceo Diego Portales ni los colegios del entorno del estadio Sánchez Rumoroso. Si la delegación también atiende El Llano, esos establecimientos se pueden sumar.'),
}

# Desplazamientos de etiqueta por establecimiento (lado, dy) para evitar choques
LAB = {}

def deleg_piece(dk, labels):
    d = next(x for x in DELEG if x['key'] == dk)
    items = [s for s in SEL if s['d'] == dk]
    n = len(items)
    MX, MY, MW, MH = 80, 250, 2160, H - 380
    PX, PW = 2300, 1460
    if n > 6:
        MW, PX, PW = 1840, 1960, 1800
    if dk == 'GU':
        pts = [GUANAQUEROS, TONGOY]
        z, clat, clon = fit_zoom(pts + [(s['lat'], s['lon']) for s in SEL if s['d'] == 'TO'], MW, MH, pad=0.18)
    else:
        pts = [(s['lat'], s['lon']) for s in items] + [(a, b) for _, a, b in REFS.get(dk, [])]
        z, clat, clon = fit_zoom(pts, MW, MH, pad=0.14 if dk in REFS else 0.2, zmax=17 if n > 1 else 16,
                                 min_span_km=1.6 if n > 1 else 2.2)
    mp, P = map_block(d['nombre'], MX, MY, MW, MH, clat, clon, z)
    body = [f'<g id="Mapa">{mp}', '<g id="Marcadores">']
    if dk == 'GU':
        gx, gy = P(*GUANAQUEROS)
        body.append(f'<g id="Guanaqueros"><circle cx="{gx:.0f}" cy="{gy:.0f}" r="150" fill="{d["color"]}" opacity="0.12" stroke="{d["color"]}" stroke-width="4" stroke-dasharray="14 10"/>'
                    + halo(gx, gy - 170, 'Guanaqueros', 44, 800, d['color'], 'middle')
                    + halo(gx, gy - 124, 'sin establecimientos con enseñanza media', 28, 600, NAVY, 'middle') + '</g>')
        t = next(s for s in SEL if s['d'] == 'TO')
        tx, ty = P(t['lat'], t['lon'])
        body.append(f'<line x1="{gx:.0f}" y1="{gy:.0f}" x2="{tx:.0f}" y2="{ty:.0f}" stroke="{NAVY}" stroke-width="4" stroke-dasharray="4 12" stroke-linecap="round"/>')
        mx_, my_ = (gx + tx) / 2, (gy + ty) / 2
        body.append(halo(mx_ + 30, my_, '≈ 10 km en línea recta', 30, 700, NAVY))
        body.append(marker(tx, ty, t['id'], DCOLOR['TO'], label=t['short'] + ' (Tongoy)', side='bottom'))
    for nm, a, b in REFS.get(dk, []):
        rx, ry = P(a, b)
        body.append(f'<g id="Localidad {esc(nm)}"><circle cx="{rx:.0f}" cy="{ry:.0f}" r="11" fill="#FFFFFF" stroke="{LGREY}" stroke-width="5"/>'
                    + halo(rx + 22, ry + 10, nm, 30, 700, GREY) + '</g>')
    pos = repel({s['id']: list(P(s['lat'], s['lon'])) for s in items}, 35)
    for s in items:
        tx, ty = P(s['lat'], s['lon']); body.append(leader(tx, ty, *pos[s['id']]))
    for s in items:
        px, py = pos[s['id']]
        side, dy = labels.get(s['id'], ('right', 0))
        body.append(marker(px, py, s['id'], d['color'], label=s['short'], side=side, dy=dy))
    body.append('</g></g>')
    # panel derecho
    panel = ['<g id="Panel">']
    panel.append(T(PX, 290, 'SUBSECTORES PLADECO', 24, 700, d['color'], extra='letter-spacing="3"'))
    sl = wrap(d['sub'], 30, 600, PW)
    for i, ln in enumerate(sl): panel.append(T(PX, 334 + i * 40, ln, 30, 600, NAVY))
    ytop = 334 + len(sl) * 40 + 30
    if items:
        c, yend = (cards_two if n > 6 else cards_column)(items, PX, ytop, PW, H - 130 - ytop)
        panel.append(c)
        if dk in NOTES and yend < H - 560:
            panel.append(T(PX, yend + 46, NOTES[dk][0], 24, 700, LGREY, extra='letter-spacing="3"'))
            for i, ln in enumerate(wrap(NOTES[dk][1], 30, 500, PW)):
                panel.append(T(PX, yend + 96 + i * 44, ln, 30, 500, GREY))
    else:
        yend = ytop
        t = next(s for s in SEL if s['d'] == 'TO')
        note = ('La base no registra establecimientos con enseñanza media en Guanaqueros. '
                'Los estudiantes de la localidad tienen como opción más cercana el liceo de Tongoy, '
                'a unos 10 km en línea recta.')
        nl = wrap(note, 32, 500, PW - 60)
        hh = 60 + len(nl) * 46 + 20
        panel.append(f'<rect x="{PX}" y="{ytop}" width="{PW}" height="{hh}" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>')
        panel.append(f'<rect x="{PX}" y="{ytop+16}" width="8" height="{hh-32}" fill="{d["color"]}"/>')
        for i, ln in enumerate(nl): panel.append(T(PX + 40, ytop + 70 + i * 46, ln, 32, 500, NAVY))
        panel.append(T(PX, ytop + hh + 70, 'ESTABLECIMIENTO MÁS CERCANO (DELEGACIÓN TONGOY)', 24, 700, LGREY, extra='letter-spacing="3"'))
        c, yend = cards_column([t], PX, ytop + hh + 100, PW, H - 130 - (ytop + hh + 100))
        panel.append(c)
    panel.append('</g>')
    right = f'{n} establecimiento{"s" if n != 1 else ""}' if n else 'Sin establecimientos con enseñanza media'
    title = f'Delegación {d["nombre"]}'
    return doc('\n'.join(body + panel), header(title, right))

def general_piece(labels_urb):
    # Mapa comunal
    CX, CY, CW, CH = 80, 250, 1000, 1100
    allpts = [(s['lat'], s['lon']) for s in SEL] + [GUANAQUEROS]
    z, clat, clon = fit_zoom(allpts, CW, CH, pad=0.08, zmax=13)
    mp, P = map_block('comuna', CX, CY, CW, CH, clat, clon, z, 'Comuna de Coquimbo')
    body = [f'<g id="Mapa comunal">{mp}']
    # Recuadro urbano
    urb = [s for s in SEL if s['d'] in ('TB', 'PA')]
    la = [s['lat'] for s in urb]; lo = [s['lon'] for s in urb]
    U0, U1 = P(max(la) + 0.006, min(lo) - 0.01), P(min(la) - 0.006, max(lo) + 0.01)
    body.append(f'<rect id="Recuadro area urbana" x="{U0[0]:.0f}" y="{U0[1]:.0f}" width="{U1[0]-U0[0]:.0f}" height="{U1[1]-U0[1]:.0f}" fill="{NAVY}" fill-opacity="0.06" stroke="{NAVY}" stroke-width="3" stroke-dasharray="10 7"/>')
    body.append(halo(U1[0], U1[1] + 34, 'Área urbana (detalle al lado)', 24, 700, anchor='end'))
    # Etiquetas de delegación en el mapa comunal
    def dl(lat, lon, k, n, side='right', dy=0):
        x, y = P(lat, lon)
        c = DCOLOR[k]
        g = (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="{c}" stroke="#FFFFFF" stroke-width="5"/>'
             + T(x, y + 9, n, 24, 800, '#FFFFFF', 'middle'))
        lab = DNAME[k]
        if side == 'right':
            g += halo(x + 34, y + 2 + dy, lab, 30, 800, c) + halo(x + 34, y + 36 + dy, f'{n} establecimiento' + ('s' if n != 1 else ''), 24, 600)
        else:
            g += halo(x - 34, y + 2 + dy, lab, 30, 800, c, 'end') + halo(x - 34, y + 36 + dy, f'{n} establecimiento' + ('s' if n != 1 else ''), 24, 600, anchor='end')
        return g
    ru = next(s for s in SEL if s['d'] == 'RU'); to = next(s for s in SEL if s['d'] == 'TO')
    body.append('<g id="Delegaciones rurales y costeras">')
    body.append(dl(ru['lat'], ru['lon'], 'RU', 1))
    body.append(dl(to['lat'], to['lon'], 'TO', 1))
    gx, gy = P(*GUANAQUEROS)
    body.append(f'<circle cx="{gx:.0f}" cy="{gy:.0f}" r="22" fill="#FFFFFF" stroke="{DCOLOR["GU"]}" stroke-width="5"/>'
                + T(gx, gy + 9, '0', 24, 800, DCOLOR['GU'], 'middle')
                + halo(gx + 34, gy + 2, 'Guanaqueros', 30, 800, DCOLOR['GU']) + halo(gx + 34, gy + 36, 'sin enseñanza media', 24, 600))
    body.append('</g></g>')
    # Mapa urbano
    UX, UY, UW, UH = 1120, 250, 1600, 1100
    z2, c2a, c2o = fit_zoom([(s['lat'], s['lon']) for s in urb], UW, UH, pad=0.07, zmax=15)
    mp2, P2 = map_block('urbano', UX, UY, UW, UH, c2a, c2o, z2, 'Área urbana')
    body.append(f'<g id="Mapa urbano">{mp2}<g id="Marcadores urbanos">')
    pos = {s['id']: list(P2(s['lat'], s['lon'])) for s in urb}
    true = {k: tuple(v) for k, v in pos.items()}
    R = 26
    repel(pos, R)
    for _ in range(0):
        moved = False
        ks = list(pos)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, b = pos[ks[i]], pos[ks[j]]
                dx, dy_ = b[0] - a[0], b[1] - a[1]; dd = math.hypot(dx, dy_) or 0.01
                if dd < 2 * R + 10:
                    push = (2 * R + 10 - dd) / 2 + 0.5
                    a[0] -= dx / dd * push; a[1] -= dy_ / dd * push; b[0] += dx / dd * push; b[1] += dy_ / dd * push
                    moved = True
        if not moved: break
    for s in urb:
        tx, ty = true[s['id']]; x, y = pos[s['id']]
        if math.hypot(x - tx, y - ty) > 4:
            body.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{NAVY}" stroke-width="2.5"/>'
                        f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="6" fill="{NAVY}"/>')
    for s in urb:
        x, y = pos[s['id']]
        body.append(marker(x, y, s['id'], DCOLOR[s['d']], r=R))
    # rótulos de delegación en el urbano
    for k, (lat, lon) in (('TB', (max(s['lat'] for s in urb if s['d']=='TB') + 0.0085, sum(s['lon'] for s in urb if s['d']=='TB')/sum(1 for s in urb if s['d']=='TB'))),
                          ('PA', (max(s['lat'] for s in urb if s['d']=='PA') + 0.005, sum(s['lon'] for s in urb if s['d']=='PA')/sum(1 for s in urb if s['d']=='PA')))):
        x, y = P2(lat, lon)
        body.append(halo(x, y, 'Delegación ' + DNAME[k], 34, 800, DCOLOR[k], 'middle'))
    body.append('</g></g>')
    # Resumen
    RX = 2770
    rs = ['<g id="Resumen">', T(RX, 290, 'ESTABLECIMIENTOS POR DELEGACIÓN', 24, 700, TEAL, extra='letter-spacing="3"')]
    yy = 350
    for d in DELEG:
        n = sum(1 for s in SEL if s['d'] == d['key'])
        rs.append(f'<rect x="{RX}" y="{yy}" width="990" height="118" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>')
        rs.append(f'<rect x="{RX}" y="{yy+14}" width="8" height="90" fill="{d["color"]}"/>')
        rs.append(T(RX + 40, yy + 74, str(n), 62, 800, d['color']))
        rs.append(T(RX + 130, yy + 52, d['nombre'], 32, 800))
        sub = wrap(d['sub'], 20, 500, 830)[0]
        if len(wrap(d['sub'], 20, 500, 830)) > 1: sub = sub.rstrip(',') + '…'
        rs.append(T(RX + 130, yy + 88, sub, 20, 500, LGREY))
        yy += 136
    tot = len(SEL)
    rs.append(T(RX, yy + 40, f'{tot} de los 43 establecimientos con enseñanza media de la comuna', 26, 700, NAVY))
    rs.append(T(RX, yy + 76, 'están en estas cinco delegaciones.', 26, 500, GREY))
    rs.append('</g>')
    body += rs
    # Tabla
    TX, TY = 80, 1420
    cols = [('N°', 70), ('Delegación', 270), ('Establecimiento', 860), ('Director/a', 560), ('Fono', 400), ('E-mail', 740), ('Dirección', 780)]
    tb = ['<g id="Tabla">']
    x = TX
    for name, cw in cols:
        tb.append(T(x + 10, TY + 30, name.upper(), 23, 700, TEAL, extra='letter-spacing="2"')); x += cw
    tb.append(f'<line x1="{TX}" y1="{TY+48}" x2="{TX+3680}" y2="{TY+48}" stroke="{NAVY}" stroke-width="2"/>')
    y = TY + 48
    fs = 28
    for i, s in enumerate(SEL):
        vals = [str(s['id']), DNAME[s['d']], s['nombre'], s['director'], s['fono'], s['email'], s['dir']]
        wrapped = [wrap(v, fs, 700 if j == 2 else 500, cols[j][1] - 24) for j, v in enumerate(vals)]
        nl = max(len(w_) for w_ in wrapped)
        rh = 18 + nl * fs * 1.22 + 6
        if i % 2 == 0:
            tb.append(f'<rect x="{TX}" y="{y:.1f}" width="3680" height="{rh:.1f}" fill="#FFFFFF"/>')
        x = TX
        for j, (wl, (name, cw)) in enumerate(zip(wrapped, cols)):
            for k, ln in enumerate(wl):
                if j == 0:
                    tb.append(f'<circle cx="{x+30}" cy="{y + 14 + fs*0.55:.1f}" r="21" fill="{DCOLOR[s["d"]]}"/>')
                    tb.append(T(x + 30, y + 14 + fs * 0.55 + 8, ln, 21, 800, '#FFFFFF', 'middle'))
                else:
                    col = DCOLOR[s['d']] if j == 1 else NAVY
                    tb.append(T(x + 10, y + 14 + fs * 0.9 + k * fs * 1.25, ln, fs, 700 if j in (1, 2) else 500, col))
            x += cw
        y += rh
    tb.append(f'<line x1="{TX}" y1="{y:.1f}" x2="{TX+3680}" y2="{y:.1f}" stroke="{LINE}" stroke-width="2"/>')
    tb.append('</g>')
    body += tb
    print('tabla termina en y =', round(y))
    return doc('\n'.join(body), header('Liceos y colegios con enseñanza media en cinco delegaciones', f'{len(SEL)} establecimientos · 5 delegaciones'))

if __name__ == '__main__':
    import labels as L
    pieces = {'MAPA GENERAL': general_piece(L.URB)}
    names = {'TB': 'MAPA DELEGACION TIERRAS BLANCAS', 'RU': 'MAPA DELEGACION RURAL', 'TO': 'MAPA DELEGACION TONGOY',
             'GU': 'MAPA DELEGACION GUANAQUEROS', 'PA': 'MAPA DELEGACION PARTE ALTA'}
    for k, nm in names.items():
        pieces[nm] = deleg_piece(k, L.DEL.get(k, {}))
    for nm, svg in pieces.items():
        open(os.path.join(OUT, nm + '.svg'), 'w').write(svg)
        print(nm, len(svg) // 1024, 'KB')
