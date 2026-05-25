import telebot
from telebot import types
from pdf2docx import Converter
from PIL import Image
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from docx2pdf import convert
import qrcode
import pikepdf
import os
import traceback

TOKEN = "8001701759:AAEEwaUqg52Z1US3tmJWqshlZE4QJKSNGB4"

bot = telebot.TeleBot(TOKEN)

user_images = {}
user_pdfs = {}
user_mode = {}

# =========================
# MENU
# =========================

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    btn1 = types.KeyboardButton("🖼 Rasm → PDF")
    btn2 = types.KeyboardButton("📄 Word → PDF")
    btn3 = types.KeyboardButton("📚 PDF Birlashtirish")
    btn4 = types.KeyboardButton("📑 PDF → Word")
    btn5 = types.KeyboardButton("🛡 Watermark")
    btn6 = types.KeyboardButton("🔳 QR Code")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)

    return markup

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔥 SUPER PDF BOT 🔥\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu()
    )

# =========================
# BUTTONS
# =========================

@bot.message_handler(func=lambda message: True)
def buttons(message):

    chat_id = message.chat.id

    # IMAGE PDF
    if message.text == "🖼 Rasm → PDF":

        user_mode[chat_id] = "image_to_pdf"

        markup = types.InlineKeyboardMarkup()

        btn = types.InlineKeyboardButton(
            "✅ PDF Tayyorlash",
            callback_data="make_pdf"
        )

        markup.add(btn)

        bot.send_message(
            chat_id,
            "🖼 Rasmlarni yuboring",
            reply_markup=markup
        )

    # WORD PDF
    elif message.text == "📄 Word → PDF":

        user_mode[chat_id] = "word_to_pdf"

        bot.send_message(
            chat_id,
            "📄 DOCX fayl yuboring"
        )

    # PDF MERGE
    elif message.text == "📚 PDF Birlashtirish":

        user_mode[chat_id] = "pdf_merge"

        markup = types.InlineKeyboardMarkup()

        btn = types.InlineKeyboardButton(
            "✅ PDF Birlashtirish",
            callback_data="merge_pdf"
        )

        markup.add(btn)

        bot.send_message(
            chat_id,
            "📚 PDF fayllarni yuboring",
            reply_markup=markup
        )

    # PDF WORD
    elif message.text == "📑 PDF → Word":

        user_mode[chat_id] = "pdf_to_word"

        bot.send_message(
            chat_id,
            "📑 PDF yuboring"
        )

    # WATERMARK
    elif message.text == "🛡 Watermark":

        user_mode[chat_id] = "watermark"

        bot.send_message(
            chat_id,
            "🛡 PDF yuboring"
        )

    # QR
    elif message.text == "🔳 QR Code":

        user_mode[chat_id] = "qr"

        bot.send_message(
            chat_id,
            "✍️ QR uchun text yuboring"
        )

    # QR CREATE
    elif user_mode.get(chat_id) == "qr":

        bot.send_message(
            chat_id,
            "⏳ QR tayyorlanmoqda..."
        )

        qr = qrcode.make(message.text)

        qr_name = f"{chat_id}_qr.png"

        qr.save(qr_name)

        with open(qr_name, "rb") as qr_img:

            bot.send_photo(
                chat_id,
                qr_img
            )

        os.remove(qr_name)

# =========================
# IMAGE SAVE
# =========================

@bot.message_handler(content_types=['photo'])
def save_image(message):

    try:

        chat_id = message.chat.id

        if user_mode.get(chat_id) != "image_to_pdf":

            return

        if chat_id not in user_images:
            user_images[chat_id] = []

        file_info = bot.get_file(
            message.photo[-1].file_id
        )

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        image_name = f"{chat_id}_{len(user_images[chat_id])}.jpg"

        with open(image_name, 'wb') as f:
            f.write(downloaded_file)

        user_images[chat_id].append(image_name)

        bot.send_message(
            chat_id,
            f"✅ Rasm saqlandi: {len(user_images[chat_id])} ta"
        )

    except Exception as e:

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

# =========================
# DOCUMENTS
# =========================

@bot.message_handler(content_types=['document'])
def handle_docs(message):

    try:

        chat_id = message.chat.id

        mode = user_mode.get(chat_id)

        file_info = bot.get_file(
            message.document.file_id
        )

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        file_name = message.document.file_name

        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        # ====================
        # WORD → PDF
        # ====================

        if (
            file_name.endswith(".docx")
            and mode == "word_to_pdf"
        ):

            bot.send_message(
                chat_id,
                "⏳ Word PDF qilinmoqda..."
            )

            pdf_name = file_name.replace(
                ".docx",
                ".pdf"
            )

            convert(file_name, pdf_name)

            with open(pdf_name, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            os.remove(file_name)
            os.remove(pdf_name)

        # ====================
        # PDF → WORD
        # ====================

        elif (
            file_name.endswith(".pdf")
            and mode == "pdf_to_word"
        ):

            bot.send_message(
                chat_id,
                "⏳ PDF Word qilinmoqda..."
            )

            docx_name = file_name.replace(
                ".pdf",
                ".docx"
            )

            cv = Converter(file_name)

            cv.convert(docx_name)

            cv.close()

            with open(docx_name, "rb") as docx:

                bot.send_document(
                    chat_id,
                    docx
                )

            os.remove(file_name)
            os.remove(docx_name)

        # ====================
        # PDF MERGE
        # ====================

        elif (
            file_name.endswith(".pdf")
            and mode == "pdf_merge"
        ):

            if chat_id not in user_pdfs:
                user_pdfs[chat_id] = []

            user_pdfs[chat_id].append(file_name)

            bot.send_message(
                chat_id,
                f"✅ PDF saqlandi: {len(user_pdfs[chat_id])} ta"
            )

        # ====================
        # WATERMARK
        # ====================

        elif (
            file_name.endswith(".pdf")
            and mode == "watermark"
        ):

            bot.send_message(
                chat_id,
                "⏳ Watermark qo‘shilmoqda..."
            )

            output_pdf = f"{chat_id}_watermark.pdf"

            watermark_file = "watermark.pdf"

            c = canvas.Canvas(watermark_file)

            c.setFont("Helvetica", 40)

            c.setFillGray(0.5, 0.5)

            c.drawString(
                120,
                400,
                "TATU PDF BOT"
            )

            c.save()

            watermark = PdfReader(watermark_file)

            reader = PdfReader(file_name)

            writer = PdfWriter()

            for page in reader.pages:

                page.merge_page(
                    watermark.pages[0]
                )

                writer.add_page(page)

            with open(output_pdf, "wb") as f:

                writer.write(f)

            with open(output_pdf, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            os.remove(file_name)
            os.remove(output_pdf)
            os.remove(watermark_file)

    except Exception as e:

        print(traceback.format_exc())

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

# =========================
# IMAGE PDF BUTTON
# =========================

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    chat_id = call.message.chat.id

    # ====================
    # MAKE PDF
    # ====================

    if call.data == "make_pdf":

        try:

            if (
                chat_id not in user_images
                or len(user_images[chat_id]) == 0
            ):

                bot.answer_callback_query(
                    call.id,
                    "❌ Rasm yo‘q"
                )

                return

            bot.send_message(
                chat_id,
                "⏳ PDF tayyorlanmoqda..."
            )

            image_list = []

            for img in user_images[chat_id]:

                image = Image.open(img).convert('RGB')

                image_list.append(image)

            pdf_name = f"{chat_id}_images.pdf"

            image_list[0].save(
                pdf_name,
                save_all=True,
                append_images=image_list[1:]
            )

            with open(pdf_name, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            for img in user_images[chat_id]:

                os.remove(img)

            os.remove(pdf_name)

            user_images[chat_id] = []

        except Exception as e:

            bot.send_message(
                chat_id,
                f"❌ Xatolik:\n{str(e)}"
            )

    # ====================
    # MERGE PDF
    # ====================

    elif call.data == "merge_pdf":

        try:

            if (
                chat_id not in user_pdfs
                or len(user_pdfs[chat_id]) == 0
            ):

                bot.answer_callback_query(
                    call.id,
                    "❌ PDF yo‘q"
                )

                return

            bot.send_message(
                chat_id,
                "⏳ PDF birlashtirilmoqda..."
            )

            merger = pikepdf.Pdf.new()

            for pdf_file in user_pdfs[chat_id]:

                src = pikepdf.open(pdf_file)

                merger.pages.extend(src.pages)

            output_pdf = f"{chat_id}_merged.pdf"

            merger.save(output_pdf)

            merger.close()

            with open(output_pdf, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            for pdf_file in user_pdfs[chat_id]:

                os.remove(pdf_file)

            os.remove(output_pdf)

            user_pdfs[chat_id] = []

        except Exception as e:

            bot.send_message(
                chat_id,
                f"❌ Xatolik:\n{str(e)}"
            )

print("🔥 SUPER PDF BOT ISHLADI")

bot.infinity_polling()