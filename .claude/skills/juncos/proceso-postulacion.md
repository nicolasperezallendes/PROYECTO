# Proceso de postulación de JUNCOS E.I.R.L.

Ciclo completo, de la búsqueda al contrato. Cada etapa dice qué hace Claude, qué hace Nicolás y qué se entrega. Las licitaciones siguen las etapas 1 a 7. Las Compras Ágiles (hasta 100 UTM) tienen su propia ruta corta, al final de este archivo.

## Etapa 1. Búsqueda de oportunidades

**Frecuencia sugerida:** lunes y jueves. Las licitaciones LE suelen tener ciclos de unos 10 días entre publicación y cierre.

```bash
cd herramientas/mercadopublico
python3 postulables.py --max-detalle 100 --md "../../claude/dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md"
python3 postulables.py --region coquimbo --max-detalle 150     # foco regional
python3 postulables.py --diseno --max-detalle 100              # consultoría + línea de diseño (piezas con poco material)
python3 postulables.py --solo-diseno                           # solo licitaciones de diseño
```

- El puntaje suma el peso de cada rubro que coincide, 1 punto por palabra clave (hasta 6) y 2 puntos si es de la Región de Coquimbo.
- Revisa las 10 primeras a mano. El filtro por nombre deja pasar ruido. Ejemplos: "diseño" trae diseños de ingeniería, y "capacitación" trae seguros o franquicias. Si aparece ruido nuevo, agrégalo a `excluir` en `perfil_juncos.json`.
- Descarta lo que cierra en menos de 3 días hábiles, salvo que sea muy simple (L1).
- Corre también la búsqueda de **Compra Ágil**, pero a diario y no solo los lunes y jueves, porque muchas cierran en uno a tres días. Sigue la «Ruta corta: Compra Ágil» al final de este archivo. Es la vía más fácil para que una consultora nueva acumule historial con el Estado.
- Anota en `seguimiento.md` las licitaciones que pasan a la etapa 2.

**Entregable:** `dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md`, que abre con 3 a 5 recomendaciones en lenguaje simple.

## Etapa 2. Decidir si postular (matriz de decisión)

Puntúa cada criterio de 0 a 2. Postula con 10 puntos o más. Entre 7 y 9, postula solo si el monto o el valor estratégico lo justifican. Con 6 o menos, no postules.

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Afinidad con las especialidades | Lejana | Parcial | Es el oficio central |
| Experiencia acreditable que piden | No la tenemos | Parcial, o vale la del titular | La cumplimos |
| Días hábiles hasta el cierre | Menos de 3 | Entre 3 y 5 | Más de 5 |
| Relación monto y esfuerzo | No compensa | Justa | Buena |
| Garantías exigidas | Altas, inmovilizan caja | Moderadas | No piden |
| Logística (distancia y campo) | Requiere equipo propio lejos | Se puede subcontratar | Región de Coquimbo o remoto |
| Historial de pago del organismo (reclamos en la ficha) | Muchos reclamos para su tamaño | Algunos | Pocos o ninguno |
| Competencia probable (adjudicaciones previas del organismo) | Proveedor incumbente fuerte | Mixta | Abierta |

Para la competencia, revisa órdenes de compra anteriores del organismo con `mercadopublico.py ordenes --organismo CODIGO --desde ... --hasta ... --detalle` y busca procesos parecidos.

## Etapa 3. Análisis de bases

**Fuentes, en este orden:**
1. `python3 mercadopublico.py ficha-web CODIGO --md ficha.md`: el resumen de las bases que publica el portal y el foro.
2. `python3 mercadopublico.py licitacion CODIGO`: productos UNSPSC, fechas, responsables y justificación del monto.
3. **Bases en PDF y anexos:** se le piden al usuario, que los descarga desde "Ver adjuntos". No se descargan de forma automática (ver `aprendizajes.md`).

**Qué se extrae siempre:**
- Objeto, productos, cantidades, tamaño de las muestras, cobertura territorial y plazos de cada producto.
- Calendario completo, **con el día de la semana verificado** (`date -d AAAA-MM-DD +%A`).
- Criterios de evaluación: peso, fórmula y subcriterios (normalmente en el artículo de evaluación de las bases).
- Requisitos de admisibilidad: qué deja la oferta fuera de concurso.
- Antecedentes administrativos, técnicos y económicos que hay que adjuntar.
- Requisitos para contratar: certificados y declaraciones.
- Garantías (de seriedad y de fiel cumplimiento): monto, glosa, vigencia y tipo de documento aceptado.
- Multas, causales de término, forma y plazo de pago, subcontratación y propiedad de los datos.
- Extensión automática del cierre: algunas bases alargan el plazo si llegan 2 ofertas o menos.

**Entregable:** `dd.mm.aaaa - ANALISIS LICITACION CODIGO NOMBRE.md`, con veredicto, datos clave, calendario, tabla de criterios, documentos, riesgos, lo que falta leer y plan día a día. El modelo es el análisis de 564953-79-LE26.

## Etapa 4. Foro de preguntas

- Prepara preguntas sobre todo lo ambiguo: experiencia aceptada, formato de los anexos, tamaño muestral, cobertura, productos y cómo se acredita el programa de integridad.
- **El plazo de preguntas suele cerrar 3 o 4 días después de publicada la licitación.** Si la oportunidad se detecta tarde, ya no se puede preguntar.
- Lee las respuestas apenas se publiquen. Pueden cambiar reglas de las bases y se consideran parte de ellas.

## Etapa 5. Armado de la oferta

| Componente | Responsable | Base |
|---|---|---|
| Propuesta técnica | Claude redacta, Nicolás valida | `plantillas.md`, sección 1 |
| Propuesta económica y presupuesto | Claude calcula, Nicolás decide el precio final | `plantillas.md`, sección 2 |
| Anexos administrativos | Claude los prellena con la ficha de la empresa | Formularios de las bases |
| Acreditación de experiencia | Nicolás reúne certificados; Claude redacta la carta tipo | `plantillas.md`, sección 4 |
| Programa de integridad o código de ética | Claude redacta, Nicolás firma | `plantillas.md`, sección 3 |
| Declaración Jurada de Requisitos para Ofertar | Nicolás, firma electrónica en la plataforma | Se hace en Mercado Público |

**Archivos que se generan después del análisis** (en `claude/`, en Markdown; método del 19-10-2026):
1. `dd.mm.aaaa - PROGRAMA DE INTEGRIDAD Y ETICA JUNCOS.md`. Es reutilizable: si ya existe, actualiza solo la fecha y revisa si el artículo de evaluación pide un formato propio. La base está en `plantillas.md`, sección 3.
2. `dd.mm.aaaa - BORRADOR PROPUESTA TECNICA CODIGO.md`. Lleva comprensión del encargo, enfoque, diseño muestral, instrumentos, campo, análisis, productos, equipo y Gantt. **Marca con [BASES] todo lo que dependa de las bases en PDF** y aún no se haya podido verificar.

**Diseño muestral de referencia para encuestas:** 95% de confianza, error de ±5% y p = 0,5, con corrección por población finita: n = 384,16 / (1 + 383,16 / N), redondeado hacia arriba.

| Universo por establecimiento (N) | Muestra |
|---|---|
| 500 | 218 |
| 1.000 | 278 |
| 5.000 | 357 |
| Muy grande | 385 |

Con presupuestos ajustados, ofrece ±5% para el total de cada área (por ejemplo, educación y salud) y entre ±7% y ±8% por establecimiento. Explica en la propuesta qué precisión tiene cada nivel de análisis.

**Estrategia según el peso de los criterios:**
- **Precio de 40% o más:** el precio decide. Ofrece bajo el referencial, pero cubre los costos reales. La fórmula típica premia al precio más bajo (precio mínimo dividido por precio ofertado), así que conviene simular escenarios.
- **Técnica de 30% o más:** apuesta a la metodología, porque ahí está la ventaja de un sociólogo. Muestra diseño muestral con su error, instrumentos validados, control de calidad del campo, plan de análisis y productos de muestra.
- **Experiencia:** si se acepta la del titular, acredita sus trabajos anteriores con certificados firmados por los mandantes.

## Etapa 6. Revisión de admisibilidad y envío

Lista de chequeo antes de enviar:
- [ ] Todos los anexos de las bases, en el formato pedido y firmados donde corresponde.
- [ ] Oferta económica en la moneda y unidad pedidas, con o sin IVA según las bases, y coherente entre el anexo y el formulario de la plataforma.
- [ ] Propuesta técnica que responde a cada subcriterio, en el mismo orden de las bases.
- [ ] Respuestas del foro incorporadas.
- [ ] Declaración Jurada de Requisitos para Ofertar firmada en la plataforma.
- [ ] Garantía de seriedad, si la piden: entregada en forma y plazo.
- [ ] Archivos en PDF, con nombres claros y bajo el tamaño máximo.
- [ ] **Envío al menos 24 horas antes del cierre.** La plataforma no acepta ofertas después de la hora exacta.
- [ ] Descargar el comprobante de envío y guardarlo.

## Etapa 7. Después del cierre

- **Apertura:** revisa quién ofertó y a qué precio. Si las ofertas técnicas son públicas, léelas para aprender.
- **Evaluación:** sigue el acta. Si hay un error en tu puntaje, se puede reclamar en Mercado Público dentro de plazo.
- **Si no ganas:** anota en `seguimiento.md` el puntaje, el ganador, su precio y la lección aprendida.
- **Si ganas:** reúne los documentos para contratar, entrega la garantía de fiel cumplimiento si la piden, revisa el contrato y arma un calendario de entregas, pagos y vencimientos.

## Ruta corta: Compra Ágil (hasta 100 UTM)

La Compra Ágil es la forma más rápida de que JUNCOS acumule ventas al Estado. No pide bases, garantías ni contrato, y cada orden de compra aceptada sirve después como respaldo de experiencia en las licitaciones. Mientras la empresa no tenga historial, tiene prioridad.

### Reglas vigentes (verificadas el 19-10-2026)

Fuentes: Directiva N° 35 de ChileCompra (Res. 563-B del 22-12-2025), página Compra Ágil de chilecompra.cl y tabla de UTM 2026 del SII.

| Regla | Qué significa para JUNCOS |
|---|---|
| Tope de 100 UTM, con impuestos, despacho y todo gasto incluido. Se usa la UTM del mes de publicación | Octubre de 2026: UTM $72.151, tope $7.215.100. Noviembre de 2026: UTM $72.440, tope $7.244.000 |
| El primer llamado es solo para Empresas de Menor Tamaño (EMT, Ley 20.416). Si queda desierto, se abre un segundo llamado a empresas de todo tamaño | JUNCOS tiene que figurar como EMT en Mercado Público. Está pendiente de verificar (ver `seguimiento.md`) |
| Hay que estar inscrito y hábil en el Registro de Proveedores al cotizar y al contratar | La inscripción vence el 29-12-2026. Si la entrega o el pago pasan de esa fecha, hay que renovar antes |
| La solicitud queda abierta al menos 24 horas | Muchas cierran en uno a tres días. Por eso la búsqueda es diaria |
| El comprador pide al menos tres cotizaciones por el sistema, pero puede comprar con menos | Vale la pena cotizar aunque ya haya ofertas |
| Gana la más barata que cumpla lo técnico, salvo que la solicitud fije otros criterios. Si no elige la más barata, debe fundamentarlo | El precio decide. Cotiza ajustado y cumple todo lo pedido |
| Se cotiza la totalidad del requerimiento, sin ofertas parciales ni condicionadas | Lo que JUNCOS no hace (impresión, traslados) se subcontrata y va incluido en el precio |
| Al enviar la cotización se firma electrónicamente una declaración jurada de no tener inhabilidades | La firma Nicolás en la plataforma |
| No hay contrato ni garantías: la compra se formaliza cuando el proveedor acepta la orden de compra en la plataforma | Acepta la OC apenas llegue y revisa sus plazos |
| El pago vence a los 30 días corridos desde la factura, después de la recepción conforme | Factura solo cuando tengas la recepción conforme |
| Todo se tramita por Mercado Público, nunca por correo | Las consultas al comprador van por la plataforma |

**El monto disponible incluye impuestos.** JUNCOS cotiza el neto más IVA, igual que en `/cotizacion`. Por eso el neto máximo es el monto disponible dividido por 1,19: con $2.500.000 disponibles, el neto no puede pasar de $2.100.840. El buscador calcula ese neto en cada fila.

### CA1. Búsqueda diaria (lunes a viernes, en la mañana)

```bash
cd herramientas/mercadopublico
python3 compras_agiles.py --md "../../claude/dd.mm.aaaa - COMPRAS AGILES AFINES JUNCOS.md"
python3 compras_agiles.py --region coquimbo --sin-prefiltro --max-detalle 200   # región completa, unos 40 min
python3 compras_agiles.py --region coquimbo --incluir-sugeridos                 # suma capacitación y otros rubros sugeridos
python3 compras_agiles.py --diseno --dias 0 --md "../../claude/dd.mm.aaaa - COMPRAS AGILES DISENO JUNCOS.md"   # línea de diseño
```

- **Solo entran Compras Ágiles cuyos productos están en los rubros inscritos de JUNCOS.** Nicolás lo pidió el 19-10-2026. Las palabras clave ya no dejan pasar nada por sí solas: sirven para ordenar y como prefiltro por nombre, antes de bajar el detalle. `--incluir-sugeridos` suma los rubros que se recomendó inscribir, y `--todas` quita el filtro por rubro.
- En la región conviene `--sin-prefiltro`: revisa el detalle de todas las Compras Ágiles no excluidas y así no se escapa ninguna cuyo nombre no diga nada. Para todo el país no es viable (unos 17 segundos por detalle), y ahí se usa el prefiltro.
- Usa el mismo `perfil_juncos.json` que las licitaciones (rubros, palabras clave y exclusiones), más su bloque `compra_agil`. Ese bloque agrega:
  - palabras propias de las compras chicas, como charla, relator, jornada, clima laboral, redes sociales o infografía;
  - exclusiones de bienes y servicios ajenos al rubro, como alimentación, traslados, premiación, primeros auxilios o asesoría legal y contable;
  - señales de que el trabajo se puede hacer a distancia.
- **Puntaje:**
  - El peso de cada rubro que coincide con los productos pedidos.
  - 1 punto por palabra clave, hasta 6.
  - 2 puntos si es de la Región de Coquimbo.
  - 1 punto si se puede hacer a distancia.
- **Alertas que marca:** cierre en menos de 24 horas, servicio presencial fuera de la región, exigencia de OTEC, código SENCE o boleta de garantía, y segundo llamado.
- Descarta lo que cierra en menos de 3 horas (`--min-horas`). Por defecto mira las publicadas en los últimos 3 días (`--dias 0` trae todas las abiertas).
- Revisa a mano las 10 primeras. Si aparece ruido nuevo, agrégalo a `compra_agil.excluir_extra`.
- Anota en `seguimiento.md` las que vas a cotizar.

**Entregable:** `dd.mm.aaaa - COMPRAS AGILES AFINES JUNCOS.md`. Abre con las 3 a 5 que conviene cotizar ese día.

### CA2. Filtro de coherencia con el perfil

Cotiza solo lo que JUNCOS hace bien con su equipo, o con un apoyo menor subcontratado.

| Coherente | Solo si se resuelve la parte ajena | No corresponde |
|---|---|---|
| Encuestas breves y mediciones de satisfacción | Diseño con impresión de piezas, subcontratando la imprenta | Bienes, insumos y equipos |
| Talleres, charlas, capacitaciones y jornadas: liderazgo, participación, comunicación, habilidades transversales | Talleres presenciales fuera de la Región de Coquimbo, con el viático en el precio | Capacitaciones técnicas o normadas: primeros auxilios, extintores, conducción, trabajo en altura, manipulación de alimentos |
| Facilitación de cabildos, diálogos y jornadas participativas; sistematizaciones | Eventos en que JUNCOS solo pone el contenido y otro la producción | Cursos que exigen ser OTEC o tener código SENCE (no consta que JUNCOS sea OTEC) |
| Diagnósticos breves, informes, indicadores y evaluaciones acotadas | | Logística: alimentación, traslados, sonido, carpas y premiación |
| Diseño gráfico, piezas, infografías, identidad visual, contenidos y redes sociales | | Asesoría legal, contable, psicológica o médica |
| Monitoreo de prensa, minutas y presentaciones | | |

### CA2-bis. Línea de diseño gráfico, en licitaciones y Compras Ágiles (agregada el 20-10-2026 a pedido de Nicolás)

Nicolás quiere incluir **piezas de diseño con poco material**: pendones y roller, lanyards y credenciales, afiches, lienzos, pasacalles, dípticos y trípticos, invitaciones, diplomas y logos. JUNCOS diseña y encarga la impresión a una imprenta, idealmente de la Región de Coquimbo.

- **Rubros admitidos aunque no estén inscritos** (`compra_agil.diseno.rubros`): 82141500 Diseño (inscrito), 82101500 Publicidad impresa (letreros, carteles y pendones), 82121500 Impresión promocional o publicitaria y 60121900 Lienzos estampables. **En las Compras Ágiles reales del 20-10-2026, los pendones y lanyards venían con 82101501, 82101502 o 82121505, y casi nunca con 82141500.** Por eso conviene inscribir 82101500 y 82121500.
- **Se descartan por material** (`motivo_material`):
  - productos con más de 60 unidades;
  - montos sobre $2.000.000;
  - textos con merchandising (tazas, botellas, poleras, mochilas), cuadernos, agendas o libros, ploteo o brandeo de vehículos, letreros luminosos o insumos.
  - Se ajusta en `compra_agil.diseno` (`max_unidades`, `monto_max`, `excluir`).
- **Corre en las dos vías.**
  - Compras Ágiles: `compras_agiles.py --diseno`.
  - Licitaciones: `postulables.py --diseno` (junto a consultoría) o `--solo-diseno`.
  - Ambas usan el mismo bloque `compra_agil.diseno` del perfil.
  - En licitaciones, además, solo se aceptan los tipos **L1 y LE** (`tipos_licitacion`) y un monto estimado de hasta **$5.000.000** (`monto_max_licitacion`). Así se descartan los suministros grandes de impresión, por ejemplo un LR de impresión publicitaria.
- **Palabras por palabra completa:** las de diseño se comparan como palabra completa, con plural (`contar_d`). La lección del 20-10-2026: "logo" calzaba con "kinesiólogo", "diploma" con "diplomado" y "roller" con "cortinas roller". Se excluyen además "cortina" y "persiana".
- **Si la API no da el detalle** de una Compra Ágil cuyo nombre es de diseño, igual se muestra, con la alerta "revisar productos y cantidades en la plataforma".
- **Antes de cotizar:** pide precio a la imprenta (impresión, estructura del roller y despacho a la comuna de entrega). El margen está en el diseño. Una pieza suelta de $100.000 a $300.000 solo conviene si la imprenta y el despacho no se comen el precio.
- **Alertas:** el buscador marca "cotizar impresión y despacho" en todas, e "incluye instalación" cuando la piden (por ejemplo, lienzos con instalación y retiro).

### CA3. Decisión rápida

Puntúa cinco criterios de 0 a 2. Cotiza con 7 puntos o más. Con 5 o 6, cotiza solo si suma experiencia en un área que interesa: mientras la empresa no tenga ventas al Estado, cada orden de compra aceptada vale como antecedente.

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Afinidad (CA2) | No corresponde | Columna del medio | Coherente |
| Plazo de entrega que piden | No se alcanza | Ajustado | Holgado |
| Tiempo para cotizar | Menos de 3 horas | Entre 3 y 24 horas | Más de 24 horas |
| Precio posible frente al neto máximo | No cubre costos | Margen bajo | Margen razonable |
| Logística | Presencial lejos y sin apoyo | Presencial fuera de la región, con viático | Región de Coquimbo o a distancia |

### CA4. Cotización

1. Lee la solicitud completa en Mercado Público, en el escritorio de proveedor, menú Compra Ágil: descripción, productos, cantidades, plazo y lugar de entrega, adjuntos y criterios.
2. Calcula el precio neto con la estructura de `plantillas.md`, sección 2, en versión corta. Tiene que cubrir los costos y quedar bajo el neto máximo.
3. Genera la cotización formal con `/cotizacion` (logo, correlativo y validez de 10 días hábiles) y pásala a PDF para adjuntarla.
4. Redacta la descripción de la oferta con `plantillas.md`, sección 6.
5. Nicolás ingresa el precio, adjunta los archivos, firma la declaración jurada y envía. Revisa si la plataforma pide el precio neto o con impuestos, y que coincida con el PDF. Envía con margen y no a última hora.

### CA5. Después de cotizar

- **Si te seleccionan:** llega la orden de compra. Acéptala en la plataforma, porque eso formaliza la compra. Después entrega, pide la recepción conforme, factura y cobra a 30 días corridos.
- **Al terminar el trabajo:** pide la carta de certificación (`plantillas.md`, sección 4) y guarda la orden de compra. Las dos son experiencia acreditable para las licitaciones.
- **Si no te seleccionan:** anota en `seguimiento.md` quién ganó y a qué precio. Las órdenes de Compra Ágil aparecen en la API de órdenes de compra con el tipo AG.
- **Necesidad repetida:** si un organismo compra varias veces lo mismo y la suma del año pasa de 100 UTM, la directiva lo obliga a licitar. Anótalo como licitación probable.

## Documentos de la empresa que conviene tener siempre al día

| Documento | Vigencia típica exigida | Dónde se obtiene |
|---|---|---|
| Certificado de vigencia de la E.I.R.L. | 60 a 90 días | Registro de Empresas y Sociedades o Conservador de Bienes Raíces, según cómo se constituyó |
| Fotocopia legalizada del RUT de la empresa | No vence | Notaría |
| Certificado del Boletín de Informes Comerciales | 30 a 60 días | Cámara de Comercio de Santiago |
| Certificado de quiebras o convenio judicial | 30 a 60 días | Superintendencia de Insolvencia y Reemprendimiento |
| Declaración jurada del art. 4, inciso 6, Ley 19.886 (parentesco con directivos) | Por proceso | Formato de las bases |
| Certificado de deuda tributaria y de cumplimiento laboral (F30) | 30 días | SII y Dirección del Trabajo |
| Currículum del titular y del equipo | Actualizar cada semestre | Interno |
| Certificados de experiencia de clientes anteriores | No vencen | Pedirlos al cerrar cada trabajo |
| Código de ética o programa de integridad | Revisar cada año | `plantillas.md`, sección 3 |
