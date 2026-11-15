"""Optional browser smoke test. Use an expendable practice workspace; creates practice proposals and policy evidence.
Requires playwright and its Chromium install. Stop the normal server first.
"""
from pathlib import Path
import json,subprocess,sys,time,atexit,os
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'runtime/ui-checks';out.mkdir(parents=True,exist_ok=True)
creds={}
for line in (root/'runtime/FIRST_LOGIN.txt').read_text().splitlines():
 if '[' in line:
  a=line.split();creds[a[0]]=a[1]
server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
atexit.register(server.terminate)
time.sleep(2)
errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.getenv('BROWSER_EXECUTABLE') or None,headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1080});page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000');page.locator('[name=username]').fill('  FACULTY  ');page.locator('[name=password]').fill(creds['faculty']);page.locator('#login button.primary').click();page.wait_for_selector('.hero');assert 'Demo ' not in page.locator('body').inner_text();page.screenshot(path=str(out/'dashboard.png'),full_page=True)
 page.locator('.nav [data-nav=new]').click();page.wait_for_selector('#intake');assert page.locator('[name=mode]').input_value()=='real';page.locator('[data-action=sample-proposal]').click();page.locator('[name=consent]').check();page.locator('#intake button.primary').click();page.wait_for_selector('[data-action=run-plan]');page.locator('[data-action=run-plan]').click();page.wait_for_selector('[data-tab=review]',timeout=30000)
 assert 'Awaiting review' in page.locator('#content').inner_text()
 page.locator('[data-tab=budget]').click();page.wait_for_selector('.check');assert page.locator('.check-icon.bad').count()==0
 page.locator('[data-tab=review]').click();page.wait_for_selector('#revision');assert 'Sign in as' in page.locator('#run-tab').inner_text()
 page.locator('[data-action=logout]').click();page.wait_for_selector('#login');page.locator('[name=username]').fill('hod');page.locator('[name=password]').fill(creds['hod']);page.locator('#login button.primary').click();page.wait_for_selector('.hero');page.locator('[data-run]').first.click();page.wait_for_selector('[data-tab=review]');page.locator('[data-tab=review]').click();page.wait_for_selector('#decision');page.locator('#decision [name=note]').fill('Checked the synthetic practice proposal, budget and validation report.');page.locator('#decision button').click();page.get_by_text('Practice package released',exact=True).first.wait_for();page.wait_for_selector('#revision')
 with page.expect_download() as d:page.locator('a[href$="/package"]').click()
 download=d.value;assert download.suggested_filename.endswith('.zip')
 page.screenshot(path=str(out/'review.png'),full_page=True)
 for name,selector in [('catalog','#catalog-results'),('calls','.cards'),('evidence','#evidence'),('assistant','#assistant'),('settings','#password'),('labs','.cards')]:
  page.locator('.nav [data-nav='+name+']').click();page.wait_for_selector(selector)
 page.locator('.nav [data-nav=assistant]').click();page.locator('#assistant [name=question]').fill('Find DDoS cybersecurity publications');page.locator('#assistant button').click();page.wait_for_selector('#answer .result');assert page.locator('#answer .result').count()>0
 page.locator('[data-action=logout]').click();page.wait_for_selector('#login');page.locator('[name=username]').fill('office');page.locator('[name=password]').fill(creds['office']);page.locator('#login button.primary').click();page.wait_for_selector('.hero')
 page.locator('.nav [data-nav=evidence]').click();page.wait_for_selector('#evidence');unique='Browser test policy '+str(int(time.time()));page.locator('#evidence [name=title]').fill(unique);page.locator('#evidence [name=kind]').select_option('policy');page.locator('#evidence [name=locator]').fill('Synthetic browser test section 1');page.locator('#evidence [name=text]').fill('Synthetic browser test policy, not a real college policy.');page.locator('#evidence button').click();page.get_by_text(unique,exact=True).wait_for();eid=page.locator('.result').filter(has_text=unique).locator('.code').inner_text()
 page.locator('.nav [data-nav=settings]').click();page.wait_for_selector('#registry');page.locator('#registry [name=id]').fill('UI-TEST-'+str(int(time.time())));page.locator('#registry [name=title]').fill(unique);page.locator('#registry [name=evidence_id]').fill(eid);page.locator('#registry [name=rules]').fill('Synthetic browser test policy only, not official.');page.locator('#registry [name=attest]').check();page.locator('#registry button').click();page.wait_for_selector('[data-template=call]');page.locator('[data-template=call]').click();page.wait_for_selector('#registry [name=deadline]');assert page.locator('#registry [name=limit_personnel]').count()==1
 page.locator('.nav [data-nav=settings]').click();page.wait_for_selector('#account-reset');assert page.locator('#llm-config').count()==1
 page.locator('#account-reset [name=username]').select_option('faculty');page.locator('#account-reset [name=password]').fill('Recovered-Faculty-2026!');page.locator('#account-reset [name=confirm]').fill('Recovered-Faculty-2026!');page.locator('#account-reset button').click();page.get_by_text('Password reset. Existing records preserved.',exact=True).wait_for()
 page.locator('[data-action=logout]').first.click();page.wait_for_selector('#login');page.locator('[name=username]').fill('faculty');page.locator('[name=password]').fill('Recovered-Faculty-2026!');page.locator('[data-action=show-password]').click();assert page.locator('[name=password]').get_attribute('type')=='text';page.locator('#login button.primary').click();page.wait_for_selector('.hero')
 page.locator('.nav [data-nav=labs]').click();page.wait_for_selector('.cards');assert page.locator('.cards .card').count()==14
 page.set_viewport_size({'width':390,'height':844});page.locator('.nav [data-nav=dashboard]').click();page.wait_for_selector('.hero');page.screenshot(path=str(out/'mobile.png'),full_page=True)
 assert page.evaluate('() => document.documentElement.scrollWidth <= innerWidth+1')
 browser.close()
assert not errors,errors
print('PASS: desktop login, create plan, parallel graph, validation, role-gated review, release, ZIP download, navigation, assistant retrieval, evidence/policy administration, mobile overflow and JS errors.')
