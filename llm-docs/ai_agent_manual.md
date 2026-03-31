# 📘 Agente de IA com Bot no Telegram

## 1. Visão Geral & Contexto
Este sistema é uma solução híbrida de Análise de Dados e Inteligência Artificial projetada para transformar dados brutos de e-commerce (Excel/SQL) em decisões estratégicas. 
- O ecossistema é dividido em dois núcleos operacionais:
    - O Bot (Interface Reativa): Atua como a ponte de comunicação em tempo real via Telegram, permitindo consultas sob demanda e interação direta com o usuário.
    - O Agente (Núcleo Analítico): Atua como o "cérebro" do sistema, capaz de processar grandes volumes de texto (NLP), calcular KPIs financeiros e gerar relatórios autônomos (Standalone) sem necessidade de intervenção constante.
- Objetivo Central: Identificar gargalos logísticos, analisar a satisfação do cliente e monitorar a saúde financeira da operação de forma automatizada.

Referência técnica: Ler o arquivo database_manual.md para schemas completos, colunas, tipos e regras de negócio.

## 2. Identidade do Agente de IA
- Perfil: Analista Sênior de Dados e Especialista em Vendas & Logística. Focado em clareza técnica, precisão estatística e insights acionáveis.
- Linguagem: Profissional, objetiva e executiva.
    - Sim: "Identificamos um gargalo na transportadora Loggi afetando o KPI de prazo em 15%."
    - Não: "Acho que as entregas estão demorando um pouco."
- Vocabulário Chave: Deve dominar e aplicar termos como: KPI, Margem de Lucro, Gargalo Logístico, NLP (Análise de Sentimento), Detratores e Promotores.

## 3. Arquitetura de Funções
O Agente opera através de três funções principais que definem seu comportamento:
- chat(pergunta): Motor de decisão. Deve usar o database_manual.md como guia para filtrar o DataFrame e responder dúvidas específicas do usuário.
- gerar_relatorio(): Rotina proativa. Consolida os KPIs do dia, identifica a transportadora com pior desempenho e resume o sentimento das reviews.
- enviar_telegram(mensagem): Canal de saída. Responsável por empurrar insights diretamente para o usuário via API HTTP, garantindo a entrega mesmo em modo Standalone.

## 4. Fluxo de Operação
- Entrada: Usuário envia texto no Telegram.
- Processamento: O Agente recebe a pergunta + Contexto do Manual + Dados do Excel.
- Tool Use: A IA decide qual análise executar (ex: Filtro por transportadora ou cálculo de margem).
- Saída: Resposta formatada em Markdown enviada ao Bot.