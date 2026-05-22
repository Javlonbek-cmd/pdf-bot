import telebot
from telebot import types
from docx2pdf import convert
from pdf2docx import Converter
from PIL import Image
import comtypes.client
import pikepdf
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import qrcode
import os
import traceback

TOKEN = "8001701759:AAEEwaUqg52Z1US3tmJWqshlZE4QJKSNGB4"

# BOT
bot = telebot.TeleBot(TOKEN)

# DATA
user_images = {}
user_pdfs = {}
user_mode = {}

# PDF COMPRESS
def compress_pdf(input_pdf, output_pdf):

    pdf = pikepdf.open(input_pdf)

    pdf.save(
        output_pdf,
        compress_streams=True
    )

    pdf.close()

# WATERMARK
def add_watermark(input_pdf, output_pdf, text):

    watermark_file = "watermark.pdf"

    c = canvas.Canvas(watermark_file)

    c.setFont("Helvetica", 40)

    c.setFillGray(0.5, 0.5)

    c.drawString(150, 400, text)

    c.save()

    watermark = PdfReader(watermark_file)

    reader_pdf = PdfReader(input_pdf)

    writer = PdfWriter()

    for page in reader_pdf.pages:

        page.merge_page(watermark.pages[0])

        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    os.remove(watermark_file)

# MENU
def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("📄 Word → PDF")
    btn2 = types.KeyboardButton("🖼 Rasm → PDF")
    btn3 = types.KeyboardButton("📚 PDF Merge")
    btn4 = types.KeyboardButton("📑 PDF → Word")
    btn5 = types.KeyboardButton("🛡 Watermark")
    btn6 = types.KeyboardButton("🔳 QR Code")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)

    return markup

# START
@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "🔥 ULTIMATE PDF BOT 🔥\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu()
    )

# BUTTONS
@bot.message_handler(content_types=['text'])
def buttons(message):

    chat_id = message.chat.id

    # WORD → PDF
    if message.text == "📄 Word → PDF":

        user_mode[chat_id] = "word_to_pdf"

        bot.send_message(
            chat_id,
            "📄 DOCX yoki PPT yuboring"
        )

    # IMAGE → PDF
    elif message.text == "🖼 Rasm → PDF":

        user_mode[chat_id] = "image_to_pdf"

        bot.send_message(
            chat_id,
            "🖼 Bir yoki bir nechta rasm yuboring\n"
            "Keyin /makepdf bosing"
        )

    # PDF MERGE
    elif message.text == "📚 PDF Merge":

        user_mode[chat_id] = "pdf_merge"

        bot.send_message(
            chat_id,
            "📚 PDF fayllarni yuboring\n"
            "Keyin /mergepdf bosing"
        )

    # PDF → WORD
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

    # QR CODE
    elif message.text == "🔳 QR Code":

        user_mode[chat_id] = "qr"

        bot.send_message(
            chat_id,
            "✍️ QR code uchun text yuboring"
        )

    # QR CREATE
    elif user_mode.get(chat_id) == "qr":

        bot.send_message(
            chat_id,
            "⏳ QR code yaratilmoqda..."
        )

        qr = qrcode.make(message.text)

        qr_name = "qr.png"

        qr.save(qr_name)

        with open(qr_name, "rb") as qr_img:

            bot.send_photo(
                chat_id,
                qr_img
            )

        os.remove(qr_name)

    else:

        bot.send_message(
            chat_id,
            "❌ Menudan foydalaning"
        )

# DOCUMENTS
@bot.message_handler(content_types=['document'])
def handle_docs(message):

    try:

        chat_id = message.chat.id

        mode = user_mode.get(chat_id)

        # SIZE LIMIT
        if message.document.file_size > 200 * 1024 * 1024:

            bot.send_message(
                chat_id,
                "❌ Fayl juda katta"
            )

            return

        file_info = bot.get_file(
            message.document.file_id
        )

        downloaded_file = bot.download_file(
            file_info.file_path
        )

        file_name = message.document.file_name

        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        # PDF → WORD
        if file_name.endswith(".pdf") and mode == "pdf_to_word":

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

        # WATERMARK
        elif file_name.endswith(".pdf") and mode == "watermark":

            bot.send_message(
                chat_id,
                "⏳ Watermark qo‘shilmoqda..."
            )

            output_pdf = "watermarked.pdf"

            add_watermark(
                file_name,
                output_pdf,
                "TATU PDF BOT"
            )

            with open(output_pdf, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            os.remove(file_name)
            os.remove(output_pdf)

        # PDF MERGE
        elif file_name.endswith(".pdf") and mode == "pdf_merge":

            if chat_id not in user_pdfs:
                user_pdfs[chat_id] = []

            user_pdfs[chat_id].append(file_name)

            bot.send_message(
                chat_id,
                f"✅ PDF saqlandi: {len(user_pdfs[chat_id])} ta\n\n"
                "/mergepdf bosing"
            )

        # DOCX → PDF
        elif file_name.endswith(".docx") and mode == "word_to_pdf":

            bot.send_message(
                chat_id,
                "⏳ DOCX PDF qilinmoqda..."
            )

            pdf_name = file_name.replace(
                ".docx",
                ".pdf"
            )

            convert(file_name, pdf_name)

            compressed_pdf = "compressed_" + pdf_name

            compress_pdf(
                pdf_name,
                compressed_pdf
            )

            with open(compressed_pdf, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            os.remove(file_name)
            os.remove(pdf_name)
            os.remove(compressed_pdf)

        # PPT/PPTX → PDF
        elif (
            file_name.endswith(".pptx")
            or file_name.endswith(".ppt")
        ) and mode == "word_to_pdf":

            bot.send_message(
                chat_id,
                "⏳ PPT PDF qilinmoqda..."
            )

            pdf_name = file_name.rsplit(".", 1)[0] + ".pdf"

            powerpoint = comtypes.client.CreateObject(
                "Powerpoint.Application"
            )

            powerpoint.Visible = 1

            presentation = powerpoint.Presentations.Open(
                os.path.abspath(file_name)
            )

            presentation.SaveAs(
                os.path.abspath(pdf_name),
                32
            )

            presentation.Close()

            powerpoint.Quit()

            compressed_pdf = "compressed_" + pdf_name

            compress_pdf(
                pdf_name,
                compressed_pdf
            )

            with open(compressed_pdf, "rb") as pdf:

                bot.send_document(
                    chat_id,
                    pdf
                )

            os.remove(file_name)
            os.remove(pdf_name)
            os.remove(compressed_pdf)

        else:

            bot.send_message(
                chat_id,
                "❌ Noto‘g‘ri format yoki menu tanlanmagan"
            )

            os.remove(file_name)

    except Exception as e:

        print(traceback.format_exc())

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

# SAVE IMAGES
@bot.message_handler(content_types=['photo'])
def save_image(message):

    try:

        chat_id = message.chat.id

        mode = user_mode.get(chat_id)

        if mode != "image_to_pdf":

            bot.send_message(
                chat_id,
                "🖼 Avval 'Rasm → PDF' ni bosing"
            )

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
            f"✅ Rasm saqlandi: {len(user_images[chat_id])} ta\n\n"
            "/makepdf bosing"
        )

    except Exception as e:

        print(traceback.format_exc())

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

# IMAGE → PDF
@bot.message_handler(commands=['makepdf'])
def make_pdf(message):

    try:

        chat_id = message.chat.id

        if (
            chat_id not in user_images
            or len(user_images[chat_id]) == 0
        ):

            bot.send_message(
                chat_id,
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

        print(traceback.format_exc())

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

# PDF MERGE
@bot.message_handler(commands=['mergepdf'])
def merge_pdf(message):

    try:

        chat_id = message.chat.id

        if (
            chat_id not in user_pdfs
            or len(user_pdfs[chat_id]) == 0
        ):

            bot.send_message(
                chat_id,
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

        print(traceback.format_exc())

        bot.send_message(
            chat_id,
            f"❌ Xatolik:\n{str(e)}"
        )

print("🔥 ULTIMATE PDF BOT ISHLADI")

bot.infinity_polling()