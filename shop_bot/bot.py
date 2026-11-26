import asyncio
from json import JSONDecodeError

from dotenv import load_dotenv
import os
import json
from pathlib import Path
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message
)
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher, F

ACCOUNTS = Path(__file__).with_name("accounts.json")

dp = Dispatcher()
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Токен бота не найден. Проверьте файл .env")

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📦 Наличие аккаунтов"), KeyboardButton(text="ℹ️О магазине")],
              [KeyboardButton(text="🌟 Оставить отзыв"),
               KeyboardButton(text="📞 Связаться с поддержкой")]],
    resize_keyboard=True
)

inline_items = {"tik_tok": "Тик ток", "telegram_channels": "Телеграм"}


def load_content():
    """
    :return: Возвращает данные из файла, где хранятся данные товаров
    """
    if not ACCOUNTS.exists():
        return {}
    try:
        return json.loads(ACCOUNTS.read_text(encoding="utf-8"))
    except JSONDecodeError:
        print("Ошибка: неверный формат в accounts.json!")
        return {}


def inline_kb():
    """
    :return:Красиво обвертанные inline кнопки с товарами
    """
    buttons = []
    for key, value in inline_items.items():
        buttons.append([InlineKeyboardButton(text=value, callback_data=f"items:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def check_item(data, key):
    """
    :arg: На вход дается key - ключ из словаря со значениями товаров {"tik_tok": "Тик ток", "telegram_channels": "Телеграм"}
    data - содержимое файла с товарами, взятое из load_content()
    :return: кол-во этого товара в магазине, если его нет - возвращает 0
    """
    value = data.get(key, None)
    if type(value) != int or value <= 0:
        return "0"
    return str(value)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    username = message.from_user.first_name
    await message.answer(
        f"Приветствую тебя, {username}. Ты попал в JamesMollShop - магазин цифровых товаров.\nДалее ориентируйся по кнопкам ниже.",
        reply_markup=main_kb)


@dp.message(F.text == "ℹ️О магазине")
async def cmd_about(message: Message):
    await message.answer("JamesMollShop - магазин цифровых товаров, основанный в 2025 году.\n"
                         "У нас вы можете купить качественные телеграм каналы для старта, а так же "
                         "прогретые тик ток аккаунты для старта в привлечении трафика.")


@dp.message(F.text == "🌟 Оставить отзыв")
async def cmd_review(message: Message):
    await message.answer("Оставить отзыв о нашем магазине вы можете в чате t.me/JamesMollShop_Reviews")


@dp.message(F.text == "📞 Связаться с поддержкой")
async def cmd_supports(message: Message):
    await message.answer("Аккаунт поддержки: @JamesMollShop_Support\nГрафик работы поддержки с 08:00 до 21:00 по МСК\n"
                         "Просьба не спамить, иначе вы будете в конце приоритета ответа")


@dp.message(F.text == "📦 Наличие аккаунтов")
async def cmd_items(message: Message):
    await message.answer("Выберите товар ниже", reply_markup=inline_kb())


@dp.callback_query(F.data.startswith("items:"))
async def on_items(callback: CallbackQuery):
    await callback.answer()
    data = load_content()
    key = callback.data.split(":")[1]
    result = inline_items.get(key, None)
    if result:
        answer = check_item(data, key)
        if answer == "0":
            await callback.message.answer("Товара нет в наличии")

            return
        await callback.message.answer(f"Товар: {result}\nНаличие:{answer}")

    else:
        await callback.message.answer("Не нашли такой товар")


async def main():
    bot = Bot(token=BOT_TOKEN)
    print("БОТ ЗАПУЩЕН")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
