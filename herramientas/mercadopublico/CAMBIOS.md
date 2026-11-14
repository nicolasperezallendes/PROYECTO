# Cambios del proceso automático de /juncos

Cada cambio en `perfil_juncos.json` › `automatizacion` (términos, topes, umbrales), en `compra_agil.excluir_extra` o en los scripts de la revisión automática sube la versión y se anota aquí: qué cambió, por qué (con la evidencia de la revisión semanal) y quién lo aprobó.

- **Versión menor** (3.0 → 3.1): ajustes de términos, exclusiones, topes o umbrales.
- **Versión mayor** (3.x → 4.0): pasos, columnas del registro o tareas programadas nuevas.

| Versión | Fecha | Qué cambió | Por qué | Aprobó |
|---|---|---|---|---|
| 3.0 | 06-11-2026 | **Se deja n8n y todo corre en Claude.** Hay dos tareas programadas: la revisión diaria (L–V) y la de mejora (viernes). Se agrega el registro de procesos (`registro.py` y `registro/procesos.json`), con términos de búsqueda, recomendación de Claude, decisión de Nicolás y resultado al cierre. Las métricas semanales incluyen la coincidencia entre Claude y Nicolás. El tablero suma la pestaña «Mejora de procesos» y adopta la línea gráfica Narrativa | Nicolás pidió dejar n8n, automatizar solo en Claude y usar lo aprendido con n8n para los procesos propios | Nicolás (06-11-2026) |
| 2.0 (n8n, descontinuado) | 06-11-2026 | Ciclo de mejora en n8n: resultados diarios, revisión semanal y planillas de Google | Primer diseño del ciclo de mejora | Nicolás |
| 1.0 (n8n, descontinuado) | 06-11-2026 | Flujo diario de Compras Ágiles en n8n | Primera automatización | Nicolás |
