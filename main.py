import contract, flask, litedb, json, uuid
from flask import Flask, request

app=Flask(__name__)
accounts=litedb.get_conn("accounts.db")
telegram_accounts=litedb.get_conn("telegram_accounts.db")
registration_tokens=litedb.get_conn("registration_tokens.db")

def make_response(a):
    if type(a) in [int, bool, dict, list]:
        a=json.dumps(a)
    resp=flask.Response(a)
    resp.headers["Access-Control-Allow-Origin"]="*"
    return resp

def event_listener():
    for event in contract.listen_for_events():
        print(event)

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
    result=result|{"balance":contract.get_balance(result["public_key"])}
    return make_response(result)

@app.get("/get_account_info")
def get_account_info():
    args=dict(request.args)
    result=accounts.get(args["private_key"])
    if result==None:
        return {"error":"account does not exist"}
    result=result|{"balance":contract.get_balance(result["public_key"])}
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

app.run(host="0.0.0.0", port=7777)