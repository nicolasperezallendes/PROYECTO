#!/usr/bin/env python3
"""Busca licitaciones activas en todo Chile afines al perfil de una empresa.

Lee el perfil (rubros UNSPSC, palabras clave, exclusiones y regiones) desde
un JSON, por defecto perfil_juncos.json, y entrega un ranking en Markdown.

    python3 postulables.py
    python3 postulables.py --region coquimbo --max-detalle 80 --md ranking.md
    python3 postulables.py --perfil otro_perfil.json --min-monto 5000000

Cómo puntúa cada licitación:
  1. Filtro inicial por nombre: debe tener al menos una palabra clave y
     ninguna palabra excluida (esto evita bajar miles de fichas).
  2. Se baja la ficha de las mejores candidatas y se suma:
     el peso de cada rubro del perfil que coincide con los productos pedidos
     (5 núcleo, 3 sugerido, 2 secundario),
     +1 por palabra clave en nombre o descripción (tope 6),
     +2 si la región está entre las preferentes.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import mercadopublico as mp


def normalizar(texto):
    texto = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def contar(texto, palabras):
    t = normalizar(texto)
    return [p for p in palabras if normalizar(p) in t]


def rubros_coincidentes(ficha, rubros):
    items = ((ficha.get("Items") or {}).get("Listado")) or []
    codigos = {str(i.get("CodigoProducto") or "") for i in items} | \
              {str(i.get("CodigoCategoria") or "") for i in items}
    hallados = []
    for r in rubros:
        codigo = str(r["codigo"])
        if not r.get("peso", 5):
            continue
        pref = codigo.rstrip("0")
        # Los códigos UNSPSC tienen 8 dígitos y los propios de ChileCompra
        # (ej. 102000000 Consultoría) 9: solo se comparan con su mismo largo.
        if any(c.startswith(pref) and len(c) == len(codigo) for c in codigos if c):
            hallados.append(r)
    return hallados


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


def excluido(nombre, perfil, usar_diseno=False):
    """Exclusión por nombre. En la línea de diseño se perdonan 'adquisicion de' y similares."""
    hits = contar(nombre, perfil.get("excluir", []))
    d = cfg_diseno(perfil) if usar_diseno else {}
    if d and contar_d(nombre, d.get("palabras", [])):
        flex = [normalizar(x) for x in d.get("excluir_flexible", [])]
        hits = [h for h in hits if normalizar(h) not in flex] + contar(nombre, d.get("excluir", []))
    return hits


def texto_ficha(ficha):
    items = ((ficha.get("Items") or {}).get("Listado")) or []
    extra = " ".join(f"{i.get('NombreProducto', '')} {i.get('Descripcion', '')}" for i in items)
    return f"{ficha.get('Nombre', '')} {ficha.get('Descripcion', '')} {extra}"


def es_diseno(ficha, perfil):
    d = cfg_diseno(perfil)
    return bool(d) and bool(rubros_coincidentes(ficha, d.get("rubros", []))
                            or contar_d(ficha.get("Nombre", ""), d.get("palabras", [])))


def motivo_material(ficha, perfil):
    """Por qué una licitación de diseño trae demasiado material o impresión ('' si está bien)."""
    d = cfg_diseno(perfil)
    tipos = d.get("tipos_licitacion", ["L1", "LE"])
    if ficha.get("Tipo") and ficha.get("Tipo") not in tipos:
        return f"licitación tipo {ficha.get('Tipo')} (demasiado grande para piezas sueltas)"
    malas = contar(texto_ficha(ficha), d.get("excluir", []))
    if malas:
        return "incluye " + ", ".join(malas[:3])
    tope = d.get("max_unidades", 60)
    for i in ((ficha.get("Items") or {}).get("Listado")) or []:
        try:
            if float(i.get("Cantidad") or 0) > tope:
                return f"{unidades(i.get('Cantidad'))} unidades de '{(i.get('NombreProducto') or '')[:30]}'"
        except (TypeError, ValueError):
            pass
    m = ficha.get("MontoEstimado") if ficha.get("VisibilidadMonto") else None
    if m and ficha.get("Moneda", "CLP") == "CLP" and m > d.get("monto_max_licitacion", 5_000_000):
        return f"monto estimado ${m:,.0f}".replace(",", ".")
    return ""


def evaluar(ficha, perfil, usar_diseno=False):
    texto = texto_ficha(ficha)
    if excluido(ficha.get("Nombre", ""), perfil, usar_diseno):
        return None
    comprador = ficha.get("Comprador") or {}
    region = comprador.get("RegionUnidad", "").strip()
    rubros = rubros_coincidentes(ficha, perfil.get("rubros", []))
    d = cfg_diseno(perfil) if usar_diseno else {}
    vistos = {r["codigo"] for r in rubros}
    rubros += [r for r in rubros_coincidentes(ficha, d.get("rubros", [])) if r["codigo"] not in vistos]
    claves = contar(texto, perfil.get("palabras_clave", [])) + contar_d(texto, d.get("palabras", []))
    pref = any(normalizar(r) in normalizar(region) for r in perfil.get("regiones_preferentes", []))
    puntaje = sum(r.get("peso", 5) for r in rubros) + min(len(claves), 6) + (2 if pref else 0)
    fila = mp.fila_licitacion(ficha)
    fila.update({
        "puntaje": puntaje,
        "linea": "diseño" if (usar_diseno and es_diseno(ficha, perfil)) else "consultoría",
        "organismo": comprador.get("NombreOrganismo", ""),
        "region": region.replace("Región de ", "").replace("Región del ", "").replace("Región ", ""),
        "rubros": ", ".join(r["nombre"] + ("" if r.get("inscrito", True) else " (no inscrito)")
                            for r in rubros),
        "claves": ", ".join(claves[:4]),
    })
    return fila


COLUMNAS = [
    (lambda r: r["puntaje"], "Pts"),
    (lambda r: f"[{r['codigo']}]({r['url']})", "Código"),
    (lambda r: r.get("linea", ""), "Línea"),
    (lambda r: r["nombre"], "Nombre"),
    (lambda r: r["organismo"], "Organismo"),
    (lambda r: r["region"], "Región"),
    (lambda r: mp.pesos(r["monto_estimado"], r["moneda"]), "Monto"),
    (lambda r: r["cierre"], "Cierre"),
    (lambda r: r["rubros"] or "—", "Rubro coincidente"),
]


def main():
    aqui = Path(__file__).parent
    p = argparse.ArgumentParser(description="Licitaciones activas afines a un perfil.")
    p.add_argument("--perfil", default=str(aqui / "perfil_juncos.json"))
    p.add_argument("--region", help="solo esta región (texto parcial, ej. coquimbo)")
    p.add_argument("--max-detalle", type=int, default=60,
                   help="cuántas candidatas revisar en detalle (cada una es una consulta)")
    p.add_argument("--min-monto", type=float, help="monto estimado mínimo en pesos")
    p.add_argument("--min-puntaje", type=int, default=3)
    p.add_argument("--diseno", action="store_true",
                   help="agrega la línea de diseño: pendones, lanyards, afiches y piezas con poco material "
                        "(usa compra_agil.diseno del perfil)")
    p.add_argument("--solo-diseno", action="store_true", help="muestra solo la línea de diseño")
    p.add_argument("--max-diseno", type=int, default=40,
                   help="candidatas de diseño a revisar en detalle, aparte de --max-detalle")
    p.add_argument("--md", help="guardar el ranking en este archivo Markdown")
    p.add_argument("--json", help="guardar el ranking en JSON")
    args = p.parse_args()

    perfil = json.loads(Path(args.perfil).read_text(encoding="utf-8"))
    print("Bajando licitaciones activas de todo el país...", file=sys.stderr)
    todas = mp.licitaciones(None, "activas")
    usar_diseno = (args.diseno or args.solo_diseno) and bool(cfg_diseno(perfil))
    claves = perfil.get("palabras_clave", [])
    pal_diseno = cfg_diseno(perfil).get("palabras", []) if usar_diseno else []
    candidatas, cand_diseno = [], []
    for l in todas:
        nombre = l.get("Nombre", "")
        if excluido(nombre, perfil, usar_diseno):
            continue
        hits_d = contar_d(nombre, pal_diseno)
        if hits_d:
            cand_diseno.append((len(hits_d), l["CodigoExterno"]))
            continue
        hits = contar(nombre, claves)
        if hits and not args.solo_diseno:
            candidatas.append((len(hits), l["CodigoExterno"]))
    candidatas.sort(reverse=True)
    cand_diseno.sort(reverse=True)
    candidatas = candidatas[: args.max_detalle] + cand_diseno[: args.max_diseno]
    print(f"{len(todas)} activas, {len(candidatas)} candidatas por nombre.", file=sys.stderr)

    filas, descartes_material = [], []
    for i, (_, codigo) in enumerate(candidatas, 1):
        mp.progreso(i, len(candidatas))
        try:
            ficha = mp.licitacion(codigo)
        except mp.ErrorAPI as e:
            print(f"\n  {codigo}: {e}", file=sys.stderr)
            continue
        if not ficha:
            continue
        if usar_diseno and es_diseno(ficha, perfil) and motivo_material(ficha, perfil):
            descartes_material.append(f"{codigo} ({motivo_material(ficha, perfil)})")
            continue
        fila = evaluar(ficha, perfil, usar_diseno)
        if not fila or fila["puntaje"] < args.min_puntaje:
            continue
        if args.region and normalizar(args.region) not in normalizar(fila["region"]):
            continue
        if args.min_monto and (fila["moneda"] in ("", "CLP")) and (fila["monto_estimado"] or 0) < args.min_monto:
            continue
        filas.append(fila)

    filas.sort(key=lambda r: (-r["puntaje"], r["cierre"] or ""))
    titulo = f"Licitaciones afines · {perfil.get('empresa', 'perfil')}"
    md = (f"# {titulo}\n\nFuente: API Mercado Público, consultada el {datetime.now():%d-%m-%Y %H:%M}. "
          f"Activas en el país: {len(todas)}. Revisadas en detalle: {len(candidatas)}. "
          f"Afines: {len(filas)}."
          + (" Incluye la línea de diseño (piezas con poco material)." if usar_diseno else "")
          + "\n\n" + mp.tabla_md(filas, COLUMNAS)
          + ("\n\nDescartadas por mucho material o impresión (línea de diseño): "
             + "; ".join(descartes_material) + "." if descartes_material else "") + "\n")
    if args.json:
        Path(args.json).write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"Markdown guardado en {args.md}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
