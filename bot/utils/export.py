import pandas as pd
from sqlalchemy import select
from datetime import datetime
import os

from bot.database.db import async_session
from bot.database.models import Client

async def generate_excel_report() -> str | None:
    """Fetches all clients and generates an Excel report, returning the filepath."""
    async with async_session() as session:
        result = await session.execute(select(Client).order_by(Client.created_at.desc()))
        clients = result.scalars().all()

    if not clients:
        return None

    # Prepare data for pandas DataFrame
    data = []
    for c in clients:
        data.append({
            "ID": c.id,
            "Telegram ID": c.telegram_id,
            "Username": f"@{c.username}" if c.username else "-",
            "Компания": c.company_name,
            "Контактное лицо": c.contact_person,
            "Телефон": c.phone_number,
            "Объем (кг/нед)": c.volume_kg,
            "Тип текстиля": c.textile_type,
            "Требуется доставка": "Да" if c.delivery_required else "Нет",
            "Статус": c.status,
            "Дата заявки": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(data)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"clients_report_{timestamp}.xlsx"

    # Save to Excel
    import asyncio
    await asyncio.to_thread(df.to_excel, filepath, index=False, engine='openpyxl')

    return filepath
