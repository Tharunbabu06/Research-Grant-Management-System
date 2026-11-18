from pathlib import Path
import ast
import contextlib
import io
import json
import os
import runpy
import sys
import tempfile

root = Path(__file__).resolve().parents[1]/'Assignments'
sys.path.insert(0,str(root/'scripts'))
results=[]
for script in sorted((root/'scripts').glob('lab[0-9][0-9]_*.py')):
    number=int(script.stem[3:5])
    notebook=next(root.glob(f'LAB_{number}_*.ipynb'))
    cells=json.loads(notebook.read_text())['cells']
    check_code=''.join(cells[-1]['source'])
    trace=io.StringIO()
    original=Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as temporary:
            try:
                os.chdir(temporary)
                with contextlib.redirect_stdout(trace):
                    runpy.run_path(str(script),run_name='__main__')
                namespace={'console':trace}
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(check_code,str(notebook), 'exec'),namespace)
                results.append({'lab':number,'passed':namespace['passed'],'total':len(namespace['results'])})
            finally:
                # Windows cannot remove a directory while it is this process's cwd.
                os.chdir(original)
    finally:
        os.chdir(original)
    print(results[-1],flush=True)
print('TOTAL',sum(x['passed'] for x in results),'/',sum(x['total'] for x in results))
Path(__file__).resolve().parents[1].joinpath('Course-Project/docs/lab_checks.json').write_text(json.dumps(results,indent=2))
assert all(item['passed']==item['total'] for item in results)
