#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Responde OK imediatamente, executa script em background"""
        # Responder ao Cloud Run que tudo OK
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write('✅ OK\n'.encode())
        
        # Executar script em background (não bloqueia resposta)
        thread = threading.Thread(target=self.executar_screenshot)
        thread.daemon = True
        thread.start()
    
    def executar_screenshot(self):
        """Executa o screenshot em background"""
        try:
            print("\n" + "="*60)
            print("🚀 Executando screenshot em background...")
            print("="*60)
            subprocess.run(['python3', 'print_page.py'], check=True)
            print("✅ Screenshot concluído!")
        except Exception as e:
            print(f"❌ Erro ao executar screenshot: {e}")
    
    def log_message(self, format, *args):
        print(f"[LOG] {format % args}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Servidor escutando em 0.0.0.0:{port}")
    
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()