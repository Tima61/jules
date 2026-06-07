import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile
from typing import List, Tuple

def generate_analytics_charts(clients_data: List[dict]) -> List[BufferedInputFile]:
    """
    Synchronous function to generate analytics charts using matplotlib.
    Expects a list of dictionaries with client data.
    """
    charts = []

    # 1. Sales Funnel
    status_counts = {"🆕 Новый": 0, "✅ Договор": 0, "❌ Отказ": 0}
    for client in clients_data:
        status = client.get('status', '🆕 Новый')
        if status in status_counts:
            status_counts[status] += 1

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(status_counts.keys(), status_counts.values(), color=['blue', 'green', 'red'])
    ax.set_title('Воронка продаж (по статусам)')
    ax.set_ylabel('Количество заявок')

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    charts.append(BufferedInputFile(buf.read(), filename="funnel.png"))
    plt.close(fig)

    # Filter clients with contract for the next charts
    contract_clients = [c for c in clients_data if c.get('status') == '✅ Договор']

    if not contract_clients:
        return charts # Return only funnel if no contracts

    # 2. Volume Chart (Top 10 by volume)
    # Sort by volume
    contract_clients_sorted = sorted(contract_clients, key=lambda x: x.get('volume_kg', 0), reverse=True)[:10]
    companies = [c.get('company_name', 'Unknown') for c in contract_clients_sorted]
    volumes = [c.get('volume_kg', 0) for c in contract_clients_sorted]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(companies, volumes, color='skyblue')
    ax.set_title('Топ-10 клиентов по объему стирки (кг/нед) - ТОЛЬКО ДОГОВОРЫ')
    ax.set_ylabel('Объем (кг)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    charts.append(BufferedInputFile(buf.read(), filename="volume.png"))
    plt.close(fig)

    # 3. Textile Type Chart
    textile_counts = {}
    for c in contract_clients:
        t_type = c.get('textile_type', 'Unknown')
        textile_counts[t_type] = textile_counts.get(t_type, 0) + 1

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(textile_counts.values(), labels=textile_counts.keys(), autopct='%1.1f%%', startangle=140)
    ax.set_title('Распределение по типам текстиля - ТОЛЬКО ДОГОВОРЫ')

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    charts.append(BufferedInputFile(buf.read(), filename="textile.png"))
    plt.close(fig)

    return charts
