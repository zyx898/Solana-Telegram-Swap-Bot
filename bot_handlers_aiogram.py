import asyncio
import logging
import sys
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from main import ALL_USERS_DATA
from config import RPC_URL
from menus import *
from db_handler_aio import *
from wallet import Wallet

import sys

class Form(StatesGroup):
    start_menu = State()
    wallet_menu = State()
    show_wallets = State()
    copy_trade_menu = State()
    transaction_menu = State()
    help_menu = State()
    swap_menu = State()
    set_wallet = State()
    waiting_for_private_key = State()
    set_slippage = State()

from main import form_router







#show_wallets Handler
@form_router.message(Form.show_wallets)
async def show_wallets(message: Message, state: FSMContext) -> None:
    await message.edit_text("Here is Your Wallet Data: -> wallet data", reply_markup=go_back_button)

