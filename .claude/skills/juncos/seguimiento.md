# Seguimiento de licitaciones y tareas de JUNCOS E.I.R.L.

Actualiza este archivo al final de cada sesión de trabajo. Estados posibles: **Detectada**, **En análisis**, **Postulando**, **Enviada**, **Adjudicada**, **No adjudicada**, **Descartada** o **Vencida**.

## Licitaciones en curso

| Código | Nombre | Organismo | Monto | Cierre | Estado | Próximo paso |
|---|---|---|---|---|---|---|
| [564953-79-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=564953-79-LE26) | Servicio de encuestas de satisfacción usuaria (educación y salud) | Corp. de Educación y Salud de Las Condes | $20.000.000 | Vie 23-10-2026, 17:00 | En análisis | Nicolás baja las bases y los anexos. Leer el foro el 20-10 a las 17:00 |
| [632-11-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=632-11-LE26) | Informe 5: diagnóstico y plan maestro del barrio Pudepar, Cartagena | Subsecretaría de Vivienda y Urbanismo | No publica | Mié 28-10-2026, 15:10 | Detectada | Decidir con la matriz de la etapa 2 |
| [752-32-LP26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=752-32-LP26) | Estudio de indicadores y metas para el seguimiento del PARCC | Gobierno Regional de Los Lagos | $100.000.000 | Mar 03-11-2026, 15:30 | Detectada | Decidir con la matriz. Probable alianza |
| [691-8-LP26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=691-8-LP26) | Diagnóstico y tramitación del Plan Regulador Comunal de Empedrado | Subsecretaría de Vivienda y Urbanismo | $200.000.000 | Mié 04-11-2026, 17:00 | Detectada | Solo en UTP con urbanistas |
| [3712-75-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=3712-75-LE26) | Talleres de oficio para el programa Quiero Mi Barrio | I. Municipalidad de Los Vilos (**Región de Coquimbo**) | No publica | Lun 26-10-2026, 15:05 | Detectada | Revisar bases. Es la única afín en la región |
| [1750-6-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=1750-6-LE26) | Diseño y ejecución de talleres de liderazgo efectivo | Dirección Nacional del Servicio Civil | $68.000.000 | Lun 26-10-2026, 15:00 | Detectada | Decidir con la matriz |
| [519302-9-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=519302-9-LE26) | Diseño, implementación y medición de marketing digital | INAPI | No publica | Lun 02-11-2026, 16:00 | Detectada | Revisar bases |

## Compras Ágiles en curso

Estados posibles: **Detectada**, **Cotizada**, **Seleccionada**, **OC aceptada**, **Entregada**, **Pagada**, **No seleccionada** o **Descartada**. El método está en `proceso-postulacion.md`, «Ruta corta: Compra Ágil».

| Código | Nombre | Organismo | Monto disponible | Cierre | Estado | Próximo paso |
|---|---|---|---|---|---|---|
| — | Todavía no se corre la búsqueda real (ruta agregada el 19-10-2026) | — | — | — | — | Primera corrida de `compras_agiles.py` |

## Análisis entregados

| Fecha | Código | Veredicto | Archivo |
|---|---|---|---|
| 19-10-2026 | 564953-79-LE26 | Postular, sujeto a revisar la experiencia exigida | `claude/19.10.2026 - ANALISIS LICITACION 564953-79-LE26 ENCUESTAS LAS CONDES.md` |

### Ficha resumida de 564953-79-LE26 (para no volver a bajarla)

- **Producto:** 81131504, encuestas por muestreo. Dos líneas: satisfacción usuaria de educación y de salud.
- **Tipo:** LE, una etapa, con contrato, sin renovación, sin toma de razón, sin garantías y con subcontratación permitida.
- **Calendario:**
  - Preguntas: 13-10 al 16-10.
  - Respuestas: 20-10 a las 17:00.
  - Cierre: 23-10 a las 17:00.
  - Apertura: 26-10 a las 09:00.
  - Adjudicación: 30-11.
  - Si llegan 2 ofertas o menos, el cierre se extiende en 2 días hábiles.
- **Criterios de evaluación:**
  - Oferta económica: 50%.
  - Propuesta técnica: 22%.
  - Experiencia: 20%.
  - Integridad, Sello Mujer, requisitos formales y buen comportamiento: 2% cada uno.
  - El detalle de cada criterio está en el artículo 9 de las bases.
- **Para ofertar:** Declaración Jurada de Requisitos para Ofertar (firma electrónica) y el archivo "ANEXOS DE LICITACIÓN".
- **Para contratar (persona jurídica):**
  - Fotocopia legalizada del RUT.
  - Declaración jurada del art. 4, inciso 6.
  - Certificado de vigencia.
  - Boletín comercial.
  - Certificado de quiebras.
- **Pago:** 30 días desde la factura, por transferencia. Responsable: Francisco Díaz (fdiaz@corplascondes.cl). El organismo tiene 22 reclamos por pagar fuera de plazo en los últimos 12 meses.
- **Ofertas técnicas:** quedan públicas tras la apertura.
- **Pendiente:** bases en PDF y anexos (los tiene que bajar Nicolás).
- **Documentos de oferta:** en otra sesión del 19-10-2026 se redactaron el programa de integridad y ética y el borrador de propuesta técnica, pero **no están en GitHub**. Si Nicolás los tiene, que los suba o los pegue. Si no, hay que regenerarlos con `plantillas.md` y el método de la etapa 5.

## Tareas pendientes de la empresa

| Tarea | Plazo | Estado |
|---|---|---|
| Renovar la inscripción en el Registro de Proveedores | Antes del 29-12-2026 | Pendiente |
| Agregar en el SII un giro de consultoría (702000, 732000 o 722000) y actualizarlo en Mercado Público | Lo antes posible | Pendiente |
| Quitar 5 rubros sin relación y agregar los 8 sugeridos. Los rubros también definen qué Compras Ágiles avisa la plataforma | Lo antes posible | Pendiente |
| Verificar en Mercado Público que JUNCOS figure como Empresa de Menor Tamaño (micro). Sin eso no puede cotizar en el primer llamado de Compra Ágil. Si no aparece, consultar a la mesa de ayuda (600 0061 211) | Antes de la primera Compra Ágil | Pendiente |
| Primera corrida real de `compras_agiles.py` | 19-10-2026 | Hecho: el ticket sirve, Coquimbo es la región 4 y `codigo_producto` es UNSPSC de 8 dígitos. Se ajustó a páginas de 10 y al filtro por rubros inscritos |
| Confirmar el enlace público a la ficha de cada Compra Ágil y probar el filtro de texto `q` | Esta semana | Pendiente |
| Pedir los certificados de vigencia, boletín comercial y quiebras | Esta semana (para 564953-79-LE26) | Pendiente |
| Redactar el código de ética o programa de integridad | Antes del 22-10-2026 | Hecho en otra sesión, sin subir a GitHub. Recuperar o regenerar |
| Reunir certificados de experiencia del titular (trabajos previos) | Antes del 22-10-2026 | Pendiente |
| Completar el teléfono y el correo de contacto en la ficha | Cuando Nicolás los entregue | Pendiente |
| Ingresar la declaración jurada de socios y beneficiarios finales en Mercado Público | Lo antes posible | Pendiente |

## Historial de resultados

| Fecha | Código | Resultado | Ganador y precio | Lección |
|---|---|---|---|---|
| — | — | Aún sin resultados | — | — |
