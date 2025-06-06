"""Basic tests for VegeHub package."""

from unittest.mock import AsyncMock, patch, Mock

import aiohttp
import pytest
from aioresponses import aioresponses

from vegehub.vegehub import VegeHub

from aiohttp.client_exceptions import ClientConnectorError, ConnectionKey

IP_ADDR = "192.168.0.100"
UNIQUE_ID = "aabbccddeeff"
TEST_MAC = "AA:BB:CC:DD:EE:FF"
TEST_MAC_SHORT = "AABBCCDDEEFF"
NUM_CHANNELS = 4
NUM_ACTUATORS = 2
SW_VER = "3.4.5"
IS_AC = False
TEST_API_KEY = "1234567890ABCD"
TEST_SERVER = "http://example.com"
ACTUATOR_INFO_PAYLOAD = {
    "actuators": [{
        "slot": 0,
        "state": 0,
        "last_run": 1730911079,
        "next_window_start": 1730916000,
        "next_window_end": 1730916600,
        "cur_ma": 0,
        "typ_ma": 0,
        "error": 0
    }],
    "error":
    "success"
}
HUB_INFO_PAYLOAD = {
    "hub": {
        "first_boot": False,
        "page_updated": False,
        "error_message": 0,
        "num_channels": NUM_CHANNELS,
        "num_actuators": NUM_ACTUATORS,
        "version": SW_VER,
        "agenda": 1,
        "batt_v": 9.0,
        "num_vsens": 0,
        "is_ac": 0,
        "has_sd": 0,
        "on_ap": 0
    },
    "wifi": {
        "ssid": "YourWiFiName",
        "strength": "-29",
        "chan": "4",
        "ip": IP_ADDR,
        "status": "3",
        "mac_addr": TEST_MAC
    }
}
WIFI_INFO_PAYLOAD = {
    "wifi": {
        "ssid": "YourWiFiName",
        "strength": "-29",
        "chan": "4",
        "ip": IP_ADDR,
        "status": "3",
        "mac_addr": TEST_MAC
    }
}


@pytest.fixture(name="basic_hub")
def fixture_basic_hub():
    """Fixture for creating a VegeHub instance."""
    return VegeHub(ip_address=IP_ADDR, unique_id=UNIQUE_ID)


@pytest.mark.asyncio
async def test_retrieve_mac_address_success(basic_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=WIFI_INFO_PAYLOAD)
        assert IP_ADDR == basic_hub.ip_address

        ret = await basic_hub.retrieve_mac_address()
        assert ret is True
        assert basic_hub.mac_address == TEST_MAC_SHORT
        assert basic_hub.unique_id == UNIQUE_ID


@pytest.mark.asyncio
async def test_retrieve_mac_address_failure_response(basic_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=WIFI_INFO_PAYLOAD,
                    status=400)
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=WIFI_INFO_PAYLOAD,
                    status=400)
        # Note: This mock is repeated twice. aioresponses is supposed to be
        # able to let you set repeat=2 and then it only repeats that response
        # twice, but there appears to be a bug that means that if you use any
        # number of repeats, it will just repeat that response forever. So for
        # now, we are using two explicit post mocks, and then one that repeats
        # forever after that.
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload={},
                    status=200,
                    repeat=True)
        with pytest.raises(ConnectionError):
            await basic_hub.retrieve_mac_address(retries=1)
        ret = await basic_hub.retrieve_mac_address(retries=5)
        assert ret is False


@pytest.mark.asyncio
async def test_retrieve_mac_address_failure_data(basic_hub):
    """Test retrieve_mac_address handles failure to retrieve MAC address."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"wifi": {}})

        ret = await basic_hub.retrieve_mac_address()

        assert ret is False
        assert basic_hub.mac_address == ""


@pytest.mark.asyncio
async def test_setup_success(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={
                        "hub": {},
                        "api_key": TEST_API_KEY
                    })

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload=HUB_INFO_PAYLOAD)

        await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert basic_hub.info == HUB_INFO_PAYLOAD["hub"]
        assert basic_hub.num_actuators == NUM_ACTUATORS
        assert basic_hub.num_sensors == NUM_CHANNELS
        assert basic_hub.is_ac == IS_AC
        assert basic_hub.url == (f"http://{IP_ADDR}")
        assert basic_hub.sw_version == SW_VER


@pytest.mark.asyncio
async def test_setup_failure_config_get(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={
                        "hub": {},
                        "api_key": TEST_API_KEY
                    },
                    status=400)
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={
                        "hub": {},
                        "api_key": TEST_API_KEY
                    },
                    status=400)
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload=None,
                    status=200,
                    repeat=True)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200,
                    repeat=True)

        with pytest.raises(ConnectionError):
            ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=1)
        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=5)
        assert ret is False


@pytest.mark.asyncio
async def test_setup_failure_config_set(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={
                        "hub": {},
                        "api_key": TEST_API_KEY
                    },
                    status=200,
                    repeat=True)

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=400)
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=400)
        mocked.post(f"http://{IP_ADDR}/api/config/set",
                    status=200,
                    repeat=True)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200,
                    repeat=True)
        with pytest.raises(ConnectionError):
            ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=1)
        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=3)
        assert ret is True


@pytest.mark.asyncio
async def test_setup_failure_missing_api_key(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={"hub": {}})

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200)

        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert ret is False


@pytest.mark.asyncio
async def test_setup_failure_missing_hub(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={"api_key": TEST_API_KEY})

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200)

        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert ret is False


@pytest.mark.asyncio
async def test_setup_failure_no_info(basic_hub):
    """Test the setup method sends the correct API key and server address."""
    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get",
                    payload={
                        "hub": {},
                        "api_key": TEST_API_KEY
                    },
                    repeat=True)

        mocked.post(f"http://{IP_ADDR}/api/config/set",
                    status=200,
                    repeat=True)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=400)
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=400)
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=None,
                    status=200,
                    repeat=True)

        with pytest.raises(ConnectionError):
            await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=1)
        await basic_hub.setup(TEST_API_KEY, TEST_SERVER, retries=1)

        assert basic_hub.num_actuators is None
        assert basic_hub.num_sensors is None
        assert basic_hub.is_ac is None
        assert basic_hub.info is None
        assert basic_hub.sw_version is None


@pytest.mark.asyncio
async def test_request_update(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/update/send", status=200)

        await basic_hub.request_update()


@pytest.mark.asyncio
async def test_request_update_fail(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/update/send", status=400)
        with pytest.raises(ConnectionError):
            await basic_hub.request_update()


@pytest.mark.asyncio
async def test_set_actuator(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/actuators/set", status=200)

        ret = await basic_hub.set_actuator(0, 0, 60)

        assert ret is True


@pytest.mark.asyncio
async def test_set_actuator_fail(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/actuators/set", status=400)
        mocked.post(f"http://{IP_ADDR}/api/actuators/set", status=400)
        mocked.post(f"http://{IP_ADDR}/api/actuators/set", status=200)
        with pytest.raises(ConnectionError):
            await basic_hub.set_actuator(0, 0, 60, retries=1)
        ret = await basic_hub.set_actuator(0, 0, 60, retries=1)
        assert ret is True


@pytest.mark.asyncio
async def test_actuator_states(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                   status=200,
                   payload=ACTUATOR_INFO_PAYLOAD)

        ret = await basic_hub.actuator_states()

        assert ret[0]["state"] is 0


@pytest.mark.asyncio
async def test_actuator_states_fail(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                   status=400,
                   payload={})
        mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                   status=400,
                   payload={})
        mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                   status=200,
                   payload={})
        with pytest.raises(ConnectionError):
            await basic_hub.actuator_states(retries=1)
        with pytest.raises(AttributeError):
            await basic_hub.actuator_states(retries=1)


@pytest.mark.asyncio
async def test_add_get_entity(basic_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    basic_hub.entities["entity_id"] = {"dummy": "data"}
    entity = basic_hub.entities["entity_id"]
    assert entity.get("dummy") == "data"


@pytest.mark.asyncio
async def test_request_update_client_connector_error_fail(basic_hub):
    """Test the _request_update method handles a connection failure properly."""
    with patch("aiohttp.ClientSession.get",
               new_callable=AsyncMock) as mock_get:
        key = Mock()
        os_error = OSError("Connection failed")
        mock_get.side_effect = ClientConnectorError(connection_key=key,
                                                    os_error=os_error)
        with pytest.raises(ConnectionError):
            await basic_hub.request_update()


@pytest.mark.asyncio
async def test_request_mac_client_connector_error_fail(basic_hub):
    """Test the _request_update method handles a connection failure properly."""
    with patch("aiohttp.ClientSession.get",
               new_callable=AsyncMock) as mock_get:
        key = Mock()
        os_error = OSError("Connection failed")
        mock_get.side_effect = ClientConnectorError(connection_key=key,
                                                    os_error=os_error)
        with pytest.raises(ConnectionError):
            await basic_hub.retrieve_mac_address()


@pytest.mark.asyncio
async def test_set_actuator_client_connector_error_fail(basic_hub):
    """Test the _request_update method handles a connection failure properly."""
    with patch("aiohttp.ClientSession.get",
               new_callable=AsyncMock) as mock_get:
        key = Mock()
        os_error = OSError("Connection failed")
        mock_get.side_effect = ClientConnectorError(connection_key=key,
                                                    os_error=os_error)
        with pytest.raises(ConnectionError):
            await basic_hub.set_actuator(0, 0, 60, retries=1)


@pytest.mark.asyncio
async def test_get_actuator_client_connector_error_fail(basic_hub):
    """Test the _request_update method handles a connection failure properly."""
    with patch("aiohttp.ClientSession.get",
               new_callable=AsyncMock) as mock_get:
        key = Mock()
        os_error = OSError("Connection failed")
        mock_get.side_effect = ClientConnectorError(connection_key=key,
                                                    os_error=os_error)
        with pytest.raises(ConnectionError):
            await basic_hub.actuator_states(retries=1)
