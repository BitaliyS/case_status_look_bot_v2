from sheets_api import add_case, get_all_cases

if __name__ == "__main__":
    case_number = "IOE0930996483"
    client_name = "Дубинин"
    status = "На рассмотрении"
    print(f"Добавляю кейс: {case_number}, {client_name}, {status}")
    add_case(case_number, client_name, status)
    print("\nТекущий список кейсов:")
    for case in get_all_cases():
        print(case) 