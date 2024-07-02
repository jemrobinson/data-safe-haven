import pytest
import requests

from data_safe_haven.exceptions import DataSafeHavenValueError
from data_safe_haven.functions import current_ip_address, ip_address_in_list


class TestCurrentIpAddress:
    def test_current_ip_address(self, requests_mock):
        requests_mock.get("https://api.ipify.org", text="1.2.3.4")
        ip_address = current_ip_address()
        assert ip_address == "1.2.3.4"

    def test_current_ip_address_as_cidr(self, requests_mock):
        requests_mock.get("https://api.ipify.org", text="1.2.3.4")
        ip_address = current_ip_address(as_cidr=True)
        assert ip_address == "1.2.3.4/32"

    def test_current_ip_address_not_resolved(self, requests_mock):
        requests_mock.get(
            "https://api.ipify.org", exc=requests.exceptions.ConnectTimeout
        )
        with pytest.raises(DataSafeHavenValueError) as exc_info:
            current_ip_address()
        assert exc_info.match(r"Could not determine IP address.")


class TestIpAddressInList:
    def test_ip_address_is_in_list(self, requests_mock):
        requests_mock.get("https://api.ipify.org", text="1.2.3.4")
        assert ip_address_in_list(["1.2.3.4", "2.3.4.5"])

    def test_ip_address_is_not_in_list(self, requests_mock):
        requests_mock.get("https://api.ipify.org", text="1.2.3.4")
        assert not ip_address_in_list(["2.3.4.5"])

    def test_ip_address_not_resolved(self, requests_mock):
        requests_mock.get(
            "https://api.ipify.org", exc=requests.exceptions.ConnectTimeout
        )
        with pytest.raises(DataSafeHavenValueError) as exc_info:
            ip_address_in_list(["2.3.4.5"])
        assert exc_info.match(r"Could not determine IP address.")
