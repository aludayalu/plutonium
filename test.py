import contract, time, threading

def event_listener():
    for event in contract.listen_for_events():
        print(event)

threading.Thread(target=event_listener).start()

print("Balance:", contract.get_balance("0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"))

contract.call_func("Create_Token", [["saut lagani hai", "https://i1.sndcdn.com/artworks-000237541959-i52bbu-t500x500.jpg", "bolna aunty au kya? Ghanti mein bajau kya?", "-", "-", "x.com", "BOLNA"]])

print(len(contract.local_call("Get_All_Tokens")))

# print(contract.local_call("Get_All_Tokens"))

# token_address=contract.local_call("Get_All_Tokens")[-1][1]

# contract.call_func("Buy_Token", [token_address], 0.01)

# print(contract.local_call("Get_All_Tokens")[-1][1])
# token_address=contract.local_call("Get_All_Tokens")[-1][1]

# print("Balance:", contract.get_balance("0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"))

# holding_amount=contract.local_call("Get_Holdings", ["0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])[-1][-1]

# print(contract.local_call("Get_Holdings", ["0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])[-1][-1])

# contract.call_func("Swap_Tokens", [token_address, token_address, holding_amount, "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])

# print(contract.local_call("Get_Holdings", ["0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])[-1][-1])

# contract.call_func("Create_Order", [token_address, holding_amount, "long", 0, 1])

# print("Holding:", contract.local_call("Get_Holdings", ["0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])[-1][-1])

# print(contract.local_call("Get_Positions", [token_address]))

# position_id=contract.local_call("Get_Positions", [token_address])[-1][0]

# contract.call_func("Buy_Token", [token_address], 1)

# contract.call_func("Close_Order", [position_id, token_address])

# print(contract.local_call("Get_Holdings", ["0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"])[-1][-1])