#!/usr/bin/env python3
"""Genera los flujos de n8n de JUNCOS a partir de perfil_juncos.json.

1. «JUNCOS · Compras Ágiles diarias» (JUNCOS - Compras Agiles diarias.json).
2. «JUNCOS · Resultados y mejora» (JUNCOS - Resultados y mejora.json): el ciclo de mejora
   continua. Cada tarde anota en la planilla cómo terminó cada Compra Ágil (ganador, precio,
   ofertas) y cada viernes calcula métricas y propone ajustes al perfil.

El flujo, de lunes a viernes a las 07:30 (hora de Chile):
  1. busca Compras Ágiles publicadas con los términos del perfil (todo el país) y
     todas las de la Región de Coquimbo publicadas desde la corrida anterior;
  2. descarta por nombre lo excluido y deja las candidatas;
  3. baja el detalle de las mejores y aplica la regla de rubros de la skill /juncos;
  4. guarda el resultado en una planilla de Google, manda un correo y, si se activa,
     despierta a la rutina de Claude Code.

Uso:
    python3 herramientas/n8n/generar_flujo_n8n.py
Deja «JUNCOS - Compras Agiles diarias.json» en esta carpeta, listo para importar en n8n
(Workflows > Import from File). Las credenciales no van en el archivo: se eligen en n8n.
"""
import json
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PERFIL = AQUI.parent / "mercadopublico" / "perfil_juncos.json"
SALIDA = AQUI / "JUNCOS - Compras Agiles diarias.json"

SALIDA_MEJORA = AQUI / "JUNCOS - Resultados y mejora.json"
# Términos, topes y umbrales viven en perfil_juncos.json > compra_agil > n8n, para que cada
# mejora se haga en un solo lugar y suba la versión (ver CAMBIOS.md).
CORREO = "juncoseirl@gmail.com"
PLANILLA_ID = "19yVuYAPHGi0fY6cVhPDxkCfec4LwHaYEPv8YSROnK7k"  # «Compras Ágiles JUNCOS (n8n)», v2 con columnas de mejora (06-11-2026)
MEJORA_ID = "1ZBYFofbAG_5QE3aN6fEP7eEbAvsCACF23ldeU2r99Ss"  # «Mejora JUNCOS (n8n)»: una fila por semana (06-11-2026)
RUT_JUNCOS = "78.390.884-0"
RUTINA_URL = "https://api.anthropic.com/v1/claude_code/routines/PEGAR_ID_trig_/fire"


def nid():
    return str(uuid.uuid4())


def main():
    p = json.loads(PERFIL.read_text(encoding="utf-8"))
    ca = p["compra_agil"]
    dis = ca.get("diseno", {})
    n8n = ca["n8n"]
    TERMINOS = n8n["terminos"]
    VERSION = n8n["version"]
    perfil_js = {
        "claves": p["palabras_clave"] + ca.get("palabras_clave_extra", []),
        "excluir": p["excluir"] + ca.get("excluir_extra", []),
        "remoto": ca.get("senales_remoto", []),
        "alertas": ca.get("alertas_texto", []),
        # Regla de Nicolás: solo rubros inscritos, más la línea de diseño
        "rubros": [r for r in p["rubros"] if r.get("inscrito") and r.get("peso")],
        "rubrosDiseno": dis.get("rubros", []),
        "palabrasDiseno": dis.get("palabras", []),
        "montoMaxDiseno": dis.get("monto_max", 2000000),
        "minPuntaje": ca.get("min_puntaje", 3),
        "minHoras": ca.get("min_horas_al_cierre", 3),
        "maxDetalle": n8n["max_detalle"],
        "terminos": TERMINOS,
        "version": VERSION,
    }
    PERFIL_JS = "const PERFIL = " + json.dumps(perfil_js, ensure_ascii=False) + ";\n"
    NORM = ("const norm = (t) => String(t || '').toLowerCase().normalize('NFD')"
            ".replace(/[\\u0300-\\u036f]/g, '');\n"
            "const tiene = (t, lista) => lista.filter((w) => norm(t).includes(norm(w)));\n"
            "const palabra = (t, lista) => lista.filter((w) => new RegExp('(^|[^a-z0-9])' + "
            "norm(w).replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '(s|es)?([^a-z0-9]|$)').test(norm(t)));\n")

    js_terminos = (
        "// Un ítem por término de búsqueda. Edita la lista para buscar otras cosas.\n"
        f"const terminos = {json.dumps(TERMINOS, ensure_ascii=False)};\n"
        "return terminos.map((q) => ({ json: { q } }));\n")

    js_nombre = PERFIL_JS + NORM + (
        "// Junta las dos búsquedas, quita duplicados y descarta por nombre lo que no corresponde.\n"
        "const vistos = new Map();\n"
        "for (const it of $input.all()) {\n"
        "  for (const ca of (it.json.payload && it.json.payload.items) || []) {\n"
        "    if (ca && ca.codigo && !vistos.has(ca.codigo)) vistos.set(ca.codigo, ca);\n"
        "  }\n"
        "}\n"
        "const ahora = DateTime.now().setZone('America/Santiago');\n"
        "const cand = [];\n"
        "for (const ca of vistos.values()) {\n"
        "  const nombre = ca.nombre || '';\n"
        "  const esDiseno = palabra(nombre, PERFIL.palabrasDiseno).length > 0;\n"
        "  if (!esDiseno && tiene(nombre, PERFIL.excluir).length) continue;\n"
        "  const cierre = DateTime.fromFormat((ca.fechas || {}).fecha_cierre || '', 'yyyy-MM-dd HH:mm', { zone: 'America/Santiago' });\n"
        "  const horas = cierre.isValid ? cierre.diff(ahora, 'hours').hours : null;\n"
        "  if (horas !== null && horas < PERFIL.minHoras) continue;\n"
        "  const hits = tiene(nombre, PERFIL.claves).length + (esDiseno ? 1 : 0);\n"
        "  const enRegion = (ca.institucion || {}).region === 4;\n"
        "  if (!hits && !enRegion) continue;\n"
        "  // Primero las que tienen palabras clave; las de la región sin palabras clave solo llenan cupos libres.\n"
        "  cand.push({ ca, orden: hits ? hits * 3 + (enRegion ? 2 : 0) : 0.5 });\n"
        "}\n"
        "cand.sort((a, b) => b.orden - a.orden);\n"
        "return cand.slice(0, PERFIL.maxDetalle).map((c) => ({ json: c.ca }));\n")

    js_rubros = PERFIL_JS + NORM + (
        "// Une cada candidata con su ficha de detalle y aplica la regla de rubros de /juncos.\n"
        "const cands = $('Filtrar por nombre').all();\n"
        "const dets = $input.all();\n"
        "const ahora = DateTime.now().setZone('America/Santiago');\n"
        "const desde = ahora.minus({ days: ahora.weekday === 1 ? 3 : 1, hours: 2 });\n"
        "const coincide = (codigos, rubros) => rubros.filter((r) => {\n"
        "  const pref = String(r.codigo).replace(/0+$/, '');\n"
        "  return codigos.some((c) => c.startsWith(pref) && c.length === String(r.codigo).length);\n"
        "});\n"
        "const filas = [];\n"
        "cands.forEach((c, i) => {\n"
        "  const ca = c.json;\n"
        "  const det = (dets[i] && dets[i].json && dets[i].json.payload) || null;\n"
        "  const it = Object.assign({}, ca, det || {});\n"
        "  const prods = it.productos_solicitados || [];\n"
        "  const codigos = prods.map((x) => String(x.codigo_producto || ''));\n"
        "  const texto = [it.nombre, it.descripcion].concat(prods.map((x) => (x.nombre || '') + ' ' + (x.descripcion || ''))).join(' ');\n"
        "  const rub = coincide(codigos, PERFIL.rubros);\n"
        "  const rubD = coincide(codigos, PERFIL.rubrosDiseno);\n"
        "  const esDiseno = palabra(it.nombre, PERFIL.palabrasDiseno).length > 0;\n"
        "  const monto = ((it.presupuesto || it.montos || {}).monto_disponible_clp) || 0;\n"
        "  const alertas = [];\n"
        "  if (!det) {\n"
        "    if (!esDiseno) return;  // sin detalle no se puede revisar el rubro\n"
        "    alertas.push('la API no dio el detalle: revisar productos en la plataforma');\n"
        "  } else if (!rub.length && !rubD.length) return;  // fuera de los rubros de JUNCOS\n"
        "  const linea = (rubD.length || esDiseno) ? 'diseño' : 'consultoría';\n"
        "  if (linea === 'diseño' && monto > PERFIL.montoMaxDiseno) return;\n"
        "  const enRegion = (it.institucion || {}).region === 4;\n"
        "  const hits = tiene(texto, PERFIL.claves);\n"
        "  const remoto = tiene(texto, PERFIL.remoto).length > 0;\n"
        "  // Qué búsqueda la trajo: sirve para medir qué términos rinden (ciclo de mejora).\n"
        "  const terminos = PERFIL.terminos.filter((t) => norm(texto).includes(norm(t))).concat(enRegion ? ['coquimbo'] : []);\n"
        "  const peso = Math.max(0, ...rub.concat(rubD).map((r) => r.peso || 0));\n"
        "  const puntaje = peso + Math.min(hits.length, 6) + (enRegion ? 2 : 0) + (remoto ? 1 : 0);\n"
        "  if (puntaje < PERFIL.minPuntaje) return;\n"
        "  const cierre = DateTime.fromFormat((it.fechas || {}).fecha_cierre || '', 'yyyy-MM-dd HH:mm', { zone: 'America/Santiago' });\n"
        "  const pub = DateTime.fromFormat(((it.fechas || {}).fecha_publicacion || '').slice(0, 16), 'yyyy-MM-dd HH:mm', { zone: 'America/Santiago' });\n"
        "  const horas = cierre.isValid ? Math.round(cierre.diff(ahora, 'hours').hours) : null;\n"
        "  if (horas !== null && horas < 24) alertas.push('cierra en menos de 24 h');\n"
        "  if (!enRegion && !remoto) alertas.push('presencial fuera de la región: revisar logística');\n"
        "  const pide = palabra(texto, PERFIL.alertas);\n"
        "  if (pide.length) alertas.push('pide ' + pide.join(', '));\n"
        "  if (/segund/i.test((it.convocatoria || {}).descripcion || '')) alertas.push('segundo llamado');\n"
        "  if (linea === 'diseño') alertas.push('cotizar impresión y despacho');\n"
        "  filas.push({\n"
        "    codigo: it.codigo,\n"
        "    nombre: it.nombre,\n"
        "    organismo: (it.institucion || {}).organismo_comprador || '',\n"
        "    region: ((it.institucion || {}).nombre_region || '').trim(),\n"
        "    monto_clp: monto,\n"
        "    neto_max_clp: Math.round(monto / 1.19),\n"
        "    cierre: (it.fechas || {}).fecha_cierre || '',\n"
        "    horas_al_cierre: horas,\n"
        "    llamado: (it.convocatoria || {}).descripcion || '',\n"
        "    puntaje,\n"
        "    linea,\n"
        "    rubro: rub.concat(rubD).map((r) => r.codigo + ' ' + r.nombre).join('; '),\n"
        "    alertas: alertas.join('; '),\n"
        "    nueva: pub.isValid ? pub >= desde : false,\n"
        "    revisada_el: ahora.toFormat('dd-MM-yyyy HH:mm'),\n"
        "    terminos: terminos.join(', '),\n"
        "    version_flujo: PERFIL.version,\n"
        "  });\n"
        "});\n"
        "filas.sort((a, b) => b.puntaje - a.puntaje || (a.horas_al_cierre || 1e9) - (b.horas_al_cierre || 1e9));\n"
        "// Un solo ítem con todas las filas: así el correo sale aunque no haya ninguna.\n"
        "return [{ json: { filas, total_candidatas: cands.length } }];\n")

    js_planilla = (
        "// Una fila por Compra Ágil para la planilla (si no hay, no escribe nada).\n"
        "return ($json.filas || []).map((f) => ({ json: f }));\n")

    js_correo = (
        "const filas = $json.filas || [];\n"
        "const nuevas = filas.filter((f) => f.nueva);\n"
        "const pesos = (v) => '$' + Number(v || 0).toLocaleString('es-CL');\n"
        "const esc = (t) => String(t || '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));\n"
        "const fila = (f) => `<tr><td><b>${esc(f.codigo)}</b></td><td>${esc(f.nombre)}<br><small>${esc(f.organismo)} · ${esc(f.region)}</small></td>`\n"
        "  + `<td style=\"text-align:right\">${pesos(f.monto_clp)}<br><small>neto máx. ${pesos(f.neto_max_clp)}</small></td>`\n"
        "  + `<td>${esc(f.cierre)}</td><td style=\"text-align:right\">${f.puntaje}</td><td><small>${esc(f.alertas)}</small></td></tr>`;\n"
        "const tabla = (lista) => lista.length ? '<table border=\"1\" cellpadding=\"6\" style=\"border-collapse:collapse;font-family:sans-serif;font-size:13px\">'\n"
        "  + '<tr><th>Código</th><th>Qué piden</th><th>Monto</th><th>Cierre</th><th>Puntaje</th><th>Alertas</th></tr>'\n"
        "  + lista.slice(0, 10).map(fila).join('') + '</table>' : '<p>Ninguna.</p>';\n"
        "const hoy = $now.setZone('America/Santiago').toFormat('dd-MM-yyyy');\n"
        "const asunto = `JUNCOS · Compras Ágiles ${hoy}: ${nuevas.length} nuevas, ${filas.length} abiertas afines`;\n"
        "const html = `<p>Revisión automática de Mercado Público (n8n), ${hoy}.</p>`\n"
        "  + `<h3>Nuevas desde la última revisión (${nuevas.length})</h3>` + tabla(nuevas)\n"
        "  + `<h3>Todas las abiertas afines (${filas.length})</h3>` + tabla(filas)\n"
        "  + '<p><small>Monto con impuestos; neto máximo = monto / 1,19. Antes de cotizar, revisa el adjunto en la plataforma y la decisión CA3 de /juncos.</small></p>';\n"
        "const texto = `REVISIÓN DIARIA. Revisión n8n del ${hoy}. Compras Ágiles afines nuevas: `\n"
        "  + (nuevas.map((f) => `${f.codigo} (${f.nombre}; ${f.organismo}; ${pesos(f.monto_clp)}; cierre ${f.cierre}; puntaje ${f.puntaje})`).join(' | ') || 'ninguna')\n"
        "  + '. Están también en la planilla «Compras Ágiles JUNCOS (n8n)».';\n"
        "return [{ json: { asunto, html, texto, nuevas: nuevas.length } }];\n")

    auth_ticket = {"authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth"}
    opciones_api = {"timeout": 60000, "batching": {"batch": {"batchSize": 1, "batchInterval": 1500}}}

    def code(nombre, js, pos, **extra):
        n = {"parameters": {"jsCode": js}, "id": nid(), "name": nombre,
             "type": "n8n-nodes-base.code", "typeVersion": 2, "position": pos}
        n.update(extra)
        return n

    nodos = [
        {"parameters": {"content": (
            f"## JUNCOS · Compras Ágiles diarias (v{VERSION})\n"
            "De lunes a viernes a las 07:30 (hora de Chile).\n\n"
            "**Para que el ciclo de mejora aprenda:** en la planilla, marca la columna `decision` "
            "(cotizar o descartar) y, si descartas, escribe el `motivo`.\n\n"
            "**Antes de activarlo:**\n"
            "1. Credencial *Header Auth* «Mercado Público ticket»: Name `ticket`, Value = tu ticket. "
            "Úsala en los tres nodos HTTP de la API.\n"
            "2. Credenciales de Google Sheets y Gmail.\n"
            "3. «Guardar en planilla» ya apunta a la planilla «Compras Ágiles JUNCOS (n8n)» de tu Drive: revisa que la hoja elegida sea la primera.\n"
            "4. (Opcional) «Avisar a Claude»: pega la URL de la rutina y crea la credencial "
            "*Header Auth* «Rutina Claude JUNCOS»: Name `Authorization`, Value `Bearer sk-ant-oat01-…`. "
            "Luego activa el nodo.\n\n"
            "Generado con herramientas/n8n/generar_flujo_n8n.py desde perfil_juncos.json. "
            "Cambios por versión: herramientas/n8n/CAMBIOS.md."),
            "height": 420, "width": 420},
         "id": nid(), "name": "Instrucciones", "type": "n8n-nodes-base.stickyNote",
         "typeVersion": 1, "position": [-520, -260]},
        {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "30 7 * * 1-5"}]}},
         "id": nid(), "name": "Lunes a viernes 07:30", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [0, 0]},
        code("Términos de búsqueda", js_terminos, [220, -120]),
        {"parameters": {
            "url": "https://api2.mercadopublico.cl/v2/compra-agil", **auth_ticket,
            "sendQuery": True,
            "queryParameters": {"parameters": [
                {"name": "estado", "value": "publicada"},
                {"name": "tamano_pagina", "value": "10"},
                {"name": "q", "value": "={{ $json.q }}"}]},
            "options": {**opciones_api, "pagination": {"pagination": {
                "parameters": {"parameters": [{"type": "qs", "name": "numero_pagina", "value": "={{ $pageCount + 1 }}"}]},
                "paginationCompleteWhen": "other",
                "completeExpression": "={{ $pageCount + 1 >= (($response.body.payload || {}).paginacion || {}).total_paginas }}",
                "limitPagesFetched": True, "maxRequests": n8n["max_paginas_termino"], "requestInterval": 1500}}}},
         "id": nid(), "name": "Buscar por términos (país)", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [440, -120], "retryOnFail": True, "maxTries": 3,
         "waitBetweenTries": 5000, "onError": "continueRegularOutput"},
        {"parameters": {
            "url": "https://api2.mercadopublico.cl/v2/compra-agil", **auth_ticket,
            "sendQuery": True,
            "queryParameters": {"parameters": [
                {"name": "estado", "value": "publicada"},
                {"name": "region", "value": "4"},
                {"name": "tamano_pagina", "value": "10"},
                {"name": "publicado_desde",
                 "value": "={{ $now.setZone('America/Santiago').minus({ days: $now.weekday === 1 ? 3 : 1, hours: 2 }).toFormat(\"yyyy-MM-dd'T'HH:mm:ss'Z'\") }}"}]},  # la API lee la hora como de Chile
            "options": {**opciones_api, "pagination": {"pagination": {
                "parameters": {"parameters": [{"type": "qs", "name": "numero_pagina", "value": "={{ $pageCount + 1 }}"}]},
                "paginationCompleteWhen": "other",
                "completeExpression": "={{ $pageCount + 1 >= (($response.body.payload || {}).paginacion || {}).total_paginas }}",
                "limitPagesFetched": True, "maxRequests": n8n["max_paginas_region"], "requestInterval": 1500}}}},
         "id": nid(), "name": "Región de Coquimbo (nuevas)", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [440, 120], "retryOnFail": True, "maxTries": 3,
         "waitBetweenTries": 5000, "onError": "continueRegularOutput"},
        {"parameters": {}, "id": nid(), "name": "Juntar", "type": "n8n-nodes-base.merge",
         "typeVersion": 3, "position": [660, 0]},
        code("Filtrar por nombre", js_nombre, [880, 0]),
        {"parameters": {
            "url": "=https://api2.mercadopublico.cl/v2/compra-agil/{{ $json.codigo }}", **auth_ticket,
            "options": opciones_api},
         "id": nid(), "name": "Detalle de cada una", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [1100, 0], "retryOnFail": True, "maxTries": 2,
         "waitBetweenTries": 5000, "onError": "continueRegularOutput"},
        code("Rubros y puntaje", js_rubros, [1320, 0]),
        code("Filas para planilla", js_planilla, [1540, -120]),
        {"parameters": {
            "operation": "appendOrUpdate",
            "documentId": {"__rl": True, "value": PLANILLA_ID, "mode": "id"},
            "sheetName": {"__rl": True, "value": "gid=0", "mode": "list", "cachedResultName": "Primera hoja"},
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": ["codigo"]},
            "options": {"handlingExtraData": "insertInNewColumn"}},
         "id": nid(), "name": "Guardar en planilla", "type": "n8n-nodes-base.googleSheets",
         "typeVersion": 4.5, "position": [1760, -120]},
        code("Armar correo", js_correo, [1540, 120]),
        {"parameters": {
            "sendTo": CORREO, "subject": "={{ $json.asunto }}", "emailType": "html",
            "message": "={{ $json.html }}", "options": {"appendAttribution": False}},
         "id": nid(), "name": "Enviar correo", "type": "n8n-nodes-base.gmail",
         "typeVersion": 2.1, "position": [1760, 120]},
        {"parameters": {
            "method": "POST", "url": RUTINA_URL, **auth_ticket,
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "anthropic-version", "value": "2023-06-01"}]},
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ text: $('Armar correo').first().json.texto }) }}",
            "options": {"timeout": 30000}},
         "id": nid(), "name": "Avisar a Claude", "type": "n8n-nodes-base.httpRequest",
         "typeVersion": 4.2, "position": [1980, 120], "disabled": True,
         "notes": "Sin reintentos: cada llamada abre una sesión nueva de Claude.",
         "onError": "continueRegularOutput"},
    ]
    con = lambda dest, idx=0: {"node": dest, "type": "main", "index": idx}  # noqa: E731
    conexiones = {
        "Lunes a viernes 07:30": {"main": [[con("Términos de búsqueda"), con("Región de Coquimbo (nuevas)")]]},
        "Términos de búsqueda": {"main": [[con("Buscar por términos (país)")]]},
        "Buscar por términos (país)": {"main": [[con("Juntar", 0)]]},
        "Región de Coquimbo (nuevas)": {"main": [[con("Juntar", 1)]]},
        "Juntar": {"main": [[con("Filtrar por nombre")]]},
        "Filtrar por nombre": {"main": [[con("Detalle de cada una")]]},
        "Detalle de cada una": {"main": [[con("Rubros y puntaje")]]},
        "Rubros y puntaje": {"main": [[con("Filas para planilla"), con("Armar correo")]]},
        "Filas para planilla": {"main": [[con("Guardar en planilla")]]},
        "Armar correo": {"main": [[con("Enviar correo")]]},
        "Enviar correo": {"main": [[con("Avisar a Claude")]]},
    }
    flujo = {
        "name": f"JUNCOS · Compras Ágiles diarias v{VERSION}",
        "nodes": nodos,
        "connections": conexiones,
        "settings": {"executionOrder": "v1", "timezone": "America/Santiago", "saveManualExecutions": True},
        "pinData": {},
        "active": False,
        "meta": {"templateCredsSetupCompleted": False},
        "tags": [],
    }
    SALIDA.write_text(json.dumps(flujo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Flujo guardado en {SALIDA}")
    flujo_mejora(n8n, VERSION, NORM, auth_ticket, opciones_api, code, con)


def flujo_mejora(n8n, VERSION, NORM, auth_ticket, opciones_api, code, con):
    """Ciclo de mejora continua: resultados diarios (19:00) y revisión semanal (viernes 17:00)."""
    U = n8n["mejora"]
    CONF = "const CONF = " + json.dumps({
        "terminos": n8n["terminos"], "version": VERSION, "rutJuncos": RUT_JUNCOS,
        "ventana": U["ventana_dias"], "minDet": U["min_detecciones_termino"],
        "minMotivo": U["min_repeticiones_motivo"], "minPrecio": U["min_resultados_precio"],
        "diasEspera": U["dias_espera_resultado"]}, ensure_ascii=False) + ";\n"
    COMUN = CONF + NORM + (
        "const ZONA = 'America/Santiago';\n"
        "const ahora = DateTime.now().setZone(ZONA);\n"
        "const num = (v) => { const n = Number(String(v == null ? '' : v).replace(/[^0-9.-]/g, '')); return isFinite(n) ? n : 0; };\n")

    js_pendientes = COMUN + (
        "// Compras Ágiles de la planilla que ya cerraron y aún no tienen resultado final.\n"
        "const FINALES = ['ganada', 'adjudicada a otro', 'adjudicada (ganador no visible)', 'desierta', 'cancelada'];\n"
        "const out = [];\n"
        "for (const it of $input.all()) {\n"
        "  const r = it.json;\n"
        "  if (!r.codigo) continue;\n"
        "  const cierre = DateTime.fromFormat(String(r.cierre || ''), 'yyyy-MM-dd HH:mm', { zone: ZONA });\n"
        "  if (!cierre.isValid || cierre > ahora.minus({ hours: 2 })) continue;\n"
        "  if (FINALES.includes(String(r.estado_final || ''))) continue;\n"
        "  if (ahora.diff(cierre, 'days').days > CONF.diasEspera) continue;  // ya no se espera resultado\n"
        "  out.push({ json: { codigo: r.codigo, monto_clp: num(r.monto_clp) } });\n"
        "}\n"
        "return out.slice(0, 30);  // unos 17 s por ficha\n")

    js_resultado = COMUN + (
        "// Cómo terminó cada una: estado, ofertas, ganador y precios visibles.\n"
        "const pend = $('Pendientes de resultado').all();\n"
        "const dets = $input.all();\n"
        "const filas = [];\n"
        "pend.forEach((p, i) => {\n"
        "  const d = (dets[i] && dets[i].json && dets[i].json.payload) || null;\n"
        "  if (!d) return;  // la API no respondió: se reintenta mañana\n"
        "  const est = (d.estado || {}).codigo || '';\n"
        "  const provs = d.proveedores_cotizando || [];\n"
        "  const sel = provs.find((q) => q.proveedor_seleccionado);\n"
        "  const juncos = provs.find((q) => q.rut_proveedor === CONF.rutJuncos);\n"
        "  const montos = provs.map((q) => num(q.monto_total)).filter((v) => v > 0);\n"
        "  let estado = est;\n"
        "  if (est === 'proveedor_seleccionado') estado = !sel ? 'adjudicada (ganador no visible)' : (sel.rut_proveedor === CONF.rutJuncos ? 'ganada' : 'adjudicada a otro');\n"
        "  else if (est === 'publicada') estado = 'abierta';\n"
        "  const disp = num((d.presupuesto || {}).monto_disponible_clp) || p.json.monto_clp;\n"
        "  const precio = sel ? num(sel.monto_total) : 0;\n"
        "  filas.push({ json: {\n"
        "    codigo: p.json.codigo,\n"
        "    estado_final: estado,\n"
        "    ofertas_final: (d.resumen || {}).total_ofertas_recibidas == null ? '' : d.resumen.total_ofertas_recibidas,\n"
        "    juncos_cotizo: juncos ? 'sí' : (provs.length ? 'no visible' : ''),\n"
        "    ganador: sel ? sel.razon_social : '',\n"
        "    precio_ganador: precio || '',\n"
        "    precio_min: montos.length ? Math.min(...montos) : '',\n"
        "    ratio_ganador: precio && disp ? Math.round(precio / disp * 100) / 100 : '',\n"
        "    resultado_revisado_el: ahora.toFormat('dd-MM-yyyy HH:mm'),\n"
        "  } });\n"
        "});\n"
        "return filas;\n")

    js_metricas = COMUN + (
        "// Revisión semanal: qué se detectó, qué se decidió, qué ganó y qué conviene ajustar.\n"
        "const rows = $input.all().map((i) => i.json).filter((r) => r.codigo);\n"
        "const fecha = (s) => DateTime.fromFormat(String(s || ''), 'dd-MM-yyyy HH:mm', { zone: ZONA });\n"
        "const dentro = (r, dias) => { const d = fecha(r.revisada_el); return d.isValid && d >= ahora.minus({ days: dias }); };\n"
        "const sem = rows.filter((r) => dentro(r, 7));\n"
        "const ven = rows.filter((r) => dentro(r, CONF.ventana));\n"
        "const dec = (r) => norm(r.decision);\n"
        "const cotizada = (r) => /cotiz/.test(dec(r)) || r.juncos_cotizo === 'sí';\n"
        "const descartada = (r) => /descart/.test(dec(r));\n"
        "const conDec = sem.filter((r) => dec(r)).length;\n"
        "const cotSem = sem.filter(cotizada).length;\n"
        "const desSem = sem.filter(descartada).length;\n"
        "const mediana = (a) => { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };\n"
        "const pct = (v) => v == null ? '—' : Math.round(v * 100) + '%';\n"
        "// Motivos de descarte en la ventana\n"
        "const motivos = {};\n"
        "ven.filter(descartada).forEach((r) => { const m = String(r.motivo || 'sin motivo').trim().toLowerCase() || 'sin motivo'; motivos[m] = (motivos[m] || 0) + 1; });\n"
        "// Rendimiento de cada término de búsqueda en la ventana\n"
        "const term = {};\n"
        "CONF.terminos.concat(['coquimbo']).forEach((t) => { term[t] = { det: 0, cot: 0 }; });\n"
        "ven.forEach((r) => String(r.terminos || '').split(',').map((x) => x.trim()).filter(Boolean).forEach((t) => {\n"
        "  term[t] = term[t] || { det: 0, cot: 0 }; term[t].det++; if (cotizada(r)) term[t].cot++; }));\n"
        "// Precios ganadores por línea (todo el historial)\n"
        "const conRes = rows.filter((r) => num(r.ratio_ganador) > 0);\n"
        "const lineas = {};\n"
        "conRes.forEach((r) => { const l = r.linea || 'consultoría'; (lineas[l] = lineas[l] || { ratios: [], ofertas: [] }).ratios.push(num(r.ratio_ganador)); if (num(r.ofertas_final)) lineas[l].ofertas.push(num(r.ofertas_final)); });\n"
        "const ganadas = rows.filter((r) => r.estado_final === 'ganada').length;\n"
        "const cotizadasTot = rows.filter(cotizada).length;\n"
        "// Sugerencias: cada una dice qué cambiar en perfil_juncos.json y con qué evidencia\n"
        "const sug = [];\n"
        "if (sem.length && conDec / sem.length < 0.5) sug.push(`Solo ${conDec} de ${sem.length} Compras Ágiles de la semana tienen decisión. Marca la columna decision (cotizar o descartar) y el motivo: sin eso el ciclo no aprende.`);\n"
        "Object.entries(term).forEach(([t, v]) => {\n"
        "  if (v.det >= CONF.minDet && v.cot === 0) sug.push(`El término «${t}» trajo ${v.det} Compras Ágiles afines en ${CONF.ventana} días y ninguna se cotizó: evaluar quitarlo de compra_agil.n8n.terminos o afinarlo.`);\n"
        "  if (ven.length >= 20 && v.det === 0 && t !== 'coquimbo') sug.push(`El término «${t}» no aportó ninguna Compra Ágil afín en ${CONF.ventana} días: evaluar reemplazarlo.`);\n"
        "});\n"
        "Object.entries(motivos).filter(([m, n]) => n >= CONF.minMotivo && m !== 'sin motivo').forEach(([m, n]) => sug.push(`«${m}» se repitió ${n} veces como motivo de descarte: evaluar una exclusión o una regla nueva en el perfil.`));\n"
        "Object.entries(lineas).forEach(([l, v]) => { if (v.ratios.length >= CONF.minPrecio) sug.push(`En ${l}, el ganador ofertó en mediana el ${pct(mediana(v.ratios))} del monto disponible, con ${mediana(v.ofertas) || '—'} ofertas en mediana (${v.ratios.length} resultados): úsalo como referencia al fijar precios.`); });\n"
        "if (cotizadasTot >= 5 && ganadas === 0) sug.push(`JUNCOS lleva ${cotizadasTot} Compras Ágiles cotizadas sin ganar: revisar precio frente a los ganadores (columna precio_ganador) y la descripción de las ofertas.`);\n"
        "const fila = {\n"
        "  semana_hasta: ahora.toFormat('dd-MM-yyyy'), version_flujo: CONF.version,\n"
        "  detectadas: sem.length, con_decision: conDec, cotizadas: cotSem, descartadas: desSem,\n"
        "  sin_decision: sem.length - conDec, precision: conDec ? Math.round(cotSem / conDec * 100) / 100 : '',\n"
        "  resultados_conocidos: conRes.length, ganadas_juncos: ganadas,\n"
        "  mediana_ratio_consultoria: lineas['consultoría'] ? mediana(lineas['consultoría'].ratios) : '',\n"
        "  mediana_ratio_diseno: lineas['diseño'] ? mediana(lineas['diseño'].ratios) : '',\n"
        "  sugerencias: sug.join(' | '),\n"
        "};\n"
        "const esc = (t) => String(t == null ? '' : t).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));\n"
        "const filaT = (a, b) => `<tr><td>${esc(a)}</td><td style=\"text-align:right\">${esc(b)}</td></tr>`;\n"
        "const tablaT = Object.entries(term).sort((a, b) => b[1].det - a[1].det).map(([t, v]) => `<tr><td>${esc(t)}</td><td style=\"text-align:right\">${v.det}</td><td style=\"text-align:right\">${v.cot}</td></tr>`).join('');\n"
        "const asunto = `JUNCOS · Mejora semanal ${fila.semana_hasta}: ${sem.length} detectadas, ${cotSem} cotizadas, ${sug.length} sugerencias`;\n"
        "const html = `<p>Revisión semanal del flujo n8n v${CONF.version}.</p>`\n"
        "  + '<h3>La semana</h3><table border=\"1\" cellpadding=\"6\" style=\"border-collapse:collapse;font-family:sans-serif;font-size:13px\">'\n"
        "  + filaT('Detectadas', sem.length) + filaT('Con decisión', conDec) + filaT('Cotizadas', cotSem) + filaT('Descartadas', desSem)\n"
        "  + filaT('Precisión (cotizadas / con decisión)', fila.precision === '' ? '—' : pct(fila.precision))\n"
        "  + filaT('Resultados conocidos (historial)', conRes.length) + filaT('Ganadas por JUNCOS', ganadas) + '</table>'\n"
        "  + `<h3>Sugerencias (${sug.length})</h3>` + (sug.length ? '<ol>' + sug.map((x) => `<li>${esc(x)}</li>`).join('') + '</ol>' : '<p>Ninguna esta semana.</p>')\n"
        "  + `<h3>Términos de búsqueda (${CONF.ventana} días)</h3><table border=\"1\" cellpadding=\"6\" style=\"border-collapse:collapse;font-family:sans-serif;font-size:13px\"><tr><th>Término</th><th>Afines</th><th>Cotizadas</th></tr>` + tablaT + '</table>'\n"
        "  + '<p><small>Las sugerencias no se aplican solas: Claude las revisa contigo y, si las apruebas, actualiza perfil_juncos.json, sube la versión y regenera el flujo.</small></p>';\n"
        "const texto = `MEJORA SEMANAL. Flujo n8n v${CONF.version}, semana hasta ${fila.semana_hasta}. `\n"
        "  + `Detectadas ${sem.length}, con decisión ${conDec}, cotizadas ${cotSem}, descartadas ${desSem}, resultados conocidos ${conRes.length}, ganadas ${ganadas}. `\n"
        "  + `Motivos de descarte: ${JSON.stringify(motivos)}. Términos: ${JSON.stringify(term)}. Sugerencias: ${sug.join(' | ') || 'ninguna'}.`;\n"
        "return [{ json: { fila, asunto, html, texto } }];\n")

    sheets = lambda nombre, doc, pos, **par: {  # noqa: E731
        "parameters": {"documentId": {"__rl": True, "value": doc, "mode": "id"},
                       "sheetName": {"__rl": True, "value": "gid=0", "mode": "list", "cachedResultName": "Primera hoja"},
                       **par},
        "id": nid(), "name": nombre, "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.5, "position": pos}
    fire = lambda nombre, origen, pos: {  # noqa: E731
        "parameters": {
            "method": "POST", "url": RUTINA_URL, **auth_ticket, "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "anthropic-version", "value": "2023-06-01"}]},
            "sendBody": True, "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ text: $('" + origen + "').first().json.texto }) }}",
            "options": {"timeout": 30000}},
        "id": nid(), "name": nombre, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": pos, "disabled": True, "onError": "continueRegularOutput",
        "notes": "Sin reintentos: cada llamada abre una sesión nueva de Claude."}

    nodos = [
        {"parameters": {"content": (
            f"## JUNCOS · Resultados y mejora (v{VERSION})\n"
            "Ciclo de mejora continua del flujo diario.\n\n"
            "**Medir (L–V 19:00):** revisa las Compras Ágiles de la planilla que ya cerraron y anota "
            "estado final, ofertas, ganador, precio ganador y si JUNCOS aparece entre los oferentes.\n\n"
            "**Aprender (viernes 17:00):** calcula detectadas, decisiones, precisión, rendimiento de cada "
            "término, motivos de descarte y precios ganadores, y propone ajustes al perfil.\n\n"
            "**Ajustar:** las sugerencias llegan por correo y, si activas el último nodo, a Claude, que las "
            "revisa contigo. Nada cambia sin tu visto bueno.\n\n"
            "Credenciales: las mismas del flujo diario. La planilla «Mejora JUNCOS (n8n)» guarda una fila por semana."),
            "height": 440, "width": 440},
         "id": nid(), "name": "Instrucciones", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
         "position": [-560, -300]},
        {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 19 * * 1-5"}]}},
         "id": nid(), "name": "Resultados L–V 19:00", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [0, -120]},
        sheets("Leer planilla (resultados)", PLANILLA_ID, [220, -120], operation="read", options={}),
        code("Pendientes de resultado", js_pendientes, [440, -120]),
        {"parameters": {"url": "=https://api2.mercadopublico.cl/v2/compra-agil/{{ $json.codigo }}",
                        **auth_ticket, "options": opciones_api},
         "id": nid(), "name": "Detalle al cierre", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
         "position": [660, -120], "retryOnFail": True, "maxTries": 2, "waitBetweenTries": 5000,
         "onError": "continueRegularOutput"},
        code("Calcular resultado", js_resultado, [880, -120]),
        sheets("Anotar resultado", PLANILLA_ID, [1100, -120], operation="appendOrUpdate",
               columns={"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": ["codigo"]}, options={"handlingExtraData": "insertInNewColumn"}),
        {"parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 17 * * 5"}]}},
         "id": nid(), "name": "Viernes 17:00", "type": "n8n-nodes-base.scheduleTrigger",
         "typeVersion": 1.2, "position": [0, 160]},
        sheets("Leer planilla (semana)", PLANILLA_ID, [220, 160], operation="read", options={}),
        code("Métricas y sugerencias", js_metricas, [440, 160]),
        code("Fila de la semana", "return [{ json: $json.fila }];\n", [660, 60]),
        sheets("Guardar semana", MEJORA_ID, [880, 60], operation="append",
               columns={"mappingMode": "autoMapInputData", "value": {}}, options={"handlingExtraData": "insertInNewColumn"}),
        {"parameters": {"sendTo": CORREO, "subject": "={{ $json.asunto }}", "emailType": "html",
                        "message": "={{ $json.html }}", "options": {"appendAttribution": False}},
         "id": nid(), "name": "Correo semanal", "type": "n8n-nodes-base.gmail", "typeVersion": 2.1,
         "position": [660, 260]},
        fire("Pedir mejora a Claude", "Métricas y sugerencias", [880, 260]),
    ]
    conexiones = {
        "Resultados L–V 19:00": {"main": [[con("Leer planilla (resultados)")]]},
        "Leer planilla (resultados)": {"main": [[con("Pendientes de resultado")]]},
        "Pendientes de resultado": {"main": [[con("Detalle al cierre")]]},
        "Detalle al cierre": {"main": [[con("Calcular resultado")]]},
        "Calcular resultado": {"main": [[con("Anotar resultado")]]},
        "Viernes 17:00": {"main": [[con("Leer planilla (semana)")]]},
        "Leer planilla (semana)": {"main": [[con("Métricas y sugerencias")]]},
        "Métricas y sugerencias": {"main": [[con("Fila de la semana"), con("Correo semanal")]]},
        "Fila de la semana": {"main": [[con("Guardar semana")]]},
        "Correo semanal": {"main": [[con("Pedir mejora a Claude")]]},
    }
    flujo = {"name": f"JUNCOS · Resultados y mejora v{VERSION}", "nodes": nodos, "connections": conexiones,
             "settings": {"executionOrder": "v1", "timezone": "America/Santiago", "saveManualExecutions": True},
             "pinData": {}, "active": False, "meta": {"templateCredsSetupCompleted": False}, "tags": []}
    SALIDA_MEJORA.write_text(json.dumps(flujo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Flujo guardado en {SALIDA_MEJORA}")


if __name__ == "__main__":
    main()
