from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return {"status": "error", "message": "Robo ja esta rodando"}

        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless") 
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.get("https://web.whatsapp.com")
            self.is_running = True
            return {"status": "success", "message": "Navegador iniciado. Por favor, escaneie o QR Code."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_running = False
            return {"status": "success", "message": "Navegador fechado"}
        return {"status": "error", "message": "Navegador ja esta fechado"}

    def send_message(self, phone, message):
        if not self.is_running:
            return {"status": "error", "message": "O Robo esta desligado"}

        try:
            # 1. Prepara a URL (codifica espacos e acentos)
            msg_encoded = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={phone}&text={msg_encoded}"
            
            # 2. Navega para o chat especifico
            self.driver.get(link)

            # 3. Espera o botao de enviar aparecer (max 30 segundos)
            # O seletor abaixo procura o icone de envio padrao do WhatsApp Web
            send_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            
            # 4. Clica em enviar
            time.sleep(2) # Pequena pausa humana
            send_button.click()
            time.sleep(2) # Espera o envio confirmar visualmente
            
            return {"status": "sent", "message": "Mensagem enviada"}
        except Exception as e:
            return {"status": "error", "message": f"Falha ao enviar: {str(e)}"}

bot_instance = WhatsAppBot()
