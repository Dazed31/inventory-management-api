import requests

API_BASE = "http://localhost:5000"


def view_inventory():
    response = requests.get(f"{API_BASE}/inventory")
    if response.status_code == 200:
        items = response.json()
        if not items:
            print("Inventory is empty.")
        for item in items:
            print(f"[{item['id']}] {item['product_name']} - Brand: {item['brand']}, Quantity: {item['quantity']}, Price: ${item['price']:.2f}")

    else:
        print(f"Failed to fetch inventory.")


def view_item():
    item_id = input("Enter the item ID: ").strip()
    if not item_id.isdigit():
        print("Invalid item ID. Please enter a numeric value.")
        return
    response = requests.get(f"{API_BASE}/inventory/{item_id}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Item with ID {item_id} not found.")

def add_item():
    product_name = input("Product name: ").strip()
    if not product_name:
        print("Product name is required.")
        return

    brand = input("Brand: ").strip()
    barcode = input("Barcode (optional): ").strip()
    quantity = input("Quantity: ").strip()
    price = input("Price: ").strip()

    payload = {
        "product_name": product_name,
        "brand": brand,
        "barcode": barcode,
        "quantity": int(quantity) if quantity.isdigit() else 0,
        "price": float(price) if price.replace(".", "", 1).isdigit() else 0.0
    }

    response = requests.post(f"{API_BASE}/inventory", json=payload)
    if response.status_code == 201:
        print("Item added:", response.json())
    else:
        print("Failed to add item:", response.json())


def update_item():
    item_id = input("Enter item id to update: ").strip()
    if not item_id.isdigit():
        print("Invalid id.")
        return

    print("Leave a field blank to skip it.")
    quantity = input("New quantity: ").strip()
    price = input("New price: ").strip()

    payload = {}
    if quantity:
        payload["quantity"] = int(quantity) if quantity.isdigit() else 0
    if price:
        payload["price"] = float(price) if price.replace(".", "", 1).isdigit() else 0.0

    if not payload:
        print("Nothing to update.")
        return

    response = requests.patch(f"{API_BASE}/inventory/{item_id}", json=payload)
    if response.status_code == 200:
        print("Item updated:", response.json())
    else:
        print("Failed to update:", response.json())


def delete_item():
    item_id = input("Enter item id to delete: ").strip()
    if not item_id.isdigit():
        print("Invalid id.")
        return
    response = requests.delete(f"{API_BASE}/inventory/{item_id}")
    if response.status_code == 204:
        print("Item deleted.")
    else:
        print("Failed to delete:", response.json())


def find_on_openfoodfacts():
    barcode = input("Enter barcode to search and add: ").strip()
    if not barcode:
        print("Barcode is required.")
        return

    quantity = input("Quantity to store (optional): ").strip()
    price = input("Price (optional): ").strip()

    payload = {}
    if quantity.isdigit():
        payload["quantity"] = int(quantity)
    if price.replace(".", "", 1).isdigit():
        payload["price"] = float(price)

    response = requests.post(f"{API_BASE}/inventory/fetch/{barcode}", json=payload)
    if response.status_code == 201:
        print("Item fetched and added:", response.json())
    else:
        print("Failed:", response.json())


def main_menu():
    while True:
        print("\n--- Inventory Management CLI ---")
        print("1. View all inventory")
        print("2. View single item")
        print("3. Add new item")
        print("4. Update item (quantity/price)")
        print("5. Delete item")
        print("6. Find product on OpenFoodFacts and add")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            view_item()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            find_on_openfoodfacts()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main_menu()
    