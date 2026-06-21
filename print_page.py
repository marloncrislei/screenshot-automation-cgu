from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import datetime 
import os
import time
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ============ CARREGAR CONFIGURAÇÃO ============
def carregar_config():
    """Carrega configuração do arquivo JSON"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Arquivo config.json não encontrado em {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"✅ Configuração carregada com {len(config.get('sites', []))} site(s)")
    return config

# ============ CONFIGURAÇÕES GLOBAIS ============
try:
    CONFIG = carregar_config()
    EMAIL_CONFIG = CONFIG.get('email', {})
    SITES = CONFIG.get('sites', [])
except Exception as e:
    print(f"❌ Erro ao carregar config.json: {e}")
    raise

data = datetime.datetime.now()
agora = data.strftime('%Y%m%d %Hh%Mm%Ss')

SHOW_BROWSER = False

# Caminhos
IMG_PATH = os.getenv('IMG_PATH', '/tmp/img/')
PDF_PATH = os.getenv('PDF_PATH', '/tmp/pdf/')

# Criar pastas
os.makedirs(IMG_PATH, exist_ok=True)
os.makedirs(PDF_PATH, exist_ok=True)

# ============ CONFIGURAR CHROME ============
def criar_driver():
    """Cria driver Chrome com opções para servidor"""
    chrome_options = Options()
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    if not SHOW_BROWSER:
        chrome_options.add_experimental_option("detach", True)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"❌ Erro ao criar Chrome driver: {e}")
        raise

# ============ CAPTURAR SCREENSHOTS ============
def capturar_screenshots(site_config):
    """Captura os dois screenshots de um site"""
    url = site_config.get('url')
    nome_site = site_config.get('nome_site')
    xpath_cookie = site_config.get('xpath_cookie')
    xpath_banner = site_config.get('xpath_banner')
    zoom_banner = site_config.get('zoom_banner', '100%')
    zoom_decisao = site_config.get('zoom_decisao', '70%')
    
    print("\n" + "=" * 60)
    print(f"🌐 Processando: {nome_site}")
    print(f"URL: {url}")
    print("=" * 60)
    
    driver = criar_driver()
    
    try:
        print("📖 Acessando URL...")
        driver.get(url)
        time.sleep(2)
        
        # Aceitar cookies (se existir)
        if xpath_cookie:
            try:
                print("🍪 Aceitando cookies...")
                submit_button = driver.find_element(by=By.XPATH, value=xpath_cookie)
                submit_button.click()
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Botão de cookies não encontrado: {e}")
        
        titulo = driver.title
        print(f'✅ Título: {titulo}')
        
        # PRIMEIRA IMAGEM: Banner
        print("📸 Capturando Banner...")
        driver.execute_script(f"document.body.style.zoom='{zoom_banner}'")
        time.sleep(2)
        
        filename_banner = f'[Banner][{agora}][{nome_site}].png'
        driver.save_screenshot(IMG_PATH + filename_banner)
        print(f"✅ Banner salvo: {filename_banner}")
        
        # Clicar no banner (se XPath for fornecido)
        if xpath_banner:
            print("🖱️  Clicando no banner...")
            try:
                submit_button = driver.find_element(By.XPATH, value=xpath_banner)
                submit_button.click()
                time.sleep(2)
                
                # Trocar para segunda guia
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.execute_script(f"document.body.style.zoom='{zoom_decisao}'")
                    
                    # SEGUNDA IMAGEM: Decisão
                    print("📸 Capturando Decisão...")
                    filename_decisao = f'[Decisao][{agora}][{nome_site}].png'
                    time.sleep(2)
                    driver.save_screenshot(IMG_PATH + filename_decisao)
                    print(f"✅ Decisão salva: {filename_decisao}")
                    
                    return filename_banner, filename_decisao, nome_site
                else:
                    print("⚠️  Segunda guia não aberta")
                    return filename_banner, None, nome_site
                    
            except Exception as e:
                print(f"❌ Erro ao clicar no banner: {e}")
                return filename_banner, None, nome_site
        else:
            return filename_banner, None, nome_site
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        raise
    finally:
        driver.quit()

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
        
        # Linhas divisórias
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
    """Envia email com PDF em anexo para múltiplos destinatários"""
    if not emails_destinatarios:
        print("⏭️  Nenhum email configurado")
        return
    
    try:
        print(f"📧 Preparando email para {len(emails_destinatarios)} destinatário(s)...")
        
        email_sender = EMAIL_CONFIG.get('sender')
        email_password = EMAIL_CONFIG.get('password')
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(EMAIL_CONFIG.get('smtp_port', 587))
        
        # Validar variáveis
        if not all([email_sender, email_password]):
            print("❌ Credenciais de email não configuradas no config.json")
            return
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = ', '.join(emails_destinatarios)
        msg['Subject'] = f'Monitoramento Publicação [{nome_site}][{data.strftime("%d/%m/%Y %H:%M:%S")}]'
        
        # Corpo do email
        corpo_email = f'<p>Monitoramento de publicações - {nome_site}</p><br>'
        msg.attach(MIMEText(corpo_email, 'html'))
        
        # Anexar PDF
        print(f"📎 Anexando PDF: {caminho_pdf}")
        with open(caminho_pdf, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(caminho_pdf)}')
            msg.attach(part)
        
        # Enviar
        print(f"📤 Conectando a {smtp_server}:{smtp_port}...")
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
    """Função principal - processa todos os sites ativos"""
    print("\n" + "=" * 60)
    print(f"🚀 INICIANDO MONITORAMENTO - {agora}")
    print("=" * 60)
    
    sites_processados = 0
    sites_erro = 0
    
    for site_config in SITES:
        if not site_config.get('ativo', True):
            print(f"⏭️  Site {site_config.get('nome_site')} desativado - pulando")
            continue
        
        try:
            # 1. Capturar screenshots
            filename_banner, filename_decisao, nome_site = capturar_screenshots(site_config)
            
            # 2. Criar PDF
            caminho_pdf = criar_pdf(
                filename_banner, 
                filename_decisao, 
                nome_site,
                site_config.get('url')
            )
            
            # 3. Enviar email
            emails = site_config.get('emails', [])
            enviar_email_pdf(caminho_pdf, emails, nome_site)
            
            sites_processados += 1
            
        except Exception as e:
            print(f"❌ ERRO ao processar {site_config.get('nome_site')}: {e}")
            sites_erro += 1
            continue
    
    print("\n" + "=" * 60)
    print(f"✅ PROCESSO CONCLUÍDO!")
    print(f"   Sites processados: {sites_processados}")
    print(f"   Erros: {sites_erro}")
    print("=" * 60 + "\n")

# Removido - agora é chamado pelo app.py
#if __name__ == "__main__":
#    main()
