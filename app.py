from flask import Flask
import print_page
import os
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def run_screenshot():
    """Executa o script de screenshot"""
    try:
        print_page.main()
        return "✅ Screenshot executado com sucesso!", 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return f"❌ Erro: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)