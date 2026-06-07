from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from typing import List

def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Main admin menu keyboard"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
            [InlineKeyboardButton(text="🗂 Управление клиентами (CRM)", callback_data="crm_list_0")],
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

def get_clients_list_kb(clients: List, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Keyboard for paginated client list in CRM"""
    inline_keyboard = []

    # Add buttons for each client in the current page
    for client in clients:
        status_icon = "🆕" if "Новый" in client.status else ("✅" if "Договор" in client.status else "❌")
        btn_text = f"{status_icon} {client.company_name} | {client.phone_number}"
        inline_keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"crm_card_{client.id}_{page}")])

    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"crm_list_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"crm_list_{page+1}"))

    if nav_buttons:
        inline_keyboard.append(nav_buttons)

    inline_keyboard.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="admin_main_menu")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_client_card_kb(client_id: int, current_page: int) -> InlineKeyboardMarkup:
    """Keyboard for client card inside CRM allowing status change"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🆕 Новый", callback_data=f"crm_status_new_{client_id}_{current_page}"),
                InlineKeyboardButton(text="✅ Договор", callback_data=f"crm_status_contract_{client_id}_{current_page}"),
                InlineKeyboardButton(text="❌ Отказ", callback_data=f"crm_status_reject_{client_id}_{current_page}")
            ],
            [InlineKeyboardButton(text="🔙 К списку клиентов", callback_data=f"crm_list_{current_page}")]
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
