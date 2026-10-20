#!/usr/bin/env python3
"""Busca Compras Ágiles abiertas afines al perfil de una empresa.

Usa la API de Compra Ágil (v2, beta desde el 22-05-2026) de ChileCompra y el
mismo perfil que postulables.py (perfil_juncos.json), más su bloque
"compra_agil". Entrega un ranking en Markdown.

    python3 compras_agiles.py
    python3 compras_agiles.py --region coquimbo --md ranking_ca.md
    python3 compras_agiles.py --dias 2 --max-detalle 80 --json ca.json

Cómo puntúa cada Compra Ágil:
  1. Baja las publicadas (abiertas) de los últimos --dias días y filtra por
     nombre: al menos una palabra clave y ninguna exclusión.
  2. Baja el detalle de las mejores candidatas y suma:
     el peso de cada rubro del perfil que coincide con los productos pedidos,
     +1 por palabra clave en nombre, descripción o productos (tope 6),
     +2 si es de una región preferente,
     +1 si el servicio se puede prestar a distancia (en línea, diseño, etc.).
  3. Marca alertas: cierre muy próximo, presencial fuera de la región,
     exigencia de OTEC o código SENCE, segundo llamado.

El ticket es el mismo de la API de Mercado Público (MERCADOPUBLICO_TICKET o
.env junto a este script). Va en el header "ticket", no en la URL.
"""

import argparse
import json
import re
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    CHILE = ZoneInfo("America/Santiago")
except Exception:  # sin base de zonas horarias: se muestra la hora tal como llega
    CHILE = None

import mercadopublico as mp
from postulables import contar, normalizar

BASE = os.environ.get("MERCADOPUBLICO_CA_BASE", "https://api2.mercadopublico.cl").rstrip("/")
RUTAS = ["/v2/compra-agil", "/v2/compraagil"]  # la guía usa las dos formas
PAUSA = 1.0
IVA = 0.19

# Códigos de región de la API (1 a 16). Verificar en la primera corrida
# contra institucion.nombre_region.
REGIONES = {
    "tarapaca": 1, "antofagasta": 2, "atacama": 3, "coquimbo": 4, "valparaiso": 5,
    "ohiggins": 6, "o'higgins": 6, "libertador": 6, "maule": 7, "biobio": 8,
    "araucania": 9, "los lagos": 10, "aysen": 11, "magallanes": 12,
    "metropolitana": 13, "santiago": 13, "los rios": 14, "arica": 15, "nuble": 16,
}


class ErrorCA(Exception):
    pass


class CuotaAgotada(ErrorCA):
    pass


_ruta_ok = None


def pedir(sufijo="", **params):
    """GET a la API de Compra Ágil con el ticket en el header y reintentos."""
    global _ruta_ok
    ticket = mp.cargar_ticket()
    rutas = [_ruta_ok] if _ruta_ok else RUTAS
    ultimo = None
    for ruta in rutas:
        url = f"{BASE}{ruta}{sufijo}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        req = urllib.request.Request(url, headers={"ticket": ticket, "Accept": "application/json"})
        espera = 2
        for intento in range(5):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    datos = json.loads(r.read().decode("utf-8"))
                _ruta_ok = ruta
                time.sleep(PAUSA)
                return datos
            except urllib.error.HTTPError as e:
                cuerpo = e.read().decode("utf-8", "replace")[:300]
                if e.code == 404 and not sufijo and ruta != rutas[-1]:
                    ultimo = f"404 en {ruta}"
                    break  # probar la otra forma de la ruta
                if e.code == 429:
                    raise CuotaAgotada("429: se agotó la cuota diaria del ticket. "
                                       "Se reinicia al cambiar el día.")
                if e.code == 401:
                    raise ErrorCA("401: falta el ticket o no es válido para la API de Compra Ágil.")
                if e.code in (500, 502, 503, 504) and intento < 4:
                    time.sleep(espera)
                    espera *= 2
                    continue
                raise ErrorCA(f"{e.code}: {cuerpo}")
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:  # incluye cortes de conexión a mitad de lectura
                if intento < 4:
                    time.sleep(espera)
                    espera *= 2
                    continue
                raise ErrorCA(f"Sin conexión con {BASE}: {e}")
    raise ErrorCA(ultimo or "Sin respuesta de la API de Compra Ágil")


def listar_publicadas(dias, region=None, tamano=10, max_paginas=200):
    # Probado el 19-10-2026: la API acepta páginas de 10 a 50, pero con 25 o 50
    # se cae siempre por tiempo (504 a los 29 s). Con 10 responde en 15 a 28 s.
    params = {"estado": "publicada", "tamano_pagina": tamano, "numero_pagina": 1,
              "ordenar_por": "FechaPublicacion"}
    if dias:
        desde = datetime.now(timezone.utc) - timedelta(days=dias)
        params["publicado_desde"] = desde.strftime("%Y-%m-%dT%H:%M:%SZ")
    if region:
        params["region"] = region
    items, vistos = [], set()
    while True:
        payload = (pedir(**params) or {}).get("payload") or {}
        for it in payload.get("items") or []:
            # la paginación puede repetir registros si se publican nuevos mientras se recorre
            if it.get("codigo") not in vistos:
                vistos.add(it.get("codigo"))
                items.append(it)
        pag = payload.get("paginacion") or {}
        total = int(pag.get("total_paginas") or 1)
        print(f"\r  página {params['numero_pagina']}/{total}", end="", file=sys.stderr, flush=True)
        if params["numero_pagina"] >= min(total, max_paginas):
            print(file=sys.stderr)
            return items
        params["numero_pagina"] += 1


def buscar_texto(terminos, region=None, max_paginas=4):
    """Busca Compras Ágiles publicadas con el filtro de texto q de la API (rápido)."""
    items, vistos = [], set()
    for t in terminos:
        params = {"estado": "publicada", "tamano_pagina": 10, "numero_pagina": 1, "q": t}
        if region:
            params["region"] = region
        while True:
            try:
                payload = (pedir(**params) or {}).get("payload") or {}
            except ErrorCA as e:
                print(f"  '{t}' página {params['numero_pagina']}: {e}", file=sys.stderr)
                break
            for it in payload.get("items") or []:
                if it.get("codigo") not in vistos:
                    vistos.add(it.get("codigo"))
                    items.append(it)
            total = int((payload.get("paginacion") or {}).get("total_paginas") or 1)
            print(f"  '{t}': página {params['numero_pagina']}/{total}, acumuladas {len(items)}", file=sys.stderr)
            if params["numero_pagina"] >= min(total, max_paginas):
                break
            params["numero_pagina"] += 1
    return items


def detalle(codigo):
    return (pedir("/" + urllib.parse.quote(codigo)) or {}).get("payload") or {}


# ---------------------------------------------------------------- utilidades

def g(d, *ruta, defecto=None):
    for clave in ruta:
        if not isinstance(d, dict):
            return defecto
        d = d.get(clave)
    return defecto if d is None else d


def fecha(texto):
    if not texto:
        return None
    try:
        f = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None
    if f.tzinfo is None and CHILE:
        f = f.replace(tzinfo=CHILE)
    return f.astimezone(CHILE) if CHILE and f.tzinfo else f


def monto(item):
    for ruta in (("presupuesto", "monto_disponible_clp"), ("montos", "monto_disponible_clp")):
        v = g(item, *ruta)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def codigos_productos(item):
    return {str(p.get("codigo_producto") or "").strip()
            for p in (item.get("productos_solicitados") or []) if p.get("codigo_producto")}


def rubros_coincidentes(codigos, rubros):
    hallados = []
    for r in rubros:
        codigo = str(r["codigo"])
        if not r.get("peso", 5):
            continue
        pref = codigo.rstrip("0")
        if any(c.startswith(pref) and len(c) == len(codigo) for c in codigos):
            hallados.append(r)
    return hallados


def texto_completo(item):
    prods = " ".join(f"{p.get('nombre', '')} {p.get('descripcion', '')}"
                     for p in (item.get("productos_solicitados") or []))
    return f"{item.get('nombre', '')} {item.get('descripcion', '')} {prods}"


# ---------------------------------------------------------------- línea de diseño

def contar_d(texto, palabras):
    """Como contar(), pero por palabra completa (con plural), para la línea de diseño.
    Evita que 'logo' calce con 'kinesiologo' o 'diploma' con 'diplomado'."""
    t = normalizar(texto)
    return [p for p in palabras
            if re.search(r"(?<![a-z0-9])" + re.escape(normalizar(p)) + r"(s|es)?(?![a-z0-9])", t)]


def unidades(c):
    try:
        return f"{float(c):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return str(c)


def cfg_diseno(perfil):
    d = perfil.get("compra_agil", {}).get("diseno", {})
    return d if d.get("activo") else {}


def excluido(nombre, perfil, extra=()):
    """Exclusión por nombre. En diseño se perdonan exclusiones genéricas como 'adquisicion de'."""
    ca = perfil.get("compra_agil", {})
    excl = perfil.get("excluir", []) + ca.get("excluir_extra", []) + list(extra)
    hits = contar(nombre, excl)
    d = cfg_diseno(perfil)
    if d and contar_d(nombre, d.get("palabras", [])):
        flex = [normalizar(x) for x in d.get("excluir_flexible", [])]
        hits = [h for h in hits if normalizar(h) not in flex]
    return hits


def es_diseno(item, perfil):
    d = cfg_diseno(perfil)
    if not d:
        return False
    return bool(rubros_coincidentes(codigos_productos(item), d.get("rubros", []))
                or contar_d(item.get("nombre", ""), d.get("palabras", [])))


def motivo_material(item, perfil):
    """Devuelve por qué una compra de diseño involucra demasiado material, o '' si está bien."""
    d = cfg_diseno(perfil)
    texto = texto_completo(item)
    malas = contar(texto, d.get("excluir", []))
    if malas:
        return "incluye " + ", ".join(malas[:3])
    tope = d.get("max_unidades", 60)
    for p in item.get("productos_solicitados") or []:
        try:
            if float(p.get("cantidad") or 0) > tope:
                return f"{unidades(p.get('cantidad'))} unidades de '{(p.get('nombre') or '')[:30]}'"
        except (TypeError, ValueError):
            pass
    m = monto(item)
    if m and m > d.get("monto_max", 2_000_000):
        return f"monto ${m:,.0f}".replace(",", ".")
    return ""


# ---------------------------------------------------------------- evaluación

def evaluar(item, perfil, ahora=None):
    ca = perfil.get("compra_agil", {})
    if excluido(item.get("nombre", ""), perfil):
        return None
    d = cfg_diseno(perfil)
    claves_todas = perfil.get("palabras_clave", []) + ca.get("palabras_clave_extra", [])
    texto = texto_completo(item)
    claves = contar(texto, claves_todas) + contar_d(texto, d.get("palabras", []))
    rubros = rubros_coincidentes(codigos_productos(item), perfil.get("rubros", []))
    vistos = {r["codigo"] for r in rubros}
    rubros += [r for r in rubros_coincidentes(codigos_productos(item), d.get("rubros", []))
               if r["codigo"] not in vistos]
    linea = "diseño" if es_diseno(item, perfil) else "consultoría"
    region = g(item, "institucion", "nombre_region", defecto="") or ""
    pref = any(normalizar(r) in normalizar(region) for r in perfil.get("regiones_preferentes", []))
    remoto = bool(contar(texto, ca.get("senales_remoto", [])))
    puntaje = sum(r.get("peso", 5) for r in rubros) + min(len(claves), 6) + \
        (2 if pref else 0) + (1 if remoto else 0)

    ahora = ahora or (datetime.now(CHILE) if CHILE else datetime.now())
    cierre = fecha(g(item, "fechas", "fecha_cierre"))
    horas = (cierre - ahora).total_seconds() / 3600 if cierre and cierre.tzinfo else None

    alertas = []
    if horas is not None and horas < ca.get("horas_alerta_cierre", 24):
        alertas.append(f"cierra en {max(horas, 0):.0f} h")
    if not pref and not remoto:
        alertas.append("presencial fuera de la región: revisar logística")
    if contar(texto, ca.get("alertas_texto", [])):
        alertas.append("pide " + ", ".join(contar(texto, ca.get("alertas_texto", []))))
    llamado = g(item, "convocatoria", "descripcion", defecto="") or \
        str(g(item, "convocatoria", "estado_convocatoria", defecto="") or "")
    if "segund" in normalizar(llamado):
        alertas.append("segundo llamado (abierto a empresas de todo tamaño)")
    if item.get("_sin_detalle"):
        alertas.append("la API no dio el detalle: revisar productos y cantidades en la plataforma")
    if linea == "diseño":
        alertas.append("cotizar impresión y despacho con imprenta antes de fijar el precio")
        if contar(texto, ["instalacion", "instalar", "retiro"]):
            alertas.append("incluye instalación")

    m = monto(item)
    return {
        "puntaje": puntaje,
        "linea": linea,
        "codigo": item.get("codigo", ""),
        "nombre": (item.get("nombre") or "").strip(),
        "organismo": g(item, "institucion", "organismo_comprador", defecto=""),
        "unidad": g(item, "institucion", "unidad_compra", defecto=""),
        "region": region.replace("Región de ", "").replace("Región del ", "").replace("Región ", ""),
        "monto_clp": m,
        "neto_max_clp": round(m / (1 + IVA)) if m else None,
        "cierre": cierre.strftime("%d-%m-%Y %H:%M") if cierre else "",
        "horas_al_cierre": round(horas, 1) if horas is not None else None,
        "ofertas": g(item, "resumen", "total_ofertas_recibidas"),
        "plazo_entrega_dias": g(item, "entrega", "plazo_entrega_dias"),
        "llamado": llamado,
        "rubros": ", ".join(r["nombre"] + ("" if r.get("inscrito", True) else " (no inscrito)")
                            for r in rubros),
        "claves": ", ".join(claves[:4]),
        "alertas": "; ".join(alertas),
    }


COLUMNAS = [
    (lambda r: r["puntaje"], "Pts"),
    (lambda r: r["codigo"], "Código"),
    (lambda r: r.get("linea", ""), "Línea"),
    (lambda r: r["nombre"], "Nombre"),
    (lambda r: r["organismo"], "Organismo"),
    (lambda r: r["region"], "Región"),
    (lambda r: mp.pesos(r["monto_clp"]), "Monto disponible"),
    (lambda r: mp.pesos(r["neto_max_clp"]), "Neto máx. (sin IVA)"),
    (lambda r: r["cierre"], "Cierre"),
    (lambda r: "" if r["ofertas"] is None else r["ofertas"], "Ofertas"),
    (lambda r: r["rubros"] or "—", "Rubro coincidente"),
    (lambda r: r["alertas"] or "—", "Alertas"),
]


def main():
    aqui = Path(__file__).parent
    p = argparse.ArgumentParser(description="Compras Ágiles abiertas afines a un perfil.")
    p.add_argument("--perfil", default=str(aqui / "perfil_juncos.json"))
    p.add_argument("--region", help="solo esta región (nombre, ej. coquimbo, o código 1-16)")
    p.add_argument("--dias", type=int, default=None,
                   help="publicadas en los últimos N días (0 = todas las abiertas; por defecto el perfil)")
    p.add_argument("--max-detalle", type=int, default=None,
                   help="cuántas candidatas revisar en detalle (cada una es una consulta)")
    p.add_argument("--min-puntaje", type=int, default=None)
    p.add_argument("--min-horas", type=float, default=None,
                   help="descarta las que cierran antes de N horas")
    p.add_argument("--incluir-sugeridos", action="store_true",
                   help="acepta también los rubros sugeridos que aún no están inscritos")
    p.add_argument("--todas", action="store_true",
                   help="no exige coincidencia de rubro (vuelve al filtro solo por palabras clave)")
    p.add_argument("--sin-prefiltro", action="store_true",
                   help="revisa el detalle de todas las no excluidas, no solo las que tienen "
                        "palabras clave en el nombre (lento: unos 17 s por Compra Ágil)")
    p.add_argument("--q", help="buscar con el filtro de texto de la API, términos separados por coma "
                               "(ej. 'clima,estudio,encuesta'). Mucho más rápido que recorrer todo")
    p.add_argument("--diseno", action="store_true",
                   help="agrega la búsqueda de piezas de diseño (pendones, lanyards, afiches...) "
                        "con los términos de compra_agil.diseno.terminos_busqueda")
    p.add_argument("--md", help="guardar el ranking en este archivo Markdown")
    p.add_argument("--json", help="guardar el ranking en JSON")
    args = p.parse_args()

    perfil = json.loads(Path(args.perfil).read_text(encoding="utf-8"))
    ca = perfil.get("compra_agil", {})
    solo_rubros = ca.get("solo_rubros", True) and not args.todas
    admitidos = [r for r in perfil.get("rubros", [])
                 if r.get("peso", 5) and (r.get("inscrito", True) or args.incluir_sugeridos)]
    dias = ca.get("dias_publicacion", 3) if args.dias is None else args.dias
    max_det = args.max_detalle or ca.get("max_detalle", 60)
    min_pts = ca.get("min_puntaje", 3) if args.min_puntaje is None else args.min_puntaje
    min_horas = ca.get("min_horas_al_cierre", 3) if args.min_horas is None else args.min_horas

    region = None
    if args.region:
        region = int(args.region) if args.region.isdigit() else REGIONES.get(normalizar(args.region))
        if not region:
            sys.exit(f"Región no reconocida: {args.region}")

    consulta = datetime.now(CHILE) if CHILE else datetime.now()
    print("Bajando Compras Ágiles publicadas...", file=sys.stderr)
    try:
        terminos = [t.strip() for t in (args.q or "").split(",") if t.strip()]
        if args.diseno:
            terminos += [t.strip() for t in cfg_diseno(perfil).get("terminos_busqueda", "").split(",") if t.strip()]
        if terminos:
            todas = buscar_texto(terminos, region)
        else:
            todas = listar_publicadas(dias, region)
    except ErrorCA as e:
        sys.exit(f"No se pudo listar: {e}")

    claves = perfil.get("palabras_clave", []) + ca.get("palabras_clave_extra", [])
    prefs = perfil.get("regiones_preferentes", [])
    candidatas = []
    for it in todas:
        nombre = it.get("nombre", "")
        if excluido(nombre, perfil, cfg_diseno(perfil).get("excluir", []) if contar_d(nombre, cfg_diseno(perfil).get("palabras", [])) else ()):
            continue
        hits = contar(nombre, claves) + contar_d(nombre, cfg_diseno(perfil).get("palabras", []))
        if hits or args.sin_prefiltro:
            reg = g(it, "institucion", "nombre_region", defecto="") or ""
            pref = any(normalizar(r) in normalizar(reg) for r in prefs)
            candidatas.append((len(hits) + (2 if pref else 0), it))
    candidatas.sort(key=lambda x: -x[0])
    candidatas = candidatas[:max_det]
    print(f"{len(todas)} publicadas, {len(candidatas)} candidatas por nombre.", file=sys.stderr)

    filas, aviso, descartes_material = [], "", []
    for i, (_, it) in enumerate(candidatas, 1):
        mp.progreso(i, len(candidatas))
        try:
            det = detalle(it.get("codigo", "")) or {}
        except CuotaAgotada as e:
            aviso = f"\n\n**Aviso:** {e} Se revisaron {i - 1} de {len(candidatas)} candidatas."
            print(f"\n  {e}", file=sys.stderr)
            break
        except ErrorCA as e:
            print(f"\n  {it.get('codigo')}: {e}", file=sys.stderr)
            det = {"_sin_detalle": True}
        item = {**it, **det}  # el detalle trae descripción, productos y entrega
        diseno = es_diseno(item, perfil)
        rubro_ok = rubros_coincidentes(codigos_productos(item), admitidos) or \
            rubros_coincidentes(codigos_productos(item), cfg_diseno(perfil).get("rubros", [])) or \
            (diseno and det.get("_sin_detalle"))  # nombre de diseño, pero la API no dio el detalle
        if solo_rubros and not rubro_ok:
            continue  # sus productos no están en los rubros de la empresa ni en la línea de diseño
        if diseno and motivo_material(item, perfil):
            descartes_material.append(f"{item.get('codigo')} ({motivo_material(item, perfil)})")
            continue  # demasiado material o impresión para la línea de diseño
        fila = evaluar(item, perfil, consulta)
        if not fila or fila["puntaje"] < min_pts:
            continue
        if fila["horas_al_cierre"] is not None and fila["horas_al_cierre"] < min_horas:
            continue
        filas.append(fila)

    filas.sort(key=lambda r: (-r["puntaje"], r["horas_al_cierre"] if r["horas_al_cierre"] is not None else 9e9))
    alcance = f"región {args.region}" if region else "todo el país"
    ventana = f"publicadas en los últimos {dias} días" if dias else "todas las abiertas"
    if solo_rubros:
        ventana += (". Filtro: solo productos de los rubros inscritos"
                    + (" y sugeridos" if args.incluir_sugeridos else "")
                    + (", más la línea de diseño" if cfg_diseno(perfil) else ""))
    if descartes_material:
        aviso += ("\n\nDescartadas por mucho material o impresión (línea de diseño): "
                  + "; ".join(descartes_material) + ".")
    md = (f"# Compras Ágiles afines · {perfil.get('empresa', 'perfil')}\n\n"
          f"Fuente: API Compra Ágil de Mercado Público (v2 beta), consultada el "
          f"{consulta:%d-%m-%Y %H:%M} (hora de Chile). Alcance: {alcance}, {ventana}. "
          f"Abiertas encontradas: {len(todas)}. Revisadas en detalle: {len(candidatas)}. "
          f"Afines: {len(filas)}.\n\n"
          "El monto disponible incluye impuestos. El neto máximo es ese monto dividido por 1,19, "
          "para cotizar con IVA sin pasarse del presupuesto.\n\n"
          + mp.tabla_md(filas, COLUMNAS) + aviso + "\n")
    if args.json:
        Path(args.json).write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"Markdown guardado en {args.md}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
