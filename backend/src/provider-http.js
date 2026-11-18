
'use strict';
const messages={key_missing:'OpenAlex key is not configured. College results remain available.',authentication_rejected:'Provider rejected credentials. Check API key activation and access.',rate_limited:'Provider rate limit reached. Wait before retrying.',timeout:'Provider request timed out. Retry later.',network_error:'Provider could not be reached. Check outbound network access.',malformed_response:'Provider returned an invalid metadata response.',unavailable:'Provider is temporarily unavailable.'};
async function jsonRequest(url,{request=fetch,headers={},timeout=10000,sleep=(ms)=>new Promise(r=>setTimeout(r,ms)),retries=2,maxWait=2000}={}) {
 for(let attempt=0;;attempt++) {
  try {
   const response=await request(url,{headers,signal:AbortSignal.timeout(timeout)});
   if(!response.ok) {
    const code=[401,403].includes(response.status)?'authentication_rejected':response.status===429?'rate_limited':'unavailable';
    const raw=response.headers?.get?.('retry-after');
    const retryAfter=raw ? (/^\d+$/.test(raw)?Number(raw)*1000:Math.max(0,Date.parse(raw)-Date.now())) : 100*2**attempt;
    if(attempt<retries&&(response.status===429||response.status>=500)&&Number.isFinite(retryAfter)&&retryAfter<=maxWait) {await sleep(retryAfter);continue;}
    return {diagnostic:{code,message:messages[code],httpStatus:response.status||null,attempts:attempt+1,retryAfterMs:Number.isFinite(retryAfter)?retryAfter:null}};
   }
   try{return {data:await response.json(),diagnostic:{code:'ok',message:'Metadata request succeeded',attempts:attempt+1}};}
   catch{return {diagnostic:{code:'malformed_response',message:messages.malformed_response,attempts:attempt+1}};}
  }catch(error) {
   const code=['AbortError','TimeoutError'].includes(error?.name)?'timeout':'network_error';
   if(attempt<retries){await sleep(100*2**attempt);continue;}
   return {diagnostic:{code,message:messages[code],attempts:attempt+1}};
  }
 }
}
module.exports={jsonRequest,messages};
