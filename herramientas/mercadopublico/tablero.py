#!/usr/bin/env python3
"""Datos del tablero de JUNCOS a partir de seguimiento.md y de las APIs de Mercado Público.

Lee las tablas de `.claude/skills/juncos/seguimiento.md` (licitaciones, Compras Ágiles y
tareas), consulta el estado de cada proceso en Mercado Público y escribe en
`tablero/datos/` los archivos que usa el tablero publicado:

    compras_agiles.json  licitaciones.json  tareas.json  empresa.json  consulta.json
    _pagina.json         (la página tablero/index.html envuelta como {"text": ...})

Uso:
    python3 tablero.py                 # consulta las APIs y escribe los datos
    python3 tablero.py --sin-red       # solo con seguimiento.md (sin estado en vivo)

El ticket se lee igual que en los otros scripts (MERCADOPUBLICO_TICKET o .env).
Cómo subir los archivos al tablero: `.claude/skills/juncos/proceso-postulacion.md`,
sección «Salida en tablero».
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
import compras_agiles as ca  # noqa: E402
import mercadopublico as mp  # noqa: E402

SEGUIMIENTO = RAIZ / ".claude/skills/juncos/seguimiento.md"
if not SEGUIMIENTO.exists():  # dentro del .zip de la skill: juncos/seguimiento.md
    SEGUIMIENTO = RAIZ / "seguimiento.md"
DIR_TABLERO = AQUI / "tablero"
CHILE = ca.CHILE or timezone(timedelta(hours=-3))

REGIONES = {1: "Tarapacá", 2: "Antofagasta", 3: "Atacama", 4: "Coquimbo", 5: "Valparaíso",
            6: "O'Higgins", 7: "Maule", 8: "Biobío", 9: "La Araucanía", 10: "Los Lagos",
            11: "Aysén", 12: "Magallanes", 13: "Metropolitana", 14: "Los Ríos",
            15: "Arica y Parinacota", 16: "Ñuble"}
COD = re.compile(r"\b\d{3,7}-\d{1,4}-(?:COT|LE|LP|L1|LR|LQ|E2|CO|B2|H2|I2)\d{2}\b")


# ---------------------------------------------------------------- seguimiento.md

def limpiar(celda):
    """Quita el formato Markdown de una celda."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", celda)
    t = t.replace("**", "").replace("~~", "").replace("`", "")
    return re.sub(r"\s+", " ", t).strip()


def tablas(texto):
    """Devuelve {título de sección: [filas como dict]} para cada tabla bajo un '## '."""
    out, seccion, cab = {}, None, None
    for linea in texto.splitlines():
        if linea.startswith("## "):
            seccion, cab = linea[3:].strip(), None
            continue
        if not linea.startswith("|") or seccion is None:
            cab = None if not linea.startswith("|") else cab
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if cab is None:
            cab = [limpiar(c) for c in celdas]
            continue
        if set("".join(celdas)) <= set("-: "):
            continue
        out.setdefault(seccion, []).append(dict(zip(cab, celdas)))
    return out


def fecha_texto(t):
    """'Lun 26-10-2026, 12:00' -> ISO con hora de Chile (la primera fecha de la celda)."""
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})(?:,?\s*(\d{1,2}):(\d{2}))?", t or "")
    if not m:
        return None
    d, mo, y, h, mi = m.groups()
    dt = datetime(int(y), int(mo), int(d), int(h or 23), int(mi or 59), tzinfo=CHILE)
    return dt.isoformat()


def monto_texto(t):
    m = re.search(r"\$\s?([\d.]+)", t or "")
    return int(m.group(1).replace(".", "")) if m else None


def estado_corto(t):
    t = limpiar(t)
    return re.split(r"[.:(]", t, maxsplit=1)[0].strip() or t


def ca3(t):
    m = re.search(r"CA3:\s*(\d+)", t or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- APIs

def detalle_ca(codigo, ticket):
    url = f"{ca.BASE}{ca.RUTAS[0]}/{urllib.parse.quote(codigo)}"
    req = urllib.request.Request(url, headers={"ticket": ticket, "Accept": "application/json"})
    for intento in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return (json.loads(r.read().decode("utf-8")) or {}).get("payload") or {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento == 0:
                time.sleep(10)  # límite por segundo; la cuota diaria también responde 429
                continue
            return None
        except Exception:
            return None
        finally:
            time.sleep(1.2)
    return None


def region_v1(texto):
    t = (texto or "").replace("Región", "").strip()
    if re.match(r"de los ", t, flags=re.I):
        return "Los " + t[7:].strip().capitalize()  # Los Lagos, Los Ríos
    t = re.sub(r"^(de la |del |de )", "", t, flags=re.I).strip()
    if "Metropolitana" in t:
        return "Metropolitana"
    if "Magallanes" in t:
        return "Magallanes"
    if "Libertador" in t:
        return "O'Higgins"
    if "Aysén" in t or "Aisén" in t:
        return "Aysén"
    return t[:1].upper() + t[1:] if t else "—"


def rubro_de(det, perfil):
    codigos = ca.codigos_productos(det or {})
    if not codigos:
        return "—"
    hall = ca.rubros_coincidentes(codigos, perfil.get("rubros", []))
    if any(r.get("inscrito", True) for r in hall):
        return "Inscrito"
    if hall:
        return f"Sugerido sin inscribir ({hall[0]['codigo']})"
    return "No inscrito (" + ", ".join(sorted(codigos))[:40] + ")"


# ---------------------------------------------------------------- armado

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sin-red", action="store_true", help="no consulta las APIs")
    ap.add_argument("--salida", default=str(DIR_TABLERO / "datos"))
    args = ap.parse_args()

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    perfil = json.loads((AQUI / "perfil_juncos.json").read_text(encoding="utf-8"))
    secciones = tablas(SEGUIMIENTO.read_text(encoding="utf-8"))
    ticket = None if args.sin_red else mp.cargar_ticket()
    ahora = datetime.now(CHILE)
    fallas = []

    # Compras Ágiles: una fila por código (una celda puede traer varios)
    filas_ca = []
    for f in secciones.get("Compras Ágiles en curso", []):
        codigos = COD.findall(limpiar(f.get("Código", "")))
        for cod in codigos:
            det = detalle_ca(cod, ticket) if ticket else None
            if ticket and det is None:
                det = detalle_ca(cod, ticket)  # segundo intento: la API da 504 seguido
            if ticket and not det:
                fallas.append(cod)
            det = det or {}
            pres = det.get("presupuesto") or {}
            inst = det.get("institucion") or {}
            monto = pres.get("monto_disponible_clp") or monto_texto(f.get("Monto disponible"))
            cierre = (det.get("fechas") or {}).get("fecha_cierre")
            cierre = (cierre.replace(" ", "T") + ":00-03:00") if cierre else fecha_texto(f.get("Cierre"))
            region = REGIONES.get(inst.get("region")) or ("Coquimbo" if "Coquimbo" in f.get("Organismo", "") else "—")
            estado = estado_corto(f.get("Estado", ""))
            filas_ca.append({
                "codigo": cod,
                "nombre": limpiar(f.get("Nombre", "")),
                "organismo": limpiar(f.get("Organismo", "")),
                "region": region,
                "en_region_coquimbo": region == "Coquimbo",
                "monto_clp": monto,
                "neto_max_clp": round(monto / 1.19) if monto else None,
                "cierre": cierre,
                "estado_api": (det.get("estado") or {}).get("codigo") or "sin datos",
                "llamado": (det.get("convocatoria") or {}).get("descripcion") or "—",
                "ofertas_api_hoy": (det.get("resumen") or {}).get("total_ofertas_recibidas"),
                "ca3": ca3(f.get("Estado")),
                "rubro": rubro_de(det, perfil) if det else "—",
                "estado_juncos": estado,
                "prioridad": None,
                "proximo_paso": limpiar(f.get("Próximo paso", "")),
            })

    # Prioridad: entre las abiertas que conviene cotizar (CA3 >= 7, o lista para enviar),
    # por fecha de cierre; después las demás abiertas. Las cerradas y descartadas no llevan.
    def abierta(r):
        return r["cierre"] and datetime.fromisoformat(r["cierre"]) > ahora and \
            not re.search(r"Descartad|Cerrad|Vencid", r["estado_juncos"])
    conviene = [r for r in filas_ca if abierta(r) and ((r["ca3"] or 0) >= 7 or re.search(r"Lista|Cotizad", r["estado_juncos"]))]
    resto = [r for r in filas_ca if abierta(r) and r not in conviene]
    for i, r in enumerate(sorted(conviene, key=lambda r: r["cierre"]) + sorted(resto, key=lambda r: r["cierre"]), 1):
        r["prioridad"] = i
    filas_ca.sort(key=lambda r: (r["prioridad"] is None, r["prioridad"] or 0, r["cierre"] or ""))

    # Licitaciones
    filas_lic = []
    for f in secciones.get("Licitaciones en curso", []):
        for cod in COD.findall(limpiar(f.get("Código", ""))):
            lic = None
            if ticket:
                try:
                    lic = mp.licitacion(cod)
                except Exception:
                    lic = None
                if not lic:
                    fallas.append(cod)
            lic = lic or {}
            fechas = lic.get("Fechas") or {}
            comp = lic.get("Comprador") or {}
            monto = lic.get("MontoEstimado") if lic.get("VisibilidadMonto") == 1 else None
            cierre = (fechas.get("FechaCierre") + "-03:00") if fechas.get("FechaCierre") else fecha_texto(f.get("Cierre"))
            region = region_v1(comp.get("RegionUnidad")) if comp else ("Coquimbo" if "Coquimbo" in f.get("Organismo", "") else "—")
            filas_lic.append({
                "codigo": cod,
                "nombre": limpiar(f.get("Nombre", "")),
                "organismo": limpiar(f.get("Organismo", "")),
                "region": region,
                "en_region_coquimbo": region == "Coquimbo",
                "tipo": cod.split("-")[-1][:2],
                "monto_clp": int(monto) if monto else monto_texto(f.get("Monto")),
                "cierre": cierre,
                "estado_api": lic.get("Estado") or "sin datos",
                "estado_juncos": estado_corto(f.get("Estado", "")),
                "proximo_paso": limpiar(f.get("Próximo paso", "")),
                "ficha": f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={cod}",
            })
    filas_lic.sort(key=lambda r: r["cierre"] or "")

    # Tareas
    filas_t = []
    for i, f in enumerate(secciones.get("Tareas pendientes de la empresa", []), 1):
        est = limpiar(f.get("Estado", ""))
        if est.startswith("Hecho") and not re.search(r"Falta|Recuperar|regenerar", est):
            estado = "Hecho"
        elif est.startswith("Revisar"):
            estado = "Revisar"
        elif est.startswith("Pendiente"):
            estado = "Pendiente"
        else:
            estado = "En curso"  # hecho a medias: el texto dice qué falta
        filas_t.append({"n": i, "tarea": limpiar(f.get("Tarea", "")), "plazo": limpiar(f.get("Plazo", "")), "estado": estado})

    empresa = json.loads((DIR_TABLERO / "empresa.json").read_text(encoding="utf-8"))
    consulta = [{
        "consultado": ahora.replace(microsecond=0).isoformat(),
        "detalle": ("Estado desde seguimiento.md de la skill /juncos. " +
                    ("Sin consulta a Mercado Público (--sin-red)." if not ticket else
                     "Cierres, montos, ofertas y región desde la API Compra Ágil v2 y la API de licitaciones v1 de Mercado Público.") +
                    (f" Sin respuesta de la API para: {', '.join(fallas)}; esas filas usan los datos de seguimiento.md." if fallas else "")),
    }]

    archivos = {"compras_agiles": filas_ca, "licitaciones": filas_lic, "tareas": filas_t,
                "empresa": empresa, "consulta": consulta}
    for nombre, filas in archivos.items():
        (salida / f"{nombre}.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (salida / "_pagina.json").write_text(
        json.dumps({"text": (DIR_TABLERO / "index.html").read_text(encoding="utf-8")}, ensure_ascii=False), encoding="utf-8")

    print(f"Consulta: {ahora:%d-%m-%Y %H:%M} (hora de Chile)")
    print(f"Compras Ágiles: {len(filas_ca)} · Licitaciones: {len(filas_lic)} · Tareas: {len(filas_t)}")
    if fallas:
        print("Sin respuesta de la API (se usó seguimiento.md): " + ", ".join(fallas))
    print(f"Archivos en {salida}")


if __name__ == "__main__":
    main()
