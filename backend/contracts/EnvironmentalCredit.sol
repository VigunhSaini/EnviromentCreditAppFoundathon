// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title EnvironmentalCredit
 * @dev ERC-721 token representing environmental credits on Sepolia testnet.
 *      - Only the contract owner (deployer/admin wallet) can mint credits.
 *      - Retired tokens are permanently locked and cannot be transferred.
 *      - Each token stores a reference to its off-chain project ID.
 */
contract EnvironmentalCredit is ERC721, Ownable {
    using Counters for Counters.Counter;

    // -----------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------

    Counters.Counter private _tokenIdCounter;

    /// @dev Maps tokenId → projectId (off-chain Supabase UUID stored as uint256 hash reference)
    mapping(uint256 => uint256) public tokenProject;

    /// @dev Maps tokenId → retired status
    mapping(uint256 => bool) private _retired;

    // -----------------------------------------------------------------------
    // Events
    // -----------------------------------------------------------------------

    event CreditMinted(address indexed to, uint256 indexed tokenId, uint256 indexed projectId);
    event CreditRetired(address indexed retiree, uint256 indexed tokenId);

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    constructor() ERC721("EnvironmentalCredit", "ECRD") Ownable(msg.sender) {}

    // -----------------------------------------------------------------------
    // Minting  (owner only)
    // -----------------------------------------------------------------------

    /**
     * @notice Mint a new environmental credit NFT.
     * @param to        Recipient wallet address.
     * @param projectId Off-chain project identifier.
     * @return tokenId  The newly minted token ID.
     */
    function mintCredit(address to, uint256 projectId)
        external
        onlyOwner
        returns (uint256 tokenId)
    {
        require(to != address(0), "EnvironmentalCredit: mint to zero address");

        _tokenIdCounter.increment();
        tokenId = _tokenIdCounter.current();

        _safeMint(to, tokenId);
        tokenProject[tokenId] = projectId;

        emit CreditMinted(to, tokenId, projectId);
    }

    // -----------------------------------------------------------------------
    // Retirement
    // -----------------------------------------------------------------------

    /**
     * @notice Permanently retire a credit. The caller must own the token.
     *         Retired tokens cannot be transferred.
     * @param tokenId Token to retire.
     */
    function retireCredit(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "EnvironmentalCredit: caller is not token owner");
        require(!_retired[tokenId], "EnvironmentalCredit: token already retired");

        _retired[tokenId] = true;
        emit CreditRetired(msg.sender, tokenId);
    }

    /**
     * @notice Check whether a token has been retired.
     * @param tokenId Token to query.
     * @return True if the token is retired.
     */
    function isRetired(uint256 tokenId) external view returns (bool) {
        // ownerOf reverts for non-existent tokens, giving us existence check for free
        ownerOf(tokenId);
        return _retired[tokenId];
    }

    // -----------------------------------------------------------------------
    // Transfer guard — block transfers of retired tokens
    // -----------------------------------------------------------------------

    /**
     * @dev Hook called before every token transfer (including mint / burn).
     *      Reverts if the token has been retired.
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal virtual override returns (address) {
        // Allow minting (from == address(0)) but block transfers of retired tokens
        address from = _ownerOf(tokenId);
        if (from != address(0) && _retired[tokenId]) {
            revert("EnvironmentalCredit: retired token cannot be transferred");
        }
        return super._update(to, tokenId, auth);
    }

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    /// @notice Returns the total number of tokens minted so far.
    function totalMinted() external view returns (uint256) {
        return _tokenIdCounter.current();
    }
}
