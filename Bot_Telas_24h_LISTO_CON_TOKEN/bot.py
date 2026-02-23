
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

DATA_FILE = "stock.json"

def cargar_stock():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_stock():
    with open(DATA_FILE, "w") as f:
        json.dump(stock, f, indent=4)

stock = cargar_stock()

def menu_principal():
    keyboard = [
        [InlineKeyboardButton("Ingresar", callback_data="ingresar")],
        [InlineKeyboardButton("Consultar", callback_data="consulta")],
        [InlineKeyboardButton("Venta", callback_data="vendido")],
        [InlineKeyboardButton("Ver Stock", callback_data="ver_stock")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def tela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Elegí una opción:", reply_markup=menu_principal())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tela(update, context)

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ingresar":
        await query.message.reply_text("/ingreso")
    elif query.data == "consulta":
        await query.message.reply_text("/consulta")
    elif query.data == "vendido":
        await query.message.reply_text("/vendido")
    elif query.data == "ver_stock":
        await mostrar_stock(query.message)

async def procesar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.lower().strip()

    if txt.startswith("/ingreso"):
        try:
            _, tela, color, cantidad = txt.split()
            cantidad = int(cantidad)
            clave = f"{tela}_{color}"
            stock[clave] = stock.get(clave, 0) + cantidad
            guardar_stock()
            await update.message.reply_text(f"✅ Ingresado: +{cantidad} de {clave} (Total: {stock[clave]})")
        except:
            await update.message.reply_text("Formato: /ingreso tela color cantidad")

    elif txt.startswith("/consulta"):
        try:
            _, tela, color = txt.split()
            clave = f"{tela}_{color}"
            await update.message.reply_text(f"{tela} {color}: {stock.get(clave, 0)}")
        except:
            await update.message.reply_text("Formato: /consulta tela color")

    elif txt.startswith("/vendido"):
        try:
            _, tela, color, cantidad = txt.split()
            cantidad = int(cantidad)
            clave = f"{tela}_{color}"
            stock[clave] = max(0, stock.get(clave, 0) - cantidad)
            guardar_stock()
            await update.message.reply_text(f"🟡 Vendido: -{cantidad} de {clave} (Total: {stock[clave]})")
            if stock[clave] <= 3:
                await update.message.reply_text(f"⚠ ALERTA: {clave} está en {stock[clave]}")
        except:
            await update.message.reply_text("Formato: /vendido tela color cantidad")

    elif txt.startswith("/stock"):
        await mostrar_stock(update.message)

async def mostrar_stock(message):
    if not stock:
        await message.reply_text("No hay stock aún.")
        return

    respuesta = ""
    ultimo = ""
    for item in sorted(stock):
        tela, color = item.split("_")
        cant = stock[item]
        if tela != ultimo:
            respuesta += f"\n📌 *{tela.upper()}*\n"
            ultimo = tela
        if cant <= 3:
            respuesta += f"   🔴 {color} — {cant}\n"
        else:
            respuesta += f"   {color} — {cant}\n"

    await message.reply_text(respuesta, parse_mode="Markdown")

TOKEN = "8734017613:AAFOySDQ4mXRN6z_ImYG2rUFy87OH5NrWKg"

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tela", tela))
    app.add_handler(CallbackQueryHandler(botones))
    app.add_handler(MessageHandler(filters.TEXT, procesar_texto))
    app.run_polling()

if __name__ == "__main__":
    main()
