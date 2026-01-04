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
import logging
import os

# Configurando logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoZapEngine")

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return {"status": "error", "message": "Robo ja esta rodando"}

        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            # Cache persistente
            cache_path = os.path.join(os.getcwd(), "chrome_cache")
            chrome_options.add_argument(f"user-data-dir={cache_path}") 

            logger.info("Iniciando Driver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.get("https://web.whatsapp.com")
            self.is_running = True
            return {"status": "success", "message": "Navegador iniciado."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_running = False
            return {"status": "success", "message": "Navegador fechado"}
        return {"status": "error", "message": "Navegador ja esta fechado"}

    def send_message(self, phone, message):
        if not self.is_running:
            return {"status": "error", "message": "O Robo esta desligado"}

        try:
            logger.info(f"Navegando para: {phone}")
            phone = "".join(filter(str.isdigit, phone))
            msg_encoded = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={phone}&text={msg_encoded}"
            self.driver.get(link)

            # --- ESTRATEGIA MULTI-ALVO ---
            try:
                # Espera 40s por QUALQUER sinal de vida do chat
                WebDriverWait(self.driver, 40).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]')), # Caixa padrao
                        EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]')),         # Caixa alternativa
                        EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]')),      # Botao enviar
                        EC.presence_of_element_located((By.ID, 'main')),                              # Painel principal
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "inválido")]')),
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "invalid")]'))
                    )
                )
            except TimeoutException:
                 # TIRA FOTO DO ERRO
                 self.driver.save_screenshot("erro_visual.png")
                 logger.error("Timeout! Screenshot salvo como 'erro_visual.png'")
                 return {"status": "error", "message": "Timeout - Veja a foto 'erro_visual.png' na pasta backend"}

            # Checa invalido
            invalid_popup = self.driver.find_elements(By.XPATH, '//div[contains(text(), "inválido")]') or \
                            self.driver.find_elements(By.XPATH, '//div[contains(text(), "invalid")]')
            
            if invalid_popup:
                time.sleep(1)
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                return {"status": "error", "message": "Numero invalido"}

            # Tenta Enviar (Foca no Main e aperta Enter)
            try:
                # Tenta focar na caixa de texto pelo Role
                input_box = self.driver.find_elements(By.XPATH, '//div[@contenteditable="true"]')
                if not input_box:
                    input_box = self.driver.find_elements(By.XPATH, '//div[@role="textbox"]')
                
                if input_box:
                    input_box[0].click()
                    time.sleep(0.5)
                    input_box[0].send_keys(Keys.ENTER)
                    logger.info("Enviado via ENTER (Input Box)")
                    time.sleep(2)
                    return {"status": "sent", "message": "Enviado"}
                
                # Se nao achou caixa, tenta clicar no botao
                send_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]')
                send_btn.click()
                logger.info("Enviado via BOTAO")
                time.sleep(2)
                return {"status": "sent", "message": "Enviado"}

            except Exception as e:
                self.driver.save_screenshot("erro_clique.png")
                logger.error(f"Falha no clique final: {e}")
                return {"status": "error", "message": "Falha no envio final"}
            
        except Exception as e:
            return {"status": "error", "message": f"Falha tecnica: {str(e)}"}

bot_instance = WhatsAppBot()
