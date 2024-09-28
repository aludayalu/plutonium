import requests
import json
import time
import web3
import secrets_parser

w3 = web3.Web3(web3.Web3.HTTPProvider("http://127.0.0.1:8545/"))

abi=json.loads(open("contract/artifacts/contracts/Lock.sol/Lock.json").read())["abi"]
private_key=secrets_parser.parse("variables.txt")["PRIVATE_KEY"]

account = w3.eth.account.from_key(private_key)

def get_contract_address():
    with open("contract.hash") as fd:
        return fd.read()

def call_func(name, args=[], eth=0):
    gwei=int(eth*(10**18))
    contract_address=get_contract_address()
    contract = w3.eth.contract(address=contract_address, abi=abi)
    tx_data={
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
        }
    if gwei!=0:
        tx_data["value"]=gwei
    call_function = getattr(contract.functions, name)(*args).build_transaction(
        tx_data
    )
    tx_create = w3.eth.account.sign_transaction(call_function, private_key)
    while True:
        try:
            tx_hash = w3.eth.send_raw_transaction(tx_create.raw_transaction)
            break
        except Exception as e:
            if web3.exceptions.TimeExhausted==type(e):
                return
            elif requests.exceptions.HTTPError==e:
                time.sleep(1)
                continue
            else:
                raise e
    while True:
        try:
            w3.eth.wait_for_transaction_receipt(tx_hash)
            break
        except Exception as e:
            if web3.exceptions.TimeExhausted==type(e):
                return
            elif requests.exceptions.HTTPError==e:
                time.sleep(1)
                continue
            else:
                raise e
    return tx_hash

def local_call(name, args=[]):
    contract_address=get_contract_address()
    contract = w3.eth.contract(address=contract_address, abi=abi)
    call_function = getattr(contract.functions, name)(*args).call({"from":account.address})
    return call_function

def get_balance(address=None):
    if address is None:
        address = account.address
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance_wei, 'ether')
    return balance_eth