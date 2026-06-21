from http.server import HTTPServer, BaseHTTPRequestHandler
import print_page
import json
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Executa quando recebe uma requisição GET"""
        try:
            print("🚀 Executando screenshot...")
            print_page.main()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'✅ Screenshot executado com sucesso!')
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'❌ Erro: {str(e)}'.encode())
    
    def log_message(self, format, *args):
        """Suprimir logs padrão"""
        pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"🌐 Servidor escutando na porta {port}...")
    server.serve_forever()