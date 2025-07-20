import time
import random
import re
import asyncio
from sheets_api import get_active_cases, update_case_status
from parser.case_parser import get_case_status
from aiogram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from config import BOT_TOKEN, ADMIN_CHAT_ID

bot = Bot(token=BOT_TOKEN)

async def notify_admin(case_number, client_name, new_status):
    text = (
        f"⚠️ Изменение статуса!\n"
        f"Кейс: <b>{case_number}</b>\n"
        f"Клиент: <b>{client_name}</b>\n"
        f"Новый статус: <b>{new_status}</b>"
    )
    await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")

def check_all_cases_sync():
    cases = get_active_cases()
    loop = asyncio.get_event_loop()
    for case in cases:
        case_number = case['Case_number']
        client_name = case['Client_name']
        old_status = case['Status']
        print(f"Проверяю кейс {case_number} ({client_name})...")
        new_status_full = get_case_status(case_number)
        match = re.search(r"<b>Latest Status:</b> (.+)", new_status_full)
        if match:
            new_status = match.group(1).strip()
        else:
            new_status = new_status_full
        if new_status != old_status:
            print(f"Статус изменился! Было: {old_status}, стало: {new_status}")
            update_case_status(case_number, new_status)
            loop.run_until_complete(notify_admin(case_number, client_name, new_status))
        else:
            print("Статус не изменился.")
        delay = random.randint(120, 180)
        print(f"Жду {delay} секунд до следующей проверки...")
        time.sleep(delay)

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Moscow")
    scheduler.add_job(check_all_cases_sync, 'cron', hour=18, minute=0)
    print("Планировщик запущен. Проверка будет выполняться каждый день в 18:00 МСК.")
    scheduler.start() 