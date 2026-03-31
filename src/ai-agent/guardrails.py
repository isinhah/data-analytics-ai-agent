class SQLGuardrails:
    def __init__(self):
        self.prohibited_commands = [
            "drop", "delete", "update", "insert", "alter",
            "truncate", "grant", "revoke", "create"
        ]

    def validar_query(self, sql: str) -> tuple[bool, str]:
        """
        Valida se a query é segura.
        Retorna (True, query_limpa) ou (False, mensagem_erro).
        """
        sql_clean = sql.strip().lower()

        if any(cmd in sql_clean for cmd in self.prohibited_commands):
            return False, "⚠️ Bloqueio de Segurança: Apenas consultas de leitura são permitidas."

        if not (sql_clean.startswith("select") or sql_clean.startswith("with")):
            return False, "⚠️ Erro: Formato de consulta não permitido."

        if "limit" not in sql_clean:
            sql = sql.strip().rstrip(';') + " LIMIT 100;"

        return True, sql

    @staticmethod
    def testar_seguranca():
        guard = SQLGuardrails()

        testes = [
            "SELECT * FROM vendas_logistica_db",
            "DROP TABLE vendas_logistica_db",
            "SELECT * FROM vendas; DELETE FROM vendas;",
            "UPDATE vendas_logistica_db SET valor = 0"
        ]

        print("🛡️ Iniciando Auditoria de Segurança...")
        for query in testes:
            sucesso, resultado = guard.validar_query(query)
            status = "✅ PASSOU" if sucesso else "❌ BLOQUEADO"
            print(f"Query: {query[:30]}... | {status} | Msg: {resultado}")

if __name__ == "__main__":
    SQLGuardrails.testar_seguranca()