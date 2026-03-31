import pandas as pd
import os
import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = './data'
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. LEITURA E LIMPEZA (Seu código original)
df_vendas = pd.read_csv(f'{DATA_DIR}/vendas_transacional.csv')
df_logistica = pd.read_csv(f'{DATA_DIR}/logistica_satisfacao.csv')

date_cols = ['data_compra', 'data_postagem', 'data_previsao_entrega', 'data_entrega_real']
for df in [df_vendas, df_logistica]:
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    text_cols = df.select_dtypes(include=['object']).columns
    df[text_cols] = df[text_cols].apply(lambda x: x.str.strip())

# 2. CONSOLIDAÇÃO E KPIs
df_consolidado = pd.merge(df_vendas, df_logistica, on='id_pedido', how='left')

# Cálculos Financeiros
df_consolidado['valor_venda_final'] = (df_consolidado['valor_unitario_venda'] * df_consolidado['quantidade']) * (
            1 - df_consolidado['percentual_desconto'].fillna(0))
df_consolidado['custo_total'] = df_consolidado['custo_unitario'] * df_consolidado['quantidade']
df_consolidado['lucro_liquido'] = df_consolidado['valor_venda_final'] - df_consolidado['custo_total'] - df_consolidado[
    'valor_frete'].fillna(0)
df_consolidado['margem_lucro_pct'] = df_consolidado['lucro_liquido'] / df_consolidado['valor_venda_final'].replace(0, 1)

# KPIs de Logística
df_consolidado['dias_atraso'] = (df_consolidado['data_entrega_real'] - df_consolidado['data_previsao_entrega']).dt.days
df_consolidado['status_entrega'] = df_consolidado['dias_atraso'].apply(lambda x: 'No Prazo' if x <= 0 else 'Atrasado')


# 3. ENVIO PARA O SUPABASE
def upload_to_supabase(df, table_name):
    """Envia o DataFrame para o Supabase via SQLAlchemy."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Erro: DATABASE_URL não encontrada no .env")
        return

    try:
        engine = create_engine(db_url)

        print(f"🚀 Enviando dados para a tabela '{table_name}'...")

        df.to_sql(table_name, engine, if_exists='replace', index=False)

        print(f"✅ Sucesso! Tabela '{table_name}' atualizada no Supabase.")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")

upload_to_supabase(df_consolidado, 'vendas_logistica_db')

# 4. SALVAMENTO LOCAL EM EXCEL COM TIMESTAMP
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
excel_name = f'RELATORIO_CONSOLIDADO_{timestamp}.xlsx'
excel_path = os.path.join(OUTPUT_DIR, excel_name)

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_consolidado.to_excel(writer, sheet_name='BASE DE DADOS', index=False)
    df_vendas.to_excel(writer, sheet_name='RAW_VENDAS', index=False)
    df_logistica.to_excel(writer, sheet_name='RAW_LOGISTICA', index=False)

print(f"💾 Cópia de segurança gerada em: {excel_path}")