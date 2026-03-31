import pandas as pd
import os

DATA_DIR = '../data'
OUTPUT_DIR = '../output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

df_vendas = pd.read_csv(f'{DATA_DIR}/vendas_transacional.csv')
df_logistica = pd.read_csv(f'{DATA_DIR}/logistica_satisfacao.csv')

date_cols = ['data_compra', 'data_postagem', 'data_previsao_entrega', 'data_entrega_real']
for col in date_cols:
    if col in df_vendas.columns:
        df_vendas[col] = pd.to_datetime(df_vendas[col], errors='coerce')
    if col in df_logistica.columns:
        df_logistica[col] = pd.to_datetime(df_logistica[col], errors='coerce')

text_cols = ['produto_nome', 'categoria', 'cidade_destino', 'status_pedido', 'transportadora']
for df in [df_vendas, df_logistica]:
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()

df_consolidado = pd.merge(df_vendas, df_logistica, on='id_pedido', how='left')

df_consolidado['valor_frete'] = df_consolidado['valor_frete'].fillna(0)
df_consolidado['percentual_desconto'] = df_consolidado['percentual_desconto'].fillna(0)

# KPIs Financeiros (Lucro Real e Margem)
df_consolidado['valor_venda_final'] = (df_consolidado['valor_unitario_venda'] * df_consolidado['quantidade']) * (1 - df_consolidado['percentual_desconto'])
df_consolidado['custo_total'] = df_consolidado['custo_unitario'] * df_consolidado['quantidade']
df_consolidado['lucro_liquido'] = df_consolidado['valor_venda_final'] - df_consolidado['custo_total'] - df_consolidado['valor_frete']

df_consolidado['margem_lucro_pct'] = df_consolidado['lucro_liquido'] / df_consolidado['valor_venda_final'].replace(0, 1)

# KPIs de Logística (Performance de Entrega)
df_consolidado['dias_atraso'] = (df_consolidado['data_entrega_real'] - df_consolidado['data_previsao_entrega']).dt.days

def rotular_prazo(row):
    if pd.isna(row['data_entrega_real']):
        return 'Em Trânsito / Pendente'
    return 'No Prazo' if row['dias_atraso'] <= 0 else 'Atrasado'

df_consolidado['status_entrega'] = df_consolidado.apply(rotular_prazo, axis=1)

excel_name = 'RELATORIO_CONSOLIDADO.xlsx'
excel_path = os.path.join(OUTPUT_DIR, excel_name)

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    # Aba Principal para o Dashboard
    df_consolidado.to_excel(writer, sheet_name='BASE DE DADOS', index=False)
    # Abas de Auditoria (Dados crus)
    df_vendas.to_excel(writer, sheet_name='RAW_VENDAS', index=False)
    df_logistica.to_excel(writer, sheet_name='RAW_LOGISTICA', index=False)

print(f"Sucesso! Relatório gerado em: {excel_path}")
print(f"Total de linhas processadas: {len(df_consolidado)}")