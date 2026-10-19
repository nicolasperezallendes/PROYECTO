# Proceso de postulación de JUNCOS E.I.R.L.

Ciclo completo, de la búsqueda al contrato. Cada etapa dice qué hace Claude, qué hace Nicolás y qué se entrega.

## Etapa 1. Búsqueda de oportunidades

**Frecuencia sugerida:** lunes y jueves. Las licitaciones LE suelen tener ciclos de unos 10 días entre publicación y cierre.

```bash
cd herramientas/mercadopublico
python3 postulables.py --max-detalle 100 --md "../../claude/dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md"
python3 postulables.py --region coquimbo --max-detalle 150     # foco regional
```

- El puntaje suma el peso de cada rubro que coincide, 1 punto por palabra clave (hasta 6) y 2 puntos si es de la Región de Coquimbo.
- Revisa las 10 primeras a mano. El filtro por nombre deja pasar ruido. Ejemplos: "diseño" trae diseños de ingeniería, y "capacitación" trae seguros o franquicias. Si aparece ruido nuevo, agrégalo a `excluir` en `perfil_juncos.json`.
- Descarta lo que cierra en menos de 3 días hábiles, salvo que sea muy simple (L1).
- Revisa también la **Compra Ágil** (compras de hasta 100 UTM con cotización simple). Es la vía más fácil para que una consultora nueva acumule historial con el Estado.
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
