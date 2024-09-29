from flask import request, redirect, Response
from monster import render, tokeniser, parser, Flask, request
import sys, json, requests
import secrets_parser

main_api_url="http://10.43.0.96:7777"

secrets=secrets_parser.parse("variables.txt")

daisyui="<script>"+open("public/pako.js").read()+"</script>"+"""<script>
    function decompressGzippedString(base64String) {
        try {
            const binaryString = atob(base64String);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            const decompressedData = pako.inflate(bytes, { to: 'string' });
            return decompressedData;
        } catch (err) {
            console.error('An error occurred while decompressing the string:', err);
            return null;
        }
    }
    """+f"""
    var daisycss="{open("public/daisyui.b64").read()}";
    var style=document.createElement("style");
    style.textContent=decompressGzippedString(daisycss);
    document.head.appendChild(style);
    </script>
    """

tailwind="<script>"+open("public/tailwind.js").read()+"</script>"

app = Flask(__name__)

@app.get("/")
def home():
    if "private_key" not in request.cookies:
        return redirect("https://t.me/PlutoniumWalletBot")
    response=requests.get(main_api_url+"/get_account_info?private_key="+request.cookies["private_key"]).json()
    if "error" in response:
        return redirect("https://t.me/PlutoniumWalletBot")
    navbar = render("navbar", locals()|globals())
    return render("index", locals()|globals())

@app.get("/register")
def registration():
    response=requests.get(main_api_url+"/registration_token_info?token="+request.args["token"]).json()
    if response:
        navbar = render("navbar", locals()|globals())
        return render("registration", locals()|globals())
    else:
        return redirect("/")

@app.get("/submit_registration")
def submit_registration():
    response=requests.get(main_api_url+"/submit_registration?token="+request.args["token"]+"&username="+request.args["username"]).json()
    resp=redirect("/")
    resp.set_cookie("private_key", response["private_key"])
    resp.set_cookie("public_key", response["public_key"])
    return resp
    
@app.get("/swap")
def swap():
    if "private_key" not in request.cookies:
        return redirect("https://t.me/PlutoniumWalletBot")
    response=requests.get(main_api_url+"/get_account_info?private_key="+request.cookies["private_key"]).json()
    if "error" in response:
        return redirect("https://t.me/PlutoniumWalletBot")
    
    navbar = render("navbar", locals()|globals())
    return render("swap", locals()|globals())

@app.get("/token")
def token():
    if "private_key" not in request.cookies:
        return redirect("https://t.me/PlutoniumWalletBot")
    response=requests.get(main_api_url+"/get_account_info?private_key="+request.cookies["private_key"]).json()
    if "error" in response:
        return redirect("https://t.me/PlutoniumWalletBot")
    token_hash=request.args["token"]
    
    data=json.dumps(requests.get(main_api_url+"/get_token_historical_data?token="+token_hash).json())
    
    responseToken = requests.get(main_api_url+"/get_token_info?token="+request.args["token"]).json()

    tokenDetails = json.dumps(list(responseToken))

    navbar = render("navbar", locals()|globals())
    chart = render("chart", locals()|globals())

    return render("token", locals()|globals())

@app.get("/account")
def account():
    if "private_key" not in request.cookies:
        return redirect("https://t.me/PlutoniumWalletBot")
    response=requests.get(main_api_url+"/get_account_info?private_key="+request.cookies["private_key"]).json()
    if "error" in response:
        return redirect("https://t.me/PlutoniumWalletBot")
    
    responseAccBal = requests.get(main_api_url+"/balance?private_key="+response["private_key"]).json()
    responseHoldings = json.dumps(requests.get(main_api_url+"/holdings?private_key="+response["private_key"]+"&public_key="+response["public_key"]).json())

    navbar = render("navbar", locals()|globals())
    return render("account", locals()|globals())

app.run(host="0.0.0.0", port=int(sys.argv[1]))