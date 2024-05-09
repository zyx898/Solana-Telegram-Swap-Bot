import sqlite3
import aiosqlite
import asyncio



#create a error decorator
def error_decorator(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper


SCHEMA = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        wallet_address TEXT NOT NULL,
        private_key TEXT NOT NULL,
        trades TEXT NOT NULL,
        slippage INTEGER NOT NULL,
        monitor_wallet TEXT NOT NULL
    )
'''

@error_decorator
async def create_db_and_table():
    # Connect to the SQLite database. If it doesn't exist, it will be created.
    async with aiosqlite.connect('users.db') as db:
        # Corrected CREATE TABLE statement with the closing parenthesis
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                wallet_address TEXT NOT NULL,
                private_key TEXT NOT NULL,
                trades TEXT NOT NULL,
                slippage INTEGER NOT NULL,
                monitor_wallet TEXT NOT NULL
            )
        ''')
        
        # Commit the changes
        await db.commit()

    return True

@error_decorator
async def insert_user(user_id, wallet_address, private_key, trades, slippage, monitor_wallet):
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            INSERT INTO users (user_id, wallet_address, private_key, trades, slippage,monitor_wallet)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, wallet_address, private_key, trades, slippage, monitor_wallet))
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect('users.db') as db:
        # Change the row factory to dictionary
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM users WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        
        if row is not None:
            return dict(row)
        else:
            return None
        
@error_decorator
async def update_user(user_id, wallet_address=None, private_key=None, trades=None, slippage=None, monitor_wallet=None):
    async with aiosqlite.connect('users.db') as db:
        # Dictionary to hold the fields to update
        updates = {}
        if wallet_address is not None:
            updates['wallet_address'] = wallet_address
        if private_key is not None:
            updates['private_key'] = private_key
        if trades is not None:
            updates['trades'] = trades
        if slippage is not None:
            updates['slippage'] = slippage
        if monitor_wallet is not None:
            updates['monitor_wallet'] = monitor_wallet

        # Construct the SQL query dynamically
        if updates:
            update_clause = ', '.join(f"{key} = ?" for key in updates)
            sql_query = f"UPDATE users SET {update_clause} WHERE user_id = ?"
            values = list(updates.values()) + [user_id]

            await db.execute(sql_query, values)
            await db.commit()
        else:
            print("No updates specified.")

@error_decorator
async def get_all_users():
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute('''
            SELECT * FROM users
        ''')
        #return as a dictionary with user_id as key
        return {user['user_id']: user for user in await cursor.fetchall()}



def get_all_users():
    dbConnection = sqlite3.connect('users.db')
    cursor = dbConnection.cursor()
    cursor.execute('''
        SELECT * FROM users
    ''')
    #return as a dictionary with user_id as key
    #
    ALLUser ={}
    for user in cursor.fetchall():
        data = {
            'id': user[0],
            'user_id': user[1],
            'wallet_address': user[2],
            'private_key': user[3],
            'trades': user[4],
            'slippage': user[5],
            'monitor_wallet': user[6]
        }
        ALLUser[user[1]] = data
    dbConnection.close()
    return ALLUser


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.run(create_db_and_table())


