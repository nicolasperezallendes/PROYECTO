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
     +5 por cada rubro del perfil que coincide con los productos pedidos,
     +1 por palabra clave en nombre o descripción (tope 6),
     +2 si la región está entre las preferentes.
"""

import argparse
import json
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
        pref = str(r["codigo"]).rstrip("0") or str(r["codigo"])
        if any(c.startswith(pref) for c in codigos if c):
            hallados.append(r["nombre"])
    return hallados


def evaluar(ficha, perfil):
    texto = f"{ficha.get('Nombre', '')} {ficha.get('Descripcion', '')}"
    if contar(ficha.get("Nombre", ""), perfil.get("excluir", [])):
        return None
    comprador = ficha.get("Comprador") or {}
    region = comprador.get("RegionUnidad", "").strip()
    rubros = rubros_coincidentes(ficha, perfil.get("rubros", []))
    claves = contar(texto, perfil.get("palabras_clave", []))
    pref = any(normalizar(r) in normalizar(region) for r in perfil.get("regiones_preferentes", []))
    puntaje = 5 * len(rubros) + min(len(claves), 6) + (2 if pref else 0)
    fila = mp.fila_licitacion(ficha)
    fila.update({
        "puntaje": puntaje,
        "organismo": comprador.get("NombreOrganismo", ""),
        "region": region.replace("Región de ", "").replace("Región del ", "").replace("Región ", ""),
        "rubros": ", ".join(rubros),
        "claves": ", ".join(claves[:4]),
    })
    return fila


COLUMNAS = [
    (lambda r: r["puntaje"], "Pts"),
    (lambda r: f"[{r['codigo']}]({r['url']})", "Código"),
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
    p.add_argument("--md", help="guardar el ranking en este archivo Markdown")
    p.add_argument("--json", help="guardar el ranking en JSON")
    args = p.parse_args()

    perfil = json.loads(Path(args.perfil).read_text(encoding="utf-8"))
    print("Bajando licitaciones activas de todo el país...", file=sys.stderr)
    todas = mp.licitaciones(None, "activas")
    excl = perfil.get("excluir", [])
    claves = perfil.get("palabras_clave", [])
    candidatas = []
    for l in todas:
        nombre = l.get("Nombre", "")
        if contar(nombre, excl):
            continue
        hits = contar(nombre, claves)
        if hits:
            candidatas.append((len(hits), l["CodigoExterno"]))
    candidatas.sort(reverse=True)
    candidatas = candidatas[: args.max_detalle]
    print(f"{len(todas)} activas, {len(candidatas)} candidatas por nombre.", file=sys.stderr)

    filas = []
    for i, (_, codigo) in enumerate(candidatas, 1):
        mp.progreso(i, len(candidatas))
        try:
            ficha = mp.licitacion(codigo)
        except mp.ErrorAPI as e:
            print(f"\n  {codigo}: {e}", file=sys.stderr)
            continue
        if not ficha:
            continue
        fila = evaluar(ficha, perfil)
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
          f"Afines: {len(filas)}.\n\n" + mp.tabla_md(filas, COLUMNAS) + "\n")
    if args.json:
        Path(args.json).write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"Markdown guardado en {args.md}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
