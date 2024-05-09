import asyncio
from datetime import datetime
import logging
import math
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
from solders.pubkey import Pubkey # type: ignore

import sys

sys.path.append('..')

from swap import Swap
from config import *
from bot_handlers_aiogram import *
from menus import *
from db_handler_aio import *
from tokenInfo import TokenInfo

TOKEN = TELEGRAM_BOT_TOKEN
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
    buy_token = State()
    start_transaction = State()


form_router = Router()
ALL_USERS_DATA = get_all_users()
#Start Menu Handler
@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.start_menu)
    userId = message.from_user.id
    userData = await get_user(user_id=userId)
    print(userData)
    if userData:
        get_user_data = await get_user(user_id=userId)
        ALL_USERS_DATA[userId] = get_user_data #store user data in a dictionary
        await message.answer("Welcome back! Choose Your Option!", reply_markup=main_menu_keyboard)
    else:
        #create new user
        await insert_user(user_id=userId, wallet_address="", private_key="", trades="{}", slippage=10, monitor_wallet="{}")
        ALL_USERS_DATA[userId] = await get_user(user_id=userId) #store user data in a dictionary
        await message.answer("Hi there! Welcome to Lucas's Solana Trading Bot!", reply_markup=main_menu_keyboard)
    await state.update_data(userId=userId)
    await state.update_data(userData=userData)

#set_slippage Handler
@form_router.message(Form.set_slippage)
async def set_slippage(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = data.get("userData")
    slippage = message.text
    if slippage.isdigit():
        slippage = float(message.text)
        if int(slippage) > 100 & int(slippage) < 0:
            await message.answer("Slippage must be less than 100 and greater than 0", reply_markup=go_back_button)
            await state.set_state(Form.set_slippage)
        else:
            await message.answer(f"Slippage had changed from {userData['slippage']} to {slippage}", reply_markup=swap_menu_keyboard)
            await update_user(user_id=userId, slippage=slippage)
            userData = await get_user(user_id=userId)
            print(userData)
            await state.update_data(userData=userData)
        await state.set_state(Form.swap_menu)
    else:
        await message.answer("Please enter a valid number", reply_markup=go_back_button)
        await state.set_state(Form.set_slippage)


#Private Key Handler
@form_router.message(Form.waiting_for_private_key)
async def process_private_key(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    await state.update_data(private_key=message.text)
    private_key = message.text
    # Save the private key to the database

    wallet = Wallet(RPC_URL, private_key)
    wallet_address = wallet.wallet.pubkey().__str__()

    if wallet_address:
        await update_user(user_id=userId, wallet_address=wallet_address, private_key=private_key, trades="{}", slippage=10)
        userData = await get_user(user_id=userId)
        await state.update_data(userData=userData)
        accBalance = await wallet.get_token_balance(wallet_address)
        await message.answer(f"You Wallet: {wallet_address} has been set Successfully\n Current Balance: {accBalance['balance']['float']} SOL", reply_markup=wallet_menu_keyboard)
    else:
        await message.answer("Invalid Private Key", reply_markup=go_back_button)
        await state.set_state(Form.wallet_menu)
    await state.set_state(Form.wallet_menu)


async def show_wallet_data(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    if userData.get("wallet_address") == "":
        await message.edit_text("You have not set your wallet yet!", reply_markup=go_back_button)
        await state.set_state(Form.wallet_menu)
    else:
        wallet = Wallet(RPC_URL, userData['private_key'])
        balance = await wallet.get_token_balance(userData['wallet_address'])
        walletData = f"Wallet Address: {userData['wallet_address']}\nPrivate Key: {userData['private_key']}\n\nCurent Balance: {balance['balance']['float']} SOL"
        await message.edit_text(f"{walletData}", reply_markup=go_back_button)

async def set_wallet(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    if userData.get("wallet_address"):
        await message.edit_text(f"You have already set your wallet address!\nWallet Address:{userData['wallet_address']}", reply_markup=go_back_button)
    else:
        await message.edit_text("Please enter your private key?",reply_markup=go_back_button)
        await state.set_state(Form.waiting_for_private_key)  # 假设这是等待私钥输入的状态
        


async def reset_wallet(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = data.get("userData")
    if userData.get("wallet_address"):
        await update_user(user_id=userId, wallet_address="", private_key="", trades="{}", slippage=10)
        await message.answer(f"You have reset your wallet data! \n Please Update The Bot with Your New Wallet\nYour Previous Wallet Detail:\nwallet_address:{userData['wallet_address']}\nprivate_key:{userData['private_key']}")
        userData = await get_user(user_id=userId)
        await state.update_data(userData=userData)
    else:
        await message.edit_text("You have not set your wallet yet!", reply_markup=go_back_button)
    await state.clear()
    await state.set_state(Form.wallet_menu)


@form_router.message(Form.swap_menu)
async def buy_token(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userData = data.get("userData")
    token_address = message.text
    swapClient = Swap(RPC_URL, userData.get("private_key"))
    # token_mint_addresss = await swapClient.get_token_mint_account(token_address)
    account_token_info = await swapClient.get_wallet_token_balance(token_address)
    token_info = await TokenInfo.get_token_info(token_address)
    await state.update_data(token_info=token_info)
    await state.update_data(token_address=token_address)
    await state.update_data(account_token_info=account_token_info)
    open_timestamp = token_info.get('open_timestamp', 0)
    if open_timestamp:
        open_date = datetime.fromtimestamp(open_timestamp).strftime('%Y-%m-%d')
    else:
        open_date = "Unknown"
    swapText = f"""You Currently have {account_token_info['balance']['float']} {token_info['symbol']} in your wallet.\n
        💵Token Info:
        |---Symbol: {token_info['symbol']}
        |---Name: {token_info['name']}
        |---Price: {TokenInfo.convert_price_to_string(token_info['price'])}
        ------------------------------------
        🔍Pool Info:
        |---24H Volume: {TokenInfo.convert_volume_to_string(token_info['volume_24h'])}
        |---Token FDV: {TokenInfo.convert_volume_to_string(int(token_info['fdv']))}
        |---Token Liquidity: {TokenInfo.convert_volume_to_string(int(token_info['liquidity']))}
        |---Holder Count: {token_info['holder_count']}
        ------------------------------------
        |---Token MAX Supply: {TokenInfo.convert_volume_to_string(token_info['max_supply'])}
        |---Token Open Date: {open_date}
        ------------------------------------
        🔗Links:
        |--- [GMGN](https://gmgn.ai/sol/token/{token_address}) | [DexScreener](https://dexscreener.com/solana/{token_address}) | [Birdeye](https://dexscreener.com/solana/{token_address}) | [Dextools](https://www.dextools.io/app/cn/ether/pair-explorer/{token_address})
        """
        # Use the correct context to reply

    await message.answer(f"{swapText}", reply_markup=swap_menu_keyboard, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    await state.set_state(Form.buy_token) 


async def start_transaction(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = await get_user(user_id=userId)
    token_address = data.get("token_address")
    swapData = data.get("swapData")
    if userData.get("private_key") is None or token_address is None:
        await message.answer("Please set your wallet first", reply_markup=wallet_menu_keyboard)
    else:
        await message.edit_text(f"Starting Transaction for {swapData.get('amount')} {data.get('token_info')['symbol']} {swapData.get('action')}ing.......\nPlease Wait....")
        swapClient = Swap(RPC_URL, userData.get("private_key"))
        token_address = data.get("token_address")
        if swapData.get("action") == "buy":
            print("Buying")
            amount = float(swapData.get("amount"))
            slippage = userData.get("slippage")
            tansactionStatus,transactionId = await swapClient.swap_token(
                input_mint="So11111111111111111111111111111111111111112",
                output_mint=token_address,
                amount=amount,
                slippage_bps=slippage
            )
        elif swapData.get("action") == "sell":
            print("Selling")
            product = (float(swapData.get("amount")) * data.get("account_token_info")["balance"]["float"]) #rounding down to near 2 decimal places
            slippage = userData.get("slippage")
            rounded_down_product = math.floor(product * 100) / 100.0
            tansactionStatus,transactionId = await swapClient.swap_token(
                input_mint=token_address,
                output_mint="So11111111111111111111111111111111111111112",
                amount=float(rounded_down_product),
                slippage_bps=slippage
            )
        else:
            await message.answer("Invalid Action")
            await state.set_state(Form.start_menu)

        if tansactionStatus:
            await message.answer(f"TX ID:{transactionId}\nTransaction sent: [View on Solana Explorer](https://explorer.solana.com/tx/{transactionId})\n--------------\nNow Checking for Transaction Status", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,reply_markup=main_menu_keyboard)
            swap_status,swap_msg = await swapClient.swap_status(transactionId)
            if swap_status:
                await message.answer(f"Transaction SUCCESS! | [View on Solana Explorer](https://explorer.solana.com/tx/{transactionId})", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            else:
                await message.answer(f"Check Transaction Status FAILED! Please Retry. {swap_msg}",reply_markup=main_menu_keyboard)
        else:
            await message.answer(f"Transaction failed: {transactionId}",reply_markup=main_menu_keyboard)

    await state.set_state(Form.start_menu)   
    

async def buy_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    userId = data.get("userId")
    userData = await get_user(user_id=userId)
    if userData.get("private_key") == "":
        await message.edit_text("Please set your wallet first", reply_markup=go_back_button)
    else:
        await message.edit_text("Please Enter The Contract Address of the Token You Want to Buy")
        await state.set_state(Form.swap_menu)  # 假设这是等待输入购买代币地址的状态



async def wallet_menu(message: Message, state: FSMContext) -> None:
    await message.edit_text("Here is the Wallet Menu, Choose Your Option!", reply_markup=wallet_menu_keyboard)


async def main_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.start_menu)
    await message.edit_text("Hi there! Welcome to Lucas's Solana Trading Bot!", reply_markup=main_menu_keyboard)

async def swap_menu(message: Message, state: FSMContext) -> None:
    await buy_handler(message, state)

async def copy_trade_menu(message: Message, state: FSMContext) -> None:
    await message.edit_text("Here is the Copy Trade Menu, Choose Your Option!", reply_markup=copy_trade_menu_keyboard)

async def transaction_menu(message: Message, state: FSMContext) -> None:
    await message.edit_text("Here is the Transaction Menu, Choose Your Option!", reply_markup=transaction_menu_keyboard)

async def help_menu(message: Message, state: FSMContext) -> None:
    await message.edit_text("Here is the Help Menu, Choose Your Option!", reply_markup=help_menu_keyboard)

async def set_slippage(message: Message, state: FSMContext) -> None:
    await message.edit_text("Please enter your slippage tolerance? Enter a number \nFor Example 5%, Please Enter 5", reply_markup=go_back_button)
    await state.set_state(Form.set_slippage)  # 假设这是等待滑点输入的状态

@form_router.callback_query()
async def callback_query_handler(message: Message, state: FSMContext) -> None:
    button_message = message.data
    message = message.message
    if button_message == "wallet_menu":
        await wallet_menu(message, state) #show wallet menu
    elif button_message == "set_wallet":
        await set_wallet(message, state) #set wallet wait for private key
    elif button_message == "show_wallet":
        await show_wallet_data(message, state) #show wallet data
    elif button_message == "reset_wallet":
        await reset_wallet(message, state) #reset wallet data
    elif button_message == "main_menu":
        await main_menu(message, state) #show main menu
    elif button_message == "swap_menu":
        await swap_menu(message, state) #show swap menu
    elif button_message == "copy_trade_menu":
        await copy_trade_menu(message, state) #show copy trade menu
    elif button_message == "transaction_menu":
        await transaction_menu(message, state) #show transaction menu
    elif button_message == "help_menu":
        await help_menu(message, state) #show help menu
    elif button_message == "set_slippage":
        #call set_slippage function
        await set_slippage(message, state)
    elif button_message.startswith("buy_"):
        swapData = {
            "amount": float(button_message.split("_")[1]),
            "action": "buy"
        }
        print(swapData)
        await state.update_data(swapData=swapData)
        await start_transaction(message, state)
    elif button_message.startswith("sell_"):
        #call sell function
        swapData = {
            "amount": float(button_message.split("_")[1]),
            "action": "sell"
        }
        print(swapData)
        await state.update_data(swapData=swapData)
        await start_transaction(message, state)
    elif button_message == "view_follow_wallet":
        #call view_follow_wallet function
        await message.edit_text("Here is the Follow Wallet are: -> follow wallet data", reply_markup=copy_trade_menu_keyboard)
    elif button_message == "add_follow_wallet":
        #call add_follow_wallet function
        await message.edit_text("You have added follow wallet succesfully! -> follow wallet data", reply_markup=copy_trade_menu_keyboard)
    elif button_message == "remove_follow_wallet":
        #call remove_follow_wallet function
        await message.edit_text("You have removed follow wallet succesfully! -> follow wallet data", reply_markup=copy_trade_menu_keyboard)
    elif button_message == "view_last_transaction":
        #call view_last_transaction function
        await message.edit_text("Here is the Last Transaction are: -> transaction data", reply_markup=transaction_menu_keyboard)
    elif button_message == "view_last_10_transaction":
        #call view_last_10_transaction function
        await message.edit_text("Here is the Last 10 Transaction are: -> transaction data", reply_markup=transaction_menu_keyboard)    
    else:
        await message.edit_text(f"Unknown callback data: {button_message}")






async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())