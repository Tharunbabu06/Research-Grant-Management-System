"""Terminal sandbox through authenticated HTTP; use real local first-run credentials."""
import getpass,httpx
client=httpx.Client(base_url='http://127.0.0.1:8000/api',headers={'X-Grant-Office':'1'},timeout=240)
u=input('Username: ');p=getpass.getpass('Password: ')
r=client.post('/login',json={'username':u,'password':p});r.raise_for_status()
req={'prompt':'Prepare an AI cardiovascular monitoring proposal','title':'AI-assisted cardiovascular monitoring feasibility','area':'cardiovascular heart artificial intelligence','funding_type':'government','mode':'sandbox','months':12,'consent':True,'lines':[{'category':'personnel','description':'SAMPLE research assistant','quantity':12,'unit_inr':25000,'basis':'Synthetic rate for sandbox only'}]}
p=client.post('/plans',json=req);p.raise_for_status();r=client.post('/plans/'+p.json()['id']+'/run');r.raise_for_status();s=r.json()
print('Run:',s['id'],'Status:',s['status'])
print('Open the dashboard and review using a HoD/research-office account.')
