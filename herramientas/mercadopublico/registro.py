#!/usr/bin/env python3
"""Registro de procesos de JUNCOS y métricas de mejora continua.

Guarda en `registro/procesos.json` una fila por Compra Ágil o licitación que pasó por /juncos:
de dónde salió (términos de búsqueda), qué recomendó Claude, qué decidió Nicolás y cómo
terminó (ganador, precio, ofertas). Con eso calcula cada semana qué está funcionando y qué
conviene ajustar. Reemplaza al ciclo que se probó en n8n (06-11-2026).

Uso:
    python3 registro.py agregar --ranking ranking.json      # salida --json de compras_agiles.py
    python3 registro.py sincronizar                         # trae los códigos de seguimiento.md
    python3 registro.py marcar CODIGO --decision cotizar --motivo "..." [--recomendacion cotizar]
                                      [--precio-ofertado 750000] [--nota "..."]
    python3 registro.py resultados                          # completa resultados al cierre (API)
    python3 registro.py metricas --md informe.md --json metricas.json

Valores de `decision`: cotizar, cotizada, descartar (o vacío). `recomendacion` (de Claude):
cotizar, alternativa o descartar. Los motivos se escriben con frases fijas (ver
proceso-postulacion.md, «Mejora continua en Claude»).
"""
import argparse
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import compras_agiles as ca  # noqa: E402
import mercadopublico as mp  # noqa: E402

RAIZ = AQUI.parents[1]
REGISTRO = AQUI / "registro" / "procesos.json"
SEGUIMIENTO = RAIZ / ".claude/skills/juncos/seguimiento.md"
CHILE = ca.CHILE
RUT_JUNCOS = "78.390.884-0"
FINALES = {"ganada", "adjudicada a otro", "adjudicada (ganador no visible)", "desierta",
           "cancelada", "revocada"}
CAMPOS = ["codigo", "tipo", "nombre", "organismo", "region", "monto_clp", "neto_max_clp", "cierre",
          "linea", "puntaje", "rubro", "terminos", "detectada_el", "version", "recomendacion",
          "motivo_recomendacion", "decision", "motivo", "precio_ofertado", "estado_final",
          "ofertas_final", "juncos_cotizo", "ganador", "precio_ganador", "precio_min",
          "ratio_ganador", "resultado_revisado_el", "notas"]
COD = re.compile(r"\b\d{3,7}-\d{1,4}-(?:COT|LE|LP|L1|LR|LQ|E2|CO|B2|H2|I2)\d{2}\b")


def ahora():
    return datetime.now(CHILE)


def perfil():
    return json.loads((AQUI / "perfil_juncos.json").read_text(encoding="utf-8"))


def cargar():
    if REGISTRO.exists():
        return {r["codigo"]: r for r in json.loads(REGISTRO.read_text(encoding="utf-8"))}
    return {}


def guardar(reg):
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    filas = sorted(reg.values(), key=lambda r: (r.get("detectada_el") or "", r["codigo"]), reverse=True)
    filas = [{k: r.get(k, "") for k in CAMPOS} for r in filas]
    REGISTRO.write_text(json.dumps(filas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def nueva(codigo):
    r = {k: "" for k in CAMPOS}
    r["codigo"] = codigo
    r["tipo"] = "compra ágil" if codigo.endswith(("COT26", "COT27")) or "-COT" in codigo else "licitación"
    return r


def iso(texto):
    """Fechas de la API o de compras_agiles.py a ISO con hora de Chile."""
    t = (texto or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(t[:19] if "T" in t else t[:16], fmt).replace(tzinfo=CHILE).isoformat()
        except ValueError:
            continue
    m = re.search(r"(\d{2})-(\d{2})-(\d{4})(?:,?\s*(\d{1,2}):(\d{2}))?", t)
    if m:
        d, mo, y, h, mi = m.groups()
        return datetime(int(y), int(mo), int(d), int(h or 23), int(mi or 59), tzinfo=CHILE).isoformat()
    return ""


def num(v):
    """Número desde la API, el registro o un texto con formato chileno ($1.000.000 o 0,95)."""
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v or "").strip().replace("$", "").replace(" ", "")
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return float(t)
    try:
        return float(t.replace(".", "").replace(",", ".")) if t else 0.0
    except ValueError:
        return 0.0


def fecha_d(texto):
    try:
        return datetime.strptime(texto, "%d-%m-%Y").replace(tzinfo=CHILE)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- comandos

def cmd_agregar(args):
    reg, p = cargar(), perfil()
    filas = json.loads(Path(args.ranking).read_text(encoding="utf-8"))
    hoy = args.fecha or ahora().strftime("%d-%m-%Y")
    n_nuevas = 0
    for f in filas:
        r = reg.get(f["codigo"])
        if not r:
            r = nueva(f["codigo"])
            r["detectada_el"] = hoy
            r["version"] = p.get("automatizacion", {}).get("version", "")
            n_nuevas += 1
        for k_dest, k_orig in [("nombre", "nombre"), ("organismo", "organismo"), ("region", "region"),
                               ("monto_clp", "monto_clp"), ("neto_max_clp", "neto_max_clp"),
                               ("linea", "linea"), ("puntaje", "puntaje"), ("rubro", "rubros")]:
            if f.get(k_orig) not in (None, ""):
                r[k_dest] = f[k_orig]
        r["cierre"] = iso(f.get("cierre")) or r.get("cierre", "")
        terms = set(filter(None, (r.get("terminos") or "").split(", "))) | \
            set(filter(None, (f.get("terminos") or "").split(", ")))
        r["terminos"] = ", ".join(sorted(terms))
        reg[f["codigo"]] = r
    guardar(reg)
    print(f"{len(filas)} filas leídas, {n_nuevas} nuevas en el registro ({len(reg)} en total).")


def cmd_sincronizar(args):
    """Trae al registro los códigos de seguimiento.md (en curso e historial)."""
    reg = cargar()
    texto = SEGUIMIENTO.read_text(encoding="utf-8")
    seccion, n = None, 0
    for linea in texto.splitlines():
        if linea.startswith("## "):
            seccion = linea[3:].strip()
            continue
        if not linea.startswith("|") or seccion not in (
                "Licitaciones en curso", "Compras Ágiles en curso", "Historial de resultados"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        codigos = COD.findall(celdas[0] if seccion != "Historial de resultados" else
                              (celdas[1] if len(celdas) > 1 else ""))
        estado = " ".join(celdas).lower()
        for cod in codigos:
            if cod in reg:
                continue
            r = nueva(cod)
            r["detectada_el"] = ""
            m = re.search(r"CA3:\s*(\d+)", linea)
            if m:
                r["recomendacion"] = "cotizar" if int(m.group(1)) >= 7 else "alternativa"
            if re.search(r"postulando|cotizada|enviada|lista para enviar", estado):
                r["decision"] = "cotizar"
            elif "descartada" in estado:
                r["decision"] = "descartar"
            r["notas"] = f"Traída de seguimiento.md ({seccion}) el {ahora():%d-%m-%Y}"
            reg[cod] = r
            n += 1
    guardar(reg)
    print(f"{n} códigos nuevos desde seguimiento.md ({len(reg)} en total).")


def cmd_marcar(args):
    reg = cargar()
    if args.codigo in reg:
        r = reg[args.codigo]
    else:  # un proceso que no venía del buscador: se registra hoy
        r = nueva(args.codigo)
        r["detectada_el"] = ahora().strftime("%d-%m-%Y")
    for campo, valor in [("decision", args.decision), ("motivo", args.motivo),
                         ("recomendacion", args.recomendacion),
                         ("motivo_recomendacion", args.motivo_recomendacion),
                         ("precio_ofertado", args.precio_ofertado), ("notas", args.nota)]:
        if valor is not None:
            r[campo] = valor
    reg[args.codigo] = r
    guardar(reg)
    print(f"{args.codigo}: " + ", ".join(f"{k}={r[k]}" for k in ("recomendacion", "decision", "motivo") if r.get(k)))


def detalle_ca(codigo, ticket):
    url = f"{ca.BASE}{ca.RUTAS[0]}/{urllib.parse.quote(codigo)}"
    req = urllib.request.Request(url, headers={"ticket": ticket, "Accept": "application/json"})
    for intento in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return (json.loads(resp.read().decode("utf-8")) or {}).get("payload") or {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento == 0:
                time.sleep(10)
                continue
            return None
        except Exception:
            return None
        finally:
            time.sleep(1.2)


def resultado_ca(r, d):
    est = (d.get("estado") or {}).get("codigo", "")
    provs = d.get("proveedores_cotizando") or []
    sel = next((q for q in provs if q.get("proveedor_seleccionado")), None)
    montos = [num(q.get("monto_total")) for q in provs if num(q.get("monto_total")) > 0]
    if est == "proveedor_seleccionado":
        r["estado_final"] = ("adjudicada (ganador no visible)" if not sel else
                             "ganada" if sel.get("rut_proveedor") == RUT_JUNCOS else "adjudicada a otro")
    else:
        r["estado_final"] = {"publicada": "abierta"}.get(est, est)
    r["ofertas_final"] = (d.get("resumen") or {}).get("total_ofertas_recibidas", "")
    propia = next((q for q in provs if q.get("rut_proveedor") == RUT_JUNCOS), None)
    if propia:
        r["juncos_cotizo"] = "sí"
        r["precio_ofertado"] = r.get("precio_ofertado") or int(num(propia.get("monto_total")))
        orden = sorted(montos)
        lugar = orden.index(num(propia.get("monto_total"))) + 1 if num(propia.get("monto_total")) in orden else ""
        nota = f"JUNCOS quedó {lugar}.º en precio de {len(orden)} visibles."
        if nota not in (r.get("notas") or ""):
            r["notas"] = ". ".join(x for x in [(r.get("notas") or "").rstrip("."), nota.rstrip(".")] if x) + "."
    elif provs and not r.get("juncos_cotizo"):
        r["juncos_cotizo"] = "no visible"
    disp = num((d.get("presupuesto") or {}).get("monto_disponible_clp")) or num(r.get("monto_clp"))
    if sel:
        r["ganador"] = sel.get("razon_social", "")
        r["precio_ganador"] = int(num(sel.get("monto_total")))
        r["ratio_ganador"] = round(num(sel.get("monto_total")) / disp, 2) if disp else ""
    r["precio_min"] = int(min(montos)) if montos else r.get("precio_min", "")
    # completa lo que falte de la ficha
    inst = d.get("institucion") or {}
    r["nombre"] = r.get("nombre") or d.get("nombre", "")
    r["organismo"] = r.get("organismo") or inst.get("organismo_comprador", "")
    r["region"] = r.get("region") or (inst.get("nombre_region") or "").replace("Región de ", "").replace("Región del ", "").strip()
    if not r.get("monto_clp") and disp:
        r["monto_clp"], r["neto_max_clp"] = int(disp), round(disp / 1.19)
    r["cierre"] = r.get("cierre") or iso((d.get("fechas") or {}).get("fecha_cierre"))


def resultado_lic(r, lic):
    estado = (lic.get("Estado") or "").lower()
    items = ((lic.get("Items") or {}).get("Listado")) or []
    adj = [it.get("Adjudicacion") for it in items if it.get("Adjudicacion")]
    if "adjudicada" in estado:
        ruts = {a.get("RutProveedor") for a in adj}
        total = sum(num(a.get("MontoUnitario")) * num(a.get("Cantidad") or 1) for a in adj)
        r["estado_final"] = "ganada" if RUT_JUNCOS in ruts else ("adjudicada a otro" if adj else "adjudicada (ganador no visible)")
        r["ganador"] = "; ".join(sorted({a.get("NombreProveedor", "") for a in adj}))
        if total:
            r["precio_ganador"] = int(total)
            if num(r.get("monto_clp")):
                r["ratio_ganador"] = round(total / num(r["monto_clp"]), 2)
    elif "desierta" in estado:
        r["estado_final"] = "desierta"
    elif "revocada" in estado or "suspendida" in estado:
        r["estado_final"] = "revocada"
    else:
        r["estado_final"] = {"publicada": "abierta"}.get(estado, estado)
    r["ofertas_final"] = (lic.get("Adjudicacion") or {}).get("NumeroOferentes", r.get("ofertas_final", ""))
    comp = lic.get("Comprador") or {}
    r["nombre"] = r.get("nombre") or lic.get("Nombre", "")
    r["organismo"] = r.get("organismo") or comp.get("NombreOrganismo", "")
    if not r.get("monto_clp") and lic.get("VisibilidadMonto") == 1 and lic.get("MontoEstimado"):
        r["monto_clp"] = int(lic["MontoEstimado"])
    r["cierre"] = r.get("cierre") or iso(((lic.get("Fechas") or {}).get("FechaCierre") or ""))


def cmd_resultados(args):
    reg, p = cargar(), perfil()
    espera = p.get("automatizacion", {}).get("mejora", {}).get("dias_espera_resultado", 20)
    ticket = mp.cargar_ticket()
    t0, revisadas = ahora(), 0
    for r in sorted(reg.values(), key=lambda r: r.get("cierre") or ""):
        if args.codigo and r["codigo"] not in args.codigo:
            continue
        if (r.get("estado_final") in FINALES and not args.codigo) or revisadas >= args.max:
            continue
        cierre = datetime.fromisoformat(r["cierre"]) if r.get("cierre") else None
        if cierre and cierre > t0 - timedelta(hours=2):
            continue  # todavía abierta
        limite = espera if r["tipo"] == "compra ágil" else 120  # una licitación tarda más en adjudicarse
        if cierre and (t0 - cierre).days > limite:
            continue
        if r["tipo"] == "compra ágil":
            d = detalle_ca(r["codigo"], ticket)
            if d:
                resultado_ca(r, d)
        else:
            try:
                lic = mp.licitacion(r["codigo"])
            except Exception:
                lic = None
            if lic:
                resultado_lic(r, lic)
        r["resultado_revisado_el"] = t0.strftime("%d-%m-%Y %H:%M")
        revisadas += 1
        print(f"  {r['codigo']}: {r.get('estado_final') or 'sin respuesta'}", flush=True)
    guardar(reg)
    print(f"{revisadas} revisadas.")


# ---------------------------------------------------------------- métricas

def norm(t):
    return ca.normalizar(t or "")


def es_cotizada(r):
    return bool(re.search(r"cotiz", norm(r.get("decision")))) or r.get("juncos_cotizo") == "sí"


def es_descartada(r):
    return norm(r.get("decision")).startswith("descart")


def mediana(xs):
    return round(statistics.median(xs), 2) if xs else None


def metricas():
    reg, p = cargar(), perfil()
    U = p.get("automatizacion", {}).get("mejora", {})
    ventana = U.get("ventana_dias", 30)
    t0 = ahora()
    filas = list(reg.values())

    def dentro(r, dias):
        d = fecha_d(r.get("detectada_el"))
        return d is not None and d >= t0 - timedelta(days=dias)

    sem = [r for r in filas if dentro(r, 7)]
    ven = [r for r in filas if dentro(r, ventana)]
    con_dec = [r for r in sem if norm(r.get("decision"))]
    cot = [r for r in sem if es_cotizada(r)]
    des = [r for r in sem if es_descartada(r)]

    # ¿Coincide la recomendación de Claude con la decisión de Nicolás? (aprendizaje propio)
    pares = [r for r in filas if norm(r.get("recomendacion")) and norm(r.get("decision"))]
    acuerdo = [r for r in pares if (norm(r["recomendacion"]) == "cotizar") == es_cotizada(r)]
    concordancia = round(len(acuerdo) / len(pares), 2) if pares else None

    motivos = {}
    for r in ven:
        if es_descartada(r):
            m = norm(r.get("motivo")) or "sin motivo"
            motivos[m] = motivos.get(m, 0) + 1
    terminos = {t: {"afines": 0, "cotizadas": 0} for t in p.get("automatizacion", {}).get("terminos", [])}
    ven_t = [r for r in ven if r.get("terminos")]  # solo lo que entró por el buscador con registro de términos
    for r in ven_t:
        for t in filter(None, (r.get("terminos") or "").split(", ")):
            terminos.setdefault(t, {"afines": 0, "cotizadas": 0})
            terminos[t]["afines"] += 1
            terminos[t]["cotizadas"] += es_cotizada(r)
    lineas = {}
    for r in filas:
        if num(r.get("ratio_ganador")) > 0:
            clave = f"{r.get('tipo') or 'compra ágil'} · {r.get('linea') or 'consultoría'}"
            lineas.setdefault(clave, {"ratios": [], "ofertas": []})
            lineas[clave]["ratios"].append(num(r["ratio_ganador"]))
            if num(r.get("ofertas_final")):
                lineas[clave]["ofertas"].append(num(r["ofertas_final"]))
    ganadas = [r for r in filas if r.get("estado_final") == "ganada"]
    cotizadas_tot = [r for r in filas if es_cotizada(r)]
    perdidas = [r for r in cotizadas_tot if r.get("estado_final") in ("adjudicada a otro",)]

    sug = []
    if sem and len(con_dec) / len(sem) < 0.5:
        sug.append(f"Solo {len(con_dec)} de {len(sem)} procesos detectados esta semana tienen decisión. "
                   "Sin decisiones el ciclo no aprende: conviene marcarlas al revisar el informe diario.")
    for t, v in terminos.items():
        if v["afines"] >= U.get("min_detecciones_termino", 8) and v["cotizadas"] == 0:
            sug.append(f"El término «{t}» trajo {v['afines']} procesos afines en {ventana} días y ninguno se cotizó: "
                       "evaluar quitarlo de automatizacion.terminos o afinarlo.")
        if len(ven_t) >= 20 and v["afines"] == 0 and t != "coquimbo":
            sug.append(f"El término «{t}» no trajo ningún proceso afín en {ventana} días: evaluar reemplazarlo.")
    for m, n in motivos.items():
        if n >= U.get("min_repeticiones_motivo", 3) and m != "sin motivo":
            sug.append(f"«{m}» se repitió {n} veces como motivo de descarte: evaluar una exclusión o regla en el perfil.")
    for clave, v in lineas.items():
        if len(v["ratios"]) >= U.get("min_resultados_precio", 3):
            sug.append(f"En {clave}, el ganador ofertó en mediana el {round(mediana(v['ratios']) * 100)}% del monto "
                       f"disponible ({len(v['ratios'])} resultados, mediana de {mediana(v['ofertas']) or '—'} ofertas): "
                       "usarlo como referencia en CA4.")
    if concordancia is not None and len(pares) >= 5 and concordancia < 0.6:
        sug.append(f"La recomendación de Claude coincidió con la decisión de Nicolás solo en {round(concordancia * 100)}% "
                   f"de {len(pares)} casos: revisar los criterios de CA2 y CA3 con los motivos de desacuerdo.")
    if len(cotizadas_tot) >= 5 and not ganadas:
        sug.append(f"JUNCOS lleva {len(cotizadas_tot)} procesos cotizados sin ganar: comparar precio_ofertado con "
                   "precio_ganador y revisar la descripción de las ofertas.")

    return {
        "fecha": t0.strftime("%d-%m-%Y %H:%M"),
        "version": p.get("automatizacion", {}).get("version", ""),
        "ventana_dias": ventana,
        "semana": {"detectados": len(sem), "con_decision": len(con_dec), "cotizados": len(cot),
                   "descartados": len(des), "sin_decision": len(sem) - len(con_dec),
                   "precision": round(len(cot) / len(con_dec), 2) if con_dec else None},
        "totales": {"procesos": len(filas), "cotizados": len(cotizadas_tot), "ganados": len(ganadas),
                    "perdidos": len(perdidas),
                    "con_resultado": sum(1 for r in filas if r.get("estado_final") in FINALES),
                    "concordancia": concordancia, "pares_concordancia": len(pares)},
        "terminos": [{"termino": t, **v} for t, v in sorted(terminos.items(), key=lambda x: -x[1]["afines"])],
        "motivos": [{"motivo": m, "veces": n} for m, n in sorted(motivos.items(), key=lambda x: -x[1])],
        "precios": [{"grupo": k, "resultados": len(v["ratios"]), "mediana_ratio": mediana(v["ratios"]),
                     "mediana_ofertas": mediana(v["ofertas"])} for k, v in lineas.items()],
        "sugerencias": sug,
    }


def cmd_metricas(args):
    m = metricas()
    if args.json:
        Path(args.json).write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    s, t = m["semana"], m["totales"]
    pct = lambda v: "—" if v is None else f"{round(v * 100)}%"  # noqa: E731
    md = [f"# Métricas de mejora JUNCOS · {m['fecha']}", "",
          f"Revisión automática v{m['version']}. Fuente: `herramientas/mercadopublico/registro/procesos.json`.", "",
          "| Últimos 7 días | |", "|---|---|",
          f"| Detectados | {s['detectados']} |", f"| Con decisión | {s['con_decision']} |",
          f"| Cotizados | {s['cotizados']} |", f"| Descartados | {s['descartados']} |",
          f"| Precisión (cotizados / con decisión) | {pct(s['precision'])} |", "",
          "| Historial | |", "|---|---|",
          f"| Procesos en el registro | {t['procesos']} |", f"| Con resultado final | {t['con_resultado']} |",
          f"| Cotizados / ganados / perdidos | {t['cotizados']} / {t['ganados']} / {t['perdidos']} |",
          f"| Coincidencia Claude–Nicolás | {pct(t['concordancia'])} ({t['pares_concordancia']} casos) |", "",
          f"## Sugerencias ({len(m['sugerencias'])})", ""]
    md += [f"{i}. {x}" for i, x in enumerate(m["sugerencias"], 1)] or ["Ninguna."]
    md += ["", f"## Términos de búsqueda (últimos {m['ventana_dias']} días)", "", "| Término | Afines | Cotizados |", "|---|---|---|"]
    md += [f"| {x['termino']} | {x['afines']} | {x['cotizadas']} |" for x in m["terminos"]]
    md += ["", "## Precios ganadores", "", "| Grupo | Resultados | Mediana precio / monto | Mediana de ofertas |", "|---|---|---|---|"]
    md += [f"| {x['grupo']} | {x['resultados']} | {pct(x['mediana_ratio'])} | {x['mediana_ofertas'] or '—'} |" for x in m["precios"]] or ["| — | 0 | — | — |"]
    texto = "\n".join(md) + "\n"
    if args.md:
        Path(args.md).write_text(texto, encoding="utf-8")
        print(f"Informe en {args.md}")
    else:
        print(texto)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("agregar")
    a.add_argument("--ranking", required=True)
    a.add_argument("--fecha", help="dd-mm-aaaa (por defecto hoy)")
    sub.add_parser("sincronizar")
    m = sub.add_parser("marcar")
    m.add_argument("codigo")
    m.add_argument("--decision")
    m.add_argument("--motivo")
    m.add_argument("--recomendacion")
    m.add_argument("--motivo-recomendacion")
    m.add_argument("--precio-ofertado")
    m.add_argument("--nota")
    r = sub.add_parser("resultados")
    r.add_argument("--max", type=int, default=30)
    r.add_argument("--codigo", nargs="*", help="revisar solo estos códigos (aunque ya tengan resultado)")
    me = sub.add_parser("metricas")
    me.add_argument("--md")
    me.add_argument("--json")
    args = ap.parse_args()
    {"agregar": cmd_agregar, "sincronizar": cmd_sincronizar, "marcar": cmd_marcar,
     "resultados": cmd_resultados, "metricas": cmd_metricas}[args.cmd](args)


if __name__ == "__main__":
    main()
