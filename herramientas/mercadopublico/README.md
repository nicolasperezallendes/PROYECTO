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
- Unidades del municipio: código 2446 (municipal central) y 2448
  (Departamento de Salud).
