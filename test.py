import contract, time

print(contract.get_balance("0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"))

contract.call_func("Create_Token", [["joe mama", "-", "-", "-", "-", "x.com", "JOEMAMA"]])

print(contract.local_call("Get_All_Tokens"))

token_address=contract.local_call("Get_All_Tokens")[-1][1]

contract.call_func("Buy_Token", [token_address], 1)

print(contract.local_call("Get_All_Tokens")[-1][1])
token_address=contract.local_call("Get_All_Tokens")[-1][1]

print(contract.get_balance("0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"))

