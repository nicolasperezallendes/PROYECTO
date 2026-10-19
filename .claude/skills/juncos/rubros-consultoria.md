# Rubros de consultoría en Mercado Público

**Verificado el 19-10-2026.** Se revisaron en detalle 166 licitaciones activas del país con nombres de consultoría, asesoría, estudio, diagnóstico, encuesta, evaluación, investigación o capacitación (de un total de 4.964 activas). La tabla muestra en cuántas aparece cada categoría.

## Lo que muestran los datos

| Licitaciones | Código | Categoría | ¿JUNCOS la tiene? | Uso para JUNCOS |
|---|---|---|---|---|
| 24 | 80111500 | Consultorías para el desarrollo de recursos humanos | No | **Inscribir.** Es la más usada: capacitaciones municipales, de salud y de servicios públicos |
| 23 | 86111600 | Educación de adultos | Sí | Núcleo: capacitaciones y talleres |
| 20 | 102000000 | Consultoría (ChileCompra), producto 102101001 "Planificación y Factibilidad" | Sí | Baja: la usa sobre todo el MOP para consultorías de ingeniería, que normalmente piden inscripción en su Registro de Consultores |
| 12 | 80111700 | Contratación de personal | No | Ocasional: servicios profesionales a honorarios (por ejemplo, "profesional del área de ciencias sociales") |
| 9 | 80101500 | Consultoría en gestión de empresas | Sí | Núcleo |
| 7 | 80111600 | Servicios de personal temporal | No | Ocasional, igual que 80111700 |
| 6 | 80141600 | Ventas y marketing | Sí | Núcleo: campañas y comunicaciones |
| 4 | 93141500 | Desarrollo social | No | **Inscribir:** diagnósticos sociales y programas comunitarios |
| 3 | 80101600 | Gestión de proyectos | No | Útil para la gestión y el seguimiento de programas |
| 3 | 93142000 | Desarrollo urbano | No | **Inscribir:** planes maestros, Quiero Mi Barrio y planes reguladores (en alianza) |
| 3 | 80161500 | Servicios de apoyo a la gestión | No | Útil |
| 2 | 86111500 | Aprendizaje a distancia | No | Útil si se ofrecen cursos en línea |
| 1 | 80141500 | Investigación de mercados | No | **Inscribir:** encuestas y estudios de opinión |
| 1 | 81131500 | Metodología y análisis estadístico (incluye 81131504, encuestas por muestreo) | No | **Inscribir:** es el código de la licitación de encuestas de Las Condes |
| 1 | 93141700 | Cultura | No | Útil: mediación y programas culturales comunitarios |
| 1 | 86101700 | Formación profesional no científica | No | Útil para capacitación |
| 1 | 86141700 | Tecnología educativa | No | Opcional |
| 1 | 82101800 | Agencias de publicidad | No | Opcional, para campañas |
| 7 | 81101500 y otros 811xxxxx | Ingeniería (civil, de transportes, mecánica, etc.) | No | No corresponde |
| 1 | 77101500 | Evaluación de impacto ambiental | No | Solo en alianza (el componente social de un estudio de impacto) |

## Recomendación de rubros (19-10-2026)

**Inscribir (prioridad alta):** 80111500, 81131500, 80141500, 93141500 y 93142000.

**Inscribir si se quiere ampliar:** 80101600, 80161500, 86101700, 86111500 y 93141700.

**Mantener:** 80101500, 80141600, 82141500, 86111600, 86141500, 102000000 y 102106000. Las dos últimas no estorban, pero rinden poco.

**Quitar:** 30222300, 43223100, 47121900, 72131700 y 86121500.

**Compra Ágil:** la plataforma avisa las Compras Ágiles a las EMT según sus rubros inscritos. Inscribir los sugeridos también amplía esos avisos. `compras_agiles.py` usa los mismos pesos de rubro que `postulables.py`.

## Lo que todavía no se ha visto

- **El árbol completo de categorías propias de ChileCompra.** Bajo "Consultoría" (102xxxxxx) solo se conocen 102000000 (con el producto 102101001) y 102106000 "Arquitectura y Urbanismo". El resto del árbol solo aparece en el buscador "+ Agregar rubros" de Mi empresa, que requiere sesión iniciada.
- **El catálogo UNSPSC completo:** la muestra cubre lo que se licitaba ese día, no todo lo posible. Repite este conteo cada cierto tiempo con `python3 herramientas/mercadopublico/rubros_en_uso.py --md rubros.md`.
