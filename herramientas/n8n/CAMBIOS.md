# Cambios de los flujos n8n de JUNCOS

Cada cambio en `perfil_juncos.json` › `compra_agil.n8n`, o en el generador, sube la versión y se anota aquí: qué cambió, por qué (con la evidencia del informe semanal) y quién lo aprobó.

- **Versión menor** (2.0 → 2.1): ajustes de términos, exclusiones, topes o umbrales.
- **Versión mayor** (2.x → 3.0): nodos o columnas nuevos. Hay que volver a importar los flujos.

Después de cada cambio:
1. Corre `python3 herramientas/n8n/generar_flujo_n8n.py`.
2. Nicolás vuelve a importar el flujo en n8n y lo reactiva.
3. Escribe el cambio en la columna `cambios_aplicados` de la semana, en la planilla «Mejora JUNCOS (n8n)».

| Versión | Fecha | Qué cambió | Por qué | Aprobó |
|---|---|---|---|---|
| 2.0 | 06-11-2026 | Ciclo de mejora continua: flujo nuevo «Resultados y mejora», con resultados de L–V a las 19:00 y revisión semanal el viernes a las 17:00. Columnas nuevas en la planilla: `terminos`, `version_flujo`, `decision`, `motivo`, `estado_final`, `ofertas_final`, `juncos_cotizo`, `ganador`, `precio_ganador`, `precio_min`, `ratio_ganador` y `resultado_revisado_el`. Planilla semanal «Mejora JUNCOS (n8n)». La configuración pasa a `perfil_juncos.json` › `compra_agil.n8n` | Nicolás pidió un proceso de mejora continua. Sin resultados ni decisiones registradas, el filtro no podía aprender | Nicolás (pedido del 06-11-2026) |
| 1.0 | 06-11-2026 | Flujo diario: 15 términos en todo el país más las nuevas de Coquimbo, filtro por nombre, 20 fichas de detalle, regla de rubros, planilla, correo y aviso opcional a Claude | Primera versión | Nicolás |
