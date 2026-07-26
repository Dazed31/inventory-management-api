from flask import Flask, jsonify, request
from external_api import fetch_product_by_barcode, fetch_products_by_name

app = Flask(__name__)

#Simmulated in-memory inventory database
inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "1234567890123",
        "quantity": 20,
        "price": 3.99,
        "ingredients_text": "Filtered water, almonds, cane sugar"
    },
    {
        "id": 2,
        "product_name": "Peanut Butter",
        "brand": "Jif",
        "barcode": "3216549870123",
        "quantity": 15,
        "price": 3.49,
        "ingredients_text": "Roasted peanuts, salt"
    }
]

def find_item(item_id):
    return  next((item for item in inventory if item["id"] == item_id), None)

def get_next_id():
    return max((item["id"] for item in inventory), default=0) + 1

@app.route("/")
def welcome():
    return jsonify({"message": "Welcome to the Inventory Management API!"})

@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200

@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    else:
        return jsonify(item), 200

@app.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json()

    if not data or "product_name" not in data or not data["product_name"]:
        return jsonify({"error": "Product name is required"}), 400\

    new_item = {
        "id": get_next_id(),
        "product_name": data["product_name"],
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "quantity": data.get("quantity", 0),
        "price": data.get("price", 0.0),
        "ingredients_text": data.get("ingredients_text", "")
    }
    inventory.append(new_item)
    return jsonify(new_item), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    for field in ["product_name", "brand", "barcode", "quantity", "price", "ingredients_text"]:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return "", 204

@app.route("/inventory/fetch/<barcode>", methods=["POST"])
def fetch_product(barcode):
    result = fetch_product_by_barcode(barcode)

    if result is None:
        return jsonify({"error": "Product not found"}), 404
    if "error" in result:
        return jsonify(result), 502

    body = request.get_json(silent=True) or {}

    new_item = {
        "id": get_next_id(),
        "product_name": result.get("product_name", "Unknown"),
        "brand": result.get("brands", ""),
        "barcode": barcode,
        "quantity": body.get("quantity", 0),
        "price": body.get("price", 0.0),
        "ingredients_text": result.get("ingredients_text", "")
    }
    inventory.append(new_item)
    return jsonify(new_item), 201


@app.route("/inventory/search", methods=["GET"])
def search_external():

    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Name query parameter is required"}), 400

    results = fetch_products_by_name(name)
    if results is None:
        return jsonify({"error": "No results found"}), 404

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)