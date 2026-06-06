from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.client import get_textile_types_kb, get_delivery_kb
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

@client_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Здравствуйте! 👋\n"
        "Мы - промышленная прачечная для бизнеса (B2B).\n\n"
        "Чтобы мы могли подготовить для вас коммерческое предложение, "
        "пожалуйста, ответьте на несколько вопросов.\n\n"
        "Как называется ваша компания / организация?"
    )
    await state.set_state(SurveyStates.company_name)

@client_router.message(StateFilter(SurveyStates.company_name), F.text)
async def process_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer("Отлично! Как к вам обращаться? (ФИО или Имя контактного лица)")
    await state.set_state(SurveyStates.contact_person)

@client_router.message(StateFilter(SurveyStates.contact_person), F.text)
async def process_contact_person(message: Message, state: FSMContext):
    await state.update_data(contact_person=message.text)
    await message.answer("Пожалуйста, укажите ваш номер телефона для связи:")
    await state.set_state(SurveyStates.phone_number)

@client_router.message(StateFilter(SurveyStates.phone_number), F.text)
async def process_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Укажите примерный объем стирки в неделю (в килограммах). Например: 100")
    await state.set_state(SurveyStates.volume_kg)

@client_router.message(StateFilter(SurveyStates.volume_kg), F.text)
async def process_volume_kg(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите только число (например: 100).")
        return

    await state.update_data(volume_kg=int(message.text))
    await message.answer(
        "Какой тип текстиля вы планируете сдавать в стирку?",
        reply_markup=get_textile_types_kb()
    )
    await state.set_state(SurveyStates.textile_type)

@client_router.message(StateFilter(SurveyStates.textile_type), F.text)
async def process_textile_type(message: Message, state: FSMContext):
    await state.update_data(textile_type=message.text)
    await message.answer(
        "Требуется ли вам доставка (забор и возврат белья)?",
        reply_markup=get_delivery_kb()
    )
    await state.set_state(SurveyStates.delivery_required)

@client_router.message(StateFilter(SurveyStates.delivery_required), F.text)
async def process_delivery_required(message: Message, state: FSMContext, bot: Bot):
    delivery_text = message.text.lower()
    delivery_required = "да" in delivery_text

    data = await state.get_data()

    # Save to database
    async with async_session() as session:
        new_client = Client(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            company_name=data['company_name'],
            contact_person=data['contact_person'],
            phone_number=data['phone_number'],
            volume_kg=data['volume_kg'],
            textile_type=data['textile_type'],
            delivery_required=delivery_required
        )
        session.add(new_client)
        await session.commit()

    # Send thank you message
    await message.answer(
        "Большое спасибо за ваши ответы! 🎉\n"
        "Мы свяжемся с вами в ближайшее время для обсуждения деталей.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Notify admins
    admin_msg = (
        "🔔 <b>Новая заявка!</b>\n\n"
        f"🏢 <b>Компания:</b> {html.escape(data['company_name'])}\n"
        f"👤 <b>Контакт:</b> {html.escape(data['contact_person'])}\n"
        f"📞 <b>Телефон:</b> {html.escape(data['phone_number'])}\n"
        f"⚖️ <b>Объем:</b> {data['volume_kg']} кг/нед.\n"
        f"👕 <b>Тип:</b> {html.escape(data['textile_type'])}\n"
        f"🚚 <b>Доставка:</b> {'Да' if delivery_required else 'Нет'}\n"
        f"🔗 <b>Пользователь:</b> @{html.escape(message.from_user.username) if message.from_user.username else 'Нет username'}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Failed to send notification to admin {admin_id}: {e}")

    await state.clear()
