pragma solidity ^0.8.27;

import "hardhat/console.sol";

contract Lock {
    Token[] tokens;

    uint256 base_liquidity=2*(10**18);

    mapping(address=>Holding[]) user_holdings;
    struct Holding {
        address user_address;
        string token_hash;
        uint256 amount;
    }
    mapping(string=>Position[]) token_hash_positions;

    function Get_Positions(string memory token_hash) public returns (Position[] memory) {
        return token_hash_positions[token_hash];
    }

    struct Token {
        address owner;
        string token_hash; // sha256 hash
        Token_Metadata metadata;
        bool graduation;
        Token_State token_state;
    }

    struct Token_State {
        uint256 total_tokens;
        uint256 liquidity;
    }

    struct Position {
        string id;
        string position_type;
        uint256 amount;
        Token_State initial_state;
        uint256 time_to_live;
        address owner;
        int leverage;
        uint256 time;
    }

    string[] private possible_types;
    mapping(uint256=>uint256) private stake_maps_percent;

    constructor() {
        possible_types.push("long");
        possible_types.push("short");
        possible_types.push("stake");
        stake_maps_percent[100]=2;
        stake_maps_percent[1000]=11;
    }

    function Hash(string memory a) public pure returns (string memory) {
        return bytes32ToString(keccak256(abi.encodePacked(a)));
    }

    function bytes32ToString(bytes32 _bytes) public pure returns (string memory) {
        bytes memory hexChars = "0123456789abcdef";
        bytes memory str = new bytes(64);
        for (uint256 i = 0; i < 32; i++) {
            uint8 byteValue = uint8(_bytes[i]);
            str[i * 2] = hexChars[byteValue >> 4];
            str[i * 2 + 1] = hexChars[byteValue & 0x0f];
        }
        return string(str);
    }

    struct Token_Metadata {
        string name;
        string icon_url;
        string description;
        string telegram;
        string x;
        string website;
        string ticker;
    }

    function Create_Token(Token_Metadata memory token_metadata) public returns (string memory) {
        string memory token_hash = Hash(string(abi.encodePacked(msg.sender, block.number, msg.sig)));
        tokens.push(Token(msg.sender, token_hash, token_metadata, false, Token_State(10**9, base_liquidity)));
        return token_hash;
    }

    function Get_All_Tokens() public view returns (Token[] memory) {
        return tokens;
    }

    function Get_Holdings(address addr) public view returns (Holding[] memory) {
        return user_holdings[addr];
    }
    
    function Get_Token(string memory token_hash) public view returns (Token memory) {
        return tokens[find_token(token_hash)];
    }

    function find_token(string memory token_hash) private view returns (uint) {
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                index=i;
            }
        }
        require(found_token, "token not found");
        return index;
    }

    function find_holding(string memory token_hash, address person) private view returns (uint, bool) {
        bool found_holding;
        uint holding_index;
        for (uint i = 0; i < user_holdings[person].length; i++) {
            if (keccak256(abi.encodePacked(user_holdings[person][i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_holding=true;
                holding_index=i;
            }
        }
        return (holding_index, found_holding);
    }

    function Buy_Token(string memory token_hash) payable public {
        uint256 amount_sent_native=(msg.value*99)/100;
        Buy_Private(msg.sender, amount_sent_native, token_hash);
    }

    function Buy_Private(address person, uint256 amount_sent_native, string memory token_hash) private {
        Token memory token;
        uint index=find_token(token_hash);
        token=tokens[index];
        uint256 togive=((token.token_state.total_tokens*amount_sent_native)/(token.token_state.liquidity+amount_sent_native));
        tokens[index].token_state.liquidity+=amount_sent_native;
        tokens[index].token_state.total_tokens-=togive;
        bool found_holding; 
        uint holding_index;
        (holding_index, found_holding)=find_holding(token_hash, person);
        if (found_holding) {
            user_holdings[person][holding_index].amount+=togive;
        } else {
            user_holdings[person].push(Holding(person, token_hash, togive));
        }
    }

    function Sell_Token_Private(string memory token_hash, uint256 amount) private returns (uint256) {
        Token memory token;
        uint index=find_token(token_hash);
        token=tokens[index];
        bool found_holding;
        uint holding_index;
        (holding_index, found_holding)=find_holding(token_hash, msg.sender);
        require(found_holding, "you must hold the token");
        require(user_holdings[msg.sender][holding_index].amount>=amount, "you cannot sell more than you own");
        uint256 togive_native=((token.token_state.liquidity*amount)/(token.token_state.total_tokens+amount));
        user_holdings[msg.sender][holding_index].amount-=amount;
        tokens[index].token_state.total_tokens+=amount;
        token.token_state.liquidity-=togive_native;
        return togive_native;
    }

    function Sell_Token(string memory token_hash, uint256 amount, address payable caller_address) public {
        caller_address.transfer(Sell_Token_Private(token_hash, amount));
    }

    function contains_string(string[] memory array, string memory value) public pure returns (bool) {
        for (uint i = 0; i < array.length; i++) {
            if (keccak256(abi.encodePacked(array[i])) == keccak256(abi.encodePacked(value))) {
                return true;
            }
        }
        return false;
    }

    function contains_uint256(uint256[] memory array, uint256 value) public pure returns (bool) {
        for (uint i = 0; i < array.length; i++) {
            if (array[i]==value) {
                return true;
            }
        }
        return false;
    }

    function Create_Order(string memory token_hash, uint256 amount, string memory order_type, uint256 ttl, int256 leverage) public {
        require(leverage<=5 && leverage>=1, "invalid leverage multiplier amount");
        require(contains_string(possible_types, order_type), "not a possible order type");
        Token memory token;
        uint index=find_token(token_hash);
        token=tokens[index];
        bool found_holding;
        uint holding_index;
        (holding_index, found_holding)=find_holding(token_hash, msg.sender);
        require(found_holding, "you must hold the token");
        require(user_holdings[msg.sender][holding_index].amount>=amount, "you cannot use more of a token for opening positions than you own");
        Token_State memory token_state;
        token_state.liquidity=token.token_state.liquidity;
        token_state.total_tokens=token.token_state.total_tokens;
        user_holdings[msg.sender][holding_index].amount-=amount;
        token_hash_positions[tokens[index].token_hash].push(Position(Hash(string(abi.encodePacked(msg.sig, token_hash, amount, block.number))), order_type, amount, token_state, ttl, msg.sender, leverage, block.number));
    }

    function Close_Order(string memory order_id, string memory token_hash) public {
        Token memory token;
        uint index=find_token(token_hash);
        token=tokens[index];
        bool found_holding;
        uint holding_index;
        (holding_index, found_holding)=find_holding(token_hash, msg.sender);
        require(found_holding, "you must hold the token");
        bool found_position;
        uint position_index;
        Position memory position;
        for (uint i = 0; i < token_hash_positions[token.token_hash].length; i++) {
            if (keccak256(abi.encodePacked(token_hash_positions[token.token_hash][i].id))==keccak256(abi.encodePacked(order_id)) && token_hash_positions[token.token_hash][i].owner==msg.sender) {
                found_position=true;
                position_index=i;
                position=token_hash_positions[token.token_hash][i];
            }
        }
        require(found_position, "position with id not found");
        if (keccak256(abi.encodePacked(position.position_type))==keccak256(abi.encodePacked("long")) || keccak256(abi.encodePacked(position.position_type))==keccak256(abi.encodePacked("short"))) {
            int256 initial_price=(int256(position.initial_state.liquidity)*(10**9))/int256(position.initial_state.total_tokens);
            int256 final_price=(int256(token.token_state.liquidity)*(10**9))/int256(token.token_state.total_tokens);
            int256 percentage_changed;
            if (keccak256(abi.encodePacked(position.position_type))==keccak256(abi.encodePacked("long"))) {
                percentage_changed=int256(((final_price-initial_price)*(10**9))/initial_price);
            } else {
                percentage_changed=int256((((final_price-initial_price)*(10**9))/initial_price)*-1);
            }
            int256 to_give=(int256(position.leverage)*percentage_changed*int256(position.amount))/(10**11);
            int256 final_amount=int256(position.amount)+to_give+int256(user_holdings[msg.sender][holding_index].amount);
            if (final_amount<0) {
                final_amount=0;
            }
            tokens[index].token_state.total_tokens=uint256(int256(tokens[index].token_state.total_tokens)+to_give);
            user_holdings[msg.sender][holding_index].amount=uint256(final_amount);
        } else {
            require(block.number>=(position.time_to_live+position.time), "cannot unstake before time to live is over for the position");
            uint256 to_give=(position.amount*stake_maps_percent[position.time_to_live])/100;
            tokens[index].token_state.total_tokens=tokens[index].token_state.total_tokens+to_give;
            user_holdings[msg.sender][holding_index].amount+=position.amount+to_give;
        }
        Position storage temp_var=token_hash_positions[token.token_hash][token_hash_positions[token.token_hash].length-1];
        token_hash_positions[token.token_hash][token_hash_positions[token.token_hash].length-1]=token_hash_positions[token.token_hash][position_index];
        token_hash_positions[token.token_hash][position_index]=temp_var;
        token_hash_positions[token.token_hash].pop();
    }

    function Send_Token(string memory token_hash, uint256 amount, address other_address) public {
        Token memory token;
        uint index=find_token(token_hash);
        token=tokens[index];
        bool found_holding; 
        uint holding_index;
        (holding_index, found_holding)=find_holding(token_hash, msg.sender);
        require(found_holding, "you must hold to send");
        require(user_holdings[msg.sender][holding_index].amount>=amount, "cannot use more of a token than you have");
        bool found2_holding; 
        uint holding2_index;
        (holding2_index, found2_holding)=find_holding(token_hash, other_address);
        user_holdings[msg.sender][holding_index].amount-=amount;
        if (found2_holding) {
            user_holdings[other_address][holding_index].amount+=amount;
        } else {
            user_holdings[other_address].push(Holding(other_address, token_hash, amount));
        }
    }

    function Swap_Tokens(string memory token1_hash, string memory token2_hash, uint256 amount) public {
        uint256 net_balance=Sell_Token_Private(token1_hash, amount);
        console.log(net_balance);
        Buy_Private(msg.sender, net_balance, token2_hash);
    }
}