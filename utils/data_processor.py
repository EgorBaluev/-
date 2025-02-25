import pandas as pd
import xlrd
from datetime import datetime

def normalize_column_name(col_name):
    """Нормализует название колонки для сопоставления."""
    if not isinstance(col_name, str):
        col_name = str(col_name)
    return col_name.lower().strip().replace(' ', '_').replace('-', '_')

def find_matching_column(columns, target):
    """Находит подходящую колонку по схожести названия."""
    target = normalize_column_name(target)

    # Расширенный словарь возможных соответствий для Bitrix24
    column_mappings = {
        'date': [
            'дата', 'date', 'datetime', 'created', 'created_at', 'дата_создания',
            'дата_обращения', 'дата_заявки', 'дата_создания_заявки', 'время_создания',
            'датасоздания', 'date_created', 'creation_date', 'крайний_срок'
        ],
        'client': [
            'client', 'customer', 'клиент', 'заказчик', 'компания', 'company',
            'организация', 'контрагент', 'название_компании', 'customer_name',
            'client_name', 'company_name', 'контакт', 'contact', 'автор'
        ],
        'ticket_type': [
            'тип', 'type', 'ticket_type', 'тип_тикета', 'категория', 'category',
            'тип_обращения', 'вид_обращения', 'тип_заявки', 'категория_заявки',
            'request_type', 'issue_type', 'тип_проблемы', 'проблема', 'уровень'
        ],
        'status': [
            'status', 'статус', 'state', 'состояние', 'статус_заявки',
            'состояние_заявки', 'ticket_status', 'текущий_статус', 
            'этап', 'стадия', 'stage', 'ticket_state', 'индикатор'
        ]
    }

    # Проверяем точное совпадение
    normalized_columns = {normalize_column_name(col): col for col in columns}
    if target in normalized_columns:
        return normalized_columns[target]

    # Проверяем соответствие по маппингу
    for col in columns:
        normalized_col = normalize_column_name(col)
        for standard_name, variations in column_mappings.items():
            if standard_name == target and normalized_col in [normalize_column_name(v) for v in variations]:
                return col

    # Пытаемся найти частичное совпадение
    for col in columns:
        normalized_col = normalize_column_name(col)
        if target in normalized_col or normalized_col in target:
            return col

    return None

def process_excel_file(file):
    """Process uploaded Excel file and return standardized DataFrame."""
    try:
        # Try reading as xlsx first
        df = pd.read_excel(file, engine='openpyxl')
    except:
        try:
            # If fails, try reading as xls
            df = pd.read_excel(file, engine='xlrd')
        except Exception as e:
            raise ValueError(f"Ошибка при чтении файла. Убедитесь, что файл в формате Excel: {str(e)}")

    # Выводим доступные колонки для отладки
    print("Доступные колонки в файле:", df.columns.tolist())

    # Создаем словарь для переименования колонок
    column_mapping = {}
    missing_columns = []
    required_columns = ['date', 'client', 'ticket_type', 'status']

    for required_col in required_columns:
        matching_col = find_matching_column(df.columns, required_col)
        if matching_col:
            column_mapping[matching_col] = required_col
        else:
            missing_columns.append(required_col)

    if missing_columns:
        error_message = f"""
Отсутствуют обязательные колонки: {', '.join(missing_columns)}

Требуемый формат файла:
- date (дата создания тикета)
- client (название клиента)
- ticket_type (тип обращения)
- status (статус тикета)

Проверьте, что в вашем файле есть эти колонки (или их аналоги).

Доступные колонки в вашем файле:
{', '.join(df.columns.tolist())}
"""
        raise ValueError(error_message)

    # Переименовываем колонки
    df = df.rename(columns=column_mapping)

    # Convert date column to datetime
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        # Fill NaT values with current date
        df['date'] = df['date'].fillna(pd.Timestamp.now())
    except Exception as e:
        raise ValueError(f"Ошибка при обработке даты: {str(e)}")

    # Calculate response time if available
    if 'response_date' in df.columns:
        try:
            df['response_date'] = pd.to_datetime(df['response_date'], errors='coerce')
            df['response_time'] = (df['response_date'] - df['date']).dt.total_seconds() / 3600
        except Exception:
            df['response_time'] = 0
    else:
        df['response_time'] = 0

    # Clean and standardize data
    df = df.fillna('')

    # Convert columns to string safely
    for col in ['client', 'ticket_type', 'status']:
        if col in df.columns:
            # Convert all values to string, including integers
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '')
            # Clean only string values
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else str(x))

    return df
Конфигурация Streamlit (.streamlit/config.toml)
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
