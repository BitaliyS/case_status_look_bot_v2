from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

def get_case_status(case_number):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Окно браузера не будет открываться
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")  # Отключаем GPU для облачной среды
    chrome_options.add_argument("--disable-extensions")  # Отключаем расширения
    chrome_options.add_argument("--disable-plugins")  # Отключаем плагины
    chrome_options.add_argument("--disable-images")  # Отключаем загрузку изображений для ускорения
    chrome_options.add_argument("--disable-javascript")  # Отключаем JavaScript если не нужен
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Прокси отключён для теста
    # proxy = f"{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    # chrome_options.add_argument(f'--proxy-server=http://{proxy}')

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.casestatusext.com/cases/")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.ant-input"))
        )
        input_box = driver.find_element(By.CSS_SELECTOR, "input.ant-input")
        input_box.clear()
        input_box.send_keys(case_number)
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='button']")
        search_btn.click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ant-descriptions"))
        )
        table = driver.find_element(By.CSS_SELECTOR, "div.ant-descriptions")
        rows = table.find_elements(By.CSS_SELECTOR, "tr.ant-descriptions-row")
        result = ""
        for row in rows:
            ths = row.find_elements(By.TAG_NAME, "th")
            tds = row.find_elements(By.TAG_NAME, "td")
            for th, td in zip(ths, tds):
                result += f"<b>{th.text}:</b> {td.text}\n"
        detail = driver.find_element(By.CSS_SELECTOR, "div.status-detail-content").text
        result += f"\n<b>Detail:</b>\n{detail}"
        return result
    except Exception as e:
        return f"Ошибка при получении статуса: {e}\n{traceback.format_exc()}"
    finally:
        driver.quit() 