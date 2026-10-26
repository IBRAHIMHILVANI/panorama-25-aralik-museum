"""Local-only museum viewer with bounded, ordered canvas-recording uploads.

Only the authored viewer on this exact origin can post. Filenames are fixed by
the server; source images, geometry, credentials and other user files are not
accepted or modified by the recording API.
"""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import json,uuid,hashlib,threading,time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25/video';OUT.mkdir(exist_ok=True)
ROUTE=ROOT/'reconstruction/full-tour-path-2026-10-26.json'
PORT=8767;ORIGIN=f'http://127.0.0.1:{PORT}'
records={};lock=threading.RLock();MAX_CHUNK=20*1024*1024;MAX_TOTAL=2*1024**3

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def json_reply(self,status,data):
  body=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_GET(self):
  if urlparse(self.path).path=='/__tour/status':
   with lock:rows=[{k:v for k,v in r.items() if k not in {'handle','chunks_meta'}} for r in records.values()]
   self.json_reply(200,{'recordings':rows});return
  super().do_GET()
 def do_POST(self):
  if self.headers.get('Origin')!=ORIGIN:self.json_reply(403,{'error':'Recording requests must originate from this local viewer.'});return
  endpoint=urlparse(self.path).path
  if endpoint not in {'/__tour/start','/__tour/chunk','/__tour/finish','/__tour/abort'}:self.json_reply(404,{'error':'Unknown endpoint'});return
  try:n=int(self.headers.get('Content-Length','0'))
  except ValueError:self.json_reply(400,{'error':'Invalid length'});return
  limit=MAX_CHUNK if endpoint.endswith('chunk') else 32768
  if not 0<n<=limit:self.json_reply(413,{'error':'Invalid or oversized payload'});return
  body=self.rfile.read(n)
  if len(body)!=n:self.json_reply(400,{'error':'Incomplete payload'});return
  try:
   if endpoint.endswith('chunk'):
    q=parse_qs(urlparse(self.path).query);sid=q.get('sessionId',[''])[0];index=int(q.get('index',['-1'])[0]);digest=hashlib.sha256(body).hexdigest()
    with lock:
     r=records.get(sid)
     if not r or r['state']!='recording':self.json_reply(409,{'error':'No active recording'});return
     if index<r['chunks']:
      old=r['chunks_meta'].get(index)
      self.json_reply(200 if old==[n,digest] else 409,{'duplicate':old==[n,digest],'chunks':r['chunks']});return
     if index!=r['chunks']:self.json_reply(409,{'error':'Chunk order mismatch','expected':r['chunks']});return
     if r['bytes']+n>MAX_TOTAL:self.json_reply(413,{'error':'Recording size limit reached'});return
     r['handle'].write(body);r['handle'].flush();r['bytes']+=n;r['chunks']+=1;r['chunks_meta'][index]=[n,digest];r['updated_at']=time.time()
     self.json_reply(200,{'chunks':r['chunks'],'bytes':r['bytes']});return
   data=json.loads(body)
   if endpoint.endswith('start'):
    current_hash=hashlib.sha256(ROUTE.read_bytes()).hexdigest()
    if data.get('route_sha256')!=current_hash:self.json_reply(409,{'error':'Route changed; reload before recording.'});return
    with lock:
     if any(r['state']=='recording' for r in records.values()):self.json_reply(409,{'error':'A recording is already active.'});return
     sid=uuid.uuid4().hex;stem='Gaziantep_Full_Journey_2026-10-26_'+sid[:8];path=OUT/(stem+'.webm.partial')
     records[sid]={'sessionId':sid,'state':'recording','path':str(path),'stem':stem,'bytes':0,'chunks':0,'started_at':time.time(),'updated_at':time.time(),'request':data,'handle':path.open('xb'),'chunks_meta':{}}
    self.json_reply(200,{'sessionId':sid});return
   sid=data.get('sessionId','')
   with lock:
    r=records.get(sid)
    if not r or r['state']!='recording':self.json_reply(409,{'error':'No active recording'});return
    if endpoint.endswith('finish') and data.get('chunks')!=r['chunks']:self.json_reply(409,{'error':'Chunk count mismatch'});return
    r['handle'].close();r.pop('handle');r['finished_at']=time.time();r['client_metadata']=data
    if endpoint.endswith('abort'):
     r['state']='aborted';r['complete']=False
    else:
     expected=float(r['request'].get('duration_seconds',0));actual=float(data.get('playback_seconds',0));r['complete']=r['bytes']>10000 and expected>0 and actual>=expected-.3;r['state']='complete' if r['complete'] else 'partial'
     old=Path(r['path']);dest=OUT/(r['stem']+('.webm' if r['complete'] else '.partial.webm'));old.rename(dest);r['path']=str(dest)
    saved={k:v for k,v in r.items() if k!='chunks_meta'};(OUT/(r['stem']+'.recording.json')).write_text(json.dumps(saved,ensure_ascii=False,indent=2));url='/'+str(Path(r['path']).relative_to(ROOT))
    self.json_reply(200,{'path':r['path'],'url':url,'complete':r['complete'],'bytes':r['bytes']})
  except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:self.json_reply(400,{'error':str(e)})
 def log_message(self,fmt,*args):
  if '/__tour/chunk' not in str(args):super().log_message(fmt,*args)

print('TOUR_RECORDING_SERVER',ORIGIN,flush=True)
ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
