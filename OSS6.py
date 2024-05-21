from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import time

app = Flask(__name__)

# Database setup
DATABASE = "online_shopping.db"
def create_tables():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        
        # Recreate the 'users' table with the new schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                full_name TEXT,
                email TEXT UNIQUE
            )
        ''')
        
        # Check if 'username' column exists and add if not
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'username' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN username TEXT UNIQUE')
            # Update existing records to ensure uniqueness (using 'email' as a unique identifier)
            cursor.execute('UPDATE users SET username = email')
                    

                        
        
        #Product Management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                price REAL,
                name TEXT,
                stock_quantity INTEGER,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        ''')

        # Category Management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT,
                price_range TEXT
            )
        ''')

        # Stock Management (Weak Entity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                quantity INTEGER,
                product_id INTEGER,
                warehouse_id INTEGER,
                PRIMARY KEY (product_id, warehouse_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')

        # Admin Management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_name TEXT
            )
        ''')

        # Supplier Management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT,
                supplier_address TEXT
            )
        ''')


        # Shopping Cart (Weak Entity)
        cursor.execute('''
          CREATE TABLE IF NOT EXISTS shopping_carts (
             cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER,
             total_cost REAL,
             product_id INTEGER,
             amount INTEGER,
             FOREIGN KEY (user_id) REFERENCES users(user_id),
             FOREIGN KEY (product_id) REFERENCES products(product_id)
              )
               ''')



        connection.commit()
def update_user_info(username, new_full_name, new_email):
    user_id = get_user_id(username)
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        cursor.execute('''
            UPDATE users
            SET full_name=?, email=?
            WHERE user_id=?
        ''', (new_full_name, new_email, user_id))

        connection.commit()
        print("User information updated successfully!")

# Add similar functions for managing shipping addresses and changing passwords
def manage_shipping_addresses(username, new_address):
       user_id = get_user_id(username)
       with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        cursor.execute('''
            UPDATE users
            SET shipping_address=?
            WHERE user_id=?
        ''', (new_address, user_id))

        connection.commit()
        print("Shipping address updated successfully!")

def change_password(username, new_password):
       user_id = get_user_id(username)
       with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        cursor.execute('''
            UPDATE users
            SET password=?
            WHERE user_id=?
        ''', (new_password, user_id))

        connection.commit()
        print("Password changed successfully!")


def search_products(category=None, price_range=None, brand=None):
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        query = '''
            SELECT products.product_id, products.name,products.price, products.stock_quantity, categories.category_name
            FROM products
            INNER JOIN categories ON products.category_id = categories.category_id
            WHERE 1=1
        '''

        params = []

        if category:
            query += ' AND categories.category_name = ?'
            params.append(category)

        if price_range:
            query += ' AND categories.price_range = ?'
            params.append(price_range)

        if brand:
            query += ' AND products.brand = ?'
            params.append(brand)

        cursor.execute(query, params)

        product_data = cursor.fetchall()

        if not product_data:
            print("No products match the search criteria.")
        else:
            print("Product ID | Name | Price | Stock Quantity | Category")
            for product in product_data:
                print(f"{product[0]} | {product[2]} | {product[1]} | {product[3]} | {product[4]} |")

def get_user_id(username):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print("User not found.")
                return None
    except sqlite3.Error as e:
        print("Error:", e)
  

def is_existing_user(username, password):
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        res = cursor.fetchone()
    return res is not None
def register_user(username, password, full_name, email):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, full_name, email)
                VALUES (?, ?, ?, ?)
            ''', (username, password, full_name, email))
            connection.commit()
            print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Username or email already exists.")
def add_product(name, price, stock_quantity, category):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO products (name, price, stock_quantity, category_id)
                VALUES (?, ?, ?, ?)
            ''', (name, price, stock_quantity, category))
            connection.commit()
            print("Product added successfully!")
    except sqlite3.IntegrityError:
        print("Product already exists.")

def delete_product(product_id):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM products WHERE product_id=?', (product_id,))
            connection.commit()
            print("Product deleted successfully!")
    except sqlite3.Error as e:
        print("Error:", e)

def update_product(product_id, name, price, stock_quantity, category):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE products
                SET name=?, price=?, stock_quantity=?, category_id=?
                WHERE product_id=?
            ''', (name,price, stock_quantity, category, product_id))
            connection.commit()
            print("Product updated successfully!")
    except sqlite3.Error as e:
        print("Error:", e)

def update_stock(product_id, new_stock_quantity):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE products SET stock_quantity=? WHERE product_id=?', (new_stock_quantity, product_id))
            connection.commit()
            print("Stock quantity updated successfully!")
    except sqlite3.Error as e:
        print("Error:", e)

def assign_category(product_id, category_id):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE products SET category_id=? WHERE product_id=?', (category_id, product_id))
            connection.commit()
            print("Category assigned successfully!")
    except sqlite3.Error as e:
        print("Error:", e)


def features():
    print("For search and filtering input 1")

    choice = input()

    if choice == '1':
        search_and_filter_menu()
    else:
        print("Invalid choice.Exiting.")
    

def search_and_filter_menu():
    print("\nSearch and Filter Menu:")
    category = input("Enter category (or leave blank for all): ")
    price_range = input("Enter price range (or leave blank for all): ")
    supplier_name = input("Enter brand: ")
    search_products(category, price_range,supplier_name)

def view_products():
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM products')
            product_data = cursor.fetchall()

            print("\nAvailable Products:")
            for product in product_data:
                print(f"Product ID: {product[0]}, Name: {product[2]}")
    except sqlite3.Error as e:
        print("Error:", e)

def view_product_details(product_id,username):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
            product_details = cursor.fetchone()

            if product_details:
                print("\nProduct Details:")
                print(f"Product ID: {product_details[0]}")
                print(f"Name: {product_details[3]}")
                print(f"Price: ${product_details[1]}")
                print(f"Stock Quantity: {product_details[4]}")
                # Add more details as needed
            else:
                print("Product not found.")
            menu(username)
    except sqlite3.Error as e:
        print("Error:", e)


def add_to_shopping_cart(username, product_id, quantity):
    user_id = get_user_id(username)
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        # Check if there is enough stock
        cursor.execute('SELECT stock_quantity FROM products WHERE product_id=?', (product_id,))
        current_stock = cursor.fetchone()[0]

        if current_stock >= quantity:
            # Deduct the quantity from stock
            cursor.execute('UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id=?', (quantity, product_id))

            # Add the product to the shopping cart
            cursor.execute('INSERT INTO shopping_carts (user_id, product_id, quantity) VALUES (?, ?, ?)', (user_id, product_id, quantity))

            connection.commit()
            print("Product added to the shopping cart successfully!")
        else:
            print("Insufficient stock. Unable to add to the shopping cart.")
        menu(username)



def view_shopping_cart(user_id):
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT products.product_id, products.name, shopping_carts.quantity, products.price
                FROM shopping_carts
                JOIN products ON shopping_carts.product_id = products.product_id
                WHERE shopping_carts.user_id = ?
            ''', (user_id,))

            cart_items = cursor.fetchall()

            if not cart_items:
                print("Shopping cart is empty.")
            else:
                total_cost = 0.0
                print("Shopping Cart:")
                print("Product ID | Product Name | Quantity | Price | Total Cost")
                for item in cart_items:
                    product_id, product_name, quantity, price = item
                    total_item_cost = quantity * price
                    total_cost += total_item_cost
                    print(f"{product_id} | {product_name} | {quantity} | ${price:.2f} | ${total_item_cost:.2f}")
                print(f"Total Cost: ${total_cost:.2f}")
        menu(username)

    except sqlite3.Error as e:
        print("Error:", e)



def checkout(username, shipping_address):
    user_id = get_user_id(username)
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()

            # Retrieve the user's shopping cart
            cursor.execute('SELECT * FROM shopping_carts WHERE user_id = ?', (user_id,))
            cart_data = cursor.fetchone()

            if cart_data:
                cart_id, user_id, total_cost = cart_data

                # Retrieve the cart items
                cursor.execute('SELECT * FROM cart_items WHERE cart_id = ?', (cart_id,))
                cart_items = cursor.fetchall()

                # Perform the checkout process
                tracking_id = generate_tracking_id()
                courier_info = input("Enter courier information: ")

                # Generate a simple payment receipt
                payment_receipt = generate_payment_receipt(cart_items, total_cost)

                # Insert the order details into the transaction_receipts table
                cursor.execute('''
                    INSERT INTO transaction_receipts (tracking_id, courier_info, payment_receipt)
                    VALUES (?, ?, ?)
                ''', (tracking_id, courier_info, payment_receipt))

                # Update product stock levels and deduct from the inventory
                for cart_item in cart_items:
                    product_id, quantity = cart_item[2], cart_item[3]
                    update_stock(product_id, -quantity)  # Deduct quantity from stock

                # Clear the user's shopping cart
                cursor.execute('DELETE FROM shopping_carts WHERE user_id = ?', (user_id,))

                print("Checkout successful!")
                print(f"Tracking ID: {tracking_id}")
                print("Payment Receipt:")
                print(payment_receipt)
            else:
                print("Shopping cart is empty. Add products before checking out.")
            menu(username)
    except sqlite3.Error as e:
        print("Error:", e)

def generate_tracking_id():
    # Using a simple timestamp-based approach for a unique tracking ID
    return int(time.time())

def generate_payment_receipt(cart_items, total_cost):
    # Generate a simple payment receipt based on cart items and total cost
    receipt_lines = []
    receipt_lines.append("Payment Receipt")
    receipt_lines.append("-" * 30)
    for cart_item in cart_items:
        product_id, quantity = cart_item[2], cart_item[3]
        receipt_lines.append(f"Product ID: {product_id}, Quantity: {quantity}")
    receipt_lines.append("-" * 30)
    receipt_lines.append(f"Total Cost: ${total_cost}")
    return "\n".join(receipt_lines)

def add_to_cart_menu(username,user_id, product_id, quantity):
    print("\nAdd to Shopping Cart:")
    add_to_shopping_cart(user_id, product_id, quantity)
    menu(username)




def add_product_menu():
    print("\nAdd Product:")
    name = input("Enter the product name: ")
    price = float(input("Enter the product price: "))
    stock_quantity = int(input("Enter the stock quantity: "))
    category = int(input("Enter the category ID: "))
    add_product(name, price, stock_quantity, category)

def delete_product_menu():
    print("\nDelete Product:")
    product_id = int(input("Enter the product ID to delete: "))

    delete_product(product_id)

def update_product_menu():
    print("\nUpdate Product Information:")
    product_id = int(input("Enter the product ID to update: "))
    name = input("Enter the new product name: ")
    price = float(input("Enter the new product price: "))
    stock_quantity = int(input("Enter the new stock quantity: "))
    category = int(input("Enter the new category ID: "))

    update_product(product_id, name,price, stock_quantity, category)

def update_stock_menu():
    print("\nUpdate Stock Levels:")
    product_id = int(input("Enter the product ID to update stock: "))
    new_stock_quantity = int(input("Enter the new stock quantity: "))

    update_stock(product_id, new_stock_quantity)

def assign_category_menu():
    print("\nAssign Category to Product:")
    product_id = int(input("Enter the product ID: "))
    category_id = int(input("Enter the category ID: "))
    assign_category(product_id, category_id)

def generate_sales_report():
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()

            # Retrieve total sales and revenue
            cursor.execute('''
                SELECT SUM(total_cost) as total_sales, COUNT(*) as total_orders
                FROM transaction_receipts
            ''')
            sales_data = cursor.fetchone()

            if sales_data:
                total_sales, total_orders = sales_data
                print("Sales Report:")
                print(f"Total Sales: ${total_sales}")
                print(f"Total Orders: {total_orders}")
            else:
                print("No sales data available.")
    except sqlite3.Error as e:
        print("Error:", e)

def generate_popular_products_report():
    try:
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()

            # Retrieve popular products based on the number of times they were purchased
            cursor.execute('''
                SELECT products.name, COUNT(*) as purchase_count
                FROM transaction_receipts
                JOIN cart_items ON transaction_receipts.tracking_id = cart_items.tracking_id
                JOIN products ON cart_items.product_id = products.product_id
                GROUP BY products.product_id
                ORDER BY purchase_count DESC
                LIMIT 5
            ''')
            popular_products = cursor.fetchall()

            if popular_products:
                print("Popular Products Report:")
                for product in popular_products:
                    product_name, purchase_count = product
                    print(f"{product_name}: {purchase_count} purchases")
            else:
                print("No popular products data available.")
    except sqlite3.Error as e:
        print("Error:", e)


def menu(username):
  print("Menu:")
  print("1. View Products")
  print("2. Display and Search products")
  print("3. Add Product to Cart")
  print("4. View Cart")
  print("5. Checkout")
  print("6. Exit")
  choice = input("Enter your choice (1-6): ")
  if choice == '1':
    view_products()  
    product_id = input("Enter the product ID to view details: ")
    view_product_details(product_id,username)
  elif choice == '2':
    features()
  elif choice == '3':
    user_id = get_user_id(username) 
    product_id = int(input("Enter the product ID to add to the cart: "))
    quantity = int(input("Enter the quantity: "))
    add_to_cart_menu(username,user_id,product_id, quantity)
  elif choice == '4':
    user_id = get_user_id(username)  
    view_shopping_cart(user_id)
  elif choice == '5':
    user_id = get_user_id(username) 
    shipping_address = input("Enter the shipping address: ")
    checkout(user_id, shipping_address)
  elif choice == '6':
        print("Thank you for visiting the Online Shopping system")
  else:
        print("Invalid choice. Please try again.")
        
    


def customer_menu():
    print("Customer Menu:")
    print("1. Login")
    print("2. Register")
    print("3. Update information")
    
    choice = input("Enter your choice (1 or 2 or 3): ")
    
    if choice == '1':
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        
        if is_existing_user(username, password):
            print("Login successful!")
            print("Enter your choice")
            print("1. View Products")
            print("2. Search products")
            print("3. Add Product to Cart")
            print("4. View Cart")
            print("5. Checkout")
            print("6. Exit")
            choice = input("Enter your choice (1-6): ")
            if choice == '1':
              view_products()  
              product_id = input("Enter the product ID to view details: ")
              view_product_details(product_id,username)
            elif choice == '2':
               features()
            elif choice == '3':
              user_id = get_user_id(username) 
              product_id = int(input("Enter the product ID to add to the cart: "))
              quantity = int(input("Enter the quantity: "))
              add_to_cart_menu(username,user_id,product_id, quantity)
              
            elif choice == '4':
                user_id = get_user_id(username)  # You need to implement this function
                view_shopping_cart(user_id)
            elif choice == '5':
               user_id = get_user_id(username)  # You need to implement this function
               shipping_address = input("Enter the shipping address: ")
               checkout(user_id, shipping_address)
            elif choice == '6':
                print("Thank you for visiting the Online Shopping system")
            else:
                print("Invalid choice. Please try again.")
                menu(username)
        else:
            print("No user found")
            customer_menu()

            
    elif choice == '2':
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        full_name = input("Enter your full name: ")
        email = input("Enter your email: ")
        register_user(username, password, full_name, email)
        print("Please login to view products ")
        customer_menu()
        
       
    elif choice == '3':
        print("1. Update Personal Information")
        print("2. Change Password")

        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
           username =input("Enter your username: ")
           new_full_name = input("Enter your new full name: ")
           new_email = input("Enter your new email: ")
           print("PLease log in again with the new login information")
           user_id= get_user_id(username)
           update_user_info(user_id, new_full_name, new_email)
           customer_menu()
        elif choice == '2':
            username = int(input("Enter your username: "))
            new_password = input("Enter your new password: ")
            print("PLease log in again with the new login information")
            user_id= get_user_id(username)
            change_password(user_id, new_password)
            customer_menu()
        
        else:
           print("Invalid choice. Exiting.")
           customer_menu()
    else:
        print("Invalid")
        customer_menu()


def admin_menu():
    print("Admin Menu:")
    print("1. Inventory Management")
    print("2. Analysis Report")
    choice = input("Enter your choice (1-5): ")
    
    if choice == '1':
        print("Welcome to inventory management")
        print("1. Add Product")
        print("2. Delete Product")
        print("3. Update Product Information")
        print("4. Update Stock Levels")
        print("5. Assign Category to Product")
        print("6. Display All Products")
        choice = input("Enter your choice(1-6) ")
        if choice == '1':
            add_product_menu()
        elif choice == '2':
            delete_product_menu()
        elif choice == '3':
            update_product_menu()
        elif choice == '4':
            update_stock_menu()
        elif choice == '5':
            assign_category_menu()
        elif choice == '6':
            view.products()
        elif choice == '7':
            print("Exiting the Online Shopping System.")
        else:
           print("Invalid choice. Please try again.")
    elif choice == '2':
         print("1.Generate sales report")
         print("Generate Popular products report")
         choice=int(input("Enter which report you want to generate(1 or 2)"))
         if choice == 1:
             generate_sales_report()
         elif choice == 2:
             generate_popular_products_report()
         else:
             print("Invalid choice")
    else:
        print("Invalid choice.")
        admin_menu()





def main():
    create_tables()
  
    print("Welcome to the Online Shopping System!")

    user_type = input("Are you a customer or an admin? Enter 'customer' or 'admin': ").lower()

    if user_type == 'customer':
        customer_menu()
    elif user_type == 'admin':
        admin_menu()
    else:
        print("Invalid user type. Exiting")

if __name__ == '__main__':
    main()






