// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title pay212 (P212) — BEP-20 token for BNB Smart Chain (chainId 56)
/// @notice Fixed supply: 1,000,000,000 P212, minted once to the deployer.
///         No mint, no tax, no blacklist, no owner powers — simple and trustless.
contract Pay212 is ERC20 {
    constructor() ERC20("pay212", "P212") {
        _mint(msg.sender, 1_000_000_000 * 10 ** decimals()); // decimals() = 18
    }
}
