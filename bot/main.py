import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN, ADMIN_CHAT_IDS
from bot.handlers import register_handlers
from sheets_api import get_active_cases, update_case_status
from parser.case_parser import get_case_status
import re
import random
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

updated_cases = []
scheduler = None  # глобально, чтобы не пересоздавался

async def update_all_cases():
    global updated_cases
    updated_cases = []
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
        updated_cases.append({
            'Case_number': case_number,
            'Client_name': client_name,
            'Old_status': old_status,
            'New_status': new_status
        })
        if idx < len(cases):
            delay = random.randint(60, 120)
            await asyncio.sleep(delay)

async def send_summary(bot):
    if not updated_cases:
        await update_all_cases()
    msk_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
    text = f'<b>Обновление статусов кейсов на {msk_time} МСК:</b>\n\n'
    for case in updated_cases:
        changed = " (изменился!)" if case['Old_status'] != case['New_status'] else ""
        text += (f"<b>{case['Case_number']}</b> — {case['Client_name']}\n"
                f"Статус: <b>{case['New_status']}</b>{changed}\n\n")
    for admin_id in ADMIN_CHAT_IDS:
        await bot.send_message(admin_id, text, parse_mode="HTML")

async def on_startup(dp):
    global scheduler
    bot = dp.bot
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(lambda: asyncio.create_task(update_all_cases()), 'cron', hour=17, minute=30)
    scheduler.add_job(lambda: asyncio.create_task(send_summary(bot)), 'cron', hour=18, minute=0)
    scheduler.start()
    print("Планировщик запущен. Обновление статусов в 17:30, рассылка отчёта в 18:00 МСК.")

def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

if __name__ == "__main__":
    main() 