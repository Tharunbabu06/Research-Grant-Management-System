
'use strict';
const fs=require('fs');
const {Document,Packer,Paragraph,HeadingLevel,Table,TableRow,TableCell,WidthType,TextRun}=require('docx');
const PDFDocument=require('pdfkit');
const {money}=require('./core').util;
const mime={docx:'application/vnd.openxmlformats-officedocument.wordprocessingml.document',pdf:'application/pdf'};
function content(saved,{runId,version,status}) {
 const markdown=saved.package?.files?.find(f=>f.name==='proposal.md')?.content;
 if(typeof markdown!=='string')throw Object.assign(new Error('This saved package has no proposal narrative to export'),{status:422});
 const paragraphs=[`GrantOffice | ${runId} | saved version ${version} | ${status}`,'Practice workflow. Internal approval is not a funding award or a research publication.',
  ...(saved.draft?.disclosure?.text?[saved.draft.disclosure.text]:[]),
  ...markdown.split(/\r?\n/).filter(line=>line.trim())];
 if(saved.budget?.lines?.some(line=>!line.category||line.category==='requirement'))paragraphs.splice(2,0,'Historical budget warning: expense categories were not captured. Recorded cap passes are not a new validation. Original saved figures and wording below are retained.');
 const missing=['params','plan','discovery','documents','validation','acceptance'].filter(key=>saved[key]==null);if(missing.length)paragraphs.splice(2,0,'Saved context unavailable: '+missing.join(', ')+'. Current content was not substituted.');
 const rows=saved.budget?.lines ? [['Expense','Category','Amount (INR)'],...saved.budget.lines.map(l=>[l.item,l.category,money(l.amount)]),
  ['Direct costs','',money(saved.budget.totals.direct)],['Overhead','',money(saved.budget.totals.overhead)],['Contingency','',money(saved.budget.totals.contingency)],['Total request','',money(saved.budget.totals.total)]] : null;
 if(!rows)paragraphs.push('Detailed budget is absent from this saved snapshot; current budget was not substituted.');
 return {paragraphs,rows};
}
async function generate(format,saved,metadata) {
 const {paragraphs,rows}=content(saved,metadata);
 if(format==='docx') {
  const children=paragraphs.map(line=>new Paragraph({text:line.replace(/^#{1,6} /,'').replace(/\*\*/g,'').replace(/^> /,''),heading:/^# /.test(line)?HeadingLevel.TITLE:/^#{2,6} /.test(line)?HeadingLevel.HEADING_1:undefined,spacing:{after:120}}));
  if(rows)children.push(new Paragraph({text:'Saved budget breakdown',heading:HeadingLevel.HEADING_1}),new Table({width:{size:100,type:WidthType.PERCENTAGE},rows:rows.map((row,index)=>new TableRow({tableHeader:index===0,children:row.map((text)=>new TableCell({children:[new Paragraph({children:[new TextRun({text,bold:index===0})]})]}))}))}));
  return Packer.toBuffer(new Document({sections:[{children}],creator:'GrantOffice',title:`${metadata.runId} saved proposal`,description:'Exported from saved package; no new model output'}));
 }
 if(format!=='pdf')throw new Error('Unsupported export format');
 const font=[process.env.GRANTOFFICE_EXPORT_FONT,'C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'].find(p=>p&&fs.existsSync(p));
 if(!font)throw Object.assign(new Error('PDF export needs a Unicode TrueType font; set GRANTOFFICE_EXPORT_FONT to an installed font file'),{status:503});
 return new Promise((resolve,reject)=>{
  const doc=new PDFDocument({size:'A4',margin:48,info:{Title:`${metadata.runId} saved proposal`,Author:'GrantOffice'}}),chunks=[];
  doc.on('data',c=>chunks.push(c));doc.on('end',()=>resolve(Buffer.concat(chunks)));doc.on('error',reject);
  doc.font(font);
  for(const line of paragraphs){const heading=/^#{1,6} /.test(line);doc.fontSize(heading?15:10).text(line.replace(/^#{1,6} /,'').replace(/\*\*/g,'').replace(/^> /,''),{paragraphGap:7});}
  if(rows){doc.moveDown().fontSize(13).text('Saved budget breakdown');doc.fontSize(9);doc.table({columnStyles:[285,90,124],data:rows,border:0.5,padding:5});}
  doc.end();
 });
}
module.exports={generate,mime,content};
