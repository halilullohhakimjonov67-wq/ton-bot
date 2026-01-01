import requests
import matplotlib.pyplot as plt
import pandas as pd
import io
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

TOKEN = "8519416109:AAHIE1hAp6GqcvvS1bOidCQzmDjAzhnHTvA"

# ---------- REAL NARXLAR ----------
def get_prices():
    ton_url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=the-open-network&vs_currencies=usd"
    )
    ton_data = requests.get(ton_url, timeout=10).json()
    ton_usd = ton_data["the-open-network"]["usd"]

    usd_url = "https://open.er-api.com/v6/latest/USD"
    usd_data = requests.get(usd_url, timeout=10).json()
    usd_uzs = usd_data["rates"]["UZS"]

    return ton_usd, usd_uzs

# ---------- REAL TARIX (TRADING STYLE) ----------
def get_history():
    url = (
        "https://api.coingecko.com/api/v3/coins/the-open-network/market_chart"
        "?vs_currency=usd&days=7"
    )
    data = requests.get(url, timeout=10).json()
    prices = data.get("prices")

    if not prices:
        return None

    df = pd.DataFrame(prices, columns=["time", "price"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom!\n\n"
        "✍️ Shunchaki yozing:\n"
        "3 ton\n"
        "2.5\n"
        "1.75 ton\n\n"
        "📈 Bot avtomatik grafik + hisob chiqaradi"
    )

# ---------- BUYRUQSIZ XABAR (ASOSIY FUNKSIYA) ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.lower()

        match = re.search(r"(\d+(\.\d+)?)", text)
        if not match:
            return

        amount = float(match.group(1))

        ton_usd, usd_uzs = get_prices()
        df = get_history()

        current_uzs = ton_usd * usd_uzs
        total_uzs = amount * current_uzs

        # Grafik bo‘lsa chizamiz
        if df is not None:
            df["price_uzs"] = df["price"] * usd_uzs

            plt.figure(figsize=(10, 5))
            plt.plot(df["time"], df["price_uzs"], color="#00ff7f", linewidth=2)
            plt.fill_between(df["time"], df["price_uzs"], alpha=0.2)

            plt.title("TON / UZS — real trading grafik", fontsize=14)
            plt.xlabel("Vaqt")
            plt.ylabel("Narx (UZS)")
            plt.grid(alpha=0.3)

            last_price = df["price_uzs"].iloc[-1]
            plt.axhline(last_price, color="yellow", linestyle="--", alpha=0.6)

            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format="png", dpi=150)
            buf.seek(0)
            plt.close()

            caption = (
                f"💎 TON / UZS (real vaqt)\n\n"
                f"1 TON ≈ {current_uzs:,.0f} UZS\n"
                f"{amount} TON ≈ {total_uzs:,.0f} UZS\n"
                f"≈ ${amount * ton_usd:.2f}"
            )

            await update.message.reply_photo(photo=buf, caption=caption)

        else:
            await update.message.reply_text(
                f"{amount} TON ≈ {total_uzs:,.0f} UZS"
            )

    except Exception as e:
        await update.message.reply_text("❌ Xatolik yuz berdi.")
        print("XATO:", e)

# ---------- BOT ----------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.run_polling()