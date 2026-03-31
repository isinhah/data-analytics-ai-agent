import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class DataAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.engine = create_engine(os.getenv("DATABASE_URL"))

        caminho_db = BASE_DIR / "llm-docs" / "database_manual.md"
        caminho_agente = BASE_DIR / "llm-docs" / "agent_manual.md"

        if not caminho_db.exists():
            raise FileNotFoundError(f"Manual do banco não encontrado em: {caminho_db}")

        with open(caminho_db, "r", encoding="utf-8") as f:
            self.db_manual = f.read()

        with open(caminho_agente, "r", encoding="utf-8") as f:
            self.agent_manual = f.read()

        print(f"🚀 Agente inicializado. Root: {BASE_DIR}")

    def executar_sql(self, sql: str):
        """Tool: Executa queries SELECT/WITH no Supabase."""
        is_safe, result = self.guardrails.validate_query(sql)

        if not is_safe:
            print(f"🛑 Tentativa de query bloqueada: {sql}")
            return result

        try:
            print(f"🔍 [SQL SEGURO]: {result}")
            with self.engine.connect() as conn:
                df_res = pd.read_sql(text(result), conn)
                return df_res.to_json(orient='records')
        except Exception as e:
            return f"Erro na execução do SQL: {str(e)}"

    def chat(self, pergunta_usuario):
        exemplo_formatacao = """
        *Relatório Analítico de Vendas* 📊

        Olá Time, segue a análise solicitada:

        🛍️ *Hardware*: Lucro de **R$ 456.865,09** com margem de **30,29%**.
        🖥️ *Software*: Lucro de **R$ 55.107,67** com margem de **35,87%**.
        🎧 *Acessórios*: Lucro de **R$ 27.801,95** com margem de **21,13%**.

        💡 *Insight do Analista*: A categoria Software possui a melhor margem, sugerindo espaço para ações de marketing agressivas para aumentar o volume. Hardware gera o maior volume, mas a margem é mais apertada.
        """

        system_instructions = f"""
        {self.agent_manual}

        ### SCHEMA DO BANCO (Tabela: vendas_logistica_db):
        {self.db_manual}

        ### INSTRUÇÕES TÉCNICAS E DE FORMATAÇÃO:
        - Use OBRIGATORIAMENTE a ferramenta 'executar_sql' para qualquer análise.
        - JAMAIS responda com a tabela textual crua (ex: * Categoria: Lucro ...).
        - **Formate o resultado como um relatório executivo profissional para o Telegram, usando emojis e negrito para destacar valores.**
        - Use este estilo como exemplo de formatação:
        {exemplo_formatacao}
        - Tente sempre adicionar um pequeno insight (💡) ao final se os dados permitirem.
        - Se o resultado vier vazio, explique ao usuário de forma amigável.
        
        ### COMPORTAMENTO DO AGENTE:
        - Você é um Analista de Dados exclusivo desta loja. 
        - NEGUE educadamente qualquer pergunta que não seja sobre vendas, logística ou produtos.
        - Se o usuário fugir do tema, responda: 'Sinto muito, meu acesso é restrito aos dados de E-commerce. Como posso ajudar com a análise de hoje?'
        - Sempre use a ferramenta 'executar_sql' para responder perguntas sobre números.
        """

        messages = [types.Content(role="user", parts=[types.Part(text=pergunta_usuario)])]

        for _ in range(10):
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_instructions,
                    tools=[self.executar_sql]
                )
            )

            if not response.candidates[0].content.parts[0].function_call:
                return response.text

            call = response.candidates[0].content.parts[0].function_call

            resultado_db = self.executar_sql(call.args['sql'])

            messages.append(response.candidates[0].content)

            messages.append(types.Content(
                role="tool",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name="executar_sql",
                        response={"result": resultado_db}
                    )
                )]
            ))

        return "Desculpe, excedi o limite de tentativas para processar essa análise."

    def gerar_relatorio_diario(self):
        """Gera o relatório com os 4 KPIs principais do Dashboard."""
        sql_kpis = """
                   SELECT SUM(valor_venda_final) as receita_total, \
                          SUM(lucro_liquido) as lucro_total, \
                          AVG(margem_lucro_pct) * 100 as margem_media_pct, \
                          (COUNT(CASE WHEN status_entrega = 'No Prazo' THEN 1 END) * 100.0 / COUNT(*)) as pct_no_prazo
                   FROM vendas_logistica_db; \
                   """
        dados = self.executar_sql(sql_kpis)

        prompt = f"""
        Aja como um analista de e-commerce sênior.
        Dados reais extraídos do banco: {dados}

        Gere um relatório executivo para o Telegram seguindo EXATAMENTE este padrão:

        1. 💰 **Financeiro**: Receita e Lucro (formate como R$).
        2. 📈 **Eficiência**: Margem Média (formate como %).
        3. 🚚 **Logística**: Pedidos no Prazo (formate como %).

        REGRAS:
        - Retorne APENAS o texto final da mensagem, sem introduções como "Aqui está o relatório".
        - Se os dados em {dados} estiverem vazios ou nulos, responda APENAS: "⚠️ Atenção: A base de dados atual não possui registros para o período solicitado."
        - Se a porcentagem no prazo for menor que 80%, adicione um alerta ⚠️ ao lado do valor.
        - Use negrito e emojis para destacar os KPIs.
        - Finalize com uma frase curta de insight sobre os números apresentados.
        """

        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
        return response.text