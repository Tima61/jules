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
    get_edit_fields_kb
)
from bot.keyboards.admin import get_user_status_kb
from bot.database.db import async_session
from bot.database.models import Client
from bot.config import ADMIN_IDS
import html

client_router = Router()

class SurveyStates(StatesGroup):
    company_name = State()
    contact_person = State()
    phone_number = State()
    volume_kg = State()
    textile_type = State()
    delivery_required = State()
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
async def start_survey_cb(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Чтобы мы могли подготовить для вас коммерческое предложение, "
        "пожалуйста, ответьте на несколько вопросов.\n\n"
        "Как называется ваша компания / организация?"
    )
    await state.set_state(SurveyStates.company_name)
    await callback.answer()

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

    summary_text = (
        "📋 <b>Пожалуйста, проверьте ваши данные:</b>\n\n"
        f"🏢 <b>Компания:</b> {html.escape(data.get('company_name', ''))}\n"
        f"👤 <b>Контакт:</b> {html.escape(data.get('contact_person', ''))}\n"
        f"📞 <b>Телефон:</b> {html.escape(data.get('phone_number', ''))}\n"
        f"⚖️ <b>Объем:</b> {data.get('volume_kg', '')} кг/нед.\n"
        f"👕 <b>Тип:</b> {html.escape(data.get('textile_type', ''))}\n"
        f"🚚 <b>Доставка:</b> {delivery_str}\n\n"
        "Всё верно?"
    )

    # Remove any reply keyboards
    msg = await message.answer("Подготавливаем сводку...", reply_markup=ReplyKeyboardRemove())
    await msg.delete()

    await message.answer(summary_text, reply_markup=get_summary_kb(), parse_mode="HTML")
    await state.set_state(SurveyStates.confirm)

@client_router.message(StateFilter(SurveyStates.company_name), F.text)
async def process_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await message.answer(
            "Отлично! Как к вам обращаться? (ФИО или Имя контактного лица)",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.contact_person)

@client_router.message(StateFilter(SurveyStates.contact_person), F.text)
async def process_contact_person(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await message.answer(
            "Пожалуйста, укажите ваш номер телефона для связи:",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.phone_number)

@client_router.message(StateFilter(SurveyStates.phone_number), F.text)
async def process_phone_number(message: Message, state: FSMContext):
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
        await message.answer(
            "Укажите примерный объем стирки в неделю (в килограммах). Например: 100",
            reply_markup=get_cancel_kb()
        )
        await state.set_state(SurveyStates.volume_kg)

@client_router.message(StateFilter(SurveyStates.volume_kg), F.text)
async def process_volume_kg(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите только число (например: 100).")
        return

    await state.update_data(volume_kg=int(message.text))
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await message.answer(
            "Какой тип текстиля вы планируете сдавать в стирку?",
            reply_markup=get_textile_types_kb()
        )
        await state.set_state(SurveyStates.textile_type)

@client_router.message(StateFilter(SurveyStates.textile_type), F.text)
async def process_textile_type(message: Message, state: FSMContext):
    await state.update_data(textile_type=message.text)
    data = await state.get_data()
    if data.get('is_editing'):
        await state.update_data(is_editing=False)
        await show_summary(message, state)
    else:
        await message.answer(
            "Требуется ли вам доставка (забор и возврат белья)?",
            reply_markup=get_delivery_kb()
        )
        await state.set_state(SurveyStates.delivery_required)

@client_router.message(StateFilter(SurveyStates.delivery_required), F.text)
async def process_delivery_required(message: Message, state: FSMContext):
    delivery_text = message.text.lower()
    delivery_required = "да" in delivery_text

    await state.update_data(delivery_required=delivery_required)

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
            delivery_required=data['delivery_required']
        )
        session.add(new_client)
        await session.commit()

    await callback.message.edit_text(
        "✅ <b>Заявка успешно отправлена!</b> 🎉\n"
        "Мы свяжемся с вами в ближайшее время для обсуждения деталей.",
        parse_mode="HTML"
    )

    # Notify admins
    admin_msg = (
        "🔔 <b>Новая заявка!</b>\n\n"
        f"🏢 <b>Компания:</b> {html.escape(data['company_name'])}\n"
        f"👤 <b>Контакт:</b> {html.escape(data['contact_person'])}\n"
        f"📞 <b>Телефон:</b> {html.escape(data['phone_number'])}\n"
        f"⚖️ <b>Объем:</b> {data['volume_kg']} кг/нед.\n"
        f"👕 <b>Тип:</b> {html.escape(data['textile_type'])}\n"
        f"🚚 <b>Доставка:</b> {'Да' if data['delivery_required'] else 'Нет'}\n"
        f"🔗 <b>Пользователь:</b> @{html.escape(callback.from_user.username) if callback.from_user.username else 'Нет username'}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_msg,
                parse_mode="HTML",
                reply_markup=get_user_status_kb(new_client.id)
            )
        except Exception as e:
            print(f"Failed to send notification to admin {admin_id}: {e}")

    await state.clear()
    await callback.answer()

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
async def process_edit_field_cb(callback: CallbackQuery, state: FSMContext):
    field_to_edit = callback.data.replace("edit_field_", "")

    await state.update_data(is_editing=True)

    # We must send a new message because ReplyKeyboardMarkups can't be added to CallbackQuery messages (only Inline)
    await callback.message.delete()

    if field_to_edit == "company_name":
        await callback.message.answer("Введите новое название компании / организации:", reply_markup=get_cancel_kb())
        await state.set_state(SurveyStates.company_name)
    elif field_to_edit == "contact_person":
        await callback.message.answer("Введите новое ФИО или Имя контактного лица:", reply_markup=get_cancel_kb())
        await state.set_state(SurveyStates.contact_person)
    elif field_to_edit == "phone_number":
        await callback.message.answer("Введите новый номер телефона для связи:", reply_markup=get_cancel_kb())
        await state.set_state(SurveyStates.phone_number)
    elif field_to_edit == "volume_kg":
        await callback.message.answer("Укажите новый примерный объем стирки в неделю (в килограммах):", reply_markup=get_cancel_kb())
        await state.set_state(SurveyStates.volume_kg)
    elif field_to_edit == "textile_type":
        await callback.message.answer("Выберите новый тип текстиля:", reply_markup=get_textile_types_kb())
        await state.set_state(SurveyStates.textile_type)
    elif field_to_edit == "delivery_required":
        await callback.message.answer("Требуется ли вам доставка (забор и возврат белья)?", reply_markup=get_delivery_kb())
        await state.set_state(SurveyStates.delivery_required)

    await callback.answer()
