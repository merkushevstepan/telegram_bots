import asyncio
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
import os
import json
from dotenv import load_dotenv
from aiogram.types import Message

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Токен не найден, проверьте файл .env")

NOTES_FILE = Path(__file__).with_name("notes.json")
dp = Dispatcher()


def load_content():
    if not NOTES_FILE.exists():
        return {}
    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def send_content(content):
    NOTES_FILE.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def numerated_list(user_id):
    content = load_content()
    list_of_tasks = content.get(user_id, None)
    if not list_of_tasks:
        return []
    num_list = []
    for number, name in enumerate(list_of_tasks, start=1):
        num_list.append(f"{number}. {name}")
    return num_list


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Приветствую тебя, {message.from_user.first_name}. Я - бот для записи задач.\nМои команды: /add - добавить задачу, /done - отметить задачу выполненной, /edit - изменить задачу")


@dp.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(f"Напиши текст: /add купить хлеб")
        return
    content = load_content()
    user_id = str(message.from_user.id)
    content.setdefault(user_id, []).append(command.args)
    send_content(content)
    await message.answer(f"Задача {command.args} добавлена.\nКол-во задач: {len(content[user_id])}")


@dp.message(Command("check"))
async def cmd_check(message: Message):
    user_id = str(message.from_user.id)
    num_list = numerated_list(user_id)
    if not num_list:
        await message.answer("У вас нет задач. Добавьте их командой /add")
        return
    await message.answer("-----ВАШИ ЗАДАЧИ-----\n\n" + "\n".join(num_list))


@dp.message(Command("done"))
async def cmd_done(message: Message, command: CommandObject):
    user_id = str(message.from_user.id)
    content = load_content()
    if not command.args:
        await message.answer("Напишите номер задачи, которую хотите удалить, например, /done 1")
        return
    num_list = numerated_list(user_id)
    if not num_list:
        await message.answer("У вас нет задач. Добавьте их командой /add")
        return
    if not command.args.isdecimal():
        await message.answer("Напишите номер задачи, которую хотите удалить, например /done 1")
        return
    com_args = int(command.args)
    if com_args > len(content[user_id]) or com_args <= 0:
        await message.answer("В списке нет задачи с таким номером")
        return

    removed = content[user_id].pop(com_args - 1)
    send_content(content)
    await message.answer(f"Задача '{removed}' удалена. Посмотрите актуальный список задач командой /check")


@dp.message(Command("edit"))  # Обработчик для изменения задачи в списке
async def cmd_edit(message: Message, command: CommandObject):
    user_id = str(message.from_user.id)  # Берем айди пользователя
    content = load_content()  # Загружаем всю базу
    new_content = []  # Переменная для обновления списка задач, когда пользователь введет каккую задачу он хочет изменить
    num_list = numerated_list(user_id)
    if not num_list:
        await message.answer("У вас нет задач. Добавьте их командой /add")
        return
    if not command.args:
        await message.answer("Напишите номер задачи, которую хотите изменить, например, /edit 1 (новая задача)")
        return  # Если пользователь ничего не ввел после /edit
    split_args = command.args.split(maxsplit=1)  # Разделяем ввод пользователя на ["2", "отправить отчет"]
    if len(split_args) <= 1:
        await message.answer("Введите новую задачу, например /edit 2 Отправить отчет")
        return
    if not split_args[0].isdecimal():  # Проверяем что пользователь ввел число, проверяем первый элемент split_args, например "2"
        await message.answer("Напишите номер задачи, которую хотите изменить, например /edit 1 (новая задача)")
        return
    com_args = int(split_args[0])  # Превращаем первую часть сплита в число
    if com_args > len(content[user_id]) or com_args <= 0:
        await message.answer("В списке нет задачи с таким номером")
        return
    for num, task in enumerate(content[user_id], start=1):
        if num == com_args:
            new_task = split_args[1]
            new_content.append(new_task)
        else:
            new_content.append(task)
    content[user_id] = new_content
    send_content(content)
    await message.answer(f"Задача номер {split_args[0]} изменена. Новая задача: {new_task}")


async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
