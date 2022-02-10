import brownie
from brownie import ZERO_ADDRESS
import pytest

FAUCET_AMOUNT = 10 ** 21  # == 1000 * 10 ** 18


@pytest.fixture(autouse=True)
def setup(alice, playground):
    # local module setup
    playground.faucet(alice, {"from": alice})

    assert playground.totalSupply() == FAUCET_AMOUNT


def test_constructor(playground, web3):
    assert playground.name() == "TellorPlayground"
    assert playground.symbol() == "TRBP"
    assert playground.decimals() == 18
    assert playground.addresses(web3.keccak(text="_GOVERNANCE_CONTRACT")) == playground.address


def test_approve(alice, bob, playground):
    amount = 500 * 10 ** 18  # no need to use BigInt

    assert playground.balanceOf(alice) == FAUCET_AMOUNT
    assert playground.allowance(alice, bob) == 0

    # do interaction
    with brownie.reverts():
        # needs to be approved first
        playground.transferFrom(alice, bob, amount, {"from": bob})
    
    playground.approve(bob, amount, {"from": alice})
    assert playground.allowance(alice, bob) == amount

    playground.transferFrom(alice, bob, amount, {"from": bob})
    assert playground.balanceOf(alice) == FAUCET_AMOUNT - amount
    assert playground.balanceOf(bob) == amount

    with brownie.reverts():
        # approval to address(0)
        playground.approve(ZERO_ADDRESS, amount, {"from": alice})

def test_begin_dispure(alice, playground):
    # no need for a uint -> bytes helper, python int builtin method
    val = (1).to_bytes(32, "big")
    # the return of a modifying (external) method is a tx object
    tx = playground.submitValue(val, 150, 0, b"", {"from": alice})
    playground.beginDispute(val, tx.timestamp, {"from": alice})

    assert playground.isDisputed(val, tx.timestamp) is True


def test_transfer_balanceOf(alice, bob, playground):
    tx = playground.transfer(bob, 100 * 10 ** 18, {"from": alice})

    assert playground.balanceOf(alice) == FAUCET_AMOUNT - 100 * 10 ** 18
    assert playground.balanceOf(bob) == 100 * 10 ** 18

    # check proper events are emitted
    assert "Transfer" in tx.events
    assert tx.events["Transfer"].values() == [alice, bob, 100 * 10 ** 18]

@pytest.mark.xfail
def test_get_current_rewards(alice, chain, playground):
    # you can make contracts initiate transactions
    playground.faucet(playground, {"from": playground})

    # brownie will autoconvert int -> bytes32
    playground.tipQuery(1, 10 ** 18, b"", {"from": alice})
    tx = playground.submitValue(2, 150, 0, b"", {"from": alice})

    # advance rpc time by 10 minutes
    chain.sleep(10 * 60)

    curr_reward = playground.getCurrentReward(1)
    assert list(curr_reward) == [5 * 10 ** 18, 10 ** 18]


def test_submit_value(alice, playground, web3):
    with brownie.reverts():
        playground.submitValue(500, 150, 0, "0xabcd", {"from": alice})
    with brownie.reverts():
        playground.submitValue(1, 150, 1, b"", {"from": alice})
    
    playground.submitValue(1, 150, 1, b"", {"from": alice})
    ts = playground.getTimestampbyQueryIdandIndex(1, 0)
    assert playground.retrieveData(1, ts) - 150 == 0

    magic_h = web3.keccak(text="abracadabra")
    playground.submitValue(magic_h, b"houdini", 0, b"abracadabra", {"from": alice})
    ts = playground.getTimestampbyQueryIdandIndex(magic_h, 0)
    assert playground.retrieveData(magic_h, ts) == b"houdini"

