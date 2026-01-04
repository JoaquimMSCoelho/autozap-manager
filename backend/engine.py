from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
            msg_encoded = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={phone}&text={msg_encoded}"
            self.driver.get(link)

            # --- AUMENTAMOS O TEMPO DE 15s PARA 40s ---
            try:
                WebDriverWait(self.driver, 40).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]')),
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "inválido")]')),
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "invalid")]'))
                    )
                )
            except TimeoutException:
                 return {"status": "error", "message": "Timeout: WhatsApp demorou mais de 40s para carregar"}

            # Verifica se apareceu o pop-up de numero invalido
            invalid_popup = self.driver.find_elements(By.XPATH, '//div[contains(text(), "inválido")]') or \
                            self.driver.find_elements(By.XPATH, '//div[contains(text(), "invalid")]')
            
            if invalid_popup:
                time.sleep(1)
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                return {"status": "error", "message": "Numero invalido ou nao possui WhatsApp"}

            # Se chegou aqui, clica em enviar.
            send_button = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]')
            time.sleep(1)
            send_button.click()
            time.sleep(2) 
            
            return {"status": "sent", "message": "Mensagem enviada"}
            
        except Exception as e:
            return {"status": "error", "message": f"Falha tecnica: {str(e)}"}

bot_instance = WhatsAppBot()