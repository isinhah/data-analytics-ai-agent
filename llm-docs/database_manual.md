# 📘 Dicionário de Dados: E-commerce

## 1. Visão Geral
Este manual descreve a estrutura da tabela consolidada de vendas e logística gerada pelo script de processamento Python. O objetivo é fornecer contexto de negócio para o Agente de IA interpretar os dados corretamente. 

## 2. Estrutura da Tabela: `df_consolidado`

| Coluna | Tipo | Descrição Técnica / Regra de Negócio | Exemplo |
| :--- | :--- | :--- | :--- |
| **id_cliente** | Integer | Identificador único do comprador. | 185 |
| **data_compra** | Datetime | Data e hora em que o pedido foi realizado. | 26/03/2025 |
| **produto_nome** | String | Nome comercial do item vendido. | Placa de Vídeo RTX 4060 |
| **categoria** | String | Segmento do produto (Hardware, Acessórios, Licenças, Software). | Hardware |
| **quantidade** | Integer | Volume de unidades vendidas no pedido. | 3 |
| **custo_unitario** | Float | Valor de custo de aquisição de uma unidade do produto. | 2110.49 |
| **valor_unitario_venda**| Float | Preço de tabela (sem descontos) de uma unidade. | 2711.53 |
| **transportadora** | String | Empresa responsável pela logística (Loggi, FedEx, Jadlog, Correios). | FedEx |
| **valor_frete** | Float | Custo logístico cobrado para a entrega do pedido. | 149.90 |
| **cidade_destino** | String | Cidade para onde o produto foi enviado. | Joinville |
| **status_pedido** | String | Etapa atual do fluxo (Entregue, Em Trânsito, Cancelado). | Entregue |
| **nota_review** | Integer | Avaliação quantitativa do cliente (escala de 1 a 5 estrelas). | 5 |
| **comentario_cliente** | Text | Depoimento qualitativo sobre a experiência de compra e entrega. | "Entrega rápida, muito satisfeito!" |
| **valor_venda_final** | Float | **KPI:** Receita líquida após descontos e quantidade. | 8134.59 |
| **custo_total** | Float | **KPI:** Investimento total (Custo Unitário × Quantidade). | 6331.47 |
| **lucro_liquido** | Float | **KPI:** Saldo real (Venda Final - Custo Total - Valor Frete). | 1685.15 |
| **margem_lucro_pct** | Float | **KPI:** Percentual de rentabilidade sobre a venda final. | 0.2072 (20,72%) |
| **dias_atraso** | Integer | **KPI:** Diferença entre Entrega Real e Previsão. Negativo = Antecipado. | -3 |
| **status_entrega** | String | **KPI:** Classificação (No Prazo, Atrasado, Em Trânsito/Pendente). | No Prazo |

## 3. Categorias e Valores Conhecidos (Filtros Fixos)

Para realizar consultas precisas, utilize exatamente estes valores:

- **Categorias:** `Hardware`, `Acessórios`, `Licenças`, `Software`.
- **Transportadoras:** `Correios`, `FedEx`, `Jadlog`, `Loggi`.
- **Status de Entrega:** `No Prazo`, `Atrasado`, `Em Trânsito / Pendente`.
- **Status de Pedido:** `Entregue`, `Em Trânsito`, `Cancelado`.
- **Escala de Satisfação** (nota_review): 1 a 5 (Sendo 1 a pior nota e 5 a melhor).
- **Cidades Frequentes:** `São Paulo`, `Joinville`, `Curitiba`, `Rio de Janeiro`, `Belo Horizonte`, `Salvador`, `Recife`.

## 4. Regras de Negócio

- **Performance de Prazo:** Valores NEGATIVOS em `dias_atraso` indicam sucesso (entrega antes do prazo).
- **Saúde Financeira:** - Margem > 30%: **Alta**
    - Margem entre 10% e 30%: **Média**
    - Margem < 10%: **Crítica (Atenção)**
    - Margem < 0%: **Prejuízo Operacional**
- **Pedidos Cancelados:** Se `status_pedido` for 'Cancelado', o lucro deve ser desconsiderado na soma de performance real.
- **Nível de Satisfação (nota_review):**
    - 4 e 5: Status Ideal (Promotores).
    - 3 ou menor: Status Preocupante (Detratores/Neutros).

## 5. Lógica de Interpretação & Insights

- **Análise Semântica (NLP):** Classifique a origem da insatisfação no `comentario_cliente` por palavras-chave:
    - **Logística:** "demora", "prazo", "entregador", "atraso", "rastreio", "transportadora".
    - **Produto:** "defeito", "errado", "estragado", "qualidade", "quebrado", "veio outro".
- **Classificação de Satisfação:**
    - Detrator: `nota_review` <= 2. (Prioridade para análise de texto).
    - Promotor: `nota_review` >= 4.
- **Diagnóstico de Causa Raiz:**
    - `nota_review` baixa + `status_entrega` 'Atrasado' significa Falha da Transportadora.
    - `nota_review` baixa + `status_entrega` 'No Prazo' significa Falha de Produto/Anúncio.
- **Saúde Financeira:** Se `margem_lucro_pct` < 0, sinalize como "Operação com Prejuízo" e verifique o peso do `valor_frete` no resultado.
- **Priorização de Performance:** Recomende transportadoras que equilibram: Alto Volume + Alta Margem + Baixo Índice de Atraso.

## 4. Regras de Negócio

- **Pedidos Cancelados:** Se `status_pedido` for 'Cancelado', o `lucro_liquido` deve ser ignorado ou tratado como perda de oportunidade, pois não houve receita real.
- **Pedidos Pendentes:** Se `status_entrega` for 'Em Trânsito / Pendente', a coluna `dias_atraso` estará vazia (null). A IA não deve calcular performance para estes itens até que a entrega seja concluída.
- **Cálculo de Margem:** A `margem_lucro_pct` é calculada sobre o `valor_venda_final`. Margens acima de 50% são consideradas "Altas", entre 20% e 50% "Médias" e abaixo de 10% "Críticas".
- **Filtro de Reclamação:** Uma `nota_review` <= 2 é automaticamente uma "Reclamação Crítica", independente do texto no comentário.

## 5. Exemplos de Perguntas de Negócio (Benchmark)

1. Performance Logística: "Qual transportadora apresenta o maior índice de atrasos na categoria 'Hardware' e como isso afeta a nota média?"
2. Análise de Causa Raiz (NLP): "Analise as reviews negativas: o problema predominante é a qualidade dos produtos ou a demora das transportadoras?"
3. Eficiência Financeira: "Existem cidades ou transportadoras onde o custo do frete está consumindo mais de 15% do lucro líquido?"
4. Detecção de Prejuízo: "Quais produtos operaram com margem de lucro negativa e qual foi o impacto do frete nesses casos?"
5. Simulação de Cenários: "Se desconsiderarmos a transportadora [Nome], como ficariam nossos indicadores de satisfação (Promotores vs Detratores)?"
6. Visão por Categoria: "Quais subcategorias de 'Acessórios' estão com margem crítica (abaixo de 10%) e possuem mais de 3 dias de atraso médio?"

*Documento de referência para Agente de IA*