#!/usr/bin/env python3
import sys
import os
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import threading

print("=" * 60)
print("🚀 Iniciando aplicação...")
print("=" * 60)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Responde OK imediatamente, executa script em background"""
        print(f"\n✅ Requisição recebida: {self.path}")
        
        # Responder ao Cloud Run que tudo OK
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write('✅ OK\n'.encode())
        
        # Executar script em background
        thread = threading.Thread(target=self.executar_screenshot)
        thread.daemon = True
        thread.start()
        print("🔄 Thread iniciada para executar screenshot")
    
    def executar_screenshot(self):
        """Executa o screenshot em background"""
        try:
            print("\n" + "="*60)
            print("📸 Iniciando screenshot...")
            print("="*60)
            
            # Executar print_page.py e capturar output
            result = subprocess.run(
                ['python3', 'print_page.py'],
                capture_output=True,
                text=True,
                timeout=1800
            )
            
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
            print(f"--- Return Code: {result.returncode} ---")
            
            if result.returncode == 0:
                print("✅ Screenshot concluído com sucesso!")
            else:
                print(f"❌ Script retornou erro: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("❌ ERRO: Script ultrapassou timeout de 30 minutos")
        except Exception as e:
            print(f"❌ ERRO ao executar screenshot: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    def log_message(self, format, *args):
        print(f"[SERVER] {format % args}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Servidor escutando em 0.0.0.0:{port}")
    print("=" * 60 + "\n")
    
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()