import os
import json

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
admin_id = int(os.getenv("ADMIN_ID"))

# Отправляем уведомление администратору

async def notify_admin(context, message):

    await context.bot.send_message(chat_id=admin_id,

        text=message,

    )

def save_order(order):
    ORDERS.append(order)

    with open("orders.json", "w", encoding="utf-8") as file:
        json.dump(ORDERS, file, ensure_ascii=False, indent=2)

# Наше меню еды
# Загружаем меню из файла
with open("menu.json", "r", encoding="utf-8") as file:
    FOOD_MENU = json.load(file)

    # Загружаем историю заказов
    with open("orders.json", "r", encoding="utf-8") as file:
        ORDERS = json.load(file)

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["☕️ Кофе с вкусняшками"],
        ["🍽️ Принести покушать"],
        ["📝 Иной запрос"],
    ]
    if update.effective_user.id == admin_id:
        keyboard.append(["⚙️ Управление"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )

    await update.message.reply_text(
        "☕️ Добро пожаловать в личную службу заботы!\n\n"
        "Ваш секретарь уже готов принять заказ 💗\n\n"
        "Что желаете?",
        reply_markup=reply_markup,
    )


# Показываем меню еды
async def show_food_menu(update: Update):
    keyboard = []

    for food in FOOD_MENU:
        keyboard.append([food])

    keyboard.append(["⬅️ Назад"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )

    await update.message.reply_text(
        "🍽️ Что принести?\n\n"
        "Сегодня есть:",
        reply_markup=reply_markup,
    )


# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text

    # Кофе
    if text == "☕️ Кофе с вкусняшками":
        await update.message.reply_text(
            "☕️ Приняла заказ!\n\n"
            "Скоро буду с кофе и чем-нибудь вкусненьким ❤️"
        )

        save_order({
            "type": "coffee",
            "item": "☕️ Кофе с вкусняшками",
        })

        await notify_admin(
            context,
            "🔔 Новый заказ!\n\n"
            "☕️ Кофе с вкусняшками"
        )

    # Еда
    elif text == "🍽️ Принести покушать":
        await show_food_menu(update)

    # Удаление блюда
    elif context.user_data.get("deleting_food") and text in FOOD_MENU:
        context.user_data["deleting_food"] = False

        FOOD_MENU.remove(text)

        with open("menu.json", "w", encoding="utf-8") as file:
            json.dump(FOOD_MENU, file, ensure_ascii=False, indent=2)

        await update.message.reply_text(
            f"🗑️ Блюдо «{text}» удалено из меню!"
        )

    # Выбрано блюдо
    elif text in FOOD_MENU:
        await update.message.reply_text(
            "✅ Приняла заказ!\n"
            "В течение 5 минут будет готово."
        )

        save_order({
            "type": "food",
            "item": text,
        })

        await notify_admin(
            context,
            f"🔔 Новый заказ!\n\n"
            f"🍽️ {text}"
        )

    # Управление
    elif text == "⚙️ Управление":
        if update.effective_user.id == admin_id:
            keyboard = [
                ["🍽️ Управление меню"],
                ["📋 Заказы"],
                ["🟢 Свободна / 🔴 Не беспокоить"],
                ["⬅️ Назад"],
            ]

            reply_markup = ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                is_persistent=True,
            )

            await update.message.reply_text(
                "⚙️ Управление\n\n"
                "Выберите действие:",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                "⛔️ Доступ запрещён."
            )

    # Управление меню
    elif text == "🍽️ Управление меню":
        if update.effective_user.id == admin_id:
            keyboard = [
                ["➕ Добавить блюдо"],
                ["🗑️ Удалить блюдо"],
                ["📋 Посмотреть меню"],
                ["⬅️ Назад"],
            ]

            reply_markup = ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                is_persistent=True,
            )

            await update.message.reply_text(
                "🍽️ Управление меню\n\n"
                "Выберите действие:",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                "⛔️ Доступ запрещён."
            )

    # Добавить блюдо
    elif text == "➕ Добавить блюдо":
        if update.effective_user.id == admin_id:
            context.user_data["adding_food"] = True

            await update.message.reply_text(
                "🍽️ Напишите название нового блюда:"
            )
        else:
            await update.message.reply_text(
                "⛔️ Доступ запрещён."
            )

    # Удалить блюдо
    elif text == "🗑️ Удалить блюдо":
        if update.effective_user.id == admin_id:
            context.user_data["deleting_food"] = True

            keyboard = []

            for food in FOOD_MENU:
                keyboard.append([food])

            keyboard.append(["⬅️ Назад"])

            reply_markup = ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                is_persistent=True,
            )

            await update.message.reply_text(
                "🗑️ Какое блюдо удалить?",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                "⛔️ Доступ запрещён."
            )

    # Посмотреть меню
    elif text == "📋 Посмотреть меню":
        if update.effective_user.id == admin_id:
            menu_text = "\n".join(FOOD_MENU)

            await update.message.reply_text(
                "🍽️ Текущее меню:\n\n"
                + menu_text
            )
        else:
            await update.message.reply_text(
                "⛔️ Доступ запрещён."
            )

    # Иной запрос
    elif text == "📝 Иной запрос":
        context.user_data["awaiting_custom_request"] = True

        await update.message.reply_text(
            "✍️ Напишите ваш запрос сообщением:"
        )

    # Назад
    elif text == "⬅️ Назад":
        await start(update, context)

    # Неизвестный текст / пользователь пишет свой запрос
    else:
        if context.user_data.get("adding_food"):
            context.user_data["adding_food"] = False

            FOOD_MENU.append(text)

            with open("menu.json", "w", encoding="utf-8") as file:
                json.dump(FOOD_MENU, file, ensure_ascii=False, indent=2)

            await update.message.reply_text(
                f"✅ Блюдо «{text}» добавлено в меню!"
            )

            return

        if context.user_data.get("awaiting_custom_request"):
            context.user_data["awaiting_custom_request"] = False

            save_order({
                "type": "custom",
                "item": text,
            })

            await update.message.reply_text(
                "✅ Приняла ваш запрос"
            )

            await notify_admin(
                context,
                f"🔔 Новый запрос!\n\n"
                f"📝 {text}"
            )

        else:
            await update.message.reply_text(
                "Я пока не знаю, что делать с этим запросом 😅\n\n"
                "Пожалуйста, выберите одну из кнопок ниже."
            )
def main():
    if not bot_token:
        raise ValueError("Не найден BOT_TOKEN в файле .env")

    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()