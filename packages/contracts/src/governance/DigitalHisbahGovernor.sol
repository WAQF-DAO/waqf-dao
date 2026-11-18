// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IERC20} from "../libraries/IERC20.sol";
import {SafeERC20} from "../libraries/SafeERC20.sol";
import {ReentrancyGuard} from "../libraries/ReentrancyGuard.sol";
import {IWaqfIdentitySBT, IWaqfPrincipalVault} from "../interfaces/IWaqfProtocol.sol";

/// @title DigitalHisbahGovernor
/// @notice Dual-Chamber DAO Governance combining SBT-gated quadratic voting (Chamber 1)
///         with a mandatory 21-day Shariah Supervisory Board review & veto gate (Chamber 2),
///         and Zero-Burn anti-spam deposit capture into WaqfPrincipalVault.
contract DigitalHisbahGovernor is AccessRoles, ReentrancyGuard {
    using SafeERC20 for IERC20;

    /// @notice Mandatory Chamber 2 SSB review clock: 21 days (1,814,400 seconds).
    uint256 public constant SSB_REVIEW_PERIOD = 21 days;
    uint256 public constant MIN_VOTING_PERIOD = 1 hours;
    uint256 public constant MAX_VOTING_PERIOD = 30 days;

    enum ProposalState {
        ACTIVE,
        DEFEATED,
        PENDING_SSB,
        SSB_APPROVED,
        VETOED,
        EXPIRED,
        EXECUTED
    }

    struct Proposal {
        uint256 id;
        address proposer;
        bytes32 targetPoolCode;
        address target;
        uint256 value;
        bytes callData;
        bytes32 descriptionHash;
        uint256 depositAmount;
        uint256 quorumSnapshot;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 createdAt;
        uint256 votingEnd;
        uint256 ssbDeadline;
        uint256 ssbApprovedAt;
        bool ssbApproved;
        bool ssbVetoed;
        bool executed;
        bool depositResolved;
        bool depositForfeited;
    }

    IWaqfIdentitySBT public immutable identitySBT;
    IWaqfPrincipalVault public immutable waqfVault;
    IERC20 public immutable reserveAsset;

    uint256 public votingPeriod;
    uint256 public proposalDeposit;
    uint256 public quorumWeight;
    uint256 public proposalCount;

    mapping(uint256 proposalId => Proposal) private _proposals;
    mapping(uint256 proposalId => mapping(address voter => bool)) public hasVoted;

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        bytes32 indexed targetPoolCode,
        address target,
        uint256 value,
        bytes32 descriptionHash,
        string description,
        uint256 depositAmount,
        uint256 votingEnd,
        uint256 ssbDeadline
    );
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalApprovedBySSB(uint256 indexed proposalId, address indexed ssbMember, uint256 approvedAt);
    event ProposalVetoedBySSB(
        uint256 indexed proposalId,
        address indexed ssbMember,
        bool isShariahViolationOrSpam,
        string reason
    );
    event ProposalExecuted(uint256 indexed proposalId, address indexed executor);
    event GovernanceDepositSeized(
        uint256 indexed proposalId,
        bytes32 indexed targetPoolCode,
        uint256 amount,
        string reason
    );
    event GovernanceDepositRefunded(uint256 indexed proposalId, address indexed proposer, uint256 amount);
    event GovernanceParamsUpdated(uint256 votingPeriod, uint256 proposalDeposit, uint256 quorumWeight);

    error UnauthorizedProposer(address account);
    error InvalidTargetPool(bytes32 poolCode);
    error EmptyDescription();
    error InvalidGovernanceParams();
    error ProposalNotFound(uint256 proposalId);
    error VotingNotActive(uint256 proposalId);
    error VotingStillActive(uint256 proposalId);
    error AlreadyVoted(uint256 proposalId, address voter);
    error NoVotingWeight(address voter);
    error ProposalDefeatedInChamber1(uint256 proposalId);
    error SSBReviewClockExpired(uint256 proposalId, uint256 deadline);
    error SSBApprovalRequired(uint256 proposalId);
    error ProposalAlreadyApprovedBySSB(uint256 proposalId);
    error ProposalAlreadyVetoed(uint256 proposalId);
    error ProposalAlreadyExecuted(uint256 proposalId);
    error DepositAlreadyResolved(uint256 proposalId);
    error DepositNotRefundableInCurrentState(uint256 proposalId, ProposalState currentState);
    error ProposalExecutionFailed(bytes returnData);

    constructor(
        address admin,
        address ssbMultisig,
        address identitySBTAddress,
        address waqfVaultAddress,
        uint256 initialVotingPeriod,
        uint256 initialProposalDeposit,
        uint256 initialQuorumWeight
    ) {
        if (
            admin == address(0) ||
            ssbMultisig == address(0) ||
            identitySBTAddress == address(0) ||
            waqfVaultAddress == address(0)
        ) {
            revert ZeroAddress();
        }

        identitySBT = IWaqfIdentitySBT(identitySBTAddress);
        waqfVault = IWaqfPrincipalVault(waqfVaultAddress);
        reserveAsset = IERC20(waqfVault.reserveAsset());

        _setRoleAdmin(SSB_ROLE, DEFAULT_ADMIN_ROLE);
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(SSB_ROLE, ssbMultisig);

        _setGovernanceParams(initialVotingPeriod, initialProposalDeposit, initialQuorumWeight);
    }

    receive() external payable {}

    /// @notice Updates governance parameters (admin or self-execution via Dual-Chamber proposal).
    function updateGovernanceParams(
        uint256 newVotingPeriod,
        uint256 newProposalDeposit,
        uint256 newQuorumWeight
    ) external {
        if (msg.sender != address(this) && !hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, DEFAULT_ADMIN_ROLE);
        }
        _setGovernanceParams(newVotingPeriod, newProposalDeposit, newQuorumWeight);
    }

    /// @notice Chamber 1: Creates an SBT-gated governance proposal backed by a refundable/seizable anti-spam deposit.
    function propose(
        bytes32 targetPoolCode,
        address target,
        uint256 value,
        bytes calldata callData,
        string calldata description
    ) external nonReentrant returns (uint256 proposalId) {
        if (!identitySBT.isCredentialActive(msg.sender) || identitySBT.getVotingWeight(msg.sender) == 0) {
            revert UnauthorizedProposer(msg.sender);
        }
        if (!waqfVault.poolExists(targetPoolCode)) revert InvalidTargetPool(targetPoolCode);
        if (target == address(0)) revert ZeroAddress();
        if (bytes(description).length == 0) revert EmptyDescription();

        uint256 deposit = proposalDeposit;
        proposalId = ++proposalCount;
        uint256 voteEnd = block.timestamp + votingPeriod;
        uint256 deadline = voteEnd + SSB_REVIEW_PERIOD;

        _proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            targetPoolCode: targetPoolCode,
            target: target,
            value: value,
            callData: callData,
            descriptionHash: keccak256(bytes(description)),
            depositAmount: deposit,
            quorumSnapshot: quorumWeight,
            forVotes: 0,
            againstVotes: 0,
            createdAt: block.timestamp,
            votingEnd: voteEnd,
            ssbDeadline: deadline,
            ssbApprovedAt: 0,
            ssbApproved: false,
            ssbVetoed: false,
            executed: false,
            depositResolved: false,
            depositForfeited: false
        });

        emit ProposalCreated(
            proposalId,
            msg.sender,
            targetPoolCode,
            target,
            value,
            keccak256(bytes(description)),
            description,
            deposit,
            voteEnd,
            deadline
        );

        reserveAsset.safeTransferFrom(msg.sender, address(this), deposit);
    }

    /// @notice Chamber 1: Casts a quadratic/capped SBT-weighted vote on an active proposal.
    function castVote(uint256 proposalId, bool support) external {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        if (state(proposalId) != ProposalState.ACTIVE) revert VotingNotActive(proposalId);
        if (hasVoted[proposalId][msg.sender]) revert AlreadyVoted(proposalId, msg.sender);

        uint256 weight = identitySBT.getVotingWeight(msg.sender);
        if (weight == 0) revert NoVotingWeight(msg.sender);

        hasVoted[proposalId][msg.sender] = true;
        Proposal storage p = _proposals[proposalId];
        if (support) {
            p.forVotes += weight;
        } else {
            p.againstVotes += weight;
        }

        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    /// @notice Chamber 2: Mandatory Shariah Supervisory Board sign-off within the 21-day review window.
    function approveBySSB(uint256 proposalId) external onlyRole(SSB_ROLE) {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        Proposal storage p = _proposals[proposalId];

        if (p.executed) revert ProposalAlreadyExecuted(proposalId);
        if (p.ssbVetoed) revert ProposalAlreadyVetoed(proposalId);
        if (p.ssbApproved) revert ProposalAlreadyApprovedBySSB(proposalId);
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp < p.votingEnd) revert VotingStillActive(proposalId);
        if (!_chamber1Passed(p)) revert ProposalDefeatedInChamber1(proposalId);
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > p.ssbDeadline) revert SSBReviewClockExpired(proposalId, p.ssbDeadline);

        p.ssbApproved = true;
        p.ssbApprovedAt = block.timestamp;

        emit ProposalApprovedBySSB(proposalId, msg.sender, block.timestamp);
    }

    /// @notice Chamber 2: Vetoes a proposal. If flagged for Shariah violation or spam, seizes the deposit
    ///         (Zero-Burn) straight into WaqfPrincipalVault Mu'abbad principal; otherwise refunds the proposer.
    function vetoBySSB(
        uint256 proposalId,
        bool isShariahViolationOrSpam,
        string calldata reason
    ) external nonReentrant onlyRole(SSB_ROLE) {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        Proposal storage p = _proposals[proposalId];

        if (p.executed) revert ProposalAlreadyExecuted(proposalId);
        if (p.ssbVetoed) revert ProposalAlreadyVetoed(proposalId);
        if (p.depositResolved) revert DepositAlreadyResolved(proposalId);

        p.ssbVetoed = true;
        p.ssbApproved = false;
        p.depositResolved = true;

        if (isShariahViolationOrSpam) {
            p.depositForfeited = true;
            emit GovernanceDepositSeized(proposalId, p.targetPoolCode, p.depositAmount, reason);
            emit ProposalVetoedBySSB(proposalId, msg.sender, true, reason);

            reserveAsset.forceApprove(address(waqfVault), p.depositAmount);
            // forge-lint: disable-next-line(reentrancy-no-eth)
            waqfVault.receiveSeizedGovernanceDeposit(p.targetPoolCode, p.depositAmount);
        } else {
            emit GovernanceDepositRefunded(proposalId, p.proposer, p.depositAmount);
            emit ProposalVetoedBySSB(proposalId, msg.sender, false, reason);

            reserveAsset.safeTransfer(p.proposer, p.depositAmount);
        }
    }

    /// @notice Executes a Dual-Chamber approved proposal and refunds the proposer's good-faith deposit.
    function executeProposal(uint256 proposalId) external nonReentrant {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        Proposal storage p = _proposals[proposalId];

        if (p.executed) revert ProposalAlreadyExecuted(proposalId);
        if (p.ssbVetoed) revert ProposalAlreadyVetoed(proposalId);
        if (!p.ssbApproved) {
            // forge-lint: disable-next-line(block-timestamp)
            if (block.timestamp >= p.votingEnd && _chamber1Passed(p) && block.timestamp > p.ssbDeadline) {
                revert SSBReviewClockExpired(proposalId, p.ssbDeadline);
            }
            revert SSBApprovalRequired(proposalId);
        }

        p.executed = true;
        emit ProposalExecuted(proposalId, msg.sender);

        if (!p.depositResolved) {
            p.depositResolved = true;
            emit GovernanceDepositRefunded(proposalId, p.proposer, p.depositAmount);
            reserveAsset.safeTransfer(p.proposer, p.depositAmount);
        }

        // forge-lint: disable-next-line(arbitrary-send-eth,reentrancy-eth)
        (bool success, bytes memory returnData) = p.target.call{value: p.value}(p.callData);
        if (!success) {
            revert ProposalExecutionFailed(returnData);
        }
    }

    /// @notice Refunds the anti-spam deposit for a good-faith proposal that was defeated or expired after 21 days.
    function claimDepositRefund(uint256 proposalId) external nonReentrant {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        Proposal storage p = _proposals[proposalId];

        if (p.depositResolved) revert DepositAlreadyResolved(proposalId);
        ProposalState currentState = state(proposalId);
        if (
            currentState != ProposalState.DEFEATED &&
            currentState != ProposalState.EXPIRED &&
            currentState != ProposalState.EXECUTED
        ) {
            revert DepositNotRefundableInCurrentState(proposalId, currentState);
        }

        p.depositResolved = true;
        emit GovernanceDepositRefunded(proposalId, p.proposer, p.depositAmount);
        reserveAsset.safeTransfer(p.proposer, p.depositAmount);
    }

    /// @notice Computes the deterministic lifecycle state of `proposalId`.
    function state(uint256 proposalId) public view returns (ProposalState) {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        Proposal storage p = _proposals[proposalId];

        if (p.executed) return ProposalState.EXECUTED;
        if (p.ssbVetoed) return ProposalState.VETOED;
        if (p.ssbApproved) return ProposalState.SSB_APPROVED;
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp < p.votingEnd) return ProposalState.ACTIVE;
        if (!_chamber1Passed(p)) return ProposalState.DEFEATED;
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp > p.ssbDeadline) return ProposalState.EXPIRED;
        return ProposalState.PENDING_SSB;
    }

    function getProposal(uint256 proposalId) external view returns (Proposal memory) {
        if (proposalId == 0 || proposalId > proposalCount) revert ProposalNotFound(proposalId);
        return _proposals[proposalId];
    }

    function _chamber1Passed(Proposal storage p) private view returns (bool) {
        return p.forVotes > p.againstVotes && (p.forVotes + p.againstVotes) >= p.quorumSnapshot;
    }

    function _setGovernanceParams(
        uint256 newVotingPeriod,
        uint256 newProposalDeposit,
        uint256 newQuorumWeight
    ) private {
        if (
            newVotingPeriod < MIN_VOTING_PERIOD ||
            newVotingPeriod > MAX_VOTING_PERIOD ||
            newProposalDeposit == 0 ||
            newQuorumWeight == 0
        ) {
            revert InvalidGovernanceParams();
        }
        votingPeriod = newVotingPeriod;
        proposalDeposit = newProposalDeposit;
        quorumWeight = newQuorumWeight;
        emit GovernanceParamsUpdated(newVotingPeriod, newProposalDeposit, newQuorumWeight);
    }
}
