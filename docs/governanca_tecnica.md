# POLÍTICA DE GOVERNANÇA TÉCNICA (PGT-01)

**1. PRINCÍPIO FUNDAMENTAL (CLÁUSULA PÉTREA)**
Fica estabelecido o padrão de **"Desenvolvimento a Partir do Extremo Zero"**.
É estritamente vedada a prática de "remendos", edições parciais ou incrementos diretos em artefatos corrompidos.
* **Falhou?** Apaga-se e reconstrói-se o artefato.
* **Mudou?** Regenera-se o fluxo completo.

**2. CONSISTÊNCIA DE AMBIENTE**
Nenhum código será promovido a Produção ou executado em novo equipamento sem a prévia validação pelo **Script de Verificação de Ambiente (SVA)**.

**3. RESPONSABILIDADES**
* **Arquiteto:** Manter os scripts de verificação atualizados.
* **Desenvolvedor:** Executar a limpeza (`clean`) e reconstrução (`build`) a cada ciclo de entrega.
