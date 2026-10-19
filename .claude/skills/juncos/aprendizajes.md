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
- **Códigos de rubro:** los productos usan UNSPSC de 8 dígitos. ChileCompra tiene además categorías propias de 9 dígitos (por ejemplo, 102000000 Consultoría), que no calzan con los productos licitados y no sirven para puntuar.
- **Unidades de la Municipalidad de Coquimbo:** 2446 es la municipal central y 2448 el Departamento de Salud (organismo 87901).
- **Ruido conocido del filtro por nombre:** "diseño" trae ingeniería y arquitectura, como puentes, ciclovías, paraderos, plazas y edificios. "Capacitación" trae franquicias y seguros. Ya están en `excluir`.

## Portal web

- **La ficha pública de la licitación** (`DetailsAcquisition.aspx`) es HTML normal y trae el resumen de las bases. Se lee con `mercadopublico.py ficha-web`. Lo mismo vale para el foro (`/Foros/.../PublicView.aspx`).
- **Los adjuntos** (`Attachment/ViewAttachment.aspx`) están protegidos con reCAPTCHA Enterprise. **No se evade:** ni llamando directo a `ViewAttachmentLC.aspx`, ni con navegadores automatizados, ni con servicios para resolver CAPTCHAs como CapSolver. El usuario ya lo pidió dos veces y se rechazó: es un control de acceso del sitio y arriesga bloqueos para la empresa. La vía es que Nicolás descargue los archivos desde "Ver adjuntos" y los suba, o que se use Claude en Chrome en una sesión en su computador, donde el navegador hace la verificación normal y él resuelve el desafío si aparece.
- **OCDS** (`apis.mercadopublico.cl/OCDS/data/record/CODIGO`): las licitaciones recientes aún no aparecen (devuelve 404).
- **La ficha pública del proveedor** (`proveedor.mercadopublico.cl/ficha/2103594`) se arma con JavaScript y casi no trae datos. No muestra los rubros.
- **Los rubros y los datos internos de la empresa** solo se ven con sesión iniciada (Mi empresa). El 19-10-2026 se leyeron con un enlace de sesión que entregó el usuario. Funcionó solo cuando él aprobó el comando con el modo de permisos fuera de "Auto". Después se borró de inmediato el enlace y todo lo capturado, que incluía una consulta de cuentas bancarias. Repetir solo con autorización explícita, solo lectura y borrando todo al terminar.
- **Certificados del entorno:** nunca desactives la verificación TLS (`--ignore-certificate-errors`). El navegador del entorno ya confía en el certificado del proxy.

## Entorno de trabajo

- Las sesiones en la nube **no pueden usar el Chrome del usuario**. Para eso hay que trabajar en la app de escritorio o con `claude remote-control` en su computador, con la extensión Claude en Chrome conectada.
- El trabajo se guarda con commits y push en la rama del proyecto. Lo que queda solo en el contenedor se pierde.

## Proceso y redacción

- **Verifica siempre el día de la semana** de cada fecha con `date -d AAAA-MM-DD +%A`. El 19-10-2026 se escribió "jueves 23" cuando era viernes, y hubo que corregir dos informes.
- **Conteos:** revisa los totales contra la tabla antes de entregar. Hubo que corregir "cuatro" por "tres" procesos sin monto.
- Los informes abren con la conclusión y las recomendaciones, y el detalle va después.
- No inventes datos de la empresa: pídeselos al usuario. El correo del usuario no se escribe en documentos sin que él lo entregue para ese fin.
- Cuando una vía falla o se bloquea, dilo claro, explica la alternativa y sigue con lo que sí se puede hacer. No rellenes con datos supuestos.
