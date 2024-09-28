pragma solidity ^0.8.27;

import "hardhat/console.sol";

contract Lock {
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
        mapping (address=>int64) owners;
        Token_State token_state;
    }
    struct Token_State {
        int64 total_tokens;
        int64 liquidity;
    }
    struct Position {
        string position_type;
        int64 amount;
        Token_State initial_state;
        int64 time_to_live;
        address owner;
    }
}