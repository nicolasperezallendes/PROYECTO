#!/usr/bin/env python3
"""Genera el flujo de n8n «JUNCOS · Compras Ágiles diarias» a partir de perfil_juncos.json.

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

# Términos de búsqueda (filtro q de la API). Pocos y amplios: cada término gasta cupo del ticket.
TERMINOS = ["clima laboral", "encuesta", "estudio", "diagnostico", "capacitacion", "taller",
            "charla", "jornada", "liderazgo", "grupo focal", "consultoria", "comunicaciones",
            "pendon", "afiche", "lanyard"]
MAX_DETALLE = 20          # fichas de detalle por corrida (unos 17 s cada una)
CORREO = "juncoseirl@gmail.com"
PLANILLA_ID = "1AVZaW4HAiRr9pcbD1zUMvfVBpP_tx3x6C5mUiRGRXqg"  # «Compras Ágiles JUNCOS (n8n)», creada el 06-11-2026
RUTINA_URL = "https://api.anthropic.com/v1/claude_code/routines/PEGAR_ID_trig_/fire"


def nid():
    return str(uuid.uuid4())


def main():
    p = json.loads(PERFIL.read_text(encoding="utf-8"))
    ca = p["compra_agil"]
    dis = ca.get("diseno", {})
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
        "maxDetalle": MAX_DETALLE,
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
        "const texto = `Revisión n8n del ${hoy}. Compras Ágiles afines nuevas: `\n"
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
            "## JUNCOS · Compras Ágiles diarias\n"
            "De lunes a viernes a las 07:30 (hora de Chile).\n\n"
            "**Antes de activarlo:**\n"
            "1. Credencial *Header Auth* «Mercado Público ticket»: Name `ticket`, Value = tu ticket. "
            "Úsala en los tres nodos HTTP de la API.\n"
            "2. Credenciales de Google Sheets y Gmail.\n"
            "3. «Guardar en planilla» ya apunta a la planilla «Compras Ágiles JUNCOS (n8n)» de tu Drive: revisa que la hoja elegida sea la primera.\n"
            "4. (Opcional) «Avisar a Claude»: pega la URL de la rutina y crea la credencial "
            "*Header Auth* «Rutina Claude JUNCOS»: Name `Authorization`, Value `Bearer sk-ant-oat01-…`. "
            "Luego activa el nodo.\n\n"
            "Generado con herramientas/n8n/generar_flujo_n8n.py desde perfil_juncos.json."),
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
                "limitPagesFetched": True, "maxRequests": 3, "requestInterval": 1500}}}},
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
                "limitPagesFetched": True, "maxRequests": 12, "requestInterval": 1500}}}},
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
            "options": {}},
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
        "name": "JUNCOS · Compras Ágiles diarias",
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


if __name__ == "__main__":
    main()
