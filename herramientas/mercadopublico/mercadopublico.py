#!/usr/bin/env python3
"""Cliente de la API de Mercado Público (ChileCompra).

Consulta licitaciones y órdenes de compra. Por defecto apunta a la
I. Municipalidad de Coquimbo (código de organismo 87901).

El ticket se lee de la variable de entorno MERCADOPUBLICO_TICKET o de un
archivo .env junto a este script (que no se sube a git).

Ejemplos:
    python3 mercadopublico.py licitaciones --estado activas
    python3 mercadopublico.py licitaciones --estado activas --detalle --md reporte.md
    python3 mercadopublico.py licitacion 2446-271-LR26
    python3 mercadopublico.py ordenes --desde 01-10-2026 --hasta 15-10-2026 --detalle
    python3 mercadopublico.py orden 2448-1195-SE26
    python3 mercadopublico.py organismos coquimbo
    python3 mercadopublico.py proveedor 76.123.456-7
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = "https://api.mercadopublico.cl/servicios/v1/publico"
MUNI_COQUIMBO = "87901"
PAUSA = 1.0  # la API rechaza peticiones simultáneas; vamos de a una

ESTADOS_LICITACION = {
    5: "Publicada", 6: "Cerrada", 7: "Desierta", 8: "Adjudicada",
    18: "Revocada", 19: "Suspendida",
}
ESTADOS_OC = {
    4: "Enviada a proveedor", 5: "En proceso", 6: "Aceptada", 9: "Cancelada",
    12: "Recepción conforme", 13: "Pendiente de recepcionar",
    14: "Recepcionada parcialmente", 15: "Recepción conforme incompleta",
}
TIPOS_LICITACION = {
    "L1": "Menor a 100 UTM", "LE": "100 a 1.000 UTM", "LP": "1.000 a 2.000 UTM",
    "LQ": "2.000 a 5.000 UTM", "LR": "Sobre 5.000 UTM", "E2": "Privada < 100 UTM",
    "CO": "Privada 100-1.000 UTM", "B2": "Privada 1.000-2.000 UTM",
    "H2": "Privada 2.000-5.000 UTM", "I2": "Privada > 5.000 UTM",
}


# ---------------------------------------------------------------- ticket

def cargar_ticket():
    ticket = os.environ.get("MERCADOPUBLICO_TICKET", "").strip()
    if ticket:
        return ticket
    env = Path(__file__).with_name(".env")
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            clave, _, valor = linea.partition("=")
            if clave.strip() == "MERCADOPUBLICO_TICKET":
                return valor.strip().strip('"').strip("'")
    sys.exit("Falta el ticket: define MERCADOPUBLICO_TICKET o crea "
             f"{env} con MERCADOPUBLICO_TICKET=...")


# ---------------------------------------------------------------- HTTP

class ErrorAPI(Exception):
    pass


def pedir(ruta, **params):
    """GET a la API con reintentos ante peticiones simultáneas o fallas de red."""
    params["ticket"] = cargar_ticket()
    url = f"{BASE}/{ruta}?{urllib.parse.urlencode(params)}"
    espera = 2
    for intento in range(5):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                datos = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode("utf-8", "replace")
            try:
                datos = json.loads(cuerpo)
            except ValueError:
                datos = {"Codigo": e.code, "Mensaje": cuerpo[:200]}
        except (urllib.error.URLError, TimeoutError) as e:
            datos = {"Codigo": "red", "Mensaje": str(e)}

        codigo = datos.get("Codigo")
        if codigo is None:
            time.sleep(PAUSA)
            return datos
        # 10500 = peticiones simultáneas; "red" = falla transitoria
        if str(codigo) in ("10500", "red", "500", "503") and intento < 4:
            time.sleep(espera)
            espera *= 2
            continue
        raise ErrorAPI(f"{codigo}: {datos.get('Mensaje')}")
    raise ErrorAPI("Sin respuesta tras varios intentos")


def fecha_api(texto):
    """'19-10-2026' o '2026-10-19' -> '19102026'."""
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d%m%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f"Fecha no válida: {texto}")


def dias(desde, hasta):
    d = desde
    while d <= hasta:
        yield d
        d += timedelta(days=1)


# ---------------------------------------------------------------- consultas

def licitaciones(organismo, estado=None, fecha=None):
    params = {"CodigoOrganismo": organismo} if organismo else {}
    if fecha:
        params["fecha"] = fecha.strftime("%d%m%Y")
    if estado:
        params["estado"] = estado
    if not fecha and not estado:
        params["estado"] = "activas"
    return pedir("licitaciones.json", **params).get("Listado", [])


def licitacion(codigo):
    lista = pedir("licitaciones.json", codigo=codigo).get("Listado", [])
    return lista[0] if lista else None


def ordenes(organismo, fecha, estado=None):
    params = {"fecha": fecha.strftime("%d%m%Y")}
    if organismo:
        params["CodigoOrganismo"] = organismo
    if estado:
        params["estado"] = estado
    return pedir("ordenesdecompra.json", **params).get("Listado", [])


def orden(codigo):
    lista = pedir("ordenesdecompra.json", codigo=codigo).get("Listado", [])
    return lista[0] if lista else None


def organismos(texto):
    lista = pedir("Empresas/BuscarComprador").get("listaEmpresas", [])
    t = texto.upper()
    return [e for e in lista if t in e["NombreEmpresa"].upper()]


def proveedor(rut):
    return pedir("Empresas/BuscarProveedor", rutempresaproveedor=rut)


# ---------------------------------------------------------------- ficha web

FICHA_WEB = "https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={}"


def _html_a_texto(crudo):
    import html as _html
    import re
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", crudo)
    t = re.sub(r"<br\s*/?>|</(tr|p|div|h\d|li)>", "\n", t)
    t = _html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def _get_web(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def ficha_publica(codigo):
    """Texto de la ficha pública (bases resumidas, plazos, criterios, requisitos) y del foro.

    Los adjuntos (bases en PDF y anexos) no se bajan: el portal los protege
    con reCAPTCHA y hay que descargarlos a mano desde el navegador.
    """
    import re
    crudo = _get_web(FICHA_WEB.format(urllib.parse.quote(codigo)))
    texto = _html_a_texto(crudo)
    inicio = texto.find("Licitación ID:")
    texto = texto[inicio:] if inicio >= 0 else texto
    foro = ""
    m = re.search(r'href="(/Foros/Modules/FNormal/PopUps/PublicView\.aspx\?qs=[^"]+)"', crudo)
    if m:
        foro = _html_a_texto(_get_web("https://www.mercadopublico.cl" + m.group(1)))
        i = foro.find("Preguntas Licitación")
        foro = foro[i:] if i >= 0 else foro
    return texto, foro


# ---------------------------------------------------------------- filas

def fila_licitacion(l):
    fechas = l.get("Fechas") or {}
    comprador = l.get("Comprador") or {}
    estado = l.get("Estado") or ESTADOS_LICITACION.get(l.get("CodigoEstado"), "")
    adj = l.get("Adjudicacion") or {}
    return {
        "codigo": l.get("CodigoExterno"),
        "nombre": (l.get("Nombre") or "").strip(),
        "estado": estado,
        "tipo": l.get("Tipo", ""),
        "unidad": comprador.get("NombreUnidad", ""),
        "monto_estimado": l.get("MontoEstimado") if l.get("VisibilidadMonto") else None,
        "moneda": l.get("Moneda", ""),
        "financiamiento": l.get("FuenteFinanciamiento", ""),
        "publicacion": (fechas.get("FechaPublicacion") or "")[:10],
        "cierre": (fechas.get("FechaCierre") or l.get("FechaCierre") or "")[:16].replace("T", " "),
        "adjudicacion": (fechas.get("FechaAdjudicacion") or "")[:10],
        "acta_adjudicacion": adj.get("UrlActa", ""),
        "url": f"https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={l.get('CodigoExterno')}",
    }


def fila_orden(o):
    fechas = o.get("Fechas") or {}
    comprador = o.get("Comprador") or {}
    prov = o.get("Proveedor") or {}
    estado = o.get("Estado") or ESTADOS_OC.get(o.get("CodigoEstado"), "")
    return {
        "codigo": o.get("Codigo"),
        "nombre": (o.get("Nombre") or "").strip(),
        "estado": estado,
        "tipo": o.get("Tipo", ""),
        "licitacion": o.get("CodigoLicitacion", ""),
        "unidad": comprador.get("NombreUnidad", ""),
        "proveedor": prov.get("Nombre", ""),
        "rut_proveedor": prov.get("RutSucursal", ""),
        "total": o.get("Total"),
        "moneda": o.get("TipoMoneda", ""),
        "envio": (fechas.get("FechaEnvio") or fechas.get("FechaCreacion") or "")[:10],
    }


# ---------------------------------------------------------------- salida

def pesos(v, moneda="CLP"):
    if v in (None, ""):
        return ""
    cifra = f"{float(v):,.0f}".replace(",", ".")
    if moneda in ("", "CLP"):
        return "$" + cifra
    return f"{cifra} {'UF' if moneda == 'CLF' else moneda}"


def tabla_md(filas, columnas):
    def celda(v):
        return str(v if v is not None else "").replace("|", "/").replace("\n", " ")
    cab = "| " + " | ".join(titulo for _, titulo in columnas) + " |"
    sep = "|" + "|".join("---" for _ in columnas) + "|"
    cuerpo = ["| " + " | ".join(celda(f(r)) for f, _ in columnas) + " |" for r in filas]
    return "\n".join([cab, sep, *cuerpo])


COLS_LIC_CORTA = [
    (lambda r: f"[{r['codigo']}]({r['url']})", "Código"),
    (lambda r: r["nombre"], "Nombre"),
    (lambda r: r["estado"], "Estado"),
    (lambda r: r["cierre"], "Cierre"),
]
COLS_LIC = COLS_LIC_CORTA[:2] + [
    (lambda r: r["tipo"], "Tipo"),
    (lambda r: r["unidad"], "Unidad"),
    (lambda r: pesos(r["monto_estimado"], r["moneda"]), "Monto estimado"),
    (lambda r: r["financiamiento"], "Financiamiento"),
    (lambda r: r["cierre"], "Cierre"),
]
COLS_OC_CORTA = [
    (lambda r: r["codigo"], "Código"),
    (lambda r: r["nombre"], "Nombre"),
    (lambda r: r["estado"], "Estado"),
]
COLS_OC = COLS_OC_CORTA + [
    (lambda r: r["proveedor"], "Proveedor"),
    (lambda r: r["unidad"], "Unidad"),
    (lambda r: pesos(r["total"], r["moneda"]), "Total"),
    (lambda r: r["envio"], "Envío"),
]


def emitir(filas, args, columnas, titulo):
    if args.json:
        Path(args.json).write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON guardado en {args.json}", file=sys.stderr)
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            if filas:
                w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
                w.writeheader()
                w.writerows(filas)
        print(f"CSV guardado en {args.csv}", file=sys.stderr)
    md = f"# {titulo}\n\nFuente: API Mercado Público (ChileCompra), consultada el " \
         f"{datetime.now():%d-%m-%Y %H:%M}. Registros: {len(filas)}.\n\n" + tabla_md(filas, columnas) + "\n"
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"Markdown guardado en {args.md}", file=sys.stderr)
    if not (args.json or args.csv or args.md):
        print(md)


def progreso(i, total):
    print(f"\r  detalle {i}/{total}", end="", file=sys.stderr, flush=True)
    if i == total:
        print(file=sys.stderr)


# ---------------------------------------------------------------- comandos

def cmd_licitaciones(args):
    base = licitaciones(args.organismo, args.estado, args.fecha)
    if args.detalle:
        filas = []
        for i, l in enumerate(base, 1):
            progreso(i, len(base))
            filas.append(fila_licitacion(licitacion(l["CodigoExterno"]) or l))
        cols = COLS_LIC
    else:
        filas = [fila_licitacion(l) for l in base]
        cols = COLS_LIC_CORTA
    filas.sort(key=lambda r: r["cierre"] or "")
    emitir(filas, args, cols, f"Licitaciones · organismo {args.organismo or 'todos'}")


def cmd_ordenes(args):
    desde = args.desde or date.today()
    hasta = args.hasta or desde
    base = []
    for d in dias(desde, hasta):
        print(f"  {d:%d-%m-%Y}", file=sys.stderr)
        base += ordenes(args.organismo, d, args.estado)
    if args.detalle:
        filas = []
        for i, o in enumerate(base, 1):
            progreso(i, len(base))
            filas.append(fila_orden(orden(o["Codigo"]) or o))
        cols = COLS_OC
    else:
        filas = [fila_orden(o) for o in base]
        cols = COLS_OC_CORTA
    emitir(filas, args, cols,
           f"Órdenes de compra · organismo {args.organismo or 'todos'} · {desde:%d-%m-%Y} a {hasta:%d-%m-%Y}")


def cmd_ficha(args, funcion):
    dato = funcion(args.codigo)
    if not dato:
        sys.exit(f"No se encontró {args.codigo}")
    print(json.dumps(dato, ensure_ascii=False, indent=2))


def cmd_ficha_web(args):
    texto, foro = ficha_publica(args.codigo)
    salida = (f"# Ficha pública {args.codigo}\n\nFuente: {FICHA_WEB.format(args.codigo)} "
              f"(leída el {datetime.now():%d-%m-%Y %H:%M})\n\n```\n{texto}\n```\n\n"
              f"## Foro de preguntas\n\n```\n{foro or 'Sin foro disponible.'}\n```\n\n"
              "Las bases en PDF y los anexos no se descargan de forma automática "
              "(el portal los protege con reCAPTCHA). Bájalos desde el botón 'Ver adjuntos' de la ficha.\n")
    if args.md:
        Path(args.md).write_text(salida, encoding="utf-8")
        print(f"Guardado en {args.md}", file=sys.stderr)
    else:
        print(salida)


def main():
    p = argparse.ArgumentParser(description="Consulta la API de Mercado Público.")
    sub = p.add_subparsers(dest="comando", required=True)

    def salidas(sp):
        sp.add_argument("--md", help="guardar tabla Markdown en este archivo")
        sp.add_argument("--csv", help="guardar CSV en este archivo")
        sp.add_argument("--json", help="guardar JSON en este archivo")
        sp.add_argument("--organismo", default=MUNI_COQUIMBO,
                        help="código de organismo (87901 = Municipalidad de Coquimbo; '' = todos)")
        sp.add_argument("--detalle", action="store_true",
                        help="baja la ficha de cada registro (montos, unidad, proveedor); más lento")

    sp = sub.add_parser("licitaciones", help="lista licitaciones")
    sp.add_argument("--estado", help="activas, publicada, cerrada, desierta, adjudicada, revocada, suspendida, todos")
    sp.add_argument("--fecha", type=fecha_api, help="día de consulta (dd-mm-aaaa)")
    salidas(sp)
    sp.set_defaults(func=cmd_licitaciones)

    sp = sub.add_parser("ordenes", help="lista órdenes de compra por día o rango")
    sp.add_argument("--desde", type=fecha_api, help="dd-mm-aaaa (por defecto hoy)")
    sp.add_argument("--hasta", type=fecha_api, help="dd-mm-aaaa (por defecto = desde)")
    sp.add_argument("--estado", help="enviadaproveedor, aceptada, cancelada, recepcionconforme, pendienterecepcion, todos")
    salidas(sp)
    sp.set_defaults(func=cmd_ordenes)

    sp = sub.add_parser("licitacion", help="ficha completa de una licitación")
    sp.add_argument("codigo")
    sp.set_defaults(func=lambda a: cmd_ficha(a, licitacion))

    sp = sub.add_parser("ficha-web", help="texto de la ficha pública y del foro de una licitación")
    sp.add_argument("codigo")
    sp.add_argument("--md", help="guardar en este archivo")
    sp.set_defaults(func=cmd_ficha_web)

    sp = sub.add_parser("orden", help="ficha completa de una orden de compra")
    sp.add_argument("codigo")
    sp.set_defaults(func=lambda a: cmd_ficha(a, orden))

    sp = sub.add_parser("organismos", help="busca códigos de organismos compradores")
    sp.add_argument("texto")
    sp.set_defaults(func=lambda a: [print(f"{e['CodigoEmpresa']}\t{e['NombreEmpresa']}") for e in organismos(a.texto)])

    sp = sub.add_parser("proveedor", help="busca un proveedor por RUT (con puntos y guion)")
    sp.add_argument("rut")
    sp.set_defaults(func=lambda a: print(json.dumps(proveedor(a.rut), ensure_ascii=False, indent=2)))

    args = p.parse_args()
    try:
        args.func(args)
    except ErrorAPI as e:
        sys.exit(f"Error de la API: {e}")


if __name__ == "__main__":
    main()
