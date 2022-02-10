import pytest

# account fixtures
@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]

@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[1]

@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[2]

# our contract
@pytest.fixture(scope="module")
def playground(alice, TellorPlayground):
    yield TellorPlayground.deploy({"from": alice})

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    # isolate each module and test function
    pass
