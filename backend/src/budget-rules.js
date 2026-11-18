
'use strict';
const CATEGORIES = ['personnel', 'equipment', 'consumables', 'travel', 'other', 'requirement'];
function amount(value) {
  const n = Number(value);
  if (!Number.isSafeInteger(n) || n < 0) throw Object.assign(new Error('Budget amounts must be non-negative whole INR'), { status:422 });
  return n;
}
function charge(base,pct) {
  const text=String(pct);if(!/^\d+(?:\.\d{1,6})?$/.test(text))throw new Error('Percentage must be a non-negative decimal with at most six fractional digits');
  const [whole,fraction='']=text.split('.');const numerator=BigInt(whole+fraction);const divisor=100n*10n**BigInt(fraction.length);
  const value=Number((BigInt(base)*numerator+divisor/2n)/divisor);
  if(!Number.isSafeInteger(value))throw new Error('Budget exceeds safe INR range');return value;
}
function sumByCategory(lines) {
  const sums = Object.fromEntries(CATEGORIES.map((k) => [k, 0]));
  for (const line of lines) sums[CATEGORIES.includes(line.category) ? line.category : 'requirement'] += amount(line.amount);
  if (!Number.isSafeInteger(Object.values(sums).reduce((a,b) => a+b,0))) throw new Error('Budget exceeds safe INR range');
  return sums;
}
function computeBudget(lines, rules = {}) {
  const categories = sumByCategory(lines);
  const direct = Object.values(categories).reduce((a,b) => a+b,0);
  const base = (name) => name === 'direct_excluding_equipment' ? direct-categories.equipment : direct;
  const overheadPct = rules.overheadAllowed === false ? 0 : Number(rules.overheadPct || 0);
  const contingencyPct = rules.contingencyAllowed === false ? 0 : Number(rules.contingencyPct || 0);
  for (const value of [overheadPct, contingencyPct]) if (!Number.isFinite(value) || value < 0) throw new Error('Invalid configured budget percentage');
  for (const key of ['overheadBase','contingencyBase']) if (rules[key] && !['direct','direct_excluding_equipment'].includes(rules[key])) throw new Error('Unsupported charge denominator');
  // Whole INR inputs; round each percentage charge once, half up, then sum.
  const overhead = charge(base(rules.overheadBase),overheadPct);
  const contingency = charge(base(rules.contingencyBase),contingencyPct);
  if(!Number.isSafeInteger(direct+overhead+contingency))throw new Error('Budget exceeds safe INR range');
  return { categories, direct, overhead, contingency, total:direct+overhead+contingency, overheadPct, contingencyPct, lineSum:direct,
    overheadBase:rules.overheadBase || 'direct', contingencyBase:rules.contingencyBase || 'direct', rounding:'whole INR; charges rounded half up once' };
}
function capReport(lines, rules = {}) {
  const t = computeBudget(lines,rules);
  return [['salary','Manpower','personnel'],['equipment','Equipment','equipment'],['travel','Travel','travel'],['consumables','Consumables','consumables'],['other','Other','other']]
    .filter(([key,,category]) => rules.categoryCaps?.[category]?.pct != null || rules[key+'CapPct'] != null)
    .map(([key,label,category]) => {
      const rule = rules.categoryCaps?.[category];
      const capPct = Number(rule?.pct ?? rules[key+'CapPct']);
      if(!Number.isFinite(capPct)||capPct<0||capPct>100)throw new Error('Invalid category cap percentage');
      const base = rule?.base || rules.capBase || 'total';
      if (!['direct','total'].includes(base)) throw new Error('Unsupported category cap denominator');
      const denominator = t[base]; const value=t.categories[category]; const limit=charge(denominator,capPct);
      const actualPct=denominator ? Math.round(value/denominator*1000)/10 : 0;
      const unclassified=t.categories.requirement>0;
      return {key,label,category,capPct,amount:value,actualPct,limit,base,denominator,
        status:unclassified?'unclassified':value>limit?'over':actualPct>=capPct-2?'at-limit':'ok'};
    });
}
module.exports={CATEGORIES,amount,sumByCategory,computeBudget,capReport};
