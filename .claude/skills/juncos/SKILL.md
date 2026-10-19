---
name: juncos
description: "Memoria y método de postulación de JUNCOS E.I.R.L. (Consultores Nicolás Pérez Allendes E.I.R.L.) en Mercado Público: ficha de la empresa, rubros, búsqueda de licitaciones y compras ágiles afines, análisis de bases, decisión de postular o cotizar, armado de ofertas, seguimiento y lecciones aprendidas. Úsala con /juncos o cuando se pida buscar, analizar o preparar una licitación o una compra ágil para la consultora, revisar sus rubros o completar datos de la empresa."
---

# /juncos — Postulación de JUNCOS E.I.R.L. a compras públicas

Esta skill es la memoria de trabajo de la consultora en Mercado Público. Cubre dos vías: las licitaciones y las Compras Ágiles (hasta 100 UTM). Antes de actuar, lee el archivo que corresponda a la tarea:

| Archivo | Cuándo leerlo | Sección del informe del proyecto |
|---|---|---|
| `proceso-postulacion.md` | Cualquier tarea del ciclo: buscar, decidir si postular, analizar bases, armar la oferta, enviarla y hacer seguimiento. Al final trae la ruta corta de Compra Ágil | 2.2 |
| `seguimiento.md` | Al empezar cada sesión: licitaciones y Compras Ágiles en curso, tareas pendientes de la empresa y su estado. **Actualízalo al terminar** | 2.3 |
| `aprendizajes.md` | Antes de usar las herramientas: límites técnicos (incluida la API de Compra Ágil), errores ya cometidos y lo que no se debe intentar | 2.4 |
| `plantillas.md` | Al redactar una propuesta técnica, un presupuesto, un código de integridad, una carta de experiencia o la descripción de una cotización de Compra Ágil | 2.5 |
| `rubros-consultoria.md` | Al revisar o ampliar los rubros inscritos, o al ajustar `perfil_juncos.json` | 2.6 |
| `perfil_juncos.json` | Al buscar licitaciones o Compras Ágiles, o al ajustar pesos, palabras clave y exclusiones | Parte 1 (copia exacta del JSON) |

## Dónde están esos archivos

Hay dos copias con el mismo contenido:

1. **Repositorio `nicolasperezallendes/PROYECTO`.** Los cinco archivos de apoyo están en `.claude/skills/juncos/`. Los scripts, su `README.md` y `perfil_juncos.json` están en `herramientas/mercadopublico/`: `postulables.py` para licitaciones y `compras_agiles.py` para Compra Ágil. Es la fuente principal y el único lugar donde corren los scripts.
2. **Proyecto JUNCOS de claude.ai.** Es el informe más reciente de `claude/licitaciones-juncos/`, con el nombre `dd.mm.aaaa - INFORME PERFIL Y SKILL JUNCOS.md`. Al 19-10-2026 es `claude/licitaciones-juncos/19.10.2026 - INFORME PERFIL Y SKILL JUNCOS.md`. Trae una copia textual del perfil (Parte 1) y de los seis archivos de la skill (Parte 2). Los títulos internos están dos niveles más abajo.

**Si un archivo de la tabla no está junto a este SKILL.md** (pasa en los chats de claude.ai, donde la skill llega sola), no lo des por inexistente ni lo rehagas de memoria. Abre el informe del proyecto con la herramienta Projects: `project_info` muestra cuál es el más reciente y `project_read` lo abre. Después usa la sección que indica la tabla.

Si el repositorio y el informe no coinciden, manda el de fecha más reciente. Avísale a Nicolás qué difiere.

### Cómo mantener las dos copias al día

- Cuando cambien la skill, el perfil o el seguimiento en el repositorio, genera el informe de nuevo con la fecha del día. Súbelo al proyecto, en `claude/licitaciones-juncos/`, con `project_write`.
- En un chat sin el repositorio, guarda los cambios en el informe del proyecto. Si son del mismo día, reemplaza la sección que cambió en el mismo archivo. Si son de otro día, crea un informe nuevo con la fecha del día. Avisa que GitHub queda atrasado hasta el próximo push.
- Para correr los scripts o hacer push desde claude.ai, agrega el repositorio a la sesión, con permiso de escritura si vas a hacer push. Si no se puede, trabaja con lo que trae el informe y dilo.

Si el usuario pega una versión distinta de esta skill (por ejemplo, de otra sesión), integra lo nuevo en el archivo que corresponda sin perder lo que ya existe, y avisa qué contenido no coincide con lo verificado.

## Ficha de la empresa (verificada el 19-10-2026 en Mercado Público, Mi empresa)

| Campo | Valor |
|---|---|
| Razón social | CONSULTORES NICOLÁS PÉREZ ALLENDES E.I.R.L. |
| Nombre de fantasía | JUNCOS E.I.R.L. |
| RUT | 78.390.884-0 |
| Tipo societario | Empresa Individual de Responsabilidad Limitada (persona jurídica) |
| Titular / representante legal | Nicolás Pérez Allendes, sociólogo |
| Domicilio legal (según SII) | Colón 352, oficina 318, edificio StudiOffice Colón, La Serena, Región de Coquimbo |
| Giro principal registrado (SII) | Compra, venta y alquiler (excepto amoblados) de inmuebles |
| Código de empresa en Mercado Público | 2103594 |
| Código de organización / sucursal principal | 1524491 |
| Estado de habilidad | HÁBIL |
| Inscripción en Registro de Proveedores | Contrato vigente hasta el 29-12-2026 |
| Acreditación en Mercado Público | Sin acreditación vigente (ficha pública) |
| Declaración jurada de socios y beneficiarios | No ingresada (ficha pública) |
| Sellos (Empresa Mujer u otros) | No tiene |
| Tamaño de empresa (EMT) en Mercado Público | PENDIENTE de verificar. Define si puede cotizar en el primer llamado de Compra Ágil |
| Historial de ventas al Estado | Sin registros a octubre de 2026 |
| Unidades adicionales | No tiene |
| Teléfono y correo de contacto | PENDIENTE (pedírselos al usuario) |
| Logo, paleta y generador de documentos | En el proyecto JUNCOS de claude.ai (skills `/cotizacion`, `/orden`, `/presentacion-juncos`) |

**Si falta un dato, pídeselo al usuario. No lo inventes.** Cuando cambie algún dato, actualiza esta tabla con la fecha de verificación.

### Alertas permanentes (repítelas cuando apliquen)

1. **Renovación del registro:** vence el 29-12-2026. Avisa si una adjudicación, un contrato o una entrega de Compra Ágil cae después de esa fecha.
2. **Giro en el SII:** el giro principal registrado (inmobiliario) no calza con una consultora. Si las bases exigen giro acorde, recomienda agregar la actividad 702000 (consultoría de gestión), 732000 (estudios de mercado y encuestas de opinión pública) o 722000 (investigación en ciencias sociales), y luego usar "Actualizar con la versión más reciente" en Mercado Público.
3. **Experiencia:** la empresa no registra ventas al Estado. En criterios de experiencia hay que revisar si las bases aceptan la del titular o la del equipo, con certificados de clientes, contratos u órdenes de compra. Las Compras Ágiles son la vía más rápida para empezar a acumularla.
4. **Puntos que hoy se pierden:** Sello Empresa Mujer y, si no se prepara, el programa de integridad.
5. **Compra Ágil y EMT:** el primer llamado es solo para Empresas de Menor Tamaño. Mientras no se confirme que JUNCOS figura como EMT, avisa este riesgo cada vez que recomiendes cotizar una.

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
| 102000000 | Consultoría (categoría ChileCompra; producto 102101001 "Planificación y Factibilidad") | Secundario: aparece en muchas licitaciones, pero casi todas son de ingeniería del MOP |
| 102106000 | Arquitectura y Urbanismo (categoría ChileCompra) | Secundario |
| 30222300 | Construcciones para educación e investigación | Sin relación, se sugirió quitarlo |
| 43223100 | Componentes y equipos de infraestructura de redes móviles y digitales | Sin relación, se sugirió quitarlo |
| 47121900 | Accesorios de equipos de limpieza | Sin relación, se sugirió quitarlo |
| 72131700 | Construcción de obras civiles y infraestructuras | Sin relación, se sugirió quitarlo |
| 86121500 | Escuelas de educación primaria y secundaria | Sin relación, se sugirió quitarlo |

**Se sugirió inscribir** (verificar el nombre exacto en el buscador de rubros; el detalle está en `rubros-consultoria.md`):
- **80111500 Consultorías para el desarrollo de recursos humanos.** Es la categoría más usada en capacitación y en los servicios de consultoría del Estado.
- 80141500 Investigación de mercados
- 81131500 Metodología y análisis (incluye 81131504, encuestas por muestreo)
- 93141500 Desarrollo social
- 93142000 Desarrollo urbano
- 86101700 Capacitación
- 86132000 Educación en gestión
- 80161500 Apoyo gerencial
- 82101500 Publicidad

Si el usuario cambia sus rubros, actualiza esta tabla y `perfil_juncos.json`. En el JSON, `peso` vale 5 para el núcleo, 4 para el sugerido de alta prioridad (80111500), 3 para los demás sugeridos o no inscritos y 2 para los secundarios. Los rubros sin relación no puntúan. Pon la nueva fecha en `estado_rubros`.

## Especialidades de la consultora (en orden de prioridad para postular)

1. Encuestas, estudios de opinión y de satisfacción usuaria.
2. Estudios y diagnósticos sociales, territoriales y comunitarios (planes maestros de barrio, líneas base, caracterizaciones).
3. Participación ciudadana, PLADECO y políticas comunales.
4. Diseño de indicadores, seguimiento y evaluación de programas públicos.
5. Capacitación, talleres y educación de adultos.
6. Comunicaciones: estrategia, monitoreo de prensa, minutas, presentaciones, diseño de piezas y campañas de escala acotada.

Las campañas de medios millonarias y los planes reguladores solo se abordan en alianza, mediante una Unión Temporal de Proveedores (UTP), con JUNCOS a cargo del componente social o comunicacional. En Compra Ágil vale lo mismo, pero a escala chica: se cotiza lo que calza con estas especialidades. El filtro está en `proceso-postulacion.md`, CA2.

## Formato de entrega (preferencias del usuario)

- Todo en **Markdown**, nunca en .docx (salvo los documentos que el generador de JUNCOS produce por diseño, como la cotización de `/cotizacion`).
- Los archivos van en `claude/` con el nombre `dd.mm.aaaa - TIPO NOMBRE.md`.
- Redacción en español natural y directo, que no suene a texto automático. Primero la conclusión, después el detalle.
- Siempre con datos frescos consultados el mismo día y con la fuente y la hora de la consulta.
- Cada mañana de trabajo parte con `seguimiento.md` (en claude.ai, la sección 2.3 del informe más reciente). De lunes a viernes, sigue con la búsqueda de Compra Ágil.
