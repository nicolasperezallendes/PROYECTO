# Conexión con Mercado Público

Script para consultar la API de ChileCompra. Por defecto trae datos de la
I. Municipalidad de Coquimbo (organismo **87901**). Solo usa Python 3, sin
librerías extra.

## Ticket

El ticket de la API **no se guarda en el repositorio**. El script lo busca en:

1. la variable de entorno `MERCADOPUBLICO_TICKET`, o
2. un archivo `.env` en esta carpeta con la línea `MERCADOPUBLICO_TICKET=...`
   (está en `.gitignore`).

## Comandos

```bash
# Licitaciones activas del municipio (lista rápida)
python3 mercadopublico.py licitaciones --estado activas

# Lo mismo, con montos, unidad y financiamiento, guardado en Markdown
python3 mercadopublico.py licitaciones --estado activas --detalle --md reporte.md

# Licitaciones de un día específico (cualquier estado)
python3 mercadopublico.py licitaciones --fecha 15-10-2026 --estado todos

# Órdenes de compra de un rango de días, con proveedor y total
python3 mercadopublico.py ordenes --desde 01-10-2026 --hasta 15-10-2026 --detalle --csv oc.csv

# Ficha completa de una licitación u orden
python3 mercadopublico.py licitacion 2446-271-LR26
python3 mercadopublico.py orden 2448-1195-SE26

# Buscar el código de otro organismo y consultarlo
python3 mercadopublico.py organismos "gobierno regional"
python3 mercadopublico.py licitaciones --estado activas --organismo 6940

# Texto de la ficha pública (bases resumidas, criterios, plazos) y del foro
python3 mercadopublico.py ficha-web 564953-79-LE26 --md ficha.md

# Licitaciones activas de todo el país afines al perfil de JUNCOS
python3 postulables.py --max-detalle 100 --md ranking.md

# Línea de diseño (pendones, lanyards, afiches y piezas con poco material)
python3 postulables.py --diseno --md ranking.md         # licitaciones: consultoría + diseño
python3 postulables.py --solo-diseno --md diseno.md     # licitaciones: solo diseño
python3 compras_agiles.py --diseno --dias 0 --md ca_diseno.md

# Compras Ágiles abiertas afines al perfil (API Compra Ágil v2, beta)
python3 compras_agiles.py --md ranking_ca.md
python3 compras_agiles.py --region coquimbo --dias 7 --md ranking_ca_coquimbo.md

# Buscar un proveedor por RUT
python3 mercadopublico.py proveedor 76.123.456-7
```

Todas las listas aceptan `--md`, `--csv` y `--json` para guardar el resultado.

## A tener en cuenta

- La API no acepta consultas simultáneas. El script va de a una, con una
  pausa de un segundo y reintentos automáticos.
- `--detalle` baja una ficha por registro. Con muchos registros se demora
  (unos 2 a 3 segundos por ficha).
- Los montos se muestran en la moneda de cada proceso (`CLF` = UF).
- Las bases en PDF y los anexos de cada licitación están protegidos con
  reCAPTCHA y se descargan a mano desde "Ver adjuntos" en la ficha.
- Unidades del municipio: código 2446 (municipal central) y 2448
  (Departamento de Salud).
- `compras_agiles.py` usa otra API (`https://api2.mercadopublico.cl/v2/compra-agil`),
  con el mismo ticket, pero enviado en el header `ticket`. Tiene cuota diaria: si
  responde 429, hay que esperar al día siguiente. Lee también el bloque
  `compra_agil` de `perfil_juncos.json`. Para pruebas sin red se puede apuntar a otra
  base con `MERCADOPUBLICO_CA_BASE`.
- `compras_agiles.py` se probó contra la API real el 19-10-2026. Usa páginas de 10
  (con 25 o 50 la API se cae por tiempo), cada detalle tarda unos 17 segundos y
  Coquimbo es la región 4. Por defecto solo muestra Compras Ágiles cuyos productos
  están en los rubros inscritos (`--incluir-sugeridos`, `--todas` y `--sin-prefiltro`
  cambian ese comportamiento).
