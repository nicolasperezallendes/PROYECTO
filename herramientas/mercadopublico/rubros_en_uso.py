#!/usr/bin/env python3
"""Cuenta qué categorías de producto usan las licitaciones activas de consultoría.

Sirve para revisar si los rubros inscritos de JUNCOS siguen siendo los que
usa el Estado. Toma unos 7 minutos con 180 licitaciones.

    python3 rubros_en_uso.py --max 180 --md rubros.md
"""
import argparse
import collections
from datetime import datetime
from pathlib import Path

import mercadopublico as mp
from postulables import normalizar

CLAVES = ["consultor", "asesoria", "estudio", "diagnostico", "encuesta", "evaluacion de programa",
          "investigacion", "capacitacion", "plan de desarrollo", "levantamiento", "sistematizacion"]
EXCLUIR = ["construccion", "obra", "suministro", "adquisicion", "mantencion", "reparacion", "arriendo"]


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--max", type=int, default=180, help="licitaciones a revisar en detalle")
    p.add_argument("--md", help="guardar la tabla en este archivo Markdown")
    args = p.parse_args()

    todas = mp.licitaciones(None, "activas")
    cand = [l for l in todas
            if any(k in normalizar(l["Nombre"]) for k in CLAVES)
            and not any(e in normalizar(l["Nombre"]) for e in EXCLUIR)][: args.max]
    conteo, nombres = collections.Counter(), {}
    for i, l in enumerate(cand, 1):
        mp.progreso(i, len(cand))
        try:
            ficha = mp.licitacion(l["CodigoExterno"])
        except mp.ErrorAPI:
            continue
        vistos = set()
        for it in ((ficha or {}).get("Items") or {}).get("Listado", []):
            c = str(it.get("CodigoCategoria"))
            if c not in vistos:
                vistos.add(c)
                conteo[c] += 1
                nombres[c] = (it.get("Categoria") or "").split(" / ")[-1]
    filas = [{"n": n, "codigo": c, "categoria": nombres[c]} for c, n in conteo.most_common()]
    md = (f"# Categorías usadas en licitaciones de consultoría\n\nConsulta del {datetime.now():%d-%m-%Y %H:%M}. "
          f"Activas: {len(todas)}. Revisadas: {len(cand)}.\n\n"
          + mp.tabla_md(filas, [(lambda r: r["n"], "Licitaciones"), (lambda r: r["codigo"], "Código"),
                                (lambda r: r["categoria"], "Categoría")]) + "\n")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
    else:
        print(md)


if __name__ == "__main__":
    main()
