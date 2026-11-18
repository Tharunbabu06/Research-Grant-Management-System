'use strict';
// Render the editable academic report; separate from saved-proposal exports.
const fs = require('fs');
const path = require('path');
const backendRequire = require('module').createRequire(path.resolve(__dirname, '../backend/package.json'));
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
  TableCell, WidthType, ImageRun, Footer, PageNumber } = backendRequire('docx');
const PDFDocument = backendRequire('pdfkit');
const root = path.resolve(__dirname, '..');
const folder = path.join(root, 'Final_Report');
const source = path.join(folder, 'GrantOffice_Technical_Report.md');
const output = path.join(folder, 'Final_Report_Research_Grant_Management_System');
const clean = text => text.replace(/!?\[([^\]]+)\]\(([^)]+)\)/g,
  (_, label, target) => /^https?:/.test(target) ? `${label} (${target})` : label).replace(/\*\*|`/g, '');
function blocks(markdown) {
  const lines = markdown.split(/\r?\n/), result = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.startsWith('```')) {
      const code = [];
      while (++i < lines.length && !lines[i].startsWith('```')) code.push(lines[i]);
      result.push({ kind: 'code', text: code.join('\n') });
    } else if (line.startsWith('|')) {
      const rows = [];
      do {
        if (!/^\|[\s:|\-]+\|$/.test(lines[i].trim())) rows.push(lines[i].trim().slice(1, -1).split('|').map(s => clean(s.trim())));
        i++;
      } while (i < lines.length && lines[i].trim().startsWith('|'));
      i--; result.push({ kind: 'table', rows });
    } else if (/^!\[/.test(line)) {
      const match = /^!\[([^\]]*)\]\(([^)]+)\)/.exec(line);
      result.push({ kind: 'image', text: match[1], file: path.resolve(folder, match[2]) });
    } else if (/^#{1,6} /.test(line)) {
      result.push({ kind: 'heading', level: line.indexOf(' '), text: clean(line.replace(/^#+ /, '')) });
    } else {
      result.push({ kind: 'text', text: clean(line.replace(/^> /, '')) });
    }
  }
  return result;
}
async function main() {
  const content = blocks(fs.readFileSync(source, 'utf8'));
  const children = [];
  for (const block of content) {
    if (block.kind === 'table') children.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: block.rows.map((row, index) => new TableRow({ tableHeader: index === 0, cantSplit: true,
        children: row.map(text => new TableCell({ children: [new Paragraph({
          children: [new TextRun({ text, bold: index === 0, size: 19 })], spacing: { after: 80 },
        })] })),
      })),
    }));
    else if (block.kind === 'image') children.push(new Paragraph({ children: [new ImageRun({
      data: fs.readFileSync(block.file), type: 'png', transformation: { width: 600, height: 39 },
    })] }), new Paragraph({ text: block.text, spacing: { after: 160 } }));
    else children.push(new Paragraph({
      text: block.text,
      heading: block.kind === 'heading' ? (block.level === 1 ? HeadingLevel.TITLE : block.level === 2 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2) : undefined,
      pageBreakBefore: block.kind === 'heading' && /^1\./.test(block.text),
      keepNext: block.kind === 'heading',
      spacing: { after: 130, line: 276 },
    }));
  }
  const doc = new Document({ creator: 'GrantOffice course project team',
    title: 'GrantOffice - Research Grant Management System: Final Report',
    styles: { default: { document: { run: { font: 'Calibri', size: 22 } } } },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 850, bottom: 850, left: 850, right: 850 } } },
      footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun('GrantOffice | Course report | '), new TextRun({ children: [PageNumber.CURRENT] })] })] }) }, children }],
  });
  fs.writeFileSync(output + '.docx', await Packer.toBuffer(doc));
  const font = [process.env.GRANTOFFICE_EXPORT_FONT, 'C:/Windows/Fonts/segoeui.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'].find(p => p && fs.existsSync(p));
  if (!font) throw new Error('Set GRANTOFFICE_EXPORT_FONT to an installed Unicode TTF');
  await new Promise((resolve, reject) => {
    const pdf = new PDFDocument({ size: 'A4', margin: 48, bufferPages: true,
      info: { Title: 'GrantOffice - Final Course Project Report', Author: 'GrantOffice course project team' } });
    const stream = fs.createWriteStream(output + '.pdf');
    stream.on('finish', resolve); stream.on('error', reject); pdf.on('error', reject); pdf.pipe(stream); pdf.font(font);
    for (const [blockIndex, block] of content.entries()) {
      if (block.kind === 'heading') {
        const followedByTable = content[blockIndex + 1]?.kind === 'table';
        if (/^1\./.test(block.text) || pdf.y > (followedByTable ? 420 : 650)) pdf.addPage();
        pdf.fontSize(block.level === 1 ? 22 : block.level === 2 ? 17 : 12).text(block.text, { paragraphGap: 10 });
      } else if (block.kind === 'table') {
        pdf.fontSize(8.5);
        const cellWidth = 499 / block.rows[0].length - 10;
        const estimatedHeight = block.rows.reduce((height, row) => height + 10 + Math.max(...row.map(text => pdf.heightOfString(text, { width: cellWidth }))), 0);
        if (estimatedHeight < 680 && pdf.y + estimatedHeight > 780) pdf.addPage();
        pdf.fontSize(8.5).table({ data: block.rows, border: 0.5, padding: 5 }); pdf.moveDown();
      } else if (block.kind === 'image') {
        if (pdf.y > 680) pdf.addPage();
        pdf.image(block.file, { fit: [499, 75] }); pdf.moveDown(2).fontSize(9).text(block.text, { paragraphGap: 8 });
      } else pdf.fontSize(block.kind === 'code' ? 8 : 9.5).text(block.text, { paragraphGap: 6 });
    }
    const range = pdf.bufferedPageRange();
    for (let page = range.start; page < range.start + range.count; page++) {
      pdf.switchToPage(page);
      pdf.fontSize(8).text(`GrantOffice | Course report | ${page + 1} / ${range.count}`, 48, 815, { lineBreak: false });
    }
    pdf.end();
  });
  console.log('Generated genuine DOCX and PDF from', path.relative(root, source));
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
