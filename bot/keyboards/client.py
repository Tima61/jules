from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_kb() -> InlineKeyboardMarkup:
    """Main Menu keyboard"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="start_survey")],
            [InlineKeyboardButton(text="ℹ️ О прачечной", callback_data="info_about")],
            [InlineKeyboardButton(text="❓ Частые вопросы (FAQ)", callback_data="info_faq")],
            [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="info_contacts")]
        ]
    )
    return kb

def get_summary_kb() -> InlineKeyboardMarkup:
    """Keyboard for confirming or editing survey data"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Все верно, отправить", callback_data="submit_survey")],
            [InlineKeyboardButton(text="✏️ Изменить данные", callback_data="edit_survey")]
        ]
    )
    return kb

def get_edit_fields_kb() -> InlineKeyboardMarkup:
    """Keyboard for selecting which field to edit"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏢 Название компании", callback_data="edit_field_company_name")],
            [InlineKeyboardButton(text="👤 Имя контактного лица", callback_data="edit_field_contact_person")],
            [InlineKeyboardButton(text="📞 Номер телефона", callback_data="edit_field_phone_number")],
            [InlineKeyboardButton(text="⚖️ Объем стирки", callback_data="edit_field_volume_kg")],
            [InlineKeyboardButton(text="👕 Тип текстиля", callback_data="edit_field_textile_type")],
            [InlineKeyboardButton(text="🚚 Доставка", callback_data="edit_field_delivery_required")],
            [InlineKeyboardButton(text="🔙 Назад к проверке", callback_data="back_to_summary")]
        ]
    )
    return kb

def get_cancel_kb() -> ReplyKeyboardMarkup:
    """Keyboard for cancelling the survey"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить опрос")]
        ],
        resize_keyboard=True
    )
    return kb

def get_textile_types_kb() -> ReplyKeyboardMarkup:
    """Keyboard for selecting textile type"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прямое белье"), KeyboardButton(text="Спецодежда")],
            [KeyboardButton(text="Махровые изделия"), KeyboardButton(text="Ресторанный текстиль")],
            [KeyboardButton(text="Смешанный тип")],
            [KeyboardButton(text="❌ Отменить опрос")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите тип текстиля"
    )
    return kb

def get_delivery_kb() -> ReplyKeyboardMarkup:
    """Keyboard for selecting delivery option"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, нужна доставка"), KeyboardButton(text="Нет, привезем сами")],
            [KeyboardButton(text="❌ Отменить опрос")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Требуется ли доставка?"
    )
    return kb
