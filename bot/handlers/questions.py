from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.client import (
    get_textile_types_kb,
    get_delivery_kb,
    get_cancel_kb,
    get_main_menu_kb,
    get_summary_kb,
    get_edit_fields_kb,
    get_location_kb
)
from bot.keyboards.admin import get_user_status_kb
from bot.database.db import async_session
from bot.database.models import Client
from bot.config import ADMIN_IDS
from bot.utils.maps import generate_route_map
from bot.utils.pdf import generate_commercial_proposal
import html
import asyncio
from aiogram.types import FSInputFile
import os

client_router = Router()

class SurveyStates(StatesGroup):
    company_name = State()
    contact_person = State()
    phone_number = State()
    volume_kg = State()
    textile_type = State()
    delivery_required = State()
    address = State()
    confirm = State()

async def show_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! 👋\n"
        "Мы - промышленная прачечная для бизнеса (B2B).\n\n"
        "Выберите нужное действие в меню ниже:",
        reply_markup=get_main_menu_kb()
    )

@client_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await show_main_menu(message, state)

@client_router.message(StateFilter(SurveyStates), F.text == "❌ Отменить опрос")
async def cancel_survey(message: Message, state: FSMContext):
    await message.answer(
        "Опрос отменен. Вы вернулись в главное меню.",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_main_menu(message, state)

# --- Main Menu Callbacks ---
@client_router.callback_query(F.data == "start_survey")
async def start_survey_cb(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")
    await asyncio.sleep(0.6)
    await callback.message.answer(
        "📊 Шаг 1 из 7 [▓░░░░░] 14%\n\n"
        "Чтобы мы могли подготовить для вас коммерческое предложение, "
        "пожалуйста, ответьте на несколько вопросов.\n\n"
        "Как называется ваша компания / организация?"
    )
    await state.set_state(SurveyStates.company_name)

@client_router.callback_query(F.data == "info_about")
async def info_about_cb(callback: CallbackQuery):
    await callback.message.answer(
        "ℹ️ <b>О нашей прачечной</b>\n\n"
        "Мы специализируемся на стирке прямого белья, спецодежды и ресторанного текстиля.\n"
        "Используем профессиональную химию и гарантируем высокое качество.\n"
        "График работы: Пн-Вс 08:00 - 20:00.",
        parse_mode="HTML"
    )
    await callback.answer()

@client_router.callback_query(F.data == "info_faq")
async def info_faq_cb(callback: CallbackQuery):
    await callback.message.answer(
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "<b>1. Какие минимальные объемы?</b>\n"
        "Мы работаем с объемами от 50 кг в неделю.\n\n"
        "<b>2. Есть ли доставка?</b>\n"
        "Да, у нас собственный автопарк. Забираем и привозим чистое.\n\n"
        "<b>3. Сроки стирки?</b>\n"
        "Обычно возврат происходит через 24-48 часов.",
        parse_mode="HTML"
    )
    await callback.answer()

@client_router.callback_query(F.data == "info_contacts")
async def info_contacts_cb(callback: CallbackQuery):
    await callback.message.answer(
        "📞 <b>Связаться с менеджером</b>\n\n"
        "Телефон: +7 (XXX) XXX-XX-XX\n"
        "Email: info@laundry-b2b.example.com\n"
        "Telegram: @manager_laundry",
        parse_mode="HTML"
    )
    await callback.answer()

# --- Survey Handlers ---
async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    delivery_str = "Да" if data.get('delivery_required') else "Нет"
    address_str = html.escape(data.get('address', '')) if data.get('address') else "-"

    summary_text = (
        "📋 <b>Пожалуйста, проверьте ваши данные:</b>\n\n"
        f"🏢 <b>Компания:</b> {html.escape(data.get('company_name', ''))}\n"
        f"👤 <b>Контакт:</b> {html.escape(data.get('contact_person', ''))}\n"
        f"📞 <b>Телефон:</b> {html.escape(data.get('phone_number', ''))}\n"
        f"⚖️ <b>Объем:</b> {data.get('volume_kg', '')} кг/нед.\n"
        f"👕 <b>Тип:</b> {html.escape(data.get('textile_type', ''))}\n"
        f"🚚 <b>Доставка:</b> {delivery_str}\n"
        f"📍 <b>Адрес:</b> {address_str}\n\n"
        "Всё верно?"
    )

    # Remove any reply keyboards
    msg = await message.answer("Подготавливаем сводку...", reply_markup=ReplyKeyboardRemove())
    await msg.delete()

    await message.answer(summary_text, reply_markup=get_summary_kb(), parse_mode="HTML")
    await state.set_state(SurveyStates.confirm)

@client_router.message(StateFilter(SurveyStates.company_name), F.text)
async def process_company_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(company_name=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📊 Шаг 2 из 6 [▓▓░░░░] 33%\n\n"
            "Отлично! Как к вам обращаться? (ФИО или Имя контактного лица)",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.contact_person)

@client_router.message(StateFilter(SurveyStates.contact_person), F.text)
async def process_contact_person(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(contact_person=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📊 Шаг 3 из 6 [▓▓▓░░░] 50%\n\n"
            "Пожалуйста, укажите ваш номер телефона для связи:",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.phone_number)

@client_router.message(StateFilter(SurveyStates.phone_number), F.text)
async def process_phone_number(message: Message, state: FSMContext, bot: Bot):
    phone_text = message.text.strip()
    # Simple validation: allow only digits, spaces, hyphens, parentheses and +
    valid_chars = set("0123456789+ -()")
    if not all(c in valid_chars for c in phone_text) or not any(c.isdigit() for c in phone_text):
        await message.answer("Пожалуйста, введите корректный номер телефона (только цифры и знак +).")
        return

    await state.update_data(phone_number=phone_text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📊 Шаг 4 из 6 [▓▓▓▓░░] 67%\n\n"
            "Укажите примерный объем стирки в неделю (в килограммах). Например: 100",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.volume_kg)

@client_router.message(StateFilter(SurveyStates.volume_kg), F.text)
async def process_volume_kg(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите только число (например: 100).")
        return

    await state.update_data(volume_kg=int(message.text))
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📊 Шаг 5 из 6 [▓▓▓▓▓░] 83%\n\n"
            "Какой тип текстиля вы планируете сдавать в стирку?",
            reply_markup=get_textile_types_kb()
        )
        await state.set_state(SurveyStates.textile_type)

@client_router.message(StateFilter(SurveyStates.textile_type), F.text)
async def process_textile_type(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(textile_type=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📊 Шаг 6 из 6 [▓▓▓▓▓▓] 100%\n\n"
            "Требуется ли вам доставка (забор и возврат белья)?",
            reply_markup=get_delivery_kb()
        )
        await state.set_state(SurveyStates.delivery_required)

@client_router.message(StateFilter(SurveyStates.delivery_required), F.text)
async def process_delivery_required(message: Message, state: FSMContext, bot: Bot):
    delivery_text = message.text.lower()
    delivery_required = "да" in delivery_text

    await state.update_data(delivery_required=delivery_required)

    data = await state.get_data()

    if delivery_required:
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        await asyncio.sleep(0.6)
        await message.answer(
            "📍 Шаг 7 из 7 [▓▓▓▓▓▓] 100%\n\n"
            "Пожалуйста, укажите адрес забора белья текстовым сообщением или отправьте геопозицию:",
            reply_markup=get_location_kb()
        )
        await state.set_state(SurveyStates.address)
    else:
        await state.update_data(address=None)
        if data.get('is_editing'):
            await state.update_data(is_editing=False)
        await show_summary(message, state)

@client_router.message(StateFilter(SurveyStates.address))
async def process_address(message: Message, state: FSMContext):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        address = f"{lat},{lon}"
    elif message.text:
        address = message.text
    else:
        await message.answer("Пожалуйста, отправьте текстовый адрес или геопозицию.")
        return

    await state.update_data(address=address)

    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)

    await show_summary(message, state)

# --- Summary and Edit Callbacks ---
@client_router.callback_query(StateFilter(SurveyStates.confirm), F.data == "submit_survey")
async def submit_survey_cb(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    # Save to database
    async with async_session() as session:
        new_client = Client(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            company_name=data['company_name'],
            contact_person=data['contact_person'],
            phone_number=data['phone_number'],
            volume_kg=data['volume_kg'],
            textile_type=data['textile_type'],
            delivery_required=data['delivery_required'],
            address=data.get('address')
        )
        session.add(new_client)
        await session.commit()

    # Map & PDF logic
    map_img_path = None
    distance = None
    if data.get('delivery_required') and data.get('address'):
        # Generate map off the main thread if possible, but geopy/requests might be fast enough
        # We wrap in to_thread just in case
        map_result = await asyncio.to_thread(generate_route_map, data['address'], callback.from_user.id)
        if map_result:
            map_img_path, distance = map_result

    pdf_path = await asyncio.to_thread(generate_commercial_proposal, data, map_img_path, distance)

    await callback.message.edit_text(
        "✅ <b>Заявка успешно отправлена!</b> 🎉\n"
        "Мы подготовили для вас предварительное коммерческое предложение (см. документ ниже).\n"
        "Наш менеджер свяжется с вами в ближайшее время.",
        parse_mode="HTML"
    )

    pdf_doc = FSInputFile(pdf_path)
    await callback.message.answer_document(
        document=pdf_doc,
        caption="Ваше коммерческое предложение 📄"
    )

    # Notify admins
    address_str = html.escape(data.get('address', '')) if data.get('address') else "-"
    admin_msg = (
        "🔔 <b>Новая заявка!</b>\n\n"
        f"🏢 <b>Компания:</b> {html.escape(data['company_name'])}\n"
        f"👤 <b>Контакт:</b> {html.escape(data['contact_person'])}\n"
        f"📞 <b>Телефон:</b> {html.escape(data['phone_number'])}\n"
        f"⚖️ <b>Объем:</b> {data['volume_kg']} кг/нед.\n"
        f"👕 <b>Тип:</b> {html.escape(data['textile_type'])}\n"
        f"🚚 <b>Доставка:</b> {'Да' if data['delivery_required'] else 'Нет'}\n"
        f"📍 <b>Адрес:</b> {address_str}\n"
        f"🔗 <b>Пользователь:</b> @{html.escape(callback.from_user.username) if callback.from_user.username else 'Нет username'}"
    )

    for admin_id in ADMIN_IDS:
        try:
            # Send notification text
            msg = await bot.send_message(
                chat_id=admin_id,
                text=admin_msg,
                parse_mode="HTML",
                reply_markup=get_user_status_kb(new_client.id)
            )
            # Send PDF to admin as well
            admin_pdf_doc = FSInputFile(pdf_path)
            await bot.send_document(
                chat_id=admin_id,
                document=admin_pdf_doc,
                reply_to_message_id=msg.message_id
            )
        except Exception as e:
            print(f"Failed to send notification to admin {admin_id}: {e}")

    await state.clear()
    await callback.answer()

    # Cleanup temp files
    try:
        os.remove(pdf_path)
        if map_img_path and os.path.exists(map_img_path):
            os.remove(map_img_path)
    except Exception as e:
        print(f"Failed to cleanup temp files: {e}")

@client_router.callback_query(StateFilter(SurveyStates.confirm), F.data == "edit_survey")
async def edit_survey_cb(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите поле, которое хотите изменить:",
        reply_markup=get_edit_fields_kb()
    )
    await callback.answer()

@client_router.callback_query(StateFilter(SurveyStates.confirm), F.data == "back_to_summary")
async def back_to_summary_cb(callback: CallbackQuery, state: FSMContext):
    # Need to delete current message and resend summary so it's a new message
    await callback.message.delete()
    await show_summary(callback.message, state)
    await callback.answer()

@client_router.callback_query(StateFilter(SurveyStates.confirm), F.data.startswith("edit_field_"))
async def process_edit_field_cb(callback: CallbackQuery, state: FSMContext, bot: Bot):
    field_to_edit = callback.data.replace("edit_field_", "")

    await state.update_data(is_editing=True)
    await callback.answer()

    # We must send a new message because ReplyKeyboardMarkups can't be added to CallbackQuery messages (only Inline)
    await callback.message.delete()

    await bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")
    await asyncio.sleep(0.6)

    if field_to_edit == "company_name":
        await callback.message.answer("📊 Шаг 1 из 6 [▓░░░░░] 17%\n\n✏️ <b>Редактирование:</b>\nВведите новое название компании / организации:", reply_markup=get_cancel_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.company_name)
    elif field_to_edit == "contact_person":
        await callback.message.answer("📊 Шаг 2 из 6 [▓▓░░░░] 33%\n\n✏️ <b>Редактирование:</b>\nВведите новое ФИО или Имя контактного лица:", reply_markup=get_cancel_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.contact_person)
    elif field_to_edit == "phone_number":
        await callback.message.answer("📊 Шаг 3 из 6 [▓▓▓░░░] 50%\n\n✏️ <b>Редактирование:</b>\nВведите новый номер телефона для связи:", reply_markup=get_cancel_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.phone_number)
    elif field_to_edit == "volume_kg":
        await callback.message.answer("📊 Шаг 4 из 6 [▓▓▓▓░░] 67%\n\n✏️ <b>Редактирование:</b>\nУкажите новый примерный объем стирки в неделю (в килограммах):", reply_markup=get_cancel_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.volume_kg)
    elif field_to_edit == "textile_type":
        await callback.message.answer("📊 Шаг 5 из 6 [▓▓▓▓▓░] 83%\n\n✏️ <b>Редактирование:</b>\nВыберите новый тип текстиля:", reply_markup=get_textile_types_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.textile_type)
    elif field_to_edit == "delivery_required":
        await callback.message.answer("📊 Шаг 6 из 7 [▓▓▓▓▓░] 85%\n\n✏️ <b>Редактирование:</b>\nТребуется ли вам доставка (забор и возврат белья)?", reply_markup=get_delivery_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.delivery_required)
    elif field_to_edit == "address":
        await callback.message.answer("📍 Шаг 7 из 7 [▓▓▓▓▓▓] 100%\n\n✏️ <b>Редактирование:</b>\nУкажите адрес забора белья текстовым сообщением или отправьте геопозицию:", reply_markup=get_location_kb(), parse_mode="HTML")
        await state.set_state(SurveyStates.address)
