import sys
from pathlib import Path

# Добавляем корень проекта в путь (работает при запуске из любой директории)
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.main import load_orders_from_file, process_orders, analyze_orders

def process_order_file(input_file, output_file):
    loading_orders = load_orders_from_file(input_file)
    if loading_orders is None:
        print("Нет данных для обработки")
        return
    processing_orders = process_orders(loading_orders)
    analytics = analyze_orders(processing_orders)
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(f"Обработано заказов: {analytics['total_orders']}\n")
        f.write(f"Общая сумма: {analytics['total_sum']} руб.\n")
        by_status_str = ", ".join(f"{k}: {v}" for k, v in analytics['by_status'].items())
        f.write(f"По статусам: {by_status_str}\n")
        f.write(f"Уникальных пользователей: {len(analytics['unique_users'])}\n")


_data_dir = _project_root / 'src' / 'data'
process_order_file(_data_dir / 'orders.txt', _data_dir / 'processed_orders_report.txt')