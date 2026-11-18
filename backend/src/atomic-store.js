
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file),{recursive:true});
  const temporary=file+'.'+process.pid+'.'+crypto.randomUUID()+'.tmp';
  let descriptor;
  try {
    descriptor=fs.openSync(temporary,'wx');
    fs.writeFileSync(descriptor,JSON.stringify(value),'utf8');fs.fsyncSync(descriptor);fs.closeSync(descriptor);descriptor=null;
    for(let attempt=0;;attempt++) {
      try { fs.renameSync(temporary,file);break; }
      catch(error) {
        if(!['EPERM','EACCES','EBUSY'].includes(error.code)||attempt===5)throw error;
        Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,10*(attempt+1));
      }
    }
  } catch(error) {
    if(descriptor!=null)fs.closeSync(descriptor);
    try{fs.unlinkSync(temporary);}catch{}
    throw Object.assign(new Error('Local storage write failed; last valid file retained'),{status:503,code:'storage_write_failed',cause:error});
  }
}
module.exports={writeJson};
