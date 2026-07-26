import pytest
from unittest.mock import patch
from app import app, inventory


@pytest.fixture(autouse=True)
def reset_inventory():
    inventory.clear()
    inventory.append({
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "3274080005003",
        "quantity": 20,
        "price": 3.49,
        "ingredients_text": "Filtered water, almonds, cane sugar"
    })
    inventory.append({
        "id": 2,
        "product_name": "Peanut Butter",
        "brand": "Jif",
        "barcode": "0051500255162",
        "quantity": 15,
        "price": 4.99,
        "ingredients_text": "Roasted peanuts, sugar, salt"
    })


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_welcome(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_create_item(client):
    response = client.post("/inventory", json={
        "product_name": "Granola Bars",
        "brand": "Nature Valley",
        "quantity": 10,
        "price": 2.99
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Granola Bars"
    assert "id" in data


def test_create_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "No Name Brand"})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"quantity": 50})
    assert response.status_code == 200
    assert response.get_json()["quantity"] == 50


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"quantity": 5})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 204


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


@patch("app.fetch_product_by_barcode")
def test_fetch_and_add_item(mock_fetch, client):
    mock_fetch.return_value = {
        "product_name": "Mock Product",
        "brands": "Mock Brand",
        "ingredients_text": "Mock ingredients"
    }
    response = client.post("/inventory/fetch/1234567890123", json={"quantity": 5, "price": 1.99})
    assert response.status_code == 201
    assert response.get_json()["product_name"] == "Mock Product"


@patch("app.fetch_product_by_barcode")
def test_fetch_and_add_item_not_found(mock_fetch, client):
    mock_fetch.return_value = None
    response = client.post("/inventory/fetch/0000000000000", json={})
    assert response.status_code == 404


@patch("app.fetch_product_by_name")
def test_search_external(mock_search, client):
    mock_search.return_value = [
        {"product_name": "Mock Result", "brands": "X", "barcode": "123", "ingredients_text": ""}
    ]
    response = client.get("/inventory/search?name=milk")
    assert response.status_code == 200


def test_search_external_missing_query(client):
    response = client.get("/inventory/search")
    assert response.status_code == 400