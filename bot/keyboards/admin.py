from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Main admin menu keyboard"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
            [InlineKeyboardButton(text="📊 Скачать отчет (Excel)", callback_data="admin_download_report")]
        ]
    )
    return kb
