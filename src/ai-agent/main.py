import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from agent import DataAgent
from messenger import TelegramMessenger
from dotenv import load_dotenv

load_dotenv()

agente = DataAgent()
messenger = TelegramMessenger()


async def responder(update: Update, context):
    try:
        texto_usuario = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        loop = asyncio.get_event_loop()
        resposta = await loop.run_in_executor(None, agente.chat, texto_usuario)

        if not resposta:
            resposta = "Desculpe, não consegui processar uma resposta agora. Pode repetir?"

        try:
            await update.message.reply_text(resposta, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(resposta)

    except Exception as e:
        print(f"❌ Erro crítico na função responder: {e}")
        await update.message.reply_text("Houve um erro interno ao processar sua pergunta.")


async def disparar_relatorio_startup(app: Application):
    """Executa o relatório assim que o loop do bot inicia."""
    print("📊 Gerando relatório inicial...")
    try:
        loop = asyncio.get_event_loop()
        relatorio = await loop.run_in_executor(None, agente.gerar_relatorio_diario)
        messenger.enviar_mensagem(f"📊 *Relatório de Inicialização:*\n\n{relatorio}")
        print("✅ Relatório enviado com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro no relatório: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando Sistema...")

    builder = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN"))
    builder.connect_timeout(30).read_timeout(30).write_timeout(30)

    app = builder.post_init(disparar_relatorio_startup).build()

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

    print("🤖 Bot ouvindo no Telegram!")
    app.run_polling(
        poll_interval=1.0,
        timeout=30,
        bootstrap_retries=5,
        close_loop=False
    )