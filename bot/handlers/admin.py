from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from sqlalchemy import select
import os

from bot.config import ADMIN_IDS
from bot.keyboards.admin import get_admin_main_kb
from bot.database.db import async_session
from bot.database.models import Client
from bot.utils.export import generate_excel_report
import html

admin_router = Router()

# Filter to allow only admins to access these handlers
admin_router.message.filter(F.from_user.id.in_(ADMIN_IDS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer(
        "🛠 <b>Панель администратора</b>\n\nВыберите нужное действие:",
        reply_markup=get_admin_main_kb(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "admin_list_users")
async def process_list_users(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Client).order_by(Client.created_at.desc()))
        clients = result.scalars().all()

    if not clients:
        await callback.message.answer("База пользователей пока пуста.")
        await callback.answer()
        return

    text = "👥 <b>Все заявки:</b>\n\n"
    for c in clients:
        text += (
            f"🔸 <b>{html.escape(c.company_name)}</b> ({html.escape(c.contact_person)})\n"
            f"📞 {html.escape(c.phone_number)} | ⚖️ {c.volume_kg} кг\n"
        )

        if len(text) > 3800:
            text += "\n... (список слишком длинный, скачайте отчет)"
            break

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@admin_router.callback_query(F.data == "admin_download_report")
async def process_download_report(callback: CallbackQuery):
    await callback.answer("Генерирую отчет...")

    # Generate the report
    filepath = await generate_excel_report()

    if not filepath:
        await callback.message.answer("Не удалось сгенерировать отчет или база пуста.")
        return

    # Send the document
    document = FSInputFile(filepath)
    await callback.message.answer_document(
        document=document,
        caption="📊 Отчет по всем заявкам"
    )

    # Clean up the generated file after sending
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"Failed to delete temporary file {filepath}: {e}")
