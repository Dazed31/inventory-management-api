from unittest.mock import patch, MagicMock
import requests
from external_api import fetch_product_by_barcode, fetch_product_by_name


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": 1,
        "product": {"product_name": "Test Product", "brands": "Test Brand"}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_product_by_barcode("1234567890123")
    assert result["product_name"] == "Test Product"


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": 0}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_product_by_barcode("0000000000000")
    assert result is None


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_request_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Network down")

    result = fetch_product_by_barcode("1234567890123")
    assert "error" in result


@patch("external_api.requests.get")
def test_fetch_product_by_name_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "products": [
            {"product_name": "Almond Milk", "brands": "Silk", "code": "123", "ingredients_text": "almonds, water"}
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_product_by_name("almond milk")
    assert len(result) == 1
    assert result[0]["product_name"] == "Almond Milk"


@patch("external_api.requests.get")
def test_fetch_product_by_name_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"products": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_product_by_name("nonexistent product xyz")
    assert result is None