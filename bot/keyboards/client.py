from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_textile_types_kb() -> ReplyKeyboardMarkup:
    """Keyboard for selecting textile type"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прямое белье"), KeyboardButton(text="Спецодежда")],
            [KeyboardButton(text="Махровые изделия"), KeyboardButton(text="Ресторанный текстиль")],
            [KeyboardButton(text="Смешанный тип")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите тип текстиля"
    )
    return kb

def get_delivery_kb() -> ReplyKeyboardMarkup:
    """Keyboard for selecting delivery option"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да, нужна доставка"), KeyboardButton(text="Нет, привезем сами")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Требуется ли доставка?"
    )
    return kb
