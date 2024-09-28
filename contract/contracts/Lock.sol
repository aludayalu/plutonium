pragma solidity ^0.8.27;

import "hardhat/console.sol";

contract Lock {
    Token[] tokens;

    uint256 base_liquidity=2*(10**9);

    mapping(address=>Holding[]) user_holdings;
    struct Holding {
        address user_address;
        string token_hash;
        uint256 amount;
    }

    struct Token {
        address owner;
        string token_hash; // sha256 hash
        string name;
        string ticker;
        string icon_url;
        string description;
        string telegram;
        string x_dot_com;
        string website_url;
        bool graduation;
        Token_State token_state;
        Position[] positions;
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

    function Create_Token(string memory name, string memory icon_url, string memory description, string memory telegram, string memory x, string memory website, string memory ticker) public returns (string memory) {
        string memory token_hash=Hash(string(abi.encodePacked(name, icon_url, description, telegram, x, website, ticker, msg.sender, block.number, msg.sig)));
        Token_State memory token_state=Token_State(10**9, base_liquidity);
        Position[] memory positions;
        Token memory token=Token(msg.sender, token_hash, name, ticker, icon_url, description, telegram, x, website, false, token_state, positions);
        tokens.push(token);
        return token_hash;
    }

    function Get_All_Tokens() public view returns (Token[] memory) {
        return tokens;
    }

    function Get_Holdings(address addr) public view returns (Holding[] memory) {
        return user_holdings[addr];
    }
    
    function Get_Token(string memory token_hash) public view returns (Token memory) {
        Token memory token;
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                token=tokens[i];
                index=i;
            }
        }
        return token;
    }

    function Buy_Token(string memory token_hash) payable public {
        uint256 amount_sent_native=(msg.value*99)/100;
        Token memory token;
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                token=tokens[i];
                index=i;
            }
        }
        require(found_token, "token not found");
        uint256 togive=((token.token_state.total_tokens*amount_sent_native)/(token.token_state.liquidity+amount_sent_native));
        togive=((token.token_state.total_tokens-togive)*amount_sent_native)/(token.token_state.liquidity+amount_sent_native);
        tokens[index].token_state.liquidity+=amount_sent_native;
        bool found_holding;
        uint holding_index;
        for (uint i = 0; i < user_holdings[msg.sender].length; i++) {
            if (keccak256(abi.encodePacked(user_holdings[msg.sender][i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_holding=true;
                holding_index=i;
            }
        }
        if (found_holding) {
            user_holdings[msg.sender][holding_index].amount+=togive;
        } else {
            user_holdings[msg.sender].push(Holding(msg.sender, token_hash, togive));
        }
    }

    function Sell_Token(string memory token_hash, uint256 amount, address payable caller_address) public {
        Token memory token;
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                token=tokens[i];
                index=i;
            }
        }
        require(found_token, "token not found");
        bool found_holding;
        uint holding_index;
        for (uint i = 0; i < user_holdings[msg.sender].length; i++) {
            if (keccak256(abi.encodePacked(user_holdings[msg.sender][i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_holding=true;
                holding_index=i;
            }
        }
        require(found_holding, "you must hold the token");
        require(user_holdings[msg.sender][holding_index].amount>=amount, "you cannot sell more than you own");
        uint256 togive_native=((token.token_state.liquidity*amount)/token.token_state.total_tokens);
        togive_native=(((token.token_state.liquidity-togive_native)*amount)/token.token_state.total_tokens);
        user_holdings[msg.sender][holding_index].amount-=amount;
        token.token_state.liquidity-=togive_native;
        caller_address.transfer(togive_native);
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
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                token=tokens[i];
                index=i;
            }
        }
        require(found_token, "token not found");
        bool found_holding;
        uint holding_index;
        for (uint i = 0; i < user_holdings[msg.sender].length; i++) {
            if (keccak256(abi.encodePacked(user_holdings[msg.sender][i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_holding=true;
                holding_index=i;
            }
        }
        require(found_holding, "you must hold the token");
        require(user_holdings[msg.sender][holding_index].amount>=amount, "you cannot use more of a token for opening positions than you own");
        Token_State memory token_state;
        token_state.liquidity=token.token_state.liquidity;
        token_state.total_tokens=token.token_state.total_tokens;
        user_holdings[msg.sender][holding_index].amount-=amount;
        tokens[index].positions.push(Position(Hash(string(abi.encodePacked(msg.sig, token_hash, amount, block.number))), order_type, amount, token_state, ttl, msg.sender, leverage, block.number));
    }

    function Close_Order(string memory order_id, string memory token_hash) public {
        Token memory token;
        bool found_token;
        uint index;
        for (uint i = 0; i < tokens.length; i++) {
            if (keccak256(abi.encodePacked(tokens[i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_token=true;
                token=tokens[i];
                index=i;
            }
        }
        require(found_token, "token not found");
        bool found_holding;
        uint holding_index;
        for (uint i = 0; i < user_holdings[msg.sender].length; i++) {
            if (keccak256(abi.encodePacked(user_holdings[msg.sender][i].token_hash))==keccak256(abi.encodePacked(token_hash))) {
                found_holding=true;
                holding_index=i;
            }
        }
        require(found_holding, "you must hold the token");
        bool found_position;
        uint position_index;
        Position memory position;
        for (uint i = 0; i < token.positions.length; i++) {
            if (keccak256(abi.encodePacked(token.positions[i].id))==keccak256(abi.encodePacked(order_id)) && token.positions[i].owner==msg.sender) {
                found_position=true;
                position_index=i;
                position=token.positions[i];
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
            int256 to_give=(int256(position.leverage)*percentage_changed*int256(position.amount))/(10**9);
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
            user_holdings[msg.sender][holding_index].amount+=to_give;
        }
    }
}