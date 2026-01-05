# CHECKLIST DE AMBIENTE E RECONSTRUÇÃO (Norma Extremo Zero)
**Projeto:** AutoZap Manager
**Data:** __/__/____

## 1. Validação de Ferramentas (Base)
- [ ] Python 3.10+ instalado e no PATH.
- [ ] Node.js instalado (LTS).
- [ ] Git instalado e autenticado.

## 2. Validação do Repositório (Extremo Zero)
- [ ] Script `python scripts/verify_env.py` executado e retornou TUDO VERDE.
- [ ] Pastas de lixo (`dist`, `build`, `__pycache__`) foram deletadas antes do build.

## 3. Configuração de Dependências
- [ ] Backend: `pip install -r requirements.txt` executado sem erros.
- [ ] Frontend: `npm install` executado na pasta frontend.

## 4. Teste de Fumaça
- [ ] Backend roda sem crashar.
- [ ] Frontend compila sem erros.

---
**Declaro que segui a norma de Reconstrução do Zero.**
