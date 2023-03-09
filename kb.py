from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


def createkb(approvedata, rejectdata):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="✅Approve", callback_data=approvedata))
    kb.add(InlineKeyboardButton(text="❌Decline", callback_data=rejectdata))
    return kb