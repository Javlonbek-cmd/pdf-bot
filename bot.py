import telebot
from telebot import types
from PIL import Image
from PyPDF2 import PdfMerger
from pdf2docx import Converter
import qrcode
import os
import subprocess

TOKEN = "8001701759:AAEEwaUqg52Z1US3tmJWqshlZE4QJKSNGB4"

bot = telebot.TeleBot(TOKEN)

user_mode = {}
user_files = {}

# START
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🖼 Rasm → PDF")
    btn2 = types.KeyboardButton("📄 Word → PDF")
    btn3 = types.KeyboardButton("📑 PDF → Word")
    btn4 = types.KeyboardButton("📚 PDF Birlashtirish")
    btn5 = types.KeyboardButton("🛡 Watermark")
    btn6 = types.KeyboardButton("◼ QR Code")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)

    bot.send_message(
        message.chat.id,
        "🔥 SUPER PDF BOT 🔥\n\nKerakli bo‘limni tanlang 👇",
        reply_markup=markup
    )

# BUTTONLAR
@bot.message_handler(func=lambda m: True)
def buttons(message):

    text = message.text

    if text == "🖼 Rasm → PDF":
        user_mode[message.chat.id] = "img2pdf"
        user_files[message.chat.id] = []

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("✅ PDF Tayyorlash"))

        bot.send_message(
            message.chat.id,
            "🖼 Rasmlarni yuboring\n\nTugatgach tugmani bosing 👇",
            reply_markup=markup
        )

    elif text == "📄 Word → PDF":
        user_mode[message.chat.id] = "word2pdf"

        bot.send_message(
            message.chat.id,
            "📄 DOCX fayl yuboring"
        )

    elif text == "📑 PDF → Word":
        user_mode[message.chat.id] = "pdf2word"

        bot.send_message(
            message.chat.id,
            "📑 PDF yuboring"
        )

    elif text == "📚 PDF Birlashtirish":
        user_mode[message.chat.id] = "merge"
        user_files[message.chat.id] = []

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("✅ PDF Birlashtirish"))

        bot.send_message(
            message.chat.id,
            "📚 PDF fayllarni yuboring\n\nTugatgach tugmani bosing 👇",
            reply_markup=markup
        )

    elif text == "🛡 Watermark":
        user_mode[message.chat.id] = "watermark"

        bot.send_message(
            message.chat.id,
            "🛡 Rasm yuboring"
        )

    elif text == "◼ QR Code":
        user_mode[message.chat.id] = "qr"

        bot.send_message(
            message.chat.id,
            "✍️ QR uchun matn yuboring"
        )

    elif text == "✅ PDF Tayyorlash":

        files = user_files.get(message.chat.id, [])

        if not files:
            bot.send_message(message.chat.id, "❌ Rasm topilmadi")
            return

        pdf_name = f"{message.chat.id}.pdf"

        images = []

        for file in files:
            img = Image.open(file).convert("RGB")
            images.append(img)

        images[0].save(
            pdf_name,
            save_all=True,
            append_images=images[1:]
        )

        with open(pdf_name, "rb") as pdf:
            bot.send_document(message.chat.id, pdf)

        for file in files:
            if os.path.exists(file):
                os.remove(file)

        if os.path.exists(pdf_name):
            os.remove(pdf_name)

    elif text == "✅ PDF Birlashtirish":

        files = user_files.get(message.chat.id, [])

        if not files:
            bot.send_message(message.chat.id, "❌ PDF topilmadi")
            return

        merger = PdfMerger()

        for pdf in files:
            merger.append(pdf)

        output = f"{message.chat.id}_merged.pdf"

        merger.write(output)
        merger.close()

        with open(output, "rb") as f:
            bot.send_document(message.chat.id, f)

        for file in files:
            if os.path.exists(file):
                os.remove(file)

        if os.path.exists(output):
            os.remove(output)

# QR CODE
@bot.message_handler(func=lambda m: user_mode.get(m.chat.id) == "qr")
def qr_make(message):

    text = message.text

    img = qrcode.make(text)

    file_name = f"{message.chat.id}_qr.png"

    img.save(file_name)

    with open(file_name, "rb") as photo:
        bot.send_photo(message.chat.id, photo)

    os.remove(file_name)

# PHOTO
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    mode = user_mode.get(message.chat.id)

    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded = bot.download_file(file_info.file_path)

    file_name = f"{message.photo[-1].file_id}.jpg"

    with open(file_name, "wb") as f:
        f.write(downloaded)

    # IMAGE TO PDF
    if mode == "img2pdf":

        if message.chat.id not in user_files:
            user_files[message.chat.id] = []

        user_files[message.chat.id].append(file_name)

        bot.reply_to(
            message,
            f"✅ Rasm saqlandi: {len(user_files[message.chat.id])} ta"
        )

    # WATERMARK
    elif mode == "watermark":

        img = Image.open(file_name)

        watermark = Image.new("RGBA", img.size, (255, 255, 255, 0))

        final = Image.alpha_composite(
            img.convert("RGBA"),
            watermark
        )

        out = "watermark.png"

        final.save(out)

        bot.send_photo(message.chat.id, open(out, "rb"))

        os.remove(out)
        os.remove(file_name)

# DOCUMENT
@bot.message_handler(content_types=['document'])
def handle_docs(message):

    mode = user_mode.get(message.chat.id)

    file_info = bot.get_file(message.document.file_id)

    downloaded = bot.download_file(file_info.file_path)

    file_name = message.document.file_name

    with open(file_name, "wb") as f:
        f.write(downloaded)

    # WORD -> PDF
    if mode == "word2pdf":

        if not file_name.endswith(".docx"):
            bot.reply_to(message, "❌ DOCX yuboring")
            return

        bot.reply_to(message, "⏳ PDF tayyorlanmoqda...")

        output_pdf = file_name.replace(".docx", ".pdf")

        try:

            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                file_name,
                "--outdir",
                "."
            ])

            with open(output_pdf, "rb") as pdf:
                bot.send_document(message.chat.id, pdf)

        except Exception as e:
            bot.reply_to(message, f"❌ Xatolik:\n{e}")

    # PDF -> WORD
    elif mode == "pdf2word":

        if not file_name.endswith(".pdf"):
            bot.reply_to(message, "❌ PDF yuboring")
            return

        bot.reply_to(message, "⏳ Word tayyorlanmoqda...")

        word_name = file_name.replace(".pdf", ".docx")

        try:

            cv = Converter(file_name)
            cv.convert(word_name)
            cv.close()

            with open(word_name, "rb") as doc:
                bot.send_document(message.chat.id, doc)

        except Exception as e:
            bot.reply_to(message, f"❌ Xatolik:\n{e}")

    # PDF MERGE
    elif mode == "merge":

        if not file_name.endswith(".pdf"):
            bot.reply_to(message, "❌ PDF yuboring")
            return

        if message.chat.id not in user_files:
            user_files[message.chat.id] = []

        user_files[message.chat.id].append(file_name)

        bot.reply_to(
            message,
            f"✅ PDF saqlandi: {len(user_files[message.chat.id])} ta"
        )

print("🔥 BOT ISHLADI")

bot.infinity_polling()