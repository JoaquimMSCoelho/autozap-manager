import sys
import os
import subprocess

def print_status(component, status, message=""):
    # Cores para terminal: Verde (92) e Vermelho (91)
    color = "\033[92m" if status == "OK" else "\033[91m" 
    reset = "\033[0m"
    print(f"[{component.ljust(15)}] {color}{status}{reset} {message}")

def check_command(command, version_flag="--version"):
    """Verifica se um comando existe no sistema e retorna a versão."""
    try:
        # shell=True para compatibilidade com Windows
        result = subprocess.run(f"{command} {version_flag}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip().split('\n')[0]
        else:
            return False, None
    except Exception:
        return False, None

def main():
    print("="*60)
    print("   VERIFICADOR DE AMBIENTE - AUTOZAP MANAGER")
    print("   Norma: Extremo Zero | Status: Validando...")
    print("="*60)
    
    # 1. Verificar Python (Execução Atual)
    py_version = sys.version.split()[0]
    if sys.version_info >= (3, 10):
        print_status("PYTHON", "OK", f"Versão: {py_version}")
    else:
        print_status("PYTHON", "ERRO", f"Versão obsoleta: {py_version}. Requer 3.10+")

    # 2. Verificar Node.js
    node_ok, node_ver = check_command("node", "-v")
    if node_ok:
        print_status("NODE.JS", "OK", f"Versão: {node_ver}")
    else:
        print_status("NODE.JS", "CRÍTICO", "Não instalado ou não está no PATH.")

    # 3. Verificar Ferramentas Essenciais
    tools = ["git", "npm"]
    for tool in tools:
        ok, ver = check_command(tool)
        if ok:
            print_status(tool.upper(), "OK", "Instalado")
        else:
            print_status(tool.upper(), "AUSENTE", "Instalação obrigatória necessária.")

    # 4. Verificar Estrutura de Pastas (Deve ser rodado da Raiz)
    # Lista de pastas esperadas na raiz do projeto
    folders = ["backend", "frontend", "docs", "scripts"]
    
    print("-" * 60)
    for folder in folders:
        if os.path.isdir(folder):
            print_status(f"DIR: {folder}", "OK", "Encontrado")
        else:
            print_status(f"DIR: {folder}", "ALERTA", "Diretório não encontrado na raiz.")

    # 5. Verificar Arquivos Críticos
    req_file = os.path.join("backend", "requirements.txt")
    if os.path.exists(req_file):
        print_status("REQ.TXT", "OK", "Encontrado em backend/")
    else:
        print_status("REQ.TXT", "ERRO", "backend/requirements.txt sumiu!")

    print("-" * 60)
    print("CONCLUSÃO DA ANÁLISE:")
    print("Se tudo estiver VERDE (OK), o ambiente está aprovado.")
    print("Se houver VERMELHO, corrija antes de trabalhar.")
    print("=" * 60)

if __name__ == "__main__":
    main()
