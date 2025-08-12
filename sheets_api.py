import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# Название файла с ключом сервисного аккаунта
SERVICE_ACCOUNT_FILE = 'case-look-b1a1e3beddf1.json'
# ID таблицы (из URL)
SPREADSHEET_ID = '1BsfR7weqOpDRLUjfdP9009tYUXmcAthcHfFFPAkMqF8'
# Имя листа (обычно 'Лист1' или 'Sheet1')
SHEET_NAME = 'Лист1'

# Подключение к Google Sheets
def get_sheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

sheet = None

# Проверка и добавление колонок Active и LastChecked, если их нет
def ensure_columns():
    sheet = get_sheet()
    headers = sheet.row_values(1)
    changed = False
    if 'Active' not in headers:
        sheet.update_cell(1, len(headers) + 1, 'Active')
        headers.append('Active')
        changed = True
    if 'LastChecked' not in headers:
        sheet.update_cell(1, len(headers) + 1, 'LastChecked')
        changed = True
    return headers if not changed else sheet.row_values(1)

def add_case(case_number, client_name, status):
    """Добавить новый кейс в таблицу с Active=Yes и текущим временем проверки"""
    sheet = get_sheet()
    headers = ensure_columns()
    row = [case_number, client_name, status]
    # Добавляем пустые значения для пропущенных колонок
    while len(row) < len(headers) - 2:
        row.append('')
    row.append('Yes')
    msk_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
    row.append(msk_time)
    sheet.append_row(row)

def get_all_cases():
    """Получить все кейсы из таблицы (список словарей)"""
    sheet = get_sheet()
    ensure_columns()
    records = sheet.get_all_records()
    return records

def update_case_status(case_number, new_status):
    """Обновить статус кейса по номеру"""
    sheet = get_sheet()
    headers = ensure_columns()
    cell = sheet.find(case_number)
    if cell:
        row = cell.row
        status_col = headers.index('Status') + 1
        sheet.update_cell(row, status_col, new_status)
        # Обновляем LastChecked
        last_checked_col = headers.index('LastChecked') + 1
        msk_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
        sheet.update_cell(row, last_checked_col, msk_time)
        # Архивация
        if new_status in ["Case Approved", "Case Was Denied"]:
            active_col = headers.index('Active') + 1
            sheet.update_cell(row, active_col, 'No')
        return True
    return False

def extract_digits(case_number):
    return ''.join(filter(str.isdigit, case_number))

def add_case_or_notify(case_number, client_name, status):
    sheet = get_sheet()
    headers = ensure_columns()
    records = sheet.get_all_records()
    new_case_digits = extract_digits(case_number)
    for row in records:
        row_digits = extract_digits(str(row.get('Case_number', '')))
        if row_digits == new_case_digits:
            # Если номер уже есть, возвращаем False и фамилию, к которой привязан
            return False, row.get('Client_name', '')
    # Если не найден — добавляем
    row = [case_number, client_name, status]
    while len(row) < len(headers) - 2:
        row.append('')
    row.append('Yes')
    msk_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
    row.append(msk_time)
    sheet.append_row(row)
    return True, None

def get_active_cases():
    sheet = get_sheet()
    ensure_columns()
    records = sheet.get_all_records()
    unique = {}
    for r in records:
        if str(r.get('Active', '')).strip().lower() == 'yes':
            digits = extract_digits(str(r.get('Case_number', '')))
            if digits and digits not in unique:
                unique[digits] = r
    return list(unique.values()) 