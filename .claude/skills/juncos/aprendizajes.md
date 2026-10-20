# Lecciones aprendidas (técnicas y de proceso)

Léelas antes de usar las herramientas. Cada lección nueva se agrega con su fecha.

## API de Mercado Público

- **Ticket:** se lee de `MERCADOPUBLICO_TICKET` o de `herramientas/mercadopublico/.env`. Nunca se sube a git: `.env` está en `.gitignore`. Las sesiones en la nube son efímeras, así que lo ideal es que el usuario lo guarde como variable de entorno del entorno de trabajo.
- **No acepta consultas simultáneas** (error 10500). El script consulta de una en una, con una pausa de 1 segundo y reintentos.
- **Velocidad:** cada ficha de detalle tarda entre 2 y 3 segundos. Revisar 100 licitaciones toma unos 4 minutos.
- **Cupo diario limitado:** no se bajan todas las fichas del país. Primero se filtra por nombre y luego se revisa el detalle de las mejores.
- **El listado trae los nombres cortados** (unos 50 caracteres). El nombre completo y la descripción están en el detalle.
- **Monedas:** `Moneda` puede ser CLP, CLF (que es UF) o USD. Por ejemplo, 3.400 en CLF son 3.400 UF, no $3.400.
- **Montos ocultos:** con `VisibilidadMonto` igual a 0, el monto no se publica. Hay que decir "no publica", no "$0".
- **Códigos de rubro:** los productos usan UNSPSC de 8 dígitos, pero también hay categorías propias de ChileCompra de 9 dígitos que **sí aparecen en las licitaciones**. Se había supuesto lo contrario y se corrigió el 19-10-2026. Por ejemplo, la categoría 102000000 "Consultoría", con el producto 102101001 "Planificación y Factibilidad", aparece en unas 20 de cada 166 licitaciones de consultoría, casi todas del MOP y de ingeniería. `postulables.py` compara cada código solo con códigos de su mismo largo.
- **Cómo revisar qué rubros se usan:** baja el detalle de las licitaciones activas cuyo nombre tenga consultoría, asesoría, estudio, diagnóstico, encuesta, evaluación, investigación o capacitación (sin obras ni suministros), y cuenta los `CodigoCategoria` de sus ítems. Lo hace `rubros_en_uso.py` en unos 7 minutos. El resultado del 19-10-2026 está en `rubros-consultoria.md`.
- **Unidades de la Municipalidad de Coquimbo:** 2446 es la municipal central y 2448 el Departamento de Salud (organismo 87901).
- **Ruido conocido del filtro por nombre:** "diseño" trae ingeniería y arquitectura, como puentes, ciclovías, paraderos, plazas y edificios. "Capacitación" trae franquicias y seguros. Ya están en `excluir`.

## API de Compra Ágil (v2, beta)

Agregado el 19-10-2026, a partir de chilecompra.cl/api y de la documentación en PDF de mayo de 2026.

- **Existe desde el 22-05-2026.** Antes, la API v1 no traía las solicitudes de cotización de Compra Ágil (ChileCompra lo confirmó en febrero de 2025). Ahora tiene su propia API, en versión beta.
- **Rutas:** la base es `https://api2.mercadopublico.cl`. El listado está en `/v2/compra-agil` y el detalle en `/v2/compra-agil/{codigo}` (los códigos son del tipo `1195-39-COT26`). La guía también usa `/v2/compraagil`, sin guion, y `compras_agiles.py` prueba las dos.
- **Ticket:** va en el header `ticket`, no en la URL. Se pide en chilecompra.cl/api con Clave Única. **Confirmado el 19-10-2026: el ticket de JUNCOS sirve también para esta API.**
- **Estados:** `publicada` (abierta y recibiendo cotizaciones), `cerrada`, `desierta`, `cancelada` y `proveedor_seleccionado`.
- **Filtros:** estado, región, texto (`q`, sin probar todavía) y fechas en ISO-8601 (`publicado_desde`). **Región verificada: Coquimbo es 4.** No hay filtro por producto, rubro ni organismo: `codigo_producto` y `rubro` devuelven 400 con "Parámetros no permitidos". La API rechaza cualquier parámetro desconocido con ese error, lo que sirve para probar nombres.
- **Paginación (probada el 19-10-2026):** acepta de 10 a 50 registros por página, pero **con 25 o 50 se cae siempre por tiempo** (504 "Endpoint request timed out" a los 29 segundos). Con 10 responde en 15 a 28 segundos. El script usa 10 y reintenta los 504. Sin `estado` también falla (500).
- **Volumen y tiempo:** un día normal hay unas 7.000 Compras Ágiles publicadas en el país y unas 3.400 de los últimos 3 días. En la Región de Coquimbo hay unas 280 abiertas y unas 130 de los últimos 3 días. **Cada detalle tarda unos 17 segundos.** Revisar todas las de Coquimbo de 3 días toma cerca de 40 minutos. Para todo el país hay que usar el prefiltro por nombre.
- **Duplicados:** la paginación puede repetir una Compra Ágil si se publican nuevas mientras se recorre. El script las elimina por código.
- **Productos:** `productos_solicitados[].codigo_producto` es un entero **UNSPSC de 8 dígitos** (por ejemplo, 90111604 "Salones"), así que calza con los rubros del perfil.
- **Filtro por rubros (pedido por Nicolás el 19-10-2026):** solo se proponen Compras Ágiles cuyos productos están en los rubros **inscritos** de JUNCOS (`compra_agil.solo_rubros: true`). Con `--incluir-sugeridos` se suman los rubros sugeridos, y con `--todas` se vuelve al filtro solo por palabras clave. Ojo: capacitación (80111500) aún no está inscrita, así que sin `--incluir-sugeridos` esas Compras Ágiles no aparecen.
- **Cuota diaria por ticket:** al agotarse responde 429, y se reinicia al cambiar el día. Por eso el script filtra por nombre antes de bajar detalles, y por defecto solo mira las publicadas en los últimos 3 días.
- **Monto:** `monto_disponible_clp` está en `montos` en el listado y en `presupuesto` en el detalle. Incluye impuestos.
- **Campos del detalle (verificados):** codigo, convocatoria, descripcion, documentos, entrega, estado, fechas, flags, id_orden_compra, institucion, motivos, nombre, presupuesto, productos_solicitados, proveedores_cotizando y resumen.
- **Sin confirmar todavía:**
  - el enlace público a la ficha de cada Compra Ágil;
  - si la API muestra el plazo para aceptar la orden de compra;
  - si el detalle de algunas Compras Ágiles falla siempre. La de clima laboral 1317954-9-COT26 dio 504 en todos los intentos del 19-10-2026, mientras otras respondían.
- **Filtro de texto `q` (probado el 19-10-2026): funciona y es rápido**, unos 10 segundos por página. Es la mejor forma de buscar: `compras_agiles.py --q "clima,estudio,encuesta,diagnostico,capacitacion,taller,charla"`. Recorrer una región entera sin `q` toma casi una hora.
- **Adjuntos de Compra Ágil:** la API solo da `id` y `nombre`, no el archivo. El buscador público (`buscador.mercadopublico.cl`) responde 403 desde la nube (firewall de CloudFront). No se intenta saltar. Los adjuntos los baja Nicolás desde su escritorio de proveedor, menú Compra Ágil, y los sube a la conversación.
- **Cortes de conexión:** la API a veces corta la conexión a mitad de la respuesta (ConnectionResetError). `compras_agiles.py` ya los reintenta, pero un recorrido largo puede perderse si se cae. Prefiere `--q`.
- **Pruebas:** `compras_agiles.py` se probó el 19-10-2026 contra una API simulada, no contra la real. La sesión del chat de claude.ai no tenía red hacia mercadopublico.cl ni ticket.
- **Las órdenes de compra de Compra Ágil** aparecen en la API v1 de órdenes con el tipo AG. Sirven para ver quién ganó y a qué precio.
- **Alertas por palabra completa (20-10-2026):** la alerta "pide otec" saltaba en todas las Compras Ágiles de Sercotec, porque "Sercotec" contiene "otec". Ahora `alertas_texto` se compara por palabra completa (`contar_d`), igual que las palabras de diseño.

## Portal web

- **La ficha pública de la licitación** (`DetailsAcquisition.aspx`) es HTML normal y trae el resumen de las bases. Se lee con `mercadopublico.py ficha-web`. Lo mismo vale para el foro (`/Foros/.../PublicView.aspx`).
- **Los adjuntos** (`Attachment/ViewAttachment.aspx`) están protegidos con reCAPTCHA Enterprise. **No se evade:** ni llamando directo a `ViewAttachmentLC.aspx`, ni con navegadores automatizados, ni con servicios para resolver CAPTCHAs como CapSolver. El usuario ya lo pidió dos veces y se rechazó: es un control de acceso del sitio y arriesga bloqueos para la empresa. La vía es que Nicolás descargue los archivos desde "Ver adjuntos" y los suba, o que se use Claude en Chrome en una sesión en su computador, donde el navegador hace la verificación normal y él resuelve el desafío si aparece.
- **OCDS** (`apis.mercadopublico.cl/OCDS/data/record/CODIGO`): las licitaciones recientes aún no aparecen (devuelve 404).
- **La ficha pública del proveedor** (`proveedor.mercadopublico.cl/ficha/2103594`) se arma con JavaScript y casi no trae datos. No muestra los rubros.
- **Los rubros y los datos internos de la empresa** solo se ven con sesión iniciada (Mi empresa). El 19-10-2026 se leyeron con un enlace de sesión que entregó el usuario. Funcionó solo cuando él aprobó el comando con el modo de permisos fuera de "Auto". Después se borró de inmediato el enlace y todo lo capturado, que incluía una consulta de cuentas bancarias. Repetir solo con autorización explícita, solo lectura y borrando todo al terminar.
- **Certificados del entorno:** nunca desactives la verificación TLS (`--ignore-certificate-errors`). El navegador del entorno ya confía en el certificado del proxy.

## Entorno de trabajo

- **El acceso a mercadopublico.cl depende de la sesión.** En una sesión en la nube del 19-10-2026 la red no llegaba a mercadopublico.cl. En otra del mismo día (rama `claude/stoic-darwin-gi9n29`) la API y la ficha pública funcionaron sin problema. En el chat del proyecto JUNCOS en claude.ai, también el 19-10-2026, no hubo red hacia `api.mercadopublico.cl` ni hacia `api2.mercadopublico.cl`. Prueba primero con `python3 mercadopublico.py organismos coquimbo`. Si falla por red, lee la ficha y el foro con Claude en Chrome o corre los scripts en el computador del usuario.
- **Para hacer push**, el repositorio `nicolasperezallendes/PROYECTO` tiene que estar agregado como fuente de la sesión, con permiso de escritura. Si no lo está, entrega los archivos por el chat y avisa que el commit quedó solo en el entorno. Así se perdieron el programa de integridad y el borrador de propuesta de 564953-79-LE26 del 19-10-2026: se hicieron en otra sesión y no llegaron a GitHub.
- Las sesiones en la nube **no pueden usar el Chrome del usuario**. Para eso hay que trabajar en la app de escritorio o con `claude remote-control` en su computador, con la extensión Claude en Chrome conectada.
- El trabajo se guarda con commits y push en la rama del proyecto. Lo que queda solo en el contenedor se pierde.

## Proceso y redacción

- **Verifica siempre el día de la semana** de cada fecha con `date -d AAAA-MM-DD +%A`. El 19-10-2026 se escribió "jueves 23" cuando era viernes, y hubo que corregir dos informes.
- **Conteos:** revisa los totales contra la tabla antes de entregar. Hubo que corregir "cuatro" por "tres" procesos sin monto.
- Los informes abren con la conclusión y las recomendaciones, y el detalle va después.
- No inventes datos de la empresa: pídeselos al usuario. El correo del usuario no se escribe en documentos sin que él lo entregue para ese fin.
- Cuando una vía falla o se bloquea, dilo claro, explica la alternativa y sigue con lo que sí se puede hacer. No rellenes con datos supuestos.
- **Compra Ágil con pauta propia (19-10-2026):** el adjunto de una Compra Ágil puede traer criterios de evaluación propios (en EPCO: precio 40%, experiencia del consultor 40% y metodología 20%) y **fechas distintas a las de la plataforma**. Cuando no coinciden, envía en la fecha más temprana. En estos casos la experiencia suele ser **del consultor o del equipo**, así que la trayectoria de Nicolás sí cuenta.
