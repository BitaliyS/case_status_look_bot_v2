from aiogram import types, Dispatcher
from sheets_api import add_case_or_notify, get_active_cases, update_case_status
from parser.case_parser import get_case_status
from config import ADMIN_CHAT_IDS
import re
import traceback
import asyncio
import random

async def start_cmd(message: types.Message):
    try:
        if message.from_user.id not in ADMIN_CHAT_IDS:
            await message.reply("Нет доступа")
            return
        help_text = (
            "Привет! Я бот для отслеживания статусов USCIS кейсов.\n\n"
            "Доступные команды:\n"
            "/add <номер_кейса> <фамилия> — добавить новый кейс на отслеживание (только для администратора)\n"
            "/list — показать список всех активных кейсов и их статусов\n"
            "/update — вручную обновить статусы всех кейсов (только для администратора)\n"
            "/start — показать это сообщение\n\n"
            "Просто отправьте номер кейса (начинается с IOE), чтобы получить его текущий статус.\n"
        )
        await message.reply(help_text)
    except Exception as e:
        print("Ошибка в start_cmd:", e)
        traceback.print_exc()

async def add_case_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_CHAT_IDS:
        await message.reply("У вас нет прав для этой команды.")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("Используйте формат: /add <номер_кейса> <фамилия>")
            return
        case_number = parts[1]
        client_name = " ".join(parts[2:])
        await message.reply("⏳ Получаю статус с сайта...")
        status_full = get_case_status(case_number)
        match = re.search(r"<b>Latest Status:</b> (.+)", status_full)
        if match:
            status_text = match.group(1).strip()
        else:
            status_text = status_full
        result, exist_name = add_case_or_notify(case_number, client_name, status_text)
        if result:
            await message.reply(f"Кейс {case_number} ({client_name}) добавлен на отслеживание!\nСтатус: {status_text}")
        else:
            await message.reply(f"Кейс с таким номером уже есть в базе для фамилии: {exist_name}")
    except Exception as e:
        print("Ошибка в add_case_cmd:", e)
        traceback.print_exc()
        await message.reply(f"Ошибка при добавлении кейса: {e}")

async def list_cases_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_CHAT_IDS:
        await message.reply("У вас нет прав для этой команды.")
        return
    try:
        cases = get_active_cases()
        if not cases:
            await message.reply("Нет активных кейсов для отслеживания.")
            return
        text = "<b>Активные кейсы:</b>\n"
        for case in cases:
            text += f"\n<b>{case['Case_number']}</b> — {case['Client_name']}\nСтатус: {case['Status']}\n"
        await message.reply(text, parse_mode="HTML")
    except Exception as e:
        print("Ошибка в list_cases_cmd:", e)
        traceback.print_exc()
        await message.reply(f"Ошибка при получении списка кейсов: {e}")

async def update_statuses_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_CHAT_IDS:
        await message.reply("У вас нет прав для этой команды.")
        return
    await message.reply("⏳ Начинаю обновление статусов всех кейсов. Это может занять до 30 минут...")
    cases = get_active_cases()
    for idx, case in enumerate(cases, 1):
        case_number = case['Case_number']
        client_name = case['Client_name']
        old_status = case['Status']
        status_full = get_case_status(case_number)
        match = re.search(r"<b>Latest Status:</b> (.+)", status_full)
        if match:
            new_status = match.group(1).strip()
        else:
            new_status = status_full
        update_case_status(case_number, new_status)
        await message.reply(f"Кейс {case_number}, {client_name}. Новый статус: {new_status}")
        # Рандомная задержка 60-120 секунд
        if idx < len(cases):
            delay = random.randint(60, 120)
            await asyncio.sleep(delay)
    await message.reply("✅ Обновление всех статусов завершено!")

async def case_status_handler(message: types.Message):
    try:
        if message.from_user.id not in ADMIN_CHAT_IDS:
            await message.reply("У вас нет прав для этой команды.")
            return
        case_number = message.text.strip()
        await message.reply("⏳ Проверяю статус, подождите...")
        status = get_case_status(case_number)
        await message.reply(status, parse_mode=types.ParseMode.HTML)
    except Exception as e:
        print("Ошибка в case_status_handler:", e)
        traceback.print_exc()
        await message.reply(f"Ошибка при получении статуса: {e}")

async def fallback(message: types.Message):
    try:
        if message.from_user.id not in ADMIN_CHAT_IDS:
            await message.reply("У вас нет прав для этой команды.")
            return
        await message.reply("Пожалуйста, отправьте номер кейса, начинающийся с IOE...")
    except Exception as e:
        print("Ошибка в fallback:", e)
        traceback.print_exc()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(add_case_cmd, commands=['add'])
    dp.register_message_handler(list_cases_cmd, commands=['list'])
    dp.register_message_handler(update_statuses_cmd, commands=['update'])
    dp.register_message_handler(case_status_handler, lambda m: m.text and m.text.strip().startswith("IOE"))
    dp.register_message_handler(fallback) 