/**
 * Lee las bases de una licitación con el motor de análisis de Telicito.cl y entrega un informe en Markdown.
 *
 * Este archivo NO contiene código de Telicito: solo llama a sus funciones. Se ejecuta desde la carpeta del
 * repositorio privado `licitia` (ver leer_bases.sh), que tiene que estar clonado y preparado.
 *
 *   bash herramientas/telicito/leer_bases.sh bases.pdf anexos.zip --md "claude/dd.mm.aaaa - LECTURA BASES CODIGO.md"
 *
 * Acepta PDF, Word, Excel, imágenes, texto y ZIP con varios adjuntos. Todo corre en la máquina: el modo de
 * reglas no envía los documentos a ningún proveedor de IA.
 */
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const telicito = (rel: string) => import(pathToFileURL(path.join(process.cwd(), "src/lib", rel)).href);

// Orden del informe: primero lo que deja fuera la oferta, después lo que hay que preparar.
const ORDEN = [
  "causal_rechazo", "garantia", "criterio_evaluacion", "documento_requerido", "requisito",
  "plazo", "lugar", "pago", "multa", "obligacion_post", "riesgo_contractual", "pregunta",
] as const;
const ETAPA: Record<string, string> = { oferta: "al ofertar", contratacion: "al contratar", ejecucion: "en la ejecución" };
const una = (s: string, max = 420) => {
  const t = s.replace(/\s+/g, " ").replace(/\|/g, "/").trim();
  return t.length <= max ? t : `${t.slice(0, max)}…`;
};

async function main() {
  const args = process.argv.slice(2);
  const base = process.env.LEER_BASES_CWD ?? process.cwd();
  let salida: string | null = null;
  let salidaJson: string | null = null;
  const archivos: string[] = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--md") salida = path.resolve(base, args[++i] ?? "");
    else if (args[i] === "--json") salidaJson = path.resolve(base, args[++i] ?? "");
    else if (!args[i].startsWith("--")) archivos.push(path.resolve(base, args[i]));
  }
  if (!archivos.length) {
    console.error("Uso: leer_bases.sh ARCHIVO [ARCHIVO...] [--md salida.md] [--json salida.json]");
    process.exit(2);
  }

  const { extractFile } = await telicito("documents/extract");
  const { detectAndValidate } = await telicito("documents/validation");
  const { isZip, expandZip } = await telicito("documents/archive");
  const { classifyTenderDocument } = await telicito("documents/classify");
  const { kindLabel } = await telicito("documents/kinds");
  const { analyzeWithRules, describeOmitted, RULES_ENGINE_VERSION } = await telicito("analysis/heuristic");
  const { verifyFindings } = await telicito("analysis/citations");
  const { FINDING_KIND_LABELS } = await telicito("analysis/types");

  const MB = 1024 * 1024;
  const entradas: Array<{ name: string; buffer: Buffer }> = [];
  const avisos: string[] = [];
  for (const archivo of archivos) {
    const buffer = readFileSync(archivo);
    if (isZip(buffer) && /\.zip$/i.test(archivo)) {
      const { entries, skipped } = expandZip(buffer, { maxEntries: 80, maxEntryBytes: 200 * MB, maxTotalBytes: 600 * MB });
      entradas.push(...entries);
      for (const s of skipped) avisos.push(`No se leyó «${s.name}» (dentro de ${path.basename(archivo)}): ${s.reason}`);
    } else {
      entradas.push({ name: path.basename(archivo), buffer });
    }
  }

  const fuentes: any[] = [];
  const lectura: string[] = [];
  for (const [n, e] of entradas.entries()) {
    try {
      const { mime, name } = await detectAndValidate(e.buffer, e.name, 200 * MB);
      const ext = await extractFile(e.buffer, mime);
      const inicio = ext.pages.slice(0, 2).map((p: any) => p.text).join("\n");
      const tipo = classifyTenderDocument(name, inicio);
      const s = ext.summary;
      const unidad = s.unit === "pagina" ? "páginas" : s.unit === "hoja" ? "hojas" : "bloques";
      lectura.push(
        `| ${una(name, 90)} | ${kindLabel(tipo.kind)} | ${s.pages} ${unidad} | ${s.quality}` +
          `${s.pagesWithoutText.length ? ` (${s.pagesWithoutText.length} sin texto)` : ""}${s.ocrPages.length ? ` (${s.ocrPages.length} con OCR)` : ""} |`,
      );
      for (const w of s.warnings) avisos.push(`${name}: ${w}`);
      fuentes.push({ documentId: `doc${n + 1}`, fileId: `doc${n + 1}`, title: name, kind: tipo.kind, unit: s.unit, pages: ext.pages.map((p: any) => ({ pageNumber: p.pageNumber, text: p.text })) });
    } catch (err) {
      avisos.push(`No se pudo leer «${e.name}»: ${err instanceof Error ? err.message : String(err)}`);
    }
  }
  if (!fuentes.length) {
    console.error(`No se pudo leer ningún documento.\n${avisos.join("\n")}`);
    process.exit(1);
  }

  const omitidos = {};
  const { kept, dropped } = verifyFindings(analyzeWithRules(fuentes, omitidos), fuentes);
  const { incomplete, notes } = describeOmitted(omitidos);
  const hallazgos = kept as any[];
  const excluyentes = hallazgos.filter((f) => f.eliminatory && !f.negated);

  const ahora = new Intl.DateTimeFormat("es-CL", { timeZone: "America/Santiago", dateStyle: "short", timeStyle: "short" }).format(new Date());
  const md: string[] = [
    "# Lectura de bases con el motor de Telicito.cl",
    "",
    `Leído el ${ahora} (hora de Chile) con el motor ${RULES_ENGINE_VERSION}, por reglas y sin IA. ` +
      "Es una primera pasada: no reemplaza la lectura completa de las bases. Cada hallazgo trae su cita literal para verificarlo.",
    "",
    `**Resumen:** ${hallazgos.length} hallazgos en ${fuentes.length} documento(s). ` +
      `${excluyentes.length} exigencias marcadas como excluyentes (dejan fuera la oferta si no se cumplen).` +
      (dropped ? ` Se descartaron ${dropped} hallazgos porque su cita no se pudo verificar en el texto.` : ""),
    "",
    "## Documentos leídos",
    "",
    "| Archivo | Tipo | Extensión | Calidad de lectura |",
    "|---|---|---|---|",
    ...lectura,
    "",
  ];
  if (avisos.length || incomplete.length || notes.length) {
    md.push("## Avisos", "", ...[...incomplete, ...avisos, ...notes].map((a) => `- ${una(a, 600)}`), "");
  }
  const unidadCorta = (f: any) => (fuentes.find((d) => d.documentId === f.citation?.documentId)?.unit === "pagina" ? "p." : "bloque");
  for (const tipo of ORDEN) {
    const grupo = hallazgos.filter((f) => f.kind === tipo && !f.absorbed);
    if (!grupo.length) continue;
    md.push(`## ${FINDING_KIND_LABELS[tipo]} (${grupo.length})`, "");
    md.push("| N.° | Qué dice | Cuándo | Excluyente | Cita |", "|---|---|---|---|---|");
    grupo.forEach((f, i) => {
      const que = [f.negated ? "**No se exige:**" : "", una(f.title, 220), f.weightPercent != null ? `(${f.weightPercent}%)` : "", f.consequence ? `· Si no se cumple: ${una(f.consequence, 200)}` : ""].filter(Boolean).join(" ");
      const cita = f.citation
        ? `${una(f.citation.documentTitle, 40)}, ${unidadCorta(f)} ${f.citation.page}${f.section ? `, ${una(f.section, 60)}` : ""}: «${una(f.citation.quote, 320)}»`
        : "Sin cita (sugerencia del motor)";
      md.push(`| ${i + 1} | ${que} | ${ETAPA[f.stage ?? ""] ?? "—"} | ${f.eliminatory && !f.negated ? "**Sí**" : "No"} | ${cita} |`);
    });
    md.push("");
  }
  const texto = md.join("\n");
  if (salidaJson) writeFileSync(salidaJson, JSON.stringify({ motor: RULES_ENGINE_VERSION, documentos: fuentes.map((d) => ({ id: d.documentId, titulo: d.title, tipo: d.kind, paginas: d.pages.length })), hallazgos, avisos }, null, 1));
  if (salida) {
    writeFileSync(salida, texto);
    console.error(`Informe guardado en ${salida} (${hallazgos.length} hallazgos, ${excluyentes.length} excluyentes).`);
  } else {
    console.log(texto);
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
