# X-BOT V2 - LLM Local (Ollama Ready) Version
import logging, random, requests, socket, json
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

BOT_TOKEN = "8002370630:AAEqe2c1wM9vtdcLPHAiOMRLqVN9V9vlJyM"  # Ganti dengan token bot kamu
ENABLE_AI = False

# === AI via Ollama ===
async def ai_reply(text: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": text, "stream": False}
        )
        result = response.json()
        return result.get("response", "Tidak ada respon.")
    except Exception as e:
        return f"⚠️ LLM Error: {e}"

# === Game Commands ===
async def dadu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 Dadu: {random.randint(1, 6)}")

async def koin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🪙 Koin: {random.choice(['HEADS', 'TAILS'])}")

async def suit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✊✋✌️: {random.choice(['Batu', 'Gunting', 'Kertas'])}")

async def tebakangka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    angka = random.randint(1, 10)
    await update.message.reply_text("🎯 Aku sudah pilih angka 1-10, tebak berapa?")
    context.user_data["angka"] = angka

async def jawab_tebakan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "angka" in context.user_data:
        try:
            tebakan = int(update.message.text.strip())
            jawaban = context.user_data["angka"]
            if tebakan == jawaban:
                await update.message.reply_text("🎉 Benar!")
            else:
                await update.message.reply_text(f"❌ Salah. Angkanya {jawaban}")
            del context.user_data["angka"]
        except:
            pass

# === IP Trace ===
async def iptrace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("📍 Contoh: /iptrace 1.1.1.1")
        return
    ip = context.args[0]
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ip-api.com/json/{ip}") as resp:
            data = await resp.json()
            if data["status"] == "success":
                reply = f"""🌍 IP Info:
IP: {ip}
Negara: {data['country']}
Kota: {data['city']}
Isp: {data['isp']}
Koordinat: {data['lat']},{data['lon']}"""
            else:
                reply = "❌ IP tidak ditemukan."
    await update.message.reply_text(reply)

# === Whois / DNS / Portscan ===
async def whois_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: /whois google.com")
        return
    domain = context.args[0]
    try:
        import whois
        info = whois.whois(domain)
        await update.message.reply_text(str(info))
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

async def dns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: /dns google.com")
        return
    try:
        result = socket.gethostbyname(context.args[0])
        await update.message.reply_text(f"DNS: {result}")
    except:
        await update.message.reply_text("❌ Tidak bisa resolve DNS.")

async def portscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Contoh: /portscan 1.1.1.1")
        return
    host = context.args[0]
    open_ports = []
    for port in [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306]:
        try:
            s = socket.create_connection((host, port), timeout=0.5)
            open_ports.append(port)
            s.close()
        except:
            pass
    await update.message.reply_text(f"🔍 Open ports di {host}: {open_ports}")

# === Auto Save Media ===
async def save_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for file in [update.message.photo, update.message.document, update.message.video]:
        if file:
            f = file[-1] if isinstance(file, list) else file
            path = await f.get_file()
            await path.download_to_drive()
            await update.message.reply_text("✅ Media disimpan.")

# === Auto AI Responder ===
async def auto_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ENABLE_AI:
        prompt = update.message.text
        response = await ai_reply(prompt)
        await update.message.reply_text(response)

# === MAIN ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 X-BOT V2 Siap Tempur!")

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dadu", dadu))
    app.add_handler(CommandHandler("koin", koin))
    app.add_handler(CommandHandler("suit", suit))
    app.add_handler(CommandHandler("tebakangka", tebakangka))
    app.add_handler(CommandHandler("iptrace", iptrace))
    app.add_handler(CommandHandler("whois", whois_cmd))
    app.add_handler(CommandHandler("dns", dns_cmd))
    app.add_handler(CommandHandler("portscan", portscan))

    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, save_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, jawab_tebakan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_ai))

    print("🤖 X-BOT V2 berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
