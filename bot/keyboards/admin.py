from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Main admin menu keyboard"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
            [InlineKeyboardButton(text="📊 Скачать отчет (Excel)", callback_data="admin_download_report")],
            [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="📊 Аналитика", callback_data="admin_analytics")]
        ]
    )
    return kb

def get_user_status_kb(client_id: int) -> InlineKeyboardMarkup:
    """Keyboard for changing a user's status"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🆕 Новый", callback_data=f"status_new_{client_id}"),
                InlineKeyboardButton(text="✅ Договор", callback_data=f"status_contract_{client_id}"),
                InlineKeyboardButton(text="❌ Отказ", callback_data=f"status_reject_{client_id}")
            ]
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
