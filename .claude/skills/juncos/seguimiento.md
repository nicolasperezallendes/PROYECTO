# Seguimiento de licitaciones y tareas de JUNCOS E.I.R.L.

Actualiza este archivo al final de cada sesión de trabajo. Estados posibles: **Detectada**, **En análisis**, **Postulando**, **Enviada**, **Adjudicada**, **No adjudicada**, **Descartada** o **Vencida**.

## Licitaciones en curso

| Código | Nombre | Organismo | Monto | Cierre | Estado | Próximo paso |
|---|---|---|---|---|---|---|
| [564953-79-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=564953-79-LE26) | Servicio de encuestas de satisfacción usuaria (educación y salud) | Corp. de Educación y Salud de Las Condes | $20.000.000 | **Lun 26-10-2026, 17:00** (confirmado en la API el 24-10) | Cerrada (06-11), en evaluación. **Confirmar con Nicolás si se envió la oferta** | Adjudicación prevista: 30-11. Si se envió, `registro.py marcar 564953-79-LE26 --decision cotizada --precio-ofertado ...` |
| [632-11-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=632-11-LE26) | Informe 5: diagnóstico y plan maestro del barrio Pudepar, Cartagena | Subsecretaría de Vivienda y Urbanismo | No publica | Mié 28-10-2026, 15:10 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 30-11) para referencia de precio |
| [752-32-LP26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=752-32-LP26) | Estudio de indicadores y metas para el seguimiento del PARCC | Gobierno Regional de Los Lagos | $100.000.000 | Mar 03-11-2026, 15:30 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 01-12) para referencia de precio |
| [691-8-LP26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=691-8-LP26) | Diagnóstico y tramitación del Plan Regulador Comunal de Empedrado | Subsecretaría de Vivienda y Urbanismo | $200.000.000 | Mié 04-11-2026, 17:00 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 19-11) para referencia de precio |
| [3712-75-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=3712-75-LE26) | Talleres de oficio para el programa Quiero Mi Barrio | I. Municipalidad de Los Vilos (**Región de Coquimbo**) | No publica | Lun 26-10-2026, 15:05 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 27-01-2027) para referencia de precio |
| [1750-6-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=1750-6-LE26) | Diseño y ejecución de talleres de liderazgo efectivo | Dirección Nacional del Servicio Civil | $68.000.000 | Lun 26-10-2026, 15:00 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 15-11) para referencia de precio |
| [519302-9-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=519302-9-LE26) | Diseño, implementación y medición de marketing digital | INAPI | No publica | Lun 02-11-2026, 16:00 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 16-11) para referencia de precio |
| [4192-63-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=4192-63-LE26) | Capacitación de desarrollo personal y profesional | I. Municipalidad de Caldera (Atacama) | No publica | Jue 29-10-2026, 15:30 | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 06-11) para referencia de precio |
| [2898-15-LE26](https://www.mercadopublico.cl/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion=2898-15-LE26) | Actualización del PLADECO de TDP | Municipalidad | No publica | **Jue 29-10-2026, 18:00** (se postergó desde el vie 23-10; visto el 21-10) | Cerrada (06-11), en evaluación. Sin registro de oferta de JUNCOS | Ver adjudicación (prevista 09-11) para referencia de precio |

## Compras Ágiles en curso

Estados posibles: **Detectada**, **Cotizada**, **Seleccionada**, **OC aceptada**, **Entregada**, **Pagada**, **No seleccionada** o **Descartada**. El método está en `proceso-postulacion.md`, «Ruta corta: Compra Ágil».

| Código | Nombre | Organismo | Monto disponible | Cierre | Cotizaciones a la fecha | Estado | Próximo paso |
|---|---|---|---|---|---|---|---|

Al 06-11-2026 no hay Compras Ágiles abiertas en seguimiento: todas las anteriores cerraron (ver historial). Las nuevas de la búsqueda del 06-11 se agregan abajo cuando conviene cotizarlas.

## Tablero

El 22-10-2026 se creó el tablero «Tablero JUNCOS Mercado Público» (https://claude.ai/artifact/MrUfVPBFpaWqkStktVptrM), con los datos de la consulta de ese día a las 13:00. No se actualiza solo: se refresca con `tablero.py` y los pasos de `proceso-postulacion.md`, «Salida en tablero». Última actualización: 24-10-2026.

El 22-10, el conteo `total_ofertas_recibidas` de la API bajó a 0 en Compras Ágiles abiertas que el 20-10 tenían 1 o 2. Mientras están abiertas, no es confiable.

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
| Decir a Claude qué se cotiza o descarta (con un motivo de la lista), para registrarlo en `registro.py`: sin eso el ciclo de mejora no aprende | Cada día | Pendiente |
| Enviar la oferta de Las Condes (564953-79-LE26) | **Antes del lun 26-10, 17:00** | Pendiente |
| Confirmar si se envió la Compra Ágil de EPCO (1317954-9-COT26) | **Antes del lun 26-10, 23:59** | Pendiente |
| Decidir y cotizar la DPR (953-82-COT26) y las jornadas de Sercotec | **Lun 26-10, 12:00 y 17:00** | Pendiente |
| Confirmar si JUNCOS cotizó la SSP (1447930-490-COT26) | Lun 26-10 | Pendiente |
| Renovar la inscripción en el Registro de Proveedores | Antes del 29-12-2026 | Pendiente |
| Agregar en el SII un giro de consultoría (702000, 732000 o 722000) y actualizarlo en Mercado Público | Lo antes posible | **Revisar:** el 15-10-2026, Mi SII ya mostraba 702000 (consultoría de gestión), 855000 (apoyo a la enseñanza) y 711003 (consultoría técnica), todas desde el 02-04-2026, junto a 681012, 682000, 811000 y 990000. Faltan 732000 y 722000. Confirmar por qué Mercado Público muestra como principal el giro inmobiliario y usar «Actualizar con la versión más reciente» |
| Quitar 5 rubros sin relación y agregar los 8 sugeridos. Los rubros también definen qué Compras Ágiles avisa la plataforma | Lo antes posible | Pendiente |
| ~~Verificar en Mercado Público que JUNCOS figure como Empresa de Menor Tamaño (micro).~~ Sin eso no puede cotizar en el primer llamado de Compra Ágil. Si no aparece, consultar a la mesa de ayuda (600 0061 211) | Antes de la primera Compra Ágil | Hecho el 19-10-2026: es EMT |
| Primera corrida real de `compras_agiles.py` | 19-10-2026 | Hecho: el ticket sirve, Coquimbo es la región 4 y `codigo_producto` es UNSPSC de 8 dígitos. Se ajustó a páginas de 10 y al filtro por rubros inscritos |
| Confirmar el enlace público a la ficha de cada Compra Ágil y probar el filtro de texto `q` | Esta semana | El filtro `q` funciona (probado el 19 y el 20-10). Falta el enlace público |
| Guardar el ticket de la API como variable del entorno | — | Hecho: el 20-10-2026 `MERCADOPUBLICO_TICKET` ya estaba cargado y respondió en las dos APIs |
| Inscribir 80111500 (Consultorías para el desarrollo de recursos humanos) | **Antes de cotizar la DPR y la SSP** | Pendiente. Es el producto 80111504 de las mejores Compras Ágiles del 20-10 |
| Inscribir los rubros 82101500 (publicidad impresa) y 82121500 (impresión promocional) para la línea de diseño | Lo antes posible | Pendiente |
| Conseguir una imprenta de confianza en La Serena o Coquimbo (precios de pendón roller, lienzo, lanyard y credencial PVC, con despacho) | Antes de la primera Compra Ágil de diseño | Pendiente |
| Pedir los certificados de vigencia, boletín comercial y quiebras | Esta semana (para 564953-79-LE26) | Pendiente |
| Redactar el código de ética o programa de integridad | Antes del 22-10-2026 | Hecho en otra sesión, sin subir a GitHub. Recuperar o regenerar |
| Reunir certificados de experiencia del titular (trabajos previos) | Antes del 22-10-2026 | Pendiente |
| Completar el teléfono y el correo de contacto en la ficha | 19-10-2026 | Hecho |
| Ingresar la declaración jurada de socios y beneficiarios finales en Mercado Público | Lo antes posible | Pendiente |

## Historial de resultados

| Fecha | Código | Resultado | Ganador y precio | Lección |
|---|---|---|---|---|
| 26-10-2026 | 1317954-9-COT26 Estudio de clima laboral, EPCO ($1.000.000) | **JUNCOS cotizó $750.000 y perdió.** Quedó 5.º en precio entre 28 ofertas visibles | Global Connect Solutions Spa: **$481.950** (48% del monto). Precio mínimo visible: $481.950 | Con 40% de precio y 28 ofertas ganó la más barata (48% del monto). En estudios cortos de clima laboral, la competencia baja mucho el precio |
| 26-10-2026 | 953-82-COT26 Curso «Trabajo en equipo», DPR Coquimbo ($3.000.000) | Sin registro de cotización de JUNCOS. 26 ofertas | Sikia Consultora Spa: **$2.850.000** (95% del monto). Precio mínimo visible: $1.900.000 | Referencia de precio |
| 26-10-2026 | 1481-21-COT26 Curso de IA para docentes EPJA, Deprov Elqui ($600.000) | Sin registro de cotización de JUNCOS. 6 ofertas | Vantia Soluciones Digitales Spa: **$490.000** (82% del monto). Precio mínimo visible: $490.000 | Referencia de precio |
| 26-10-2026 | 1615-4-COT26 Jornada de cohesión de equipos, Sercotec Antofagasta ($1.400.000) | Sin registro de cotización de JUNCOS. 6 ofertas | Smg Innovacion Spa: **$1.380.400** (99% del monto). Precio mínimo visible: $1.100.000 | Referencia de precio |
| 26-10-2026 | 1220-12-COT26 Jornada de cohesión de equipos, Sercotec Araucanía ($1.400.000) | Sin registro de cotización de JUNCOS. 5 ofertas | Servicios De Turismo Wilma Levil Carrillo E.I.R.L.: **$1.400.000** (100% del monto). Precio mínimo visible: $1.123.000 | Referencia de precio |
| 26-10-2026 | 723-20-COT26 Jornada de cohesión de equipos, Sercotec Aysén ($1.400.000) | Sin registro de cotización de JUNCOS. 11 ofertas | Refugio Macales Spa: **$1.350.000** (96% del monto). Precio mínimo visible: $960.000 | Referencia de precio |
| 26-10-2026 | 724-13-COT26 Jornada de comunicación y trabajo en equipo, Sercotec Maule ($1.400.000) | Sin registro de cotización de JUNCOS. 7 ofertas | Asesorías En Gestión Omar Ahumada Gatica E.I.R.L.: **$1.190.000** (85% del monto). Precio mínimo visible: $1.050.000 | Referencia de precio |
| Visto el 06-11-2026 | 1447930-490-COT26 Gestión del cambio, SSP ($3.700.000) | Sin registro de cotización de JUNCOS. 9 ofertas | Pulsus Consultores Spa: **$2.689.000** (73% del monto). Mínimo visible: $1.548.730 | Referencia de precio |
| Visto el 06-11-2026 | 1305552-116-COT26 Diagnóstico de bienestar, SLEP Tamarugal ($7.200.000) | Sin registro de cotización de JUNCOS. 10 ofertas | Fundacion Chile: **$7.200.000** (100% del monto). Mínimo visible: $2.380.000 | Referencia de precio |
| Visto el 06-11-2026 | 1040758-203-COT26 Afiches, Seremi de Salud Ñuble ($875.959) | Sin registro de cotización de JUNCOS. 6 ofertas | Producciones Publicitarias Creapop Spa: **$873.460** (100% del monto). Mínimo visible: $702.100 | Referencia de precio |
| Visto el 06-11-2026 | 2708-641-COT26 Jornadas de cuidado HPV, Ovalle ($1.500.000) | Sin registro de cotización de JUNCOS. 3 ofertas | Los Nietos Inversiones Limitada: **$1.455.000** (97% del monto). Mínimo visible: $1.404.200 | Referencia de precio |
| 06-11-2026 | **Resumen de precios** | 12 Compras Ágiles de capacitación y consultoría con ganador conocido | Mediana del precio ganador: **96% del monto disponible**, con 3 a 28 ofertas | Salvo con mucha competencia (EPCO, DPR), el ganador oferta cerca del tope. Revisar `registro.py metricas` antes de cada precio |
| 22-10-2026 | 3260-101-COT26 Curso de buen trato y clima laboral, Salud Río Hurtado ($1.000.000) | Sin registro de cotización de JUNCOS. Segundo llamado con 4 ofertas. Proveedor seleccionado (OC 55716238, visto el 24-10) | Jaime Alejandro Rojas Briceño (persona natural, no EMT; el impuesto es el 15,25%, propio de boleta de honorarios): **$1.000.000** ($847.500 + $152.500 de impuesto). Las otras visibles: Compañía de Capacitación Integra Ltda., OTEC NCh 2728 con Sello Empresa Mujer, **$800.000 exento**; DDG del Valle Capacitaciones SpA, $956.000 exento | **No ganó la más barata**: el comprador puede fundamentar otra elección. En capacitación compiten **OTEC exentas de IVA**: con el mismo neto, JUNCOS (afecta a IVA) queda 19% más cara. La precotización de JUNCOS ($820.000 neto, $975.800 con IVA) habría quedado tercera en precio |
| 21-10-2026 | 1305552-116-COT26 Diagnóstico de bienestar de equipos, SLEP Tamarugal ($7.200.000) | Sin registro de cotización de JUNCOS. Cerrada con 10 ofertas, sin selección al 24-10 | Visibles: Global Connect Solutions SpA, $2.380.000 con IVA; Escuela de Coaching Yagán Ltda., $6.000.000 exento; Kinesiología Andrés Zumarán Rojas EIRL, $7.100.000 exento; Fundación Chile, $7.200.000 con IVA | Los precios van del 33% al 100% del monto disponible. Hay que ver quién gana para saber si pesa el precio o la trayectoria |
| 23-10-2026 | 1447930-490-COT26 Gestión del cambio, SSP ($3.700.000) | Cerrada con 9 ofertas. **Confirmar con Nicolás si JUNCOS cotizó** | La API aún no muestra cotizaciones | Mucha competencia en consultoría organizacional en Santiago |
| 23-10-2026 | 1040758-203-COT26 Afiches de vigilancia epidemiológica, Ñuble ($875.959) | Sin registro de cotización de JUNCOS. Cerrada con 6 ofertas | La API aún no muestra cotizaciones | Diseño con impresión atrae a muchas imprentas locales |
| 22-10-2026 | 1153-16-COT26 Talleres de calidad de servicio, Corfo ($3.500.000) | Sin registro de cotización de JUNCOS. Cerrada con 4 ofertas (la API marcaba 0 mientras estaba abierta) | La API aún no muestra cotizaciones | El conteo de ofertas solo es real al cierre |
| 21-10-2026 | 2708-641-COT26 Jornadas de cuidado HPV, Ovalle; 3760-612-COT26 Grupos focales, El Monte; 1109692-245-COT26 Factibilidad CFT Magallanes | Sin registro de cotización de JUNCOS. Cerraron con 3, 7 y 6 ofertas | — | — |
| 22-10-2026 | 2699-36-LE26 PLADECO La Reina | No se postuló (poco plazo). Cerrada | Adjudicación prevista: 05-11-2026 | Ver el resultado: es la especialidad 3 |
