---
name: juncos
description: "Ficha de JUNCOS EIRL (Consultores Nicolás Pérez Allendes E.I.R.L.) para Mercado Público: razón social, RUT, código de proveedor, rubros y perfil de postulación. Úsala con /juncos o cuando se pida buscar licitaciones afines a la consultora, revisar sus rubros o completar datos de la empresa en una postulación."
---

# /juncos — Perfil de postulación de JUNCOS EIRL

## Ficha de la empresa

| Campo | Valor |
|---|---|
| Razón social | CONSULTORES NICOLÁS PÉREZ ALLENDES E.I.R.L. |
| Nombre de fantasía | JUNCOS EIRL |
| RUT | 78.390.884-0 |
| Tipo societario | Empresa Individual de Responsabilidad Limitada |
| Titular / representante legal | Nicolás Pérez Allendes |
| Correo de contacto | perez.allendes.sociologo@gmail.com |
| Código de proveedor en Mercado Público | 2103594 |
| Domicilio legal | PENDIENTE |
| Comuna / región | PENDIENTE (se trabaja desde la Región de Coquimbo) |
| Teléfono | PENDIENTE |
| Giro / actividades SII | PENDIENTE |

Estado en Mercado Público al 19-10-2026 (ficha pública):
- "Proveedor sin acreditación vigente".
- Sin declaración jurada de socios ni datos de administración ingresados.

**Alerta.** Para que el Estado le adjudique contratos, la empresa debe estar inscrita y hábil en el Registro de Proveedores (Ley 21.634). Antes de postular, revisa ese estado y súbele a la ficha los datos que falten.

Si un dato aparece como PENDIENTE, pídeselo al usuario y actualiza esta tabla. No lo inventes.

## Rubros

La lista oficial está en Mercado Público, en Mi empresa > Rubros, y solo se ve con sesión iniciada. Mientras no se confirme, el perfil usa un **borrador** de rubros UNSPSC propuesto para una consultora en ciencias sociales y comunicaciones. Está en `herramientas/mercadopublico/perfil_juncos.json` (campo `estado_rubros`).

Cuando el usuario entregue sus rubros:
1. Reemplaza la lista `rubros` del JSON por los códigos y nombres reales (8 dígitos UNSPSC).
2. Ajusta `palabras_clave` y `excluir` para que coincidan con esos rubros.
3. Cambia `estado_rubros` a "CONFIRMADO dd-mm-aaaa".
4. Copia aquí la lista confirmada.

## Buscar licitaciones afines

Requiere el ticket de la API en `MERCADOPUBLICO_TICKET` o en `herramientas/mercadopublico/.env`. Nunca subas el ticket a git.

```bash
cd herramientas/mercadopublico
python3 postulables.py --md "../../claude/dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md"
python3 postulables.py --region coquimbo          # solo la región
python3 postulables.py --max-detalle 100 --min-monto 5000000
```

Puntaje: +5 por cada rubro del perfil que coincide con los productos licitados, +1 por cada palabra clave (máximo 6) y +2 si la región es preferente.

Al entregar el resultado:
- Guárdalo en `claude/` con el formato de nombre `dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md`.
- Abre con 3 a 5 recomendaciones en lenguaje simple: cuál conviene, por qué y cuándo cierra.
- Marca las que cierran en menos de 3 días hábiles.
- Indica cuando el monto viene en UF o USD.
- Si una licitación pide experiencia o boletas de garantía, menciónalo después de revisar la ficha con `python3 mercadopublico.py licitacion CODIGO`.
