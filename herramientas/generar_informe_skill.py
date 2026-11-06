#!/usr/bin/env python3
"""Genera el informe del perfil y la skill /juncos, y el paquete .zip de la skill.

Lee los archivos tal como están en el repositorio y los copia textualmente:
el perfil (Parte 1) y los seis archivos de la skill (Parte 2, con los títulos
dos niveles más abajo). Los pendientes salen de la tabla de tareas de
seguimiento.md (las filas cuyo estado no empieza con "Hecho").

    python3 herramientas/generar_informe_skill.py            # fecha de hoy
    python3 herramientas/generar_informe_skill.py --nota "actualizado con ..."

Deja en claude/:
    dd.mm.aaaa - INFORME PERFIL Y SKILL JUNCOS.md
    dd.mm.aaaa - SKILL JUNCOS.zip   (sin el .env con el ticket)

El informe es el que se sube al proyecto JUNCOS de claude.ai, en
claude/licitaciones-juncos/, para mantener las dos copias al día.
"""
import argparse
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / ".claude" / "skills" / "juncos"
HERR = RAIZ / "herramientas" / "mercadopublico"
SALIDA = RAIZ / "claude"

ORDEN = [
    ("SKILL.md", "Ficha de la empresa, alertas, rubros, especialidades, formato de entrega e índice"),
    ("proceso-postulacion.md", "Ciclo completo en 7 etapas, matriz de decisión, diseño muestral, lista de chequeo y ruta corta de Compra Ágil (CA1 a CA5)"),
    ("seguimiento.md", "Licitaciones y Compras Ágiles en curso, ficha de 564953-79-LE26, tareas de la empresa e historial"),
    ("aprendizajes.md", "Límites de la API, de la API de Compra Ágil, del portal y del entorno, y errores para no repetir"),
    ("plantillas.md", "Propuesta técnica, presupuesto, integridad, carta de experiencia, preguntas al foro y descripción de cotización de Compra Ágil"),
    ("rubros-consultoria.md", "Rubros que usa el Estado en consultoría y qué inscribir, mantener o quitar"),
]
ARCHIVOS_ZIP = ["mercadopublico.py", "postulables.py", "compras_agiles.py", "rubros_en_uso.py",
                "tablero.py", "tablero/index.html", "tablero/empresa.json",
                "perfil_juncos.json", "README.md"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def bajar_titulos(md, n=2):
    out, cerca = [], False
    for linea in md.splitlines():
        if linea.startswith("```"):
            cerca = not cerca
        if not cerca and re.match(r"^#{1,6} ", linea):
            linea = "#" * n + linea
        out.append(linea)
    return "\n".join(out)


def peso_txt(p):
    return {5: "Núcleo (5)", 4: "Alta (4)", 3: "Sugerido (3)", 2: "Secundario (2)"}.get(p, str(p))


def lista(valores):
    return ", ".join(f"`{v.strip()}`" for v in valores)


def pendientes():
    texto = (SKILL / "seguimiento.md").read_text(encoding="utf-8")
    bloque = texto.split("## Tareas pendientes de la empresa", 1)[-1].split("\n## ", 1)[0]
    filas = []
    for linea in bloque.splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 3 or celdas[0] in ("Tarea", "---") or set(celdas[0]) <= {"-"}:
            continue
        if not celdas[2].lower().startswith("hecho"):
            filas.append(f"{celdas[0]} ({celdas[1]}).")
    return filas


def informe(fecha, nota):
    perfil = json.loads((HERR / "perfil_juncos.json").read_text(encoding="utf-8"))
    ca = perfil.get("compra_agil", {})
    inscritos = [r for r in perfil["rubros"] if r.get("inscrito")]
    sugeridos = [r for r in perfil["rubros"] if not r.get("inscrito")]
    fecha_txt = f"{DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"

    L = ["# Perfil de postulación y skill /juncos de JUNCOS E.I.R.L.\n",
         f"**Fecha:** {fecha_txt}" + (f", {nota}" if nota else "") +
         " · **Rama:** `claude/stoic-darwin-gi9n29` · **Fuentes:** `herramientas/mercadopublico/perfil_juncos.json` "
         "y `.claude/skills/juncos/` (copiados textualmente)\n",
         "## Resumen\n",
         "- **Perfil de búsqueda:** dice cuánto pesa cada rubro, qué palabras acercan una licitación o una Compra Ágil "
         "al trabajo de la consultora y cuáles la descartan. Con él, los buscadores ordenan las licitaciones activas "
         "del país y las Compras Ágiles abiertas.",
         "- **Skill `/juncos`:** es la memoria del proceso. Guarda la ficha de la empresa, el ciclo completo de "
         "postulación, la ruta corta de Compra Ágil, el seguimiento, las lecciones aprendidas, las plantillas y el "
         "análisis de rubros de consultoría.",
         f"- **En números:** {len(inscritos)} rubros inscritos que puntúan, {len(sugeridos)} rubros sugeridos para "
         f"inscribir, {len(perfil['rubros_inscritos_sin_puntaje'])} rubros inscritos sin relación, "
         f"{len(perfil['palabras_clave'])} palabras clave y {len(perfil['excluir'])} exclusiones."
         + (f" Para Compra Ágil se suman {len(ca.get('palabras_clave_extra', []))} palabras clave, "
            f"{len(ca.get('excluir_extra', []))} exclusiones, {len(ca.get('senales_remoto', []))} señales de trabajo "
            f"a distancia y {len(ca.get('alertas_texto', []))} alertas propias." if ca else ""),
         "- **Lo que sigue pendiente** (tabla de tareas de `seguimiento.md`):"]
    L += [f"  - {p}" for p in pendientes()] + [""]

    L += ["## Parte 1. Perfil de postulación\n", "| Campo | Valor |\n|---|---|"]
    for k, t in [("empresa", "Empresa"), ("rut", "RUT"), ("codigo_proveedor_mp", "Código de proveedor en Mercado Público"),
                 ("estado_rubros", "Estado de los rubros"), ("nota_pesos", "Cómo se asignan los pesos")]:
        L.append(f"| {t} | {perfil.get(k, '')} |")
    L.append(f"| Regiones preferentes | {', '.join(perfil['regiones_preferentes'])} (+2 puntos) |\n")
    L += ["### Rubros que puntúan\n", "| Código | Rubro | ¿Inscrito? | Peso |\n|---|---|---|---|"]
    for r in sorted(perfil["rubros"], key=lambda r: (-r["peso"], not r.get("inscrito"), r["codigo"])):
        L.append(f"| {r['codigo']} | {r['nombre']} | {'Sí' if r.get('inscrito') else 'No, sugerido'} | {peso_txt(r['peso'])} |")
    L += ["\n### Rubros inscritos que no puntúan (se sugiere quitarlos)\n", "| Código | Rubro |\n|---|---|"]
    L += [f"| {r['codigo']} | {r['nombre']} |" for r in perfil["rubros_inscritos_sin_puntaje"]]
    L += ["\n### Palabras clave (suman 1 punto cada una, hasta 6)\n", lista(perfil["palabras_clave"]) + "\n",
          "### Exclusiones (si el nombre contiene una, se descarta)\n", lista(perfil["excluir"]) + "\n",
          "### Cómo se calcula el puntaje\n",
          "Puntaje = suma de los pesos de los rubros que coinciden con los productos licitados + 1 punto por palabra "
          "clave (hasta 6) + 2 puntos si la licitación es de una región preferente.\n",
          "Los códigos UNSPSC de 8 dígitos y las categorías de ChileCompra de 9 dígitos solo se comparan con códigos "
          "de su mismo largo. Antes de revisar el detalle, el buscador filtra por nombre: debe tener al menos una "
          "palabra clave y ninguna exclusión.\n"]
    if ca:
        L += ["### Compra Ágil (bloque `compra_agil`)\n",
              "`compras_agiles.py` usa los mismos rubros, palabras clave y exclusiones de arriba, más lo siguiente:\n"]
        if ca.get("solo_rubros", True):
            L.append("- **Filtro por rubros:** solo se proponen Compras Ágiles cuyos productos están en los rubros "
                     "inscritos. `--incluir-sugeridos` suma los sugeridos y `--todas` quita el filtro.")
        L += [f"- **Palabras clave adicionales:** {lista(ca.get('palabras_clave_extra', []))}",
              f"- **Exclusiones adicionales:** {lista(ca.get('excluir_extra', []))}",
              f"- **Señales de trabajo a distancia (+1 punto):** {lista(ca.get('senales_remoto', []))}",
              f"- **Alertas en el texto:** {lista(ca.get('alertas_texto', []))}",
              f"- **Parámetros:** publicadas en los últimos {ca.get('dias_publicacion', 3)} días, hasta "
              f"{ca.get('max_detalle', 60)} fichas de detalle, puntaje mínimo {ca.get('min_puntaje', 3)}, se descarta "
              f"lo que cierra en menos de {ca.get('min_horas_al_cierre', 3)} horas y se marca lo que cierra en menos "
              f"de {ca.get('horas_alerta_cierre', 24)}.\n",
              "Puntaje de una Compra Ágil = suma de los pesos de los rubros que coinciden con los productos pedidos "
              "+ 1 punto por palabra clave (hasta 6) + 2 puntos si es de la Región de Coquimbo + 1 punto si se puede "
              "hacer a distancia.\n"]
    L += ["### Perfil en formato JSON (copia exacta)\n",
          "```json\n" + json.dumps(perfil, ensure_ascii=False, indent=2) + "\n```\n",
          "## Parte 2. Skill /juncos actualizada\n",
          "La skill está en `.claude/skills/juncos/` y tiene seis archivos. Abajo va cada uno completo. Los títulos "
          "internos bajaron dos niveles para que calcen con este informe; el texto no cambió.\n",
          "| Archivo | Para qué sirve |\n|---|---|"]
    L += [f"| `{f}` | {d} |" for f, d in ORDEN] + [""]
    for i, (f, _) in enumerate(ORDEN, 1):
        txt = (SKILL / f).read_text(encoding="utf-8")
        L.append(f"### 2.{i} Archivo `{f}`\n")
        m = re.match(r"(?s)^---\n(.*?)\n---\n", txt)
        if m:
            L.append("Encabezado de la skill:\n\n```yaml\n---\n" + m.group(1) + "\n---\n```\n")
            txt = txt[m.end():]
        L.append(bajar_titulos(txt.strip()) + "\n")
    L.append(f"---\n\n*Informe generado con `herramientas/generar_informe_skill.py` el {fecha:%d-%m-%Y}. "
             "Si cambias la skill o el perfil, genéralo de nuevo.*\n")
    return "\n".join(L)


def paquete(destino):
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f, _ in ORDEN:
            z.write(SKILL / f, f"juncos/{f}")
        for f in ARCHIVOS_ZIP:
            if (HERR / f).exists():
                z.write(HERR / f, f"juncos/herramientas/mercadopublico/{f}")
    for info in zipfile.ZipFile(destino).infolist():
        if info.filename.endswith(".env"):
            raise SystemExit("El paquete incluye un .env: no se debe distribuir el ticket.")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--fecha", help="dd-mm-aaaa (por defecto hoy)")
    p.add_argument("--nota", default="", help="texto que sigue a la fecha, ej. 'actualizado con ...'")
    args = p.parse_args()
    fecha = datetime.strptime(args.fecha, "%d-%m-%Y") if args.fecha else datetime.now()
    md = SALIDA / f"{fecha:%d.%m.%Y} - INFORME PERFIL Y SKILL JUNCOS.md"
    md.write_text(informe(fecha, args.nota), encoding="utf-8")
    zp = SALIDA / f"{fecha:%d.%m.%Y} - SKILL JUNCOS.zip"
    paquete(zp)
    print(md)
    print(zp)


if __name__ == "__main__":
    main()
