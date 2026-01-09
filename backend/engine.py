from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import urllib.parse
import psutil 

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.is_running = False

    def _kill_zombies(self):
        """FAXINEIRO CIRÚRGICO"""
        print("[INFO] Iniciando varredura de processos zumbis...")
        current_dir = os.getcwd()
        target_folder = "chrome_cache"
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmd_str = " ".join(cmdline)
                        if target_folder in cmd_str and current_dir in cmd_str:
                            proc.kill()
                            killed_count += 1
                elif proc.info['name'] and 'chromedriver' in proc.info['name'].lower():
                    proc.kill()
            except:
                pass
        
        if killed_count > 0:
            print(f"[INFO] Limpeza concluída. {killed_count} processos removidos.")
            time.sleep(2) 

    def start(self):
        if self.is_running:
            return {"status": "already_running", "message": "Robo ja esta rodando!"}

        try:
            self._kill_zombies()
            print("[INFO:AutoZapEngine] --- MOTOR V17: TYPE & CLICK (HIBRIDO) ---")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            dir_path = os.getcwd()
            profile_path = os.path.join(dir_path, "chrome_cache")
            chrome_options.add_argument(f"user-data-dir={profile_path}")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("[INFO] Abrindo WhatsApp...")
            self.driver.get("https://web.whatsapp.com")
            self.is_running = True
            return {"status": "success", "message": "Navegador iniciado."}
        except Exception as e:
            print(f"[ERRO AO INICIAR] {str(e)}")
            return {"status": "error", "message": str(e)}

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.is_running = False
        return {"status": "success", "message": "Navegador fechado."}

    def _click_element(self, element):
        """Marreta JS"""
        self.driver.execute_script("arguments[0].click();", element)

    def send_message(self, phone, message_content):
        if not self.is_running or not self.driver:
            return {"status": "error", "message": "O robo esta desligado."}

        try:
            # 1. Preparação
            text_msg = message_content
            media_path = None
            
            if "|||media:" in message_content:
                parts = message_content.split("|||media:")
                text_msg = parts[0].strip()
                media_path = parts[1].strip()

            print(f"\n[ENGINE] Disparando para: {phone} | Mídia: {'SIM' if media_path else 'NÃO'}")

            # 2. Navegação
            encoded_text = urllib.parse.quote(text_msg) if text_msg else ""
            link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_text}"
            self.driver.get(link)

            # 3. Aguarda Chat
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )
            except:
                print(f"[TIMEOUT] Chat nao carregou para {phone}.")
                return {"status": "error", "message": "Timeout chat"}

            time.sleep(2)

            # 4. ROTINA DE MÍDIA (V17: Escreve -> Espera -> Clica)
            if media_path:
                if not os.path.exists(media_path):
                    print(f"[ERRO] Arquivo nao existe: {media_path}")
                else:
                    try:
                        print(f"[ENGINE] Injetando midia: {media_path}")
                        
                        # Injeção
                        self.driver.execute_script("""
                        document.querySelectorAll("input[type='file']").forEach(i => {
                            i.style.display='block'; i.style.height='1px'; i.style.opacity='1';
                        });
                        """)
                        
                        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            target = file_inputs[0]
                            ext = os.path.splitext(media_path)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png', '.mp4', '.avi']:
                                for inp in file_inputs:
                                    if "image" in (inp.get_attribute("accept") or ""):
                                        target = inp
                                        break
                            
                            target.send_keys(os.path.abspath(media_path))
                            print("[ENGINE] Aguardando Preview...")
                            
                            # Espera a caixa de legenda aparecer e ficar interativa
                            try:
                                caption_box = WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"]'))
                                )
                                time.sleep(1) # Estabiliza
                                
                                # --- PASSO 1: DIGITAR (Se tiver texto) ---
                                if text_msg:
                                    print("[ENGINE] Digitando legenda...")
                                    caption_box.click() # Foca
                                    # Limpa eventual lixo da URL
                                    caption_box.clear() 
                                    # Digita
                                    caption_box.send_keys(text_msg)
                                    time.sleep(1) # Espera o React processar o texto
                                
                                # --- PASSO 2: CLICAR NO BOTÃO (Não usar Enter) ---
                                print("[ENGINE] Buscando botão enviar...")
                                send_buttons_xpaths = [
                                    '//span[@data-icon="send"]',
                                    '//div[@aria-label="Enviar"]',
                                    '//div[contains(@class, "btn")]//span[@data-icon="send"]'
                                ]
                                
                                clicked = False
                                for xpath in send_buttons_xpaths:
                                    try:
                                        btns = self.driver.find_elements(By.XPATH, xpath)
                                        for btn in btns:
                                            if btn.is_displayed():
                                                print(f"[ENGINE] Clicando no botão ({xpath})...")
                                                self._click_element(btn)
                                                clicked = True
                                                break
                                    except: pass
                                    if clicked: break
                                
                                if not clicked:
                                    print("[AVISO] Botão não clicado. Tentando Enter de emergência.")
                                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()

                            except Exception as e_step:
                                print(f"[FALHA STEPS] {str(e_step)}")

                            is_video = ext in ['.mp4', '.avi']
                            time.sleep(15 if is_video else 5)
                            return {"status": "sent", "message": "Enviado com anexo"}

                    except Exception as e:
                        print(f"[FALHA ANEXO] {str(e)}")

            # 5. ROTINA DE TEXTO (Se não tinha mídia)
            if text_msg and text_msg.strip() != "":
                print("[ENGINE] Verificando envio de texto puro...")
                try:
                    box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    if box.text.strip():
                        # Clica no botão enviar em vez de dar enter
                        send_btn = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]')
                        self._click_element(send_btn)
                except:
                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()

            time.sleep(2)
            return {"status": "sent", "message": "Processado"}

        except Exception as e:
            print(f"[ERRO GERAL] {str(e)}")
            return {"status": "error", "message": str(e)}

bot_instance = WhatsAppBot()