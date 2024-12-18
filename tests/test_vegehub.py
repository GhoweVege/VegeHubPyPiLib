"""Basic tests for VegeHub package."""

import pytest
from aioresponses import aioresponses
from vegehub.vegehub import VegeHub  # Update import as necessary based on your project structure

IP_ADDR = "192.168.0.100"
UNIQUE_ID = "aabbccddeeff"
TEST_MAC = "AA:BB:CC:DD:EE:FF"
TEST_MAC_SHORT = "AABBCCDDEEFF"
NUM_CHANNELS = 4
NUM_ACTUATORS = 2
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
        "version": "5.1.2",
        "agenda": 1,
        "batt_v": 9.0,
        "num_vsens": 0,
        "is_ac": 0,
        "has_sd": 0,
        "on_ap": 0
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

        ret = await basic_hub.retrieve_mac_address()
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
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD)

        await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert basic_hub.info == HUB_INFO_PAYLOAD
        assert basic_hub.num_actuators == NUM_ACTUATORS
        assert basic_hub.num_sensors == NUM_CHANNELS
        assert basic_hub.is_ac == IS_AC


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

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200)

        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

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
                    status=200)

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=400)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=200)

        ret = await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert ret is False


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
                    })

        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get",
                    payload=HUB_INFO_PAYLOAD,
                    status=400)

        await basic_hub.setup(TEST_API_KEY, TEST_SERVER)

        assert basic_hub.info is None
        assert basic_hub.num_actuators is None
        assert basic_hub.num_sensors is None
        assert basic_hub.is_ac is None


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
    with pytest.raises(ConnectionError):
        with aioresponses() as mocked:
            mocked.post(f"http://{IP_ADDR}/api/actuators/set", status=400)

            await basic_hub.set_actuator(0, 0, 60)


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
    with pytest.raises(AttributeError):
        with aioresponses() as mocked:
            mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                       status=200,
                       payload={})

            await basic_hub.actuator_states()


@pytest.mark.asyncio
async def test_actuator_states_fail_connect(basic_hub):
    """Test the _request_update method sends the update request to the device."""
    with pytest.raises(ConnectionError):
        with aioresponses() as mocked:
            mocked.get(f"http://{IP_ADDR}/api/actuators/status",
                       status=400,
                       payload={})

            await basic_hub.actuator_states()


@pytest.mark.asyncio
async def test_add_get_entity(basic_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    basic_hub.entities["entity_id"] = {"dummy": "data"}
    entity = basic_hub.entities["entity_id"]
    assert entity.get("dummy") == "data"
