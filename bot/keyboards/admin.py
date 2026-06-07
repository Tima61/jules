from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Main admin menu keyboard"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
            [InlineKeyboardButton(text="📊 Скачать отчет (Excel)", callback_data="admin_download_report")],
            [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="admin_broadcast")]
        ]
    )
    return kb

def get_broadcast_confirm_kb() -> InlineKeyboardMarkup:
    """Keyboard for confirming broadcast"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Запустить рассылку", callback_data="broadcast_start")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="broadcast_cancel")]
        ]
    )
    return kb
