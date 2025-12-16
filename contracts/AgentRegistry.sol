// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title AgentRegistry - registra agenti "trusted"
contract AgentRegistry {
    address public owner;
    mapping(address => bool) private trusted;

    event AgentRegistered(address indexed agent, address indexed registrant);
    event AgentRevoked(address indexed agent, address indexed registrant);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Registrare un agent come trusted (solo owner)
    function registerAgent(address agent) external onlyOwner {
        trusted[agent] = true;
        emit AgentRegistered(agent, msg.sender);
    }

    /// @notice Revocare un agent (solo owner)
    function revokeAgent(address agent) external onlyOwner {
        trusted[agent] = false;
        emit AgentRevoked(agent, msg.sender);
    }

    /// @notice Verifica se un agent è trusted
    function isTrusted(address agent) external view returns (bool) {
        return trusted[agent];
    }
}
