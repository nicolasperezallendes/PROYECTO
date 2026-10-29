# Instrucciones del proyecto

## Mapas: formato estándar (pedido de Nicolás, 28.10.2026)

Todo mapa que se pida en este proyecto se entrega, salvo que se indique otra cosa, como **lámina de 90 × 60 cm a 200 ppp**:

- Horizontal, proporción 3:2. Lienzo de diseño de 3840 × 2560 unidades, exportado a **7.087 × 4.724 px**.
- **PDF a tamaño real (90 × 60 cm)**, con texto vectorial: es el archivo para la imprenta.
- **PNG** de 7.087 × 4.724 px, con 200 ppp en sus metadatos.
- **SVG** con capas por nombre, para editar en Affinity.
- Mapa base con resolución real de 200 ppp. Las teselas de OpenStreetMap se bajan un nivel de zoom más cerca del que pide la composición, para que el raster no quede ampliado.
- Sin sangrado ni marcas de corte, a menos que se pidan (lo habitual es 3 a 5 mm por lado).
- Estilo: tipografía Montserrat. Paleta: fondo #F6F4EF, azul marino #0B2545, azul petróleo #007C99, ámbar #D98E00. En el pie, fuente y "Mapa base © colaboradores de OpenStreetMap".
- Antes de entregar, revisar las láminas en versión reducida y un recorte al 100% para confirmar la nitidez.

El generador de los mapas de enseñanza media por delegación está en `claude/herramientas/mapas/` (`build.py`, `tiles.py`, `render.js`, `setdpi.py`). Sirve de plantilla: `python3 build.py <salida>`, luego `node render.js <salida> pdf` y al final `python3 setdpi.py <salida>`. Necesita Montserrat instalada en `~/.fonts`. `data.py` lee un `base.json` extraído de la planilla de establecimientos, que no está en el repo; para un mapa nuevo se cambia por los datos que correspondan.

## Otras preferencias

- Las minutas se entregan en Markdown, no en .docx.
