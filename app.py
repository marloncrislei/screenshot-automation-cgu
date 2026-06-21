#!/usr/bin/env python3
import sys
import os
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

print("=" * 60)
print("🚀 Iniciando aplicação...")
print("=" * 60)

# Debug: verificar porta
port = int(os.environ.get('PORT', 8080))
print(f"✅ Porta: {port}")

# Debug: verificar se pode usar socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)
    sock.close()
    print(f"✅ Porta {port} disponível para uso")
except Exception as e:
    print(f"❌ Erro ao vincular porta: {e}")
    sys.exit(1)

# Tentar importar print_page
try:
    import print_page
    print("✅ print_page importado com sucesso")
except Exception as e:
    print(f"⚠️  Aviso ao importar print_page: {e}")
    print_page = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Executa quando recebe uma requisição GET"""
        try:
            if self.path == '/health' or self.path == '/':
                # Health check
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'✅ OK')
                print("✅ Health check ok")
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

# Iniciar servidor
try:
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"✅ Servidor iniciado em 0.0.0.0:{port}")
    print("=" * 60)
    server.serve_forever()
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    sys.exit(1)