"""Start the local review server when this project is opened again."""
from pathlib import Path
import http.server,socketserver,urllib.request,webbrowser,os
root=Path(__file__).resolve().parents[1];url='http://127.0.0.1:8766/review/walkthrough/?part=part00&view=tramstart'
try:
 with urllib.request.urlopen('http://127.0.0.1:8766/review/walkthrough/parts.json',timeout=1) as r:
  if r.status==200:webbrowser.open(url);raise SystemExit
except (OSError,TimeoutError):pass
os.chdir(root)
class Server(socketserver.ThreadingTCPServer):allow_reuse_address=True
with Server(('127.0.0.1',8766),http.server.SimpleHTTPRequestHandler) as server:
 print(url,flush=True);webbrowser.open(url);server.serve_forever()
