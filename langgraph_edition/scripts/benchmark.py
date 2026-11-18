"""Report real serial/parallel candidate latency and exact ranking equality; no invented speedup."""
import os,tempfile,time,sys,json,statistics
from pathlib import Path
os.environ['GRANT_DATA_DIR']=tempfile.mkdtemp(prefix='grant-benchmark-')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import store
from app.connector import Connector,demo_calls
store.init();actor={'username':'benchmark','role':'faculty','department':'TEST'};c=Connector(actor)
plan={'area':'cardiovascular heart artificial intelligence','title':'Cardiovascular monitoring','funding_type':'government','mode':'sandbox','months':12}
records=demo_calls();timing={};outputs={}
for mode in [False,True]:
 ts=[]
 for _ in range(10):
  t=time.perf_counter();result=c.candidates(records,plan,parallel=mode);ts.append(time.perf_counter()-t)
 key='parallel' if mode else 'serial';timing[key]=round(statistics.median(ts)*1000,3);outputs[key]=result
report={'fixture_candidates':len(records),'repeats':10,'median_milliseconds':timing,'identical_ranking_and_rejection_reasons':outputs['parallel']==outputs['serial'],'parallel_faster':timing['parallel']<timing['serial'],'note':'Includes audit write. Tiny CPU-bound local fixtures may be slower with threads; do not extrapolate to network I/O workloads.'}
print(json.dumps(report,indent=2))
assert report['identical_ranking_and_rejection_reasons']
