from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


def createkb(approveData, rejectData):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="✅ Approve", callback_data=approveData))
    kb.add(InlineKeyboardButton(text="❌ Decline", callback_data=rejectData))
    return kb
