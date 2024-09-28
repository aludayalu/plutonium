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

    function Create_Token(string memory name, string memory icon_url, string memory description, string memory telegram, string memory x, string memory website, string memory ticker) public {
        string memory token_hash=Hash(string(abi.encodePacked(name, icon_url, description, telegram, x, website, ticker, msg.sender, block.number)));
        Token_State memory token_state=Token_State(10**9, base_liquidity);
        Token memory token=Token(msg.sender, token_hash, name, ticker, icon_url, description, telegram, x, website, false, token_state);
        tokens.push(token);
    }

    function Get_All_Tokens() public view returns (Token[] memory) {
        return tokens;
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
        token.token_state.total_tokens-=togive;
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
        token.token_state.total_tokens+=amount;
        togive_native=(((token.token_state.liquidity*amount)-togive_native)/token.token_state.total_tokens);
        user_holdings[msg.sender][holding_index].amount-=amount;
        token.token_state.liquidity-=togive_native;
        caller_address.transfer(togive_native);
    }
}