from parser.case_parser import get_case_status

if __name__ == "__main__":
    case_number = "IOE0930996483"
    print("Пробуем получить статус для кейса:", case_number)
    status = get_case_status(case_number)
    print("\nРезультат парсинга:\n")
    print(status) 