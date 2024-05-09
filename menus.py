
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)




def make_main_menu_keyboard() -> None:
    wallet_btn = InlineKeyboardButton(text="Wallet", callback_data="wallet_menu")
    swap_btn = InlineKeyboardButton(text="Buy | Sell", callback_data="swap_menu")
    copy_trade_btn = InlineKeyboardButton(text="Copy Trade", callback_data="copy_trade_menu")
    transaction_menu_btn = InlineKeyboardButton(text="Transaction", callback_data="transaction_menu")
    help_btn = InlineKeyboardButton(text="Help", callback_data="help_menu")
    main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[[wallet_btn,swap_btn], [copy_trade_btn,transaction_menu_btn],[help_btn]])
    return main_menu_keyboard

def make_wallet_menu_keyboard() -> None:
    set_wallet_btn = InlineKeyboardButton(text="Set Wallet", callback_data="set_wallet")
    show_wallet_btn = InlineKeyboardButton(text="Show Wallets", callback_data="show_wallet")
    reset_wallet_btn = InlineKeyboardButton(text="Reset Wallet", callback_data="reset_wallet")
    main_menu_btn = InlineKeyboardButton(text="Main Menu", callback_data="main_menu")
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[[set_wallet_btn,show_wallet_btn], [reset_wallet_btn],[main_menu_btn]])
    return wallet_keyboard

def make_swap_menu_keyboard() -> None:
    buy_0_25_btn = InlineKeyboardButton(text="Buy 0.05 SoL", callback_data="buy_0.05")
    buy_0_5_btn = InlineKeyboardButton(text="Buy 0.1 SoL", callback_data="buy_0.1")
    buy_1_0_btn = InlineKeyboardButton(text="Buy 0.5 SoL", callback_data="buy_0.5")
    buy_option_btn = InlineKeyboardButton(text="Buy _ Sol", callback_data="buy_option")

    sell_0_25_btn = InlineKeyboardButton(text="Sell 25 %", callback_data="sell_0.25")
    sell_0_5_btn = InlineKeyboardButton(text="Sell 50 %", callback_data="sell_0.5")
    sell_1_0_btn = InlineKeyboardButton(text="Sell 100 %", callback_data="sell_1")
    sell_option_btn = InlineKeyboardButton(text="Sell _ %", callback_data="sell_option")

    set_slippage_btn = InlineKeyboardButton(text="Set Slippage", callback_data="set_slippage")
    main_menu_btn = InlineKeyboardButton(text="Main Menu", callback_data="main_menu")
    swap_keyboard = InlineKeyboardMarkup(inline_keyboard=[[buy_0_25_btn,buy_0_5_btn,buy_1_0_btn,buy_option_btn], [sell_0_25_btn,sell_0_5_btn,sell_1_0_btn,sell_option_btn],[set_slippage_btn],[main_menu_btn]])
    return swap_keyboard

def make_copy_trade_menu() -> None:
    view_follow_wallet_btn = InlineKeyboardButton(text="View Follow Wallet", callback_data="view_follow_wallet")
    add_follow_wallet_btn = InlineKeyboardButton(text="Add Follow Wallet", callback_data="add_follow_wallet")
    remove_follow_wallet_btn = InlineKeyboardButton(text="Remove Follow Wallet", callback_data="remove_follow_wallet")
    main_menu_btn = InlineKeyboardButton(text="Main Menu", callback_data="main_menu")
    copy_trade_keyboard = InlineKeyboardMarkup(inline_keyboard=[[view_follow_wallet_btn,add_follow_wallet_btn], [remove_follow_wallet_btn],[main_menu_btn]])
    return copy_trade_keyboard


def make_transaction_menu() -> None:
    view_last_transaction_btn = InlineKeyboardButton(text="View Last Transaction", callback_data="view_last_transaction")
    view_last_10_transaction_btn = InlineKeyboardButton(text="View Last 10 Transaction", callback_data="view_last_10_transaction")
    main_menu_btn = InlineKeyboardButton(text="Main Menu", callback_data="main_menu")
    transaction_keyboard = InlineKeyboardMarkup(inline_keyboard=[[view_last_transaction_btn,view_last_10_transaction_btn], [main_menu_btn]])
    return transaction_keyboard

def make_help_menu() -> None:
    main_menu_btn = InlineKeyboardButton(text="Main Menu", callback_data="main_menu")
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[[main_menu_btn]])
    return help_keyboard


def go_back_btn() -> None:
    go_back_btn = InlineKeyboardButton(text="Go Back", callback_data="main_menu")
    go_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[[go_back_btn]])
    return go_back_keyboard




go_back_button = go_back_btn()
main_menu_keyboard = make_main_menu_keyboard()
wallet_menu_keyboard = make_wallet_menu_keyboard()
swap_menu_keyboard = make_swap_menu_keyboard()
copy_trade_menu_keyboard = make_copy_trade_menu()
transaction_menu_keyboard = make_transaction_menu()
help_menu_keyboard = make_help_menu()
