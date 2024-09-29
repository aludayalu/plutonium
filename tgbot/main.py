from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

app = Client("my_bot")

callbacks={}

def call_api(user_id):
    api_url = f"http://10.43.0.96:7777/get_telegram_account_info?telegram_id={user_id}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
        
def get_positions(user_id):
    api_url = f"http://10.43.0.96:7777/positions?telegram_id={user_id}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_main_menu(client, message):
    keyboard = [
        [InlineKeyboardButton("Balance", callback_data="balance"),
         InlineKeyboardButton("Positions", callback_data="positions")],
        [InlineKeyboardButton("Holdings", callback_data="holdings"),
         InlineKeyboardButton("Stake", callback_data="stake")],
        [InlineKeyboardButton("Send", callback_data="send"),
         InlineKeyboardButton("Recieve", callback_data="showkey")],
        [InlineKeyboardButton("Sell", callback_data="sell"),
         InlineKeyboardButton("Buy", callback_data="buy")],
        [InlineKeyboardButton("Long", callback_data="long"),
         InlineKeyboardButton("Short", callback_data="short")],
        [InlineKeyboardButton("Swap", callback_data="swap")] 

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text("Please select an action to proceed with. Every option is accompanied by a brief description of it when clicked.\n\nContact @aludayalu for support.", reply_markup=reply_markup)

@app.on_message(filters.command("start"))
def start(client, message):
    user_id = message.from_user.id
    data = call_api(user_id)

    if data and data.get("registered") == True:
        send_main_menu(client, message)
    else:
        print(data.get("url"))
        keyboard = [[InlineKeyboardButton("Register", url=data.get("url"))]]    

        reply_markup = InlineKeyboardMarkup(keyboard)
        message.reply_text("Welcome to the Plutonium Bot.\n\nExperience real market dynamics with leverage and advanced order types, including longs, shorts, and futures and options trading for each token on the platform. We offer starting liquidity and are 100% rug-safe, ensuring a secure trading environment. Our platform features quick trading capabilities, real-time candlestick charts, and extensive statistics.\n\n You are not registered. Please register by clicking the button below:", reply_markup=reply_markup)

@app.on_callback_query(filters.regex("balance"))
def balance(client, callback_query):
    user_id = callback_query.from_user.id
    balance_data = call_api(user_id)

    if balance_data:
        balance = balance_data.get("balance", "No balance found")
        callback_query.message.reply_text(f"This command shows your current balance.\n\nYour current balance is: `{balance}` GAS")
    else:
        callback_query.message.reply_text("Failed to fetch balance. Please try again.")
        
@app.on_callback_query(filters.regex("positions"))
def positions(client, callback_query):
    user_id = callback_query.from_user.id

    callback_query.answer()

    api_url = f"http://10.43.0.96:7777/holdings?telegram_id={user_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        holdings_data = response.json()
        if holdings_data:
            keyboard = [
                [InlineKeyboardButton(f"Show Positions for {holding['token']['name']}", callback_data=f"show_positions:{holding['token']['name']}")]
                for holding in holdings_data
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            callback_query.message.reply_text("This command shows all your current open positions.\nPlease a select a position from the menu below", reply_markup=reply_markup)
        else:
            callback_query.message.reply_text("No positions found.")
    else:
        callback_query.message.reply_text("Failed to fetch holdings. Please try again.")

@app.on_callback_query(filters.regex(r"show_positions:(\w+)"))
def show_positions(client, callback_query):
    user_id = callback_query.from_user.id
    token = callback_query.data.split(":")[1]  
    
    api_url = f"http://10.43.0.96:7777/positions?telegram_id={user_id}&token={token}"
    response = requests.get(api_url)

    if response.status_code == 200:
        positions_data = response.json()
        if positions_data:
            keyboard = [
                [InlineKeyboardButton(f"Close Position {pos['id']}", callback_data=f"close_position:{pos['id']},{pos['token']}")]
                for pos in positions_data
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            callback_query.message.reply_text(f"Select a position to close for {token}:", reply_markup=reply_markup)  
        else:
            callback_query.message.reply_text(f"No positions found for {token}.")
    else:
        callback_query.message.reply_text(f"Failed to fetch positions for {token}. Please try again.")


@app.on_callback_query(filters.regex(r"close_position:(\w+),(\w+)"))
def close_position(client, callback_query):
    user_id = callback_query.from_user.id
    position_id, token_id = callback_query.data.split(":")[1].split(",")

    api_url = f"http://10.43.0.96:7777/close_position?telegram_id={user_id}&id={position_id}&token={token_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        result_data = response.json()
        if result_data:
            callback_query.message.reply_text(f"Position closed successfully: {result_data}")
        else:
            callback_query.message.reply_text("Failed to close position. Please try again.")
    else:
        callback_query.message.reply_text("Failed to close position. Please try again.")


@app.on_callback_query(filters.regex("short"))
def short(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This command allows you to short a specific token.\n\nPlease enter the amount, leverage, and token in the format: &lt;amount&gt;, &lt;leverage&gt;, &lt;token&gt;.")
    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)
    def process_short(client, message):
        try:
            amount, leverage, token = message.text.split(",")
            api_url = f"http://10.43.0.96:7777/short?telegram_id={user_id}&amount={amount.strip()}&leverage={leverage.strip()}&token={token.strip()}"
            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                callback_query.message.reply_text(f"Short order placed successfully: {result_data}")
            else:
                callback_query.message.reply_text("Failed to place short order. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;amount&gt;, &lt;leverage&gt;, &lt;token&gt;.")
    callbacks[user_id]=process_short
@app.on_callback_query(filters.regex("long"))
def long_order(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This command allows you to long a specific token.\n\nPlease enter the amount, token, and leverage in the format: &lt;amount&gt;, &lt;leverage&gt;, &lt;token&gt;.")
    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)

    def process_long_order(client, message):
        try:
            amount, leverage, token = message.text.split(",")

            api_url = f"http://10.43.0.96:7777/long?telegram_id={user_id}&amount={amount.strip()}&token={token.strip()}&leverage={leverage.strip()}"

            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                if result_data:
                    callback_query.message.reply_text("Long order created successfully.")
                else:
                    callback_query.message.reply_text("Failed to create long order. Please try again.")
            else:
                callback_query.message.reply_text("Failed to create long order. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;amount&gt;, &lt;token&gt;, &lt;leverage&gt;.")
        except Exception as e:
            callback_query.message.reply_text(f"An error occurred: {str(e)}")
    callbacks[user_id]=process_long_order

    
@app.on_callback_query(filters.regex("holdings"))
def holdings(client, callback_query):
    user_id = callback_query.from_user.id
    api_url = f"http://10.43.0.96:7777/holdings?telegram_id={user_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        holdings_list = data
        if holdings_list:
            holdings_message = "\n".join([
                f"{holding['token']['name']} - `{holding['token']['hash']}`\n{holding['token']['name']} - {holding['amount']} {holding['token']['name']}"
                for holding in holdings_list
            ])
            callback_query.message.reply_text(f"This commands lists all the tokens you currently own.\n\nPlease find the list below:\n{holdings_message}")
        else:
            callback_query.message.reply_text("No holdings found.")
    else:
        callback_query.message.reply_text("Failed to fetch holdings. Please try again.")
        
@app.on_callback_query(filters.regex("stake"))
def stake(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This command allows you to stake a specific token.\n\nPlease enter the amount and token address of said token in the format: &lt;amount&gt;, &lt;token_addr&gt;.")
    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)

    def stake_amount_token(client, message):
        try:
            amount, token_addr, ttl = message.text.split(",")
            api_url = f"http://10.43.0.96:7777/stake?telegram_id={user_id}&amount={amount}&token={token_addr.strip()}&ttl={ttl.strip()}"
            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                callback_query.message.reply_text(f"Staking successful: {result_data}")
            else:
                callback_query.message.reply_text("Failed to stake. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;amount&gt;, &lt;token_addr&gt;.")
    callbacks[user_id]=stake_amount_token

@app.on_callback_query(filters.regex("swap"))  
def swap(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This command allows you to swap between two tokens.\n\nPlease enter the two token addresses and the swap amount in the format: &lt;token_addr1&gt;, &lt;token_addr2&gt;, &lt;swap_amount&gt;.")

    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)
    def swap_tokens(client, message):
        try:
            token_addr1, token_addr2, swap_amount = message.text.split(",")
            api_url = f"http://10.43.0.96:7777/swap_tokens?token1={token_addr1.strip()}&token2={token_addr2.strip()}&amount={swap_amount.strip()}"
            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                callback_query.message.reply_text(f"Swap successful: {result_data}")
            else:
                callback_query.message.reply_text("Failed to swap. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;token_addr1&gt;, &lt;token_addr2&gt;, &lt;swap_amount&gt;.")
    callbacks[user_id]=swap_tokens
@app.on_callback_query(filters.regex("showkey"))  
def showkey(client, callback_query):
    user_id = callback_query.from_user.id
    data = call_api(user_id)

    if data:
        privkey = data.get("private_key", "Private key not found")
        address = data.get("public_key", "Address not found")
        callback_query.message.reply_text(f"Private Key: {privkey}\nAddress: {address}")
    else:
        callback_query.message.reply_text("Failed to fetch keys. Please try again.")
        
@app.on_callback_query(filters.regex("send"))  
def send(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This allows you to send an amount of tokens to a specific address.\n\nPlease enter the recipient address, amount, and token hash in the format: &lt;addr&gt;, &lt;send_amount&gt;, &lt;token_hash&gt;.")

    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)
    def process_send(client, message):
        try:
            addr, send_amount, token_hash = message.text.split(",")
            api_url = f"http://10.43.0.96:7777/send?telegram_id={user_id}&addr={addr.strip()}&send_amount={send_amount.strip()}&token_hash={token_hash.strip()}"
            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                callback_query.message.reply_text(f"Send successful: {result_data}")
            else:
                callback_query.message.reply_text("Failed to send tokens. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;addr&gt;, &lt;send_amount&gt;, &lt;token_hash&gt;.")
    callbacks[user_id]=process_send
    
@app.on_callback_query(filters.regex("buy"))  
def buy(client, callback_query):
    user_id = callback_query.from_user.id
    callback_query.message.reply_text("This command allows you to buy a token using its hash.\n\nPlease enter the amount, and token hash in the format: &lt;addr&gt;, &lt;send_amount&gt;, &lt;token_hash&gt;.")

    @app.on_message(filters.private)
    def execute_latest_callback(client, message):
        callbacks[user_id](client, message)
    def process_buy(client, message):
        try:
            buy_amount , token_hash = message.text.split(",")
            api_url = f"http://10.43.0.96:7777/buy?telegram_id={user_id}&amount={buy_amount.strip()}&token={token_hash.strip()}"
            response = requests.get(api_url)

            if response.status_code == 200:
                result_data = response.json()
                callback_query.message.reply_text(f"Buy successful: {result_data}")
            else:
                callback_query.message.reply_text("Failed to buy tokens. Please try again.")
        except ValueError:
            callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;addr&gt;, &lt;send_amount&gt;, &lt;token_hash&gt;.")
    callbacks[user_id]=process_buy

@app.on_callback_query(filters.regex("sell"))
def sell(client, callback_query):
    user_id = callback_query.from_user.id

    api_url = f"http://10.43.0.96:7777/holdings?telegram_id={user_id}"
    response = requests.get(api_url)

    if response.status_code == 200:
        holdings = response.json()  
        buttons = [
            f"{token['token']['name']} ({token['token']['name']}): {token['amount']} available" for token in holdings
        ]
        
        callback_query.message.reply_text(
            "This command allows you to sell your currently held tokens.\n\nSelect a token to sell by entering the amount and token hash in the format: &lt;amount&gt;, &lt;token_hash&gt;.\nAvailable tokens:\n" + "\n".join(buttons)
        )
        
        @app.on_message(filters.private)
        def execute_latest_callback(client, message):
            callbacks[user_id](client, message)
        def process_sell(client, message):
            try:
                sell_amount, token_hash = message.text.split(",")

                sell_amount = float(sell_amount.strip())
                
                api_url = f"http://10.43.0.96:7777/holdings?telegram_id={user_id}"
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    holdings = response.json()
                    token = next((t for t in holdings if t['token']['hash'] == token_hash.strip()), None)

                    if token:
                        owned_amount = float(token['amount'])
                        if sell_amount > owned_amount:
                            callback_query.message.reply_text("You cannot sell more than you own.")
                            return
                        
                        api_url = f"http://10.43.0.96:7777/sell?telegram_id={user_id}&amount={sell_amount}&token={token_hash.strip()}"
                        
                        response = requests.get(api_url)

                        if response.status_code == 200:
                            result_data = response.json()
                            callback_query.message.reply_text(f"Sell successful: {result_data}")
                        else:
                            callback_query.message.reply_text("Failed to sell tokens. Please try again.")
                    else:
                        callback_query.message.reply_text(f"Token with hash {token_hash.strip()} not found.")
                else:
                    callback_query.message.reply_text("Failed to fetch your holdings. Please try again.")
            except ValueError:
                callback_query.message.reply_text("Invalid format. Please enter in the format: &lt;amount&gt;, &lt;token_hash&gt;.")
            except Exception as e:
                callback_query.message.reply_text(f"An error occurred: {str(e)}")
        callbacks[user_id]=process_sell
    else:
        callback_query.message.reply_text("Failed to fetch your holdings. Please try again.")

app.run()
