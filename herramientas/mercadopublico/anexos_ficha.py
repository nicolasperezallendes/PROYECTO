#!/usr/bin/env python3
"""Baja los archivos que el comprador adjuntó a cada antecedente de la ficha pública de una licitación.

    python3 anexos_ficha.py 624-28-LE26 --dir "../../claude/licitaciones/624-28-LE26/originales"
    python3 anexos_ficha.py 624-28-LE26 --listar        # solo muestra qué hay, sin bajar nada

Qué baja: los formatos de anexos y documentos de referencia de la sección 4 de la ficha («Antecedentes para
incluir en la oferta»), que el portal muestra sin inicio de sesión y sin captcha (VerAntecedentes.aspx).

Qué NO baja: las bases y el resto de los adjuntos de la ventana «Ver adjuntos» (ViewAttachment.aspx). Esa
ventana tiene reCAPTCHA y no se salta: esos archivos los baja una persona.

Reglas de uso: una licitación a la vez y solo cuando se va a analizar para postular; entra como visitante
anónimo, hace una consulta a la vez con pausas y se detiene si aparece un captcha.
"""
import argparse
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

FICHA = "https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={}"
BASE = "https://www.mercadopublico.cl/Procurement/Modules/Attachment/"
AGENTE = {"User-Agent": "Mozilla/5.0"}
PAUSA = 3


def texto(pagina):
    sin = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", pagina)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", sin))).strip()


def campos_ocultos(pagina):
    campos = {}
    for m in re.finditer(r'(?is)<input[^>]+type="hidden"[^>]*>', pagina):
        nombre = re.search(r'name="([^"]+)"', m.group(0))
        valor = re.search(r'value="([^"]*)"', m.group(0))
        if nombre:
            campos[nombre.group(1)] = html.unescape(valor.group(1)) if valor else ""
    return campos


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("codigo", help="código de la licitación, por ejemplo 624-28-LE26")
    p.add_argument("--dir", default=".", help="carpeta donde guardar los archivos")
    p.add_argument("--listar", action="store_true", help="solo lista los archivos, sin bajarlos")
    args = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]{3,40}", args.codigo):
        sys.exit("Código de licitación con formato inválido.")

    abrir = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())).open
    ficha = FICHA.format(args.codigo)
    pagina = abrir(urllib.request.Request(ficha, headers=AGENTE), timeout=90).read().decode("utf-8", "replace")
    enlaces = list(dict.fromkeys(re.findall(r"\.\./Attachment/VerAntecedentes\.aspx\?enc=[^\"'<> ]+", pagina)))
    if not enlaces:
        sys.exit("La ficha no trae archivos adjuntos a los antecedentes (o la licitación no existe).")
    print(f"{len(enlaces)} antecedentes con archivo en la ficha de {args.codigo}.", file=sys.stderr)

    destino = Path(args.dir)
    if not args.listar:
        destino.mkdir(parents=True, exist_ok=True)
    indice = []
    for n, enlace in enumerate(enlaces, 1):
        url = BASE + html.unescape(enlace).replace("../Attachment/", "")
        time.sleep(PAUSA)
        lista = abrir(urllib.request.Request(url, headers={**AGENTE, "Referer": ficha}), timeout=90).read().decode("utf-8", "replace")
        if "captcha" in lista.lower():
            sys.exit("Apareció un captcha: me detengo. Estos archivos hay que bajarlos a mano.")
        botones = re.findall(r'name="(grdAttachment\$ctl\d+\$grdIbtnView)"', lista)
        descripcion = re.sub(r"^.*?Fecha Acciones ", "", texto(lista)).replace(" Cerrar", "")
        print(f"  {n}. {descripcion[:150]}", file=sys.stderr)
        if args.listar:
            indice.append({"n": n, "descripcion": descripcion})
            continue
        for boton in botones:
            campos = campos_ocultos(lista)
            campos[boton + ".x"] = "8"
            campos[boton + ".y"] = "8"
            time.sleep(PAUSA)
            pedido = urllib.request.Request(
                url, data=urllib.parse.urlencode(campos).encode(),
                headers={**AGENTE, "Referer": url, "Content-Type": "application/x-www-form-urlencoded"})
            try:
                with abrir(pedido, timeout=180) as r:
                    datos = r.read()
                    disposicion = r.headers.get("content-disposition") or ""
            except urllib.error.HTTPError as e:
                print(f"     no se pudo bajar (HTTP {e.code})", file=sys.stderr)
                continue
            if datos[:200].lstrip().lower().startswith((b"<html", b"<!doctype")):
                print("     el portal respondió una página y no un archivo: no se guarda", file=sys.stderr)
                continue
            m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", disposicion)
            nombre = urllib.parse.unquote(m.group(1)) if m else f"antecedente_{n}.bin"
            nombre = f"{n:02d} - " + re.sub(r'[\\/:*?"<>|]', "_", nombre)
            (destino / nombre).write_bytes(datos)
            indice.append({"n": n, "archivo": nombre, "bytes": len(datos), "descripcion": descripcion})
            print(f"     guardado: {nombre} ({len(datos):,} bytes)".replace(",", "."), file=sys.stderr)
    print(json.dumps(indice, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
