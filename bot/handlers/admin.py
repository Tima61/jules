from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from sqlalchemy import select
import os

from bot.config import ADMIN_IDS
from bot.keyboards.admin import get_admin_main_kb, get_broadcast_confirm_kb
from bot.database.db import async_session
from bot.database.models import Client
from bot.utils.export import generate_excel_report
import html

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast_text = State()

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

@admin_router.callback_query(F.data == "admin_broadcast")
async def process_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите текст для рассылки всем клиентам. Вы можете использовать HTML-разметку. "
        "Для отмены напишите 'отмена'."
    )
    await state.set_state(AdminStates.waiting_for_broadcast_text)
    await callback.answer()

@admin_router.message(StateFilter(AdminStates.waiting_for_broadcast_text), F.text)
async def process_broadcast_text(message: Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.clear()
        await message.answer("Рассылка отменена.")
        return

    await state.update_data(broadcast_text=message.text)

    preview_text = "<b>Превью рассылки:</b>\n\n" + message.text

    try:
        await message.answer(
            preview_text,
            reply_markup=get_broadcast_confirm_kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка в HTML-разметке: {e}\nПопробуйте отправить текст заново или напишите 'отмена'.")

@admin_router.callback_query(StateFilter(AdminStates.waiting_for_broadcast_text), F.data == "broadcast_cancel")
async def broadcast_cancel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Рассылка отменена.")
    await callback.answer()

@admin_router.callback_query(StateFilter(AdminStates.waiting_for_broadcast_text), F.data == "broadcast_start")
async def broadcast_start_cb(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text")

    await callback.message.edit_text("🚀 Запускаю рассылку, подождите...")
    await state.clear()

    async with async_session() as session:
        # Get unique telegram IDs
        result = await session.execute(select(Client.telegram_id).distinct())
        telegram_ids = result.scalars().all()

    success_count = 0
    for t_id in telegram_ids:
        try:
            await bot.send_message(chat_id=t_id, text=broadcast_text, parse_mode="HTML")
            success_count += 1
        except Exception:
            # Skip if user blocked the bot or account deleted
            pass

    await callback.message.answer(f"Рассылка завершена. Успешно отправлено сообщений: {success_count}")
    await callback.answer()
