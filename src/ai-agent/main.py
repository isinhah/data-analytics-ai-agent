import os
import re
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from agent import DataAgent
from dotenv import load_dotenv

load_dotenv()

agente = DataAgent()

def preparar_para_telegram(texto):
    """Escapa caracteres para MarkdownV2, ignorando blocos de código."""
    partes = re.split(r'(```.*?```)', texto, flags=re.DOTALL)
    texto_final = []

    for parte in partes:
        if parte.startswith('```'):
            texto_final.append(parte)
        else:
            chars_especiais = r'_[]()~`>#+-=|{}.!'
            res = re.sub(f'([{re.escape(chars_especiais)}])', r'\\\1', parte)
            texto_final.append(res)

    return "".join(texto_final)

async def start(update: Update, context):
    """Inicia o bot e explica os comandos."""
    boas_vindas = (
        "🤖 *Olá! O Analista de E-commerce está online.*\n\n"
        "Para ver os KPIs principais agora, use o comando:\n"
        "👉 /relatorio\n\n"
        "Ou simplesmente me envie uma pergunta sobre as vendas, produtos ou logística!"
    )
    await update.message.reply_text(preparar_para_telegram(boas_vindas), parse_mode="MarkdownV2")

async def comando_relatorio(update: Update, context):
    """Gera o relatório apenas quando solicitado via /relatorio."""
    await update.message.reply_text("📊 Gerando relatório executivo, um momento...")
    try:
        loop = asyncio.get_running_loop()
        relatorio_cru = await loop.run_in_executor(None, agente.gerar_relatorio_diario)
        relatorio_final = preparar_para_telegram(relatorio_cru)

        await update.message.reply_text(
            text=f"📊 *Relatório Consolidado:*\n\n{relatorio_final}",
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"⚠️ Erro no comando relatório: {e}")
        await update.message.reply_text("❌ Erro ao gerar relatório.")

async def responder(update: Update, context):
    """Responde perguntas livres usando o Agente."""
    try:
        texto_usuario = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        loop = asyncio.get_running_loop()
        resposta_crua = await loop.run_in_executor(None, agente.chat, texto_usuario)

        if not resposta_crua:
            await update.message.reply_text("Sem resposta do agente.")
            return

        resposta_final = preparar_para_telegram(resposta_crua)

        try:
            await update.message.reply_text(resposta_final, parse_mode="MarkdownV2")
        except Exception as e:
            print(f"⚠️ Erro MarkdownV2: {e}. Enviando texto puro.")
            await update.message.reply_text(resposta_crua)

    except Exception as e:
        print(f"❌ Erro crítico em responder: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar sua análise.")

if __name__ == "__main__":
    print("🚀 Iniciando Sistema...")

    app = (
        Application.builder()
        .token(os.getenv("TELEGRAM_BOT_TOKEN"))
        .connect_timeout(120)
        .read_timeout(120)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("relatorio", comando_relatorio))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

    print("🤖 Bot ouvindo no Telegram!")
    app.run_polling(drop_pending_updates=True)