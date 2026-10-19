---
name: juncos
description: "Ficha de JUNCOS E.I.R.L. (Consultores Nicolás Pérez Allendes E.I.R.L.) para Mercado Público: razón social, RUT, domicilio legal, habilidad, rubros inscritos y perfil de postulación. Úsala con /juncos o cuando se pida buscar licitaciones afines a la consultora, revisar sus rubros o completar datos de la empresa en una postulación."
---

# /juncos — Perfil de postulación de JUNCOS E.I.R.L.

## Ficha de la empresa (verificada el 19-10-2026 en Mercado Público, Mi empresa)

| Campo | Valor |
|---|---|
| Razón social | CONSULTORES NICOLÁS PÉREZ ALLENDES E.I.R.L. |
| Nombre de fantasía | JUNCOS E.I.R.L. |
| RUT | 78.390.884-0 |
| Tipo societario | Empresa Individual de Responsabilidad Limitada (persona jurídica) |
| Titular / representante legal | Nicolás Pérez Allendes |
| Domicilio legal (según SII) | Colón 352, oficina 318, edificio StudiOffice Colón, La Serena, Región de Coquimbo |
| Giro principal registrado (SII) | Compra, venta y alquiler (excepto amoblados) de inmuebles |
| Código de empresa en Mercado Público | 2103594 |
| Código de organización / sucursal principal | 1524491 |
| Estado de habilidad | HÁBIL |
| Inscripción en Registro de Proveedores | Contrato vigente hasta el 29-12-2026 |
| Unidades adicionales | No tiene |
| Teléfono y correo de contacto | PENDIENTE (pedírselos al usuario) |

Alertas que debes repetir cuando sean pertinentes:
- **Renovación:** la inscripción en el Registro de Proveedores vence el 29-12-2026. Avisa si una licitación se adjudica o firma después de esa fecha.
- **Giro:** el giro principal registrado (inmobiliario) no calza con una consultora. Si las bases exigen giro acorde, recomienda agregar en el SII la actividad 702000, 732000 o 722000, y luego actualizar los datos en Mercado Público.
- **Datos pendientes:** si falta un dato, pídeselo al usuario. No lo inventes.

## Rubros inscritos en Mercado Público (14, verificados el 19-10-2026)

| Código | Rubro | Coherencia |
|---|---|---|
| 80101500 | Servicios de consultoría en gestión de empresas | Núcleo |
| 80141600 | Ventas y marketing | Núcleo |
| 82141500 | Diseño | Núcleo |
| 86111600 | Educación de adultos | Núcleo |
| 86141500 | Servicios de orientación educacional | Núcleo |
| 43232300 | Software de consultas y gestión de datos | Secundario |
| 52161600 | Accesorios de equipos audiovisuales | Secundario |
| 102000000 | Consultoría (categoría ChileCompra) | Genérico |
| 102106000 | Arquitectura y Urbanismo (categoría ChileCompra) | Genérico |
| 30222300 | Construcciones para educación e investigación | Sin relación, se sugirió quitarlo |
| 43223100 | Componentes y equipos de infraestructura de redes móviles y digitales | Sin relación, se sugirió quitarlo |
| 47121900 | Accesorios de equipos de limpieza | Sin relación, se sugirió quitarlo |
| 72131700 | Construcción de obras civiles y infraestructuras | Sin relación, se sugirió quitarlo |
| 86121500 | Escuelas de educación primaria y secundaria | Sin relación, se sugirió quitarlo |

Rubros que se sugirió inscribir: 80141500 Investigación de mercados, 81131500 Metodología y análisis, 93141500 Desarrollo social, 93142000 Desarrollo urbano, 86101700 Capacitación, 86132000 Educación en gestión, 80161500 Apoyo gerencial y 82101500 Publicidad.

Si el usuario cambia sus rubros, actualiza esta tabla y `herramientas/mercadopublico/perfil_juncos.json`. En el JSON, los campos `inscrito` y `peso` siguen esta regla: 5 = núcleo, 3 = sugerido o no inscrito, 2 = secundario, y los rubros sin relación no puntúan. Pon la nueva fecha en `estado_rubros`.

## Buscar licitaciones afines

Requiere el ticket de la API en `MERCADOPUBLICO_TICKET` o en `herramientas/mercadopublico/.env`. Nunca subas el ticket a git.

```bash
cd herramientas/mercadopublico
python3 postulables.py --max-detalle 100 --md "../../claude/dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md"
python3 postulables.py --region coquimbo
python3 postulables.py --min-monto 5000000
```

Para revisar la ficha completa de una licitación (requisitos, garantías, plazos): `python3 mercadopublico.py licitacion CODIGO`.

## Analizar una licitación (método probado el 19-10-2026)

Fuentes públicas, en este orden:
1. **Ficha web pública y foro:** `python3 mercadopublico.py ficha-web CODIGO --md ficha.md`. Trae el resumen de las bases que publica el portal: características, organismo, plazos, antecedentes, requisitos para contratar, criterios de evaluación con su peso, monto, garantías, cláusulas y demandas. También trae las preguntas y respuestas del foro.
2. **API:** `python3 mercadopublico.py licitacion CODIGO`. Entrega productos con su código UNSPSC, fechas, responsables y la justificación del monto.
3. **Bases en PDF y anexos:** NO se pueden bajar de forma automática. La página `ViewAttachment.aspx` está protegida con reCAPTCHA Enterprise, y no se intenta saltar ese control (ni llamando directo a `ViewAttachmentLC.aspx` ni con navegadores automatizados). Pídele al usuario que los descargue desde el botón "Ver adjuntos" de la ficha y los suba a la conversación.
4. **OCDS** (`https://apis.mercadopublico.cl/OCDS/data/record/CODIGO`): las licitaciones recientes suelen no aparecer aún (devuelve 404).

El análisis se entrega en `claude/dd.mm.aaaa - ANALISIS LICITACION CODIGO NOMBRE CORTO.md` y lleva:
- Veredicto: postular o no, y bajo qué condiciones.
- Datos clave.
- Calendario, con el día de la semana verificado (`date -d AAAA-MM-DD +%A`).
- Tabla de criterios con su peso y qué significa cada uno para JUNCOS.
- Documentos para ofertar y para contratar.
- Riesgos: giro SII, vencimiento del registro, distancia y comportamiento de pago del organismo.
- Lo que falta leer en las bases.
- Plan día a día hasta el cierre.

El ejemplo de referencia es el análisis de 564953-79-LE26 del 19-10-2026.

## Cómo entregar el resultado

- Guarda el informe en `claude/` con el formato de nombre `dd.mm.aaaa - LICITACIONES AFINES JUNCOS.md`. Usa siempre Markdown, nunca .docx.
- Abre con 3 a 5 recomendaciones en lenguaje simple: qué es, quién la licita, cuánto vale, cuándo cierra y por qué calza con JUNCOS. El ejemplo de referencia es el informe del 19-10-2026.
- Prioriza en este orden: encuestas, estudios, diagnósticos sociales y territoriales, participación ciudadana, indicadores y evaluación de programas, capacitación y comunicaciones.
- Cuando el proceso exige un equipo grande (planes reguladores, campañas de medios millonarias), sugiere entrar en alianza mediante una unión temporal de proveedores.
- Marca lo que cierra en menos de 3 días hábiles. Señala los montos en UF o USD. Indica si no hay oportunidades en la Región de Coquimbo.
- Repite las alertas de la ficha que apliquen (renovación, giro).
