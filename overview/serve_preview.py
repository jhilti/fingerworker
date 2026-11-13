"""Serve only the generated overview for UI QA, never arbitrary workspace files."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
PAGE=Path(__file__).resolve().parent.parent/'Uebersicht.html'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/','/overview'):
            self.send_error(404);return
        data=PAGE.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(data)
    def log_message(self,*args):pass
print('Overview-only preview: http://127.0.0.1:8789/overview',flush=True)
ThreadingHTTPServer(('127.0.0.1',8789),Handler).serve_forever()
