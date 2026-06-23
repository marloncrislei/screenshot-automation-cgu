from playwright.sync_api import sync_playwright
import datetime 
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

# ============ CARREGAR CONFIGURAÇÃO ============
def carregar_config():
    """Carrega configuração do arquivo JSON"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Arquivo config.json não encontrado")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

# ============ CONFIGURAÇÕES ============
CONFIG = carregar_config()
EMAIL_CONFIG = CONFIG.get('email', {})
SITES = CONFIG.get('sites', [])

data = datetime.datetime.now()
agora = data.strftime('%Y%m%d %Hh%Mm%Ss')

IMG_PATH = os.getenv('IMG_PATH', '/tmp/img/')
PDF_PATH = os.getenv('PDF_PATH', '/tmp/pdf/')

os.makedirs(IMG_PATH, exist_ok=True)
os.makedirs(PDF_PATH, exist_ok=True)

print("=" * 60)
print(f"🚀 INICIANDO MONITORAMENTO - {agora}")
print("=" * 60)

# ============ CAPTURAR SCREENSHOTS COM PLAYWRIGHT ============
def capturar_screenshots(site_config):
    """Captura os dois screenshots usando Playwright"""
    url = site_config.get('url')
    nome_site = site_config.get('nome_site')
    xpath_cookie = site_config.get('xpath_cookie')
    xpath_banner = site_config.get('xpath_banner')
    
    print("\n" + "=" * 60)
    print(f"🌐 Processando: {nome_site}")
    print(f"URL: {url}")
    print("=" * 60)
    
    filename_banner = None
    filename_decisao = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("📖 Acessando URL...")
            page.goto(url, wait_until="networkidle")
            time.sleep(2)
            
            # Aceitar cookies
            if xpath_cookie:
                try:
                    print("🍪 Clicando em aceitar cookies...")
                    page.click(f"xpath={xpath_cookie}")
                    time.sleep(1)
                except:
                    print("⚠️  Botão de cookies não encontrado")
            
            # PRIMEIRA IMAGEM
            print("📸 Capturando Banner...")
            filename_banner = f'[Banner][{agora}][{nome_site}].png'
            page.screenshot(path=IMG_PATH + filename_banner)
            print(f"✅ Banner salvo: {filename_banner}")
            
            # Clicar no banner
            if xpath_banner:
                try:
                    print("🖱️  Clicando no banner...")
                    page.click(f"xpath={xpath_banner}")
                    time.sleep(2)
                    
                    # SEGUNDA IMAGEM
                    print("📸 Capturando Decisão...")
                    filename_decisao = f'[Decisao][{agora}][{nome_site}].png'
                    page.screenshot(path=IMG_PATH + filename_decisao)
                    print(f"✅ Decisão salva: {filename_decisao}")
                except Exception as e:
                    print(f"⚠️  Erro ao clicar: {e}")
            
            return filename_banner, filename_decisao, nome_site
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise
        finally:
            browser.close()

# ============ CRIAR PDF ============
def criar_pdf(filename_banner, filename_decisao, nome_site, url):
    """Cria PDF com as imagens"""
    try:
        print("📄 Criando PDF...")
        filename_pdf = filename_banner.replace('[Banner][', '[Banner_Decisao][').replace('.png', '.pdf')
        
        cnv = canvas.Canvas(PDF_PATH + filename_pdf, pagesize=A4)
        cnv.setLineWidth(.1)
        cnv.setStrokeGray(0.7)
        
        # Bordas
        cnv.line(20,  820, 580, 820)
        cnv.line(20,  820,  20,  20)
        cnv.line(20,   20, 580,  20)
        cnv.line(580,  20, 580, 820)
        
        # Adicionar imagens
        cnv.drawImage(IMG_PATH + filename_banner, 40, 241, width=525, preserveAspectRatio=True)
        if filename_decisao:
            cnv.drawImage(IMG_PATH + filename_decisao, 40, -120, width=525, preserveAspectRatio=True)
        
        # Linhas
        cnv.setLineWidth(1)
        cnv.setStrokeGray(0.95)
        cnv.line(40, 730, 565.5, 730)
        cnv.line(40, 394, 565.5, 394)
        cnv.line(40, 730.5,  40, 394.5)
        cnv.line(565, 730, 565, 394)
        
        # Informações
        cnv.setFont('Helvetica-Bold', 10)
        cnv.drawString(40, 780, "Endereço Eletrônico: ")
        cnv.setFont('Helvetica', 10)
        cnv.drawString(160, 780, url)
        cnv.setFont('Helvetica-Bold', 10)
        cnv.drawString(40, 760, "Acessada em: ")
        cnv.setFont('Helvetica', 10)
        cnv.drawString(160, 760, data.strftime('%d/%m/%Y %H:%M:%S'))
        
        cnv.save()
        print(f"✅ PDF criado: {filename_pdf}")
        
        return PDF_PATH + filename_pdf
        
    except Exception as e:
        print(f"❌ Erro ao criar PDF: {e}")
        raise

# ============ ENVIAR EMAIL ============
def enviar_email_pdf(caminho_pdf, emails_destinatarios, nome_site):
    """Envia email com PDF"""
    if not emails_destinatarios:
        print("⏭️  Nenhum email configurado")
        return
    
    try:
        print(f"📧 Preparando email...")
        
        email_sender = EMAIL_CONFIG.get('sender')
        email_password = EMAIL_CONFIG.get('password')
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(EMAIL_CONFIG.get('smtp_port', 587))
        
        if not all([email_sender, email_password]):
            print("❌ Credenciais não configuradas")
            return
        
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = ', '.join(emails_destinatarios)
        msg['Subject'] = f'Monitoramento [{nome_site}][{data.strftime("%d/%m/%Y %H:%M:%S")}]'
        
        corpo_email = f'<p>Monitoramento de publicações - {nome_site}</p><br>'
        msg.attach(MIMEText(corpo_email, 'html'))
        
        # Anexar PDF
        with open(caminho_pdf, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(caminho_pdf)}')
            msg.attach(part)
        
        # Enviar
        print(f"📤 Enviando para {len(emails_destinatarios)} destinatário(s)...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        
        for email in emails_destinatarios:
            server.sendmail(email_sender, email, msg.as_string())
            print(f"✅ Email enviado para: {email}")
        
        server.quit()
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        raise

# ============ MAIN ============
def main():
    """Função principal"""
    sites_processados = 0
    sites_erro = 0
    
    for site_config in SITES:
        if not site_config.get('ativo', True):
            print(f"⏭️  Site {site_config.get('nome_site')} desativado")
            continue
        
        try:
            filename_banner, filename_decisao, nome_site = capturar_screenshots(site_config)
            caminho_pdf = criar_pdf(filename_banner, filename_decisao, nome_site, site_config.get('url'))
            emails = site_config.get('emails', [])
            enviar_email_pdf(caminho_pdf, emails, nome_site)
            
            sites_processados += 1
            
        except Exception as e:
            print(f"❌ ERRO: {e}")
            sites_erro += 1
    
    print("\n" + "=" * 60)
    print(f"✅ CONCLUÍDO! Processados: {sites_processados}, Erros: {sites_erro}")
    print("=" * 60)

if __name__ == "__main__":
    main()