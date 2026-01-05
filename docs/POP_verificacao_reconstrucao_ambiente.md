# POP-001: Verificação e Reconstrução de Ambiente

**OBJETIVO:** Garantir que o ambiente de desenvolvimento seja uma réplica exata e funcional do padrão aprovado.

**FLUXO DE EXECUÇÃO:**

1. **Pré-Migração / Início de Trabalho:**
   * Acessar o diretório raiz do projeto.
   * Executar o script: `python scripts/verify_env.py`
   * Ler o relatório de saída.

2. **Análise de Divergências:**
   * Se o script retornar `[AUSENTE]` ou `[VERSÃO INCORRETA]`: **PARAR**.
   * Não tentar rodar o projeto.
   * Executar as instalações listadas no relatório.
   * Reexecutar o script até obter `[STATUS: VERDE/OK]`.

3. **Desenvolvimento/Alteração (Norma Extremo Zero):**
   * Caso seja necessário alterar a estrutura (ex: banco de dados, build do executável):
   * **DELETAR** as pastas de artefatos antigos (`dist`, `build`, `__pycache__`).
   * **REGERAR** os arquivos de configuração do zero.
   * **EXECUTAR** o comando de build limpo.
