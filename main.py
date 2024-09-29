import contract, flask, litedb, json, uuid, threading, time
from flask import Flask, request, Response

app=Flask(__name__)
accounts=litedb.get_conn("accounts.db")
telegram_accounts=litedb.get_conn("telegram_accounts.db")
registration_tokens=litedb.get_conn("registration_tokens.db")
prices=litedb.get_conn("prices.db")

def make_response(a):
    if type(a) in [int, bool, dict, list]:
        a=json.dumps(a)
    resp=flask.Response(a)
    resp.headers["Access-Control-Allow-Origin"]="*"
    return resp

def event_listener():
    for event in contract.listen_for_events():
        x=event
        event=dict(event["args"])
        event["token_state"]=dict(event["token_state"])
        token_prices=prices.get(event["token_hash"])
        if token_prices==None:
            token_prices=[]
            prices.set(event["token_hash"], [])
        token_prices.append(event | {"time":time.time()})
        prices.set(event["token_hash"], token_prices)

threading.Thread(target=event_listener).start()

@app.get("/")
def main():
    return ""

@app.get("/get_telegram_account_info")
def get_telegram_account_info():
    args=dict(request.args)
    telegram_id=args["telegram_id"]
    result=telegram_accounts.get(telegram_id)
    if result==None:
        private_key, public_key=contract.create_account()
        uid=uuid.uuid4().__str__()
        registration_tokens.set(uid, telegram_id)
        user={"private_key":private_key, "public_key":str(public_key), "registered":False, "token":uid, "url":"http://10.43.0.105:5000/register?token="+uid, "username":""}
        telegram_accounts.set(telegram_id, private_key)
        accounts.set(private_key, user)
        result=user
    else:
        result=accounts.get(result)
    result=result|{"balance":float(contract.get_balance(result["public_key"]))}
    return make_response(result)

@app.get("/get_account_info")
def get_account_info():
    args=dict(request.args)
    result=accounts.get(args["private_key"])
    if result==None:
        return {"error":"account does not exist"}
    result=result|{"balance":float(contract.get_balance(result["public_key"]))}
    return make_response(result)

@app.get("/registration_token_info")
def registration_token_info():
    args=dict(request.args)
    token=args["token"]
    if registration_tokens.get(token)!=None:
        return make_response(True)
    else:
        return make_response(False)

@app.get("/submit_registration")
def submit_registration():
    args=dict(request.args)
    token=args["token"]
    result=registration_tokens.get(token)
    if result!=None:
        registration_tokens.delete(token)
        account=accounts.get(telegram_accounts.get(result))
        account["registered"]=True
        account["username"]=args["username"]
        accounts.set(telegram_accounts.get(result), account)
        return make_response(account)
    else:
        return make_response(False)

@app.get("/balance")
def account_balance():
    args=dict(request.args)
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    return make_response(str(float(contract.get_balance(account["public_key"]))))

@app.get("/buy")
def buy_token():
    args=dict(request.args)
    amount=float(args["amount"])
    token=args["token"]
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    signer=contract.w3.eth.account.from_key(private_key)
    try:
        contract.call_func("Buy_Token", [token], amount, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/sell")
def sell_token():
    args=dict(request.args)
    amount=int(float(args["amount"]))
    token=args["token"]
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    signer=contract.w3.eth.account.from_key(private_key)
    try:
        contract.call_func("Sell_Token", [token, amount, account["public_key"]], 0, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/long")
def long_order():
    args=dict(request.args)
    amount=int(float(args["amount"]))
    token=args["token"]
    leverage=int(args["leverage"])
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    signer=contract.w3.eth.account.from_key(private_key)
    try:
        contract.call_func("Create_Order", [token, amount, "long", 0, leverage], 0, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/short")
def short_order():
    args=dict(request.args)
    amount=int(float(args["amount"]))
    token=args["token"]
    leverage=int(args["leverage"])
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    signer=contract.w3.eth.account.from_key(private_key)
    try:
        contract.call_func("Create_Order", [token, amount, "short", 0, leverage], 0, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/stake")
def stake_order():
    args=dict(request.args)
    amount=int(float(args["amount"]))
    token=args["token"]
    ttl=int(args["ttl"])
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    signer=contract.w3.eth.account.from_key(private_key)
    try:
        contract.call_func("Create_Order", [token, amount, "stake", ttl, 1], 0, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/positions")
def get_positions():
    args=dict(request.args)
    token=args["token"]
    positions=contract.local_call("Get_Positions", [token])
    keys="id,position_type,amount,initial_state,time_to_live,owner,leverage,time".split(",")
    new_positions=[]
    for position in positions:
        temp=[]
        for i in range(len(position)):
            temp.append([keys[i], position[i]])
        new_positions.append(dict(temp))
    return make_response(new_positions)

@app.get("/close_position")
def close_position():
    args=dict(request.args)
    private_key=""
    id=args["id"]
    token=args["token"]
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    try:
        contract.call_func("Close_Order", [id, token], 0, signer, private_key)
        return make_response(True)
    except:
        return make_response(False)

@app.get("/holdings")
def holdings():
    args=dict(request.args)
    private_key=""
    if "telegram_id" in args:
        private_key=telegram_accounts.get(args["telegram_id"])
    else:
        private_key=args["private_key"]
    account=accounts.get(private_key)
    all_holdings=contract.local_call("Get_Holdings", [account["public_key"]])
    user_holdings=[]
    for holding in all_holdings:
        token_details=contract.local_call("Get_Token", [holding[1]])
        hash=token_details[1]
        token_details=token_details[2]
        token_details={"name":token_details[0], "icon_url":token_details[1], "description":token_details[3], "ticker":token_details[6], "hash":hash}
        user_holdings.append({"token":token_details, "amount":int(holding[2])})
    return make_response(user_holdings)

@app.get("/get_token_historical_data")
def get_token_historical_data():
    args=dict(request.args)
    token=args["token"]
    token_prices=prices.get(token)
    if token_prices==None:
        prices.set(token, [])
        token_prices=[]
    candles=[]
    times={}
    for event in token_prices:
        event["time"]=(event["time"] // 60) * 60
        if event["time"] not in times:
            times[event["time"]]={"time":event["time"], "open":event["token_state"]["liquidity"]/event["token_state"]["total_tokens"], "close":0, "high":0, "close":0, "trades":[]}
        times[event["time"]]["trades"].append(event)
    for timeslot in times:
        highest=0
        lowest=10**400
        times[timeslot]["close"]=times[timeslot]["trades"][-1]["token_state"]["liquidity"]/times[timeslot]["trades"][-1]["token_state"]["total_tokens"]
        for trade in times[timeslot]["trades"]:
            price=trade["token_state"]["liquidity"]/trade["token_state"]["total_tokens"]
            if price<lowest:
                lowest=price
            if price>highest:
                highest=price
        times[timeslot]["high"]=highest
        times[timeslot]["low"]=lowest
        candles.append(times[timeslot])
    return make_response(candles)

@app.get("/get_token_info")
def get_token_info():
    args=dict(request.args)
    token=args["token"]
    for x in contract.local_call("Get_All_Tokens"):
        if x[1]==token:
            return make_response(json.dumps(x))

@app.get("/tokens_web")
def tokens_web():
    args=dict(request.args)
    search=""
    if "search" in args:
        search=args["search"]
    all_tokens=[x for x in contract.local_call("Get_All_Tokens") if search.lower() in str(x).lower()]
    tokens=sorted(all_tokens, key=lambda x:x[-1], reverse=True)[:100]
    return make_response(tokens)

def event_stream(token_hash):
    token=token_hash
    token_prices=prices.get(token)
    if token_prices==None:
        prices.set(token, [])
        token_prices=[]
    last_length=len(token_prices)
    while True:
        time.sleep(1)
        token_prices=prices.get(token)
        if len(token_prices)>last_length:
            for x in token_prices[::-1][:len(token_prices)-last_length][::-1]:
                x["time"]=(x["time"]//60)*60
                yield f"data: {json.dumps(x)}\n\n"
            last_length=len(token_prices)

@app.get("/listen_for_price_updates")
def listening_for_price_updates():
    args=dict(request.args)
    resp=Response(event_stream(args["token"]), content_type="text/event-stream")
    resp.headers["Access-Control-Allow-Origin"]="*"
    return resp

@app.get("/all_user_balances")
def user_balances():
    args=dict(request.args)
    holdings={"eth":float(contract.get_balance(args["address"]))}
    for holding in contract.local_call("Get_Holdings", [args["address"]]):
        holdings[holding[1]]=holding[2]
    return make_response(holdings)

app.run(host="0.0.0.0", port=7777)