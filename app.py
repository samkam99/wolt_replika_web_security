from flask import Flask, session, render_template, redirect, url_for, make_response, request, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid 
import time
import redis
import os


from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', etc.
Session(app)


app.secret_key = "your_secret_key"

##############################
##############################
##############################

def _________GET_________(): pass

##############################
##############################

##############################
@app.get("/test-set-redis")
def view_test_set_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    redis_client.set("name", "Santiago", ex=10)
    # name = redis_client.get("name")
    return "name saved"

@app.get("/test-get-redis")
def view_test_get_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    name = redis_client.get("name")
    if not name: name = "no name"
    return name

##############################
@app.get("/")
def view_index():
    try:
        # Connect to the database and fetch items
        db, cursor = x.db()
        cursor.execute("""
            SELECT 
                items.item_pk, 
                items.item_title, 
                items.item_description, 
                items.item_price, 
                items.item_image,
                users.user_name
            FROM 
                items
            LEFT JOIN 
                users
            ON 
                items.item_user_fk = users.user_pk
            LIMIT 20  -- Adjust limit based on your needs
        """)
        items = cursor.fetchall()

        # Pass items to the template
        return render_template("view_index.html", items=items, title="Homepage")

    except Exception as ex:
        print(f"Error fetching items for homepage: {ex}")
        return render_template("view_index.html", items=[], error="System under maintenance.", title="Homepage")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")


##############################
@app.get("/login")
@x.no_cache
def view_login():
    ic(session)

    # Check if session has a valid user
    user = session.get("user")
    if user:
        roles = user.get("roles")
        
        # Ensure roles is a list (or iterable) before calling len()
        if roles and isinstance(roles, list):
            if len(roles) > 1:
                return redirect(url_for("view_choose_role"))
            if "admin" in roles:
                return redirect(url_for("view_admin"))
            if "customer" in roles:
                return redirect(url_for("view_customer"))
            if "partner" in roles:
                return redirect(url_for("view_partner"))
    
    # Render login view if no valid user or roles
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))

# @app.get("/login")
# @x.no_cache
# def view_login():  
#     # ic("#"*20, "VIEW_LOGIN")
#     ic(session)
#     # print(session, flush=True)  
#     if session.get("user"):
#         if len(session.get("user").get("roles")) > 1:
#             return redirect(url_for("view_choose_role")) 
#         if "admin" in session.get("user").get("roles"):
#             return redirect(url_for("view_admin"))
#         if "customer" in session.get("user").get("roles"):
#             return redirect(url_for("view_customer")) 
#         if "partner" in session.get("user").get("roles"):
#             return redirect(url_for("view_partner"))         
#     return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))


##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    try:
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))
        user = session.get("user")
        if len(user.get("roles", "")) > 1:
            return redirect(url_for("view_choose_role"))
        
        db, cursor = x.db()
        cursor.execute("""
            SELECT 
                items.item_pk, 
                items.item_user_fk, 
                items.item_title, 
                items.item_description, 
                items.item_price, 
                items.item_image,
                users.user_name
            FROM 
                items
            INNER JOIN 
                users
            ON 
                items.item_user_fk = users.user_pk
            WHERE
                item_deleted_at IS NULL
        """)
        items = cursor.fetchall()

        return render_template("view_customer.html", x=x, user=user, items=items, title="customer")
    except Exception as e:
        return str(e), 500

    except Exception as ex:
        # Log error for debugging
        print(f"Error occurred in /admin: {ex}")
        error = "System under maintenance. Please try again."
        return {"error": error}, 500

    finally:
        # Ensure database connection is properly closed
        if cursor:
            cursor.close()
        if db:
            db.close()

##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_partner.html", x=x, user=user)

##############################

@app.get("/restaurant")
def view_restaurant():
    try:
        # Debug start of function
        ic("Starting view_restaurant function")

        # Ensure the user is logged in
        if not session.get("user", ""): 
            ic("User not logged in")
            return redirect(url_for("view_login"))
        
        user = session.get("user")
        ic("User data:", user)

        # Check if the user has multiple roles
        if len(user.get("roles", "")) > 1:
            ic("User has multiple roles")
            return redirect(url_for("view_choose_role"))
        
        # Database connection
        db, cursor = x.db()
        ic("Database connection established")

        # Execute SQL to fetch items
        cursor.execute("""
            SELECT 
                item_pk, item_user_fk, item_title, item_description, item_price, item_image
            FROM 
                items
            WHERE 
                item_user_fk = %s AND item_deleted_at IS NULL
            """, (user["user_pk"],))  # Match user_pk in session

        # Fetch all filtered items
        items = cursor.fetchall()
        ic("Fetched items from DB:", items)

        # Commit the transaction
        db.commit()
        ic("DB transaction committed")

        # Debug: Print the retrieved items
        # print("Retrieved items:", items)

        return render_template("view_restaurant.html", x=x, user=user, items=items, title="Restaurant")

    except Exception as ex:
        db.rollback()  # Rollback the transaction in case of error
        # Log error for debugging
        ic(f"Error occurred in /restaurant: {ex}")
        error = "System under maintenance. Please try again. View"
        return {"error": error}

# @app.get("/restaurant")
# @x.no_cache
# def view_restaurant():
#     try:
#         # Ensure the user is logged in
#         if not session.get("user", ""): 
#             return redirect(url_for("view_login"))
        
#         user = session.get("user")

#         # Check if the user has multiple roles
#         if len(user.get("roles", "")) > 1:
#             return redirect(url_for("view_choose_role"))
        
#         # Database connection
#         db, cursor = x.db()
        
#         cursor.execute("""
#             SELECT 
#                 item_pk, item_user_fk, item_title, item_description, item_price, item_image
#             FROM 
#                 items
#             WHERE 
#                 item_user_fk = %s
#             """, (user["user_pk"],))  # Match user_pk in session

#         # Fetch all filtered items
#         items = cursor.fetchall()

#         ic("Fetched items from DB:", items)

#         db.commit()

#         # Debug: Print the retrieved items
#         # print("Retrieved items:", items)

#         return render_template("view_restaurant.html", x=x, user=user, items=items, title="Restaurant")

#     except Exception as ex:
#         db.rollback()  # Rollback the transaction in case of error
#         # Log error for debugging
#         ic(f"Error occurred in /restaurant: {ex}")
#         error = "System under maintenance. Please try again. View"
#         return {"error": error}, 500

#     finally:
#         # Ensure database connection is properly closed
#         if cursor:
#             cursor.close()
#         if db:
#             db.close()


##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    db = None
    cursor = None
    try:
        # Check if the user is logged in
        user = session.get("user")
        if not user: 
            return redirect(url_for("view_login"))

        # Check if the user has admin privileges
        if "admin" not in user.get("roles", []):  # Assumes roles is a list
            return redirect(url_for("view_login"))

        # Connect to the database and fetch users
        db, cursor = x.db()  # Get the database connection
        cursor.execute("""
            SELECT 
                users.user_pk, users.user_name, users.user_last_name, 
                users.user_email, users.user_blocked_at,
                GROUP_CONCAT(roles.role_name) AS roles
            FROM 
                users
            LEFT JOIN 
                users_roles ON users.user_pk = users_roles.user_role_user_fk
            LEFT JOIN 
                roles ON roles.role_pk = users_roles.user_role_role_fk
            WHERE 
                users.user_deleted_at IS NULL
            GROUP BY 
                users.user_pk
        """)
        users = cursor.fetchall()

        # cursor.execute("SELECT * FROM items")
        # items = cursor.fetchall()

        # Fetch all items
        cursor.execute("""
            SELECT 
                item_pk, item_title, item_price
            FROM 
                items
            WHERE 
                item_deleted_at IS NULL
        """)
        items = cursor.fetchall()

        # Render the template with the fetched users and items
        return render_template("view_admin.html", user=user, users=users, items=items, title="Admin Home Page")

    except Exception as ex:
        # Log error for debugging
        print(f"Error occurred in /admin: {ex}")
        error = "System under maintenance. Please try again."
        return {"error": error}, 500

    finally:
        # Ensure database connection is properly closed
        if cursor:
            cursor.close()
        if db:
            db.close()



##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    user = session.get("user", {})
    
    # Ensure user is logged in
    if not user: 
        ic("No user in session, redirecting to login")
        return redirect(url_for("view_login"))
    
    # Ensure roles exist in session
    roles = user.get("roles", [])
    if not roles: 
        ic("User has no roles, redirecting to assign-role")
        return render_template("view_assign_role.html", user=user, title="Assign role")
        # return redirect(url_for("view_login"))  # Consider redirecting elsewhere, like "/choose-role"
    
    # Handle single-role users
    if len(roles) == 1: 
        ic(f"User has a single role: {roles[0]}")
        return redirect(f"/{roles[0]}")  # Redirect to role-specific page
    
    # Deduplicate roles and render choose-role page
    user["roles"] = list(set(roles))
    ic("Rendering choose-role page with user:", user)
    return render_template("view_choose_role.html", user=user, title="Choose role")


##############################
@app.get("/assign_role")
@x.no_cache
def view_assign_role():
    return render_template("assign_role.html")

##############################

@app.get("/profile-user")
def view_user_profile():
    user = session.get("user")
    user["roles"] = list(set(user["roles"]))
    return render_template("profile.html", user=user)



##############################
@app.get("/verify")
def verify_email():
    return render_template("verify_email.html")

##############################
@app.get("/recipt")
def view_recipt():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    cart = session.get('cart', [])
    return render_template("view_recipt.html", cart=cart, user=user)

##############################
@app.get("/search")
def search_items():
    try:
        query = request.args.get("query", "").strip()
        user = session.get("user", None)

        if not query:
            return render_template(
                "view_customer.html" if user else "view_index.html",
                items=[],
                user=user,
                error="Please enter a search query."
            )

        db, cursor = x.db()
        cursor.execute("""
            SELECT 
                items.item_pk, items.item_title, items.item_description, items.item_price, items.item_image,
                users.user_name
            FROM 
                items
            LEFT JOIN 
                users 
            ON 
                items.item_user_fk = users.user_pk
            WHERE 
                MATCH(items.item_title) AGAINST (%s IN NATURAL LANGUAGE MODE)
                OR users.user_name LIKE %s
        """, (query, f"%{query}%"))

        results = cursor.fetchall()

        print("Search results:", results)  # Debugging

        return render_template(
            "view_customer.html" if user else "view_index.html",
            items=results,
            user=user,
            query=query
        )

    except Exception as e:
        print("Error during search:", e)
        return render_template(
            "view_customer.html" if user else "view_index.html",
            items=[],
            user=user,
            error="An error occurred while searching."
        )
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



############################## GET TIL FORGOT PASSWORD

@app.get("/forgot_password")
@x.no_cache
def forgot_password():
    try:
        # Render HTML-siden for "Forgot Password"
        return render_template("view_forgot_password.html", x=x, title="Forgot Password")
    except Exception as ex:
        print(f"Error: {ex}")
        return """<template mix-target="#toast">System under maintenance</template>""", 500



############################## GET TIL RESET PASSWORD
@app.get("/password_reset_sent")
@x.no_cache
def password_reset_sent():
    try:
        return render_template("password_reset_sent.html", title="Reset Password Sent")
    except Exception as ex:
        print(f"Error: {ex}")
        return """<template mix-target="#toast">System under maintenance</template>""", 500



@app.get("/customer-map")
def view_customer_map():
    # Ensure the user is logged in and has the "customer" role
    if not session.get("user", "") or "customer" not in session.get("user").get("roles"):
        return redirect(url_for("view_login"))

    # Pass the restaurant data to the template
    restaurants = [
    {"name": "McDonald's", "coords": [55.676098, 12.568337]},
    {"name": "Jagger", "coords": [55.673711, 12.56553]},
    {"name": "Sticks'n'Sushi", "coords": [55.679558, 12.571619]},
    {"name": "Burger King", "coords": [55.681755, 12.563342]},
    {"name": "Domino's Pizza", "coords": [55.67562, 12.565463]},
    {"name": "KFC", "coords": [55.678941, 12.571212]},
    {"name": "Starbucks", "coords": [55.674802, 12.569824]},
    {"name": "Subway", "coords": [55.680715, 12.576937]},
    {"name": "Pizza Hut", "coords": [55.677631, 12.566902]},
    {"name": "Five Guys", "coords": [55.676274, 12.567419]}
]
    return render_template("view_customer_map.html", restaurants=restaurants, user=session.get("user"))

##############################
##############################
##############################

def _________POST_________(): pass

##############################
##############################
##############################

@app.post("/logout")
def logout():
    # ic("#"*30)
    # ic(session)
    session.pop("user", None)
    # session.clear()
    # session.modified = True
    # ic("*"*30)
    # ic(session)
    return redirect(url_for("view_login"))


##############################
@app.post("/signup")
@x.no_cache
def signup():
    try:
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        
        user_pk = str(uuid.uuid4())
        user_avatar = ""
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())
        reset_key = None #reset_key

        db, cursor = x.db()
        q = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' #reset_key
        cursor.execute(q, (user_pk, user_name, user_last_name, user_email, 
                        hashed_password, user_avatar, user_created_at, user_deleted_at, user_blocked_at, 
                        user_updated_at, user_verified_at, user_verification_key, reset_key)) #reset_key
        
        x.send_verify_email(user_email, user_verification_key)
        db.commit()

        session["user"] = {
            "id": user_pk,
            "email": user_email,
            "roles": [0]  
        }
    
        return """<template mix-redirect="/verify"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/login")
def login():
    try:
        # Get the user's email and password from the form
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        # Connect to the database
        db, cursor = x.db()

        # Query the database to get user details
        q = """ 
            SELECT * 
            FROM users 
            LEFT JOIN users_roles 
                ON user_pk = user_role_user_fk 
            LEFT JOIN roles
                ON role_pk = user_role_role_fk
            WHERE user_email = %s
        """
        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()

        # Check if no user exists with the provided email
        if not rows:
            toast = render_template("___toast.html", message="User not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400
        
        user_data = rows[0]  # Get the first (and only) row

        # Check if the user is deleted
        if user_data["user_deleted_at"]:
            toast = render_template("___toast.html", message="Account has been deleted")
            return f"""<template mix-target="#toast">{toast}</template>""", 403  # Forbidden access

        # Check if the user's password is correct
        if not check_password_hash(user_data["user_password"], user_password):
            toast = render_template("___toast.html", message="Invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401  # Unauthorized

        # Get the roles associated with the user
        roles = [row["role_name"] for row in rows if row["role_name"]]

        # Create a user session
        user = {
            "user_pk": user_data["user_pk"],
            "user_name": user_data["user_name"],
            "user_last_name": user_data["user_last_name"],
            "user_email": user_data["user_email"],
            "roles": roles
        }
        session["user"] = user

        # Redirect based on the user's roles
        if not roles:
            return f"""<template mix-redirect="/choose-role"></template>"""
        elif len(roles) == 1:  # User has exactly one role
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        else:  # User has multiple roles
            return f"""<template mix-redirect="/choose-role"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/assign-role")
def assign_role():
    try:
        # Ensure user is logged in
        user = session.get("user")
        if not user:
            return redirect(url_for('view_login'))  # Redirect if the user is not logged in
        
        user_pk = user.get("user_pk")
        if not user_pk:
            return "User primary key is missing in session", 400

        # Get role_pk from the form data
        role_pk = request.form.get("role_pk")
        if not role_pk:
            return "Role primary key is missing", 400

        # Connect to the database
        db, cursor = x.db()

        # Check if the user already has the role
        cursor.execute("""
            SELECT 1 FROM users_roles WHERE user_role_user_fk = %s AND user_role_role_fk = %s
        """, (user_pk, role_pk))
        existing_role = cursor.fetchone()

        if existing_role:
            # If the role already exists, inform the user
            return f"User already has the {role_pk} role.", 400

        # Insert the role into the users_roles table
        cursor.execute("""
            INSERT INTO users_roles (user_role_user_fk, user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, role_pk))

        db.commit()

        # Redirect user to the appropriate role page
        if role_pk == "c56a4180-65aa-42ec-a945-5fd21dec0538":
            return f"""<template mix-redirect="/customer"></template>"""  # Redirect to customer view
        elif role_pk == "f47ac10b-58cc-4372-a567-0e02b2c3d479":
            return f"""<template mix-redirect="/partner"></template>"""  # Redirect to partner view
        elif role_pk == "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15":
            return f"""<template mix-redirect="/restaurant"></template>"""  # Redirect to restaurant view
        else:
            return redirect(url_for('view_assign_role'))  # Default redirect if role is not recognized
        # Redirect user to the appropriate role page
        #return f"""<template mix-redirect="view_choose_role.html"></template>"""  # Use a clear URL pattern for role-specific pages


    except (x.CustomException, x.mysql.connector.Error) as ex:
        # Handle MySQL errors and CustomExceptions uniformly
        ic(ex)
        db.rollback()  # Rollback the transaction in case of error
        
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        
        # Return a general MySQL error message
        return "<template>System upgrading</template>", 500  

    except Exception as ex:
        # Handle any other exceptions
        ic(ex)
        return "<template>System under maintenance</template>", 500  

    finally:
        # Close database resources directly without checking if they exist
        cursor.close()
        db.close()


##############################
@app.post("/items")
def create_item():
    try:
        # Get user details from the session
        user = session.get("user")
        if not user:
            return redirect(url_for("view_login"))  # Redirect if the user is not logged in

        item_pk = str(uuid.uuid4())
        item_user_fk = user.get("user_pk")  # Assuming user_pk is the unique user ID in the session
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        # file, item_image_name = x.validate_item_images()

        item_deleted_at = None
        item_blocked_at = None
        # Validate uploaded images
        validated_files = x.validate_item_images()

        saved_files = []
        for file, filename in validated_files:
            # Save each file to the upload folder
            file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, filename))
            saved_files.append(filename)

        # Select the first image as the primary image for the `items` table
        primary_file, primary_filename = validated_files[0]

        # Database operations
        db, cursor = x.db()

        # Insert the main item record with the primary image
        cursor.execute("""
        INSERT INTO items
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (item_pk, item_user_fk, item_title, item_description, item_price, primary_filename, item_deleted_at, item_blocked_at))

        # Insert all images into the item_images table
        for filename in saved_files:
            cursor.execute("""
            INSERT INTO item_images (item_fk, image_name)
            VALUES (%s, %s)
            """, (item_pk, filename))

        # Commit transaction
        db.commit()



        # TODO: Success, commit

        db.commit()
        # return item_image_name
        return f"""<template mix-redirect="/restaurant"></template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()    


##############################
##############################
##############################

############################## EDIT FILE START
##############################
##############################
##############################
##############################


@app.post("/update-profile")
def update_profile():
    db_conn = None
    cursor = None
    try:
        # Get user details from the session
        user = session.get("user")
        if not user:
            return redirect(url_for("view_login"))  # Redirect if the user is not logged in

        user_id = user.get("user_pk")  # Assuming user_pk is the unique user ID in the session
        user_name = request.form.get("user_name")
        user_last_name = request.form.get("user_last_name")
        user_email = request.form.get("user_email")

        # Validate fields
        if not user_name or not user_last_name or not user_email:
            return make_response({"error": "All fields are required."}, 400)

        # Connect to the database
        db_conn, cursor = x.db()

        # Update user information in the database
        query = """
            UPDATE users
            SET user_name = %s, user_last_name = %s, user_email = %s
            WHERE user_pk = %s
        """
        cursor.execute(query, (user_name, user_last_name, user_email, user_id))
        db_conn.commit()

        # Update session data
        session["user"]["user_name"] = user_name
        session["user"]["user_last_name"] = user_last_name
        session["user"]["user_email"] = user_email

        # Redirect to profile page after a successful update
        return redirect(url_for("view_user_profile"))

    except Exception as ex:
        return make_response({"error": "An unexpected error occurred: " + str(ex)}, 500)
    finally:
        # Close the database connection and cursor
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()


##############################
@app.post("/add_to_cart")
def add_to_cart():
    item_pk = request.json.get('item_pk')
    item_title = request.json.get('item_title')
    item_price = request.json.get('item_price')
    item_image = request.json.get('item_image')  # Add this if you need item image
    ic("Received Item Image:", item_image)

    
    if "cart" not in session:
        session["cart"] = []

    # Check if item already exists in the cart
    for cart_item in session['cart']:
        if cart_item['item_pk'] == item_pk:
            cart_item['quantity'] += 1
            break
    else:
        # If item does not exist, add it as a new entry
        session['cart'].append({
            'item_pk': item_pk,  # Ensure 'item_pk' is added
            'item_title': item_title,
            'item_price': item_price,
            'item_image': item_image,  # Add item image if needed
            'quantity': 1
        })

        # Debugging: log the session cart contents
    ic("Cart in session:", session.get('cart'))

    session.modified = True
    return jsonify({'message': 'Item added to cart successfully', 'cart': session['cart']})

##############################
@app.post("/remove_from_cart")
def remove_from_cart():
    if request.is_json:
        item_pk = request.json.get('item_pk')
        ic(f"Received item_pk: {item_pk}")  # Debugging

        if 'cart' in session:
            session['cart'] = [
                item for item in session['cart'] if str(item.get('item_pk')) != str(item_pk)
            ]
            session.modified = True

        return jsonify({'message': 'Item removed', 'cart': session.get('cart', [])})
    else:
        return jsonify({'error': 'Request must be JSON'}), 400


##############################

@app.post("/order")
def order():
    try:
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))
        user = session.get("user")
        # Get the cart from the session
        cart = session.get('cart', [])
        
        # Check if the cart is empty
        if not cart:
            return "Your cart is empty. Please add items to your cart before placing an order.", 400
        x.send_recipt_email(cart)

        # Clear the cart after the order
        session['cart'] = []
        session.modified = True

        # Render the "Thank You" page after order placement
        # return render_template("view_recipt.html", cart=cart, user=user)
        return f"""<template mix-redirect="/recipt"></template>"""


    except Exception as ex:
        ic(ex)
        return "System under maintenance", 500
    finally:
        pass


################## POST RESET PASSWORD  #########
@app.post("/reset_password")
@x.no_cache
def reset_password():
    """
    Route to handle forgot password requests.
    Sends a reset link to the user's email if the email exists.
    """
    try:
        # Validate the user's email input
        user_email = x.validate_user_email()

        # Check if the email exists in the database
        db, cursor = x.db()
        cursor.execute("SELECT user_pk FROM users WHERE user_email = %s", (user_email,))
        user = cursor.fetchone()

        if not user:
            # If the email doesn't exist, show a message
            toast = render_template("___toast.html", message="Email not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        # Generate a unique reset key
        reset_key = str(uuid.uuid4())

        # Save the reset key in the database
        cursor.execute("UPDATE users SET reset_key = %s WHERE user_email = %s", (reset_key, user_email))
        db.commit()

        print(f"Sending reset email to: {user_email}")

        # Send a reset email with a unique link
        # reset_link = url_for('reset_password.html', reset_key=reset_key)
        
        x.send_reset_email(user_email, reset_key)

        # Notify the user to check their email
        # return """<template mix-redirect="/password-reset-sent"></template>""", 200
        return """<template mix-redirect="/password_reset_sent"></template>""", 201

    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast">{toast}</template>""", ex.code
        return """<template mix-target="#toast">System under maintenance</template>""", 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

################# RESET PASSWORD RESET KEY ##################

@app.post("/reset-password/<reset_key>")
@x.no_cache
def handle_password_reset(reset_key):
    """
    Handles the password reset form submission.
    Updates the user's password in the database if the reset key is valid.
    """
    print(request.form)
    try:
        # CHANGES START: Get both new password fields from the form
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        print(f"New password: {new_password}, Confirm password: {confirm_password}")  # Debug log

        # Ensure both passwords are provided and match
        if not new_password or not confirm_password:
            toast = render_template("___toast.html", message="Both password fields are required")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        if new_password != confirm_password:
            toast = render_template("___toast.html", message="Passwords do not match")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        # Validate password length
        if len(new_password) < x.USER_PASSWORD_MIN or len(new_password) > x.USER_PASSWORD_MAX:
            toast = render_template("___toast.html", message="Password must meet the required length")
            return f"""<template mix-target="#toast">{toast}</template>""", 400
        # CHANGES END

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Connect to the database
        db, cursor = x.db()
        print("Database connection established")  # Debug log

        # Check if the reset key exists in the database
        cursor.execute("SELECT user_pk FROM users WHERE reset_key = %s", (reset_key,))
        user = cursor.fetchone()
        print(f"Database query result: {user}")  # Debug log

        if not user:
            print("Invalid or expired reset key")  # Debug log
            toast = render_template("___toast.html", message="Invalid or expired reset key")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        # Update the user's password and clear the reset key
        cursor.execute("""
            UPDATE users
            SET user_password = %s, reset_key = NULL
            WHERE reset_key = %s
        """, (hashed_password, reset_key))
        db.commit()
        print("Password updated successfully")  # Debug log

        # Redirect to the login page with a success message
        toast = render_template("___toast.html", message="Password updated successfully")
        return f"""<template mix-redirect="/login">{toast}</template>""", 200

    except Exception as ex:
        print(f"Error during POST /reset-password: {ex}")  # Debug log
        if "db" in locals(): db.rollback()
        return """<template mix-target="#toast">System under maintenance</template>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
##############################
##############################

def _________PUT_________(): pass

##############################
##############################
##############################

@app.put("/users")
def user_update():
    try:
        if not session.get("user"): x.raise_custom_exception("please login", 401)

        user_pk = session.get("user").get("user_pk")
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot update user", 401)
        db.commit()
        return """<template>user updated</template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): return "<template>email not available</template>", 400
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################

@app.put("/update/items")
def update_items():
    try:
        # Verify user session
        if not session.get("user"):
            x.raise_custom_exception("Please login", 401)

        # Get item details
        item_pk = request.form.get("item_pk")
        ic(item_pk)  # Debugging the value of item_pk
        item_title = x.validate_item_title()
        ic(item_title)  # Debugging the value of item_title
        item_description = x.validate_item_description()
        ic(item_description)  # Debugging the value of item_description
        item_price = x.validate_item_price()
        ic(item_price)  # Debugging the value of item_price
        validated_files = x.validate_item_images()
        ic(validated_files)  # Debugging the validated_files list

        if not item_pk:
            x.raise_custom_exception("Invalid item", 400)

        # Save new images
        saved_files = []
        if validated_files:
            for file, filename in validated_files:
                file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, filename))
                saved_files.append(filename)
        ic(saved_files)  # Debugging the list of saved files

        db, cursor = x.db()

        # Verify if the item exists in the database
        cursor.execute("""
            SELECT 1 FROM items WHERE item_pk = %s
        """, (item_pk,))
        item_exists = cursor.fetchone()
        if not item_exists:
            x.raise_custom_exception("Item not found", 400)

        # Update item text details
        cursor.execute("""
            UPDATE items
            SET item_title = %s, item_description = %s, item_price = %s
            WHERE item_pk = %s
        """, (item_title, item_description, item_price, item_pk))

        # Debug the cursor rowcount after update
        ic(cursor.rowcount)  # How many rows were affected by the update

        # Update image only if new ones are provided
        if validated_files:
            cursor.execute("""
                SELECT item_image FROM items WHERE item_pk = %s
            """, (item_pk,))
            current_image = cursor.fetchone()
            ic(current_image)  # Debugging the current image

            # Check if there is a current image and delete it if it exists
            if current_image and 'item_image' in current_image:
                old_image_name = current_image['item_image']
                # Optionally, delete the old image from the filesystem
                old_image_path = os.path.join(x.UPLOAD_ITEM_FOLDER, old_image_name)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    ic(f"Deleted old image: {old_image_name}")  # Debugging image deletion
            else:
                ic("No current image found for item.")  # Log a message if no current image is found

            # Now update the `item_image` column in the `items` table with the new image
            cursor.execute("""
                UPDATE items
                SET item_image = %s
                WHERE item_pk = %s
            """, (saved_files[0], item_pk))  # Save only the first new image name (for now)

            ic(f"Updated item_image column for item_pk {item_pk} with new image: {saved_files[0]}")  # Debugging image update in items table

            # Delete old images from the item_images table
            cursor.execute("""DELETE FROM item_images WHERE item_fk = %s""", (item_pk,))
            ic(f"Deleted images from item_images for item_pk {item_pk}")  # Debugging image deletion from item_images table

            # Insert new images into the item_images table
            for filename in saved_files:
                cursor.execute("""
                    INSERT INTO item_images (item_fk, image_name)
                    VALUES (%s, %s)
                """, (item_pk, filename))
                ic(f"Inserted new image: {filename}")  # Debugging each image insertion

        if cursor.rowcount == 0:
            x.raise_custom_exception("Item not found or not updated", 400)

        db.commit()
        ic("Database commit successful!")  # Debugging commit success

        # Return success response with the new image filename (if any)
        return f"""<template mix-redirect="/restaurant"></template>"""

    except Exception as ex:
        ic(ex)  # Debugging the exception message
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        return "<template>System under maintenance</template>", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/block/<user_pk>")
def user_block(user_pk):
    try:
        # Check the admin priviliges
        user = session.get("user")
        if not user or "admin" not in user.get("roles", []):
            return {"error": "Unauthorized"}, 403

        # Validate the user ID
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())

        # Update database with the new block/unblock status
        db, cursor = x.db()
        cursor.execute("UPDATE users SET user_blocked_at = %s WHERE user_pk = %s", (user_blocked_at, user_pk))
        if cursor.rowcount != 1:
            return {"error": "Cannot block user"}, 400
        db.commit()

        # Send email notification
        x.send_action_email(to_email="wolteksamen@gmail.com", action="blocked", entity="user")

        return {"message": "User blocked successfully"}, 200

    except Exception as ex:
        return {"error": str(ex)}, 500



##############################
@app.put("/users/unblock/<user_pk>")
def user_unblock(user_pk):
    try:
        # Check the admin priviliges
        user = session.get("user")
        if not user or "admin" not in user.get("roles", []):
            return {"error": "Unauthorized"}, 403

        # Validate the user ID
        user_pk = x.validate_uuid4(user_pk)

        # Update database with the new block/unblock status
        db, cursor = x.db()
        cursor.execute("UPDATE users SET user_blocked_at = NULL WHERE user_pk = %s", (user_pk,))
        if cursor.rowcount != 1:
            return {"error": "Cannot unblock user"}, 400
        db.commit()

        # Send email notification
        x.send_action_email(to_email="wolteksamen@gmail.com", action="unblocked", entity="user")

        return {"message": "User unblocked successfully"}, 200

    except Exception as ex:
        return {"error": str(ex)}, 500



##############################
@app.put("/items/block/<item_pk>")
def block_item(item_pk):
    try:
        # Check admin privileges
        user = session.get("user")
        if not user or "admin" not in user.get("roles", []):
            return {"error": "Unauthorized"}, 403

        # Validate the item ID
        item_pk = x.validate_uuid4(item_pk)
        item_blocked_at = int(time.time())

        # Update database with the new block/unblock status
        db, cursor = x.db()
        cursor.execute("UPDATE items SET item_blocked_at = %s WHERE item_pk = %s", (item_blocked_at, item_pk))
        if cursor.rowcount != 1:
            return {"error": "Cannot block item"}, 400
        db.commit()

        # Send email notification
        x.send_action_email(to_email="wolteksamen@gmail.com", action="blocked", entity="item")

        return {"message": "Item blocked successfully"}, 200

    except Exception as ex:
        return {"error": str(ex)}, 500


##############################
@app.put("/items/unblock/<item_pk>")
def unblock_item(item_pk):
    try:
        # Check if the user is an admin
        user = session.get("user")
        if not user or "admin" not in user.get("roles", []):
            return {"error": "Unauthorized"}, 403

        # Validate the item ID
        item_pk = x.validate_uuid4(item_pk)

        # Update database with the new block/unblock status
        db, cursor = x.db()
        cursor.execute("UPDATE items SET item_blocked_at = NULL WHERE item_pk = %s", (item_pk,))
        if cursor.rowcount != 1:
            return {"error": "Cannot unblock item"}, 400
        db.commit()

        # Send email notification
        x.send_action_email(to_email="wolteksamen@gmail.com", action="Unblocked", entity="item")


        return {"message": "Item unblocked successfully"}, 200

    except Exception as ex:
        return {"error": str(ex)}, 500




##############################
##############################
##############################

def _________DELETE_________(): pass

##############################
##############################
##############################

def _________DELETE_________(): pass

##############################
##############################
##############################


##############################
@app.delete("/users/<user_pk>")
def user_delete(user_pk):
    try:
        # Ensure the user is logged in
        current_user = session.get("user")
        if not current_user:
            return redirect(url_for("view_login"))

        # Check if the user is an admin or the user being deleted
        is_admin = "admin" in current_user.get("roles", [])
        if not is_admin and current_user["user_pk"] != user_pk:
            return make_response("Unauthorized", 403)

        # Non-admin users must provide a password
        password = None
        if not is_admin:
            data = request.get_json()
            if not data or not data.get("password"):
                return make_response("Password is required", 400)
            password = data.get("password")

        # Validate the user_pk
        user_pk = x.validate_uuid4(user_pk)

        # Connect to the database
        db, cursor = x.db()

        # Fetch the user's current data
        cursor.execute("SELECT user_password, user_email, user_deleted_at FROM users WHERE user_pk = %s", (user_pk,))
        user_data = cursor.fetchone()

        if not user_data:
            return make_response("User not found", 404)

        if user_data["user_deleted_at"]:
            return make_response("Account already deleted", 403)

        # Validate password for non-admin users
        if not is_admin and not check_password_hash(user_data["user_password"], password):
            return make_response("Invalid password", 403)

        # Perform the soft delete
        user_deleted_at = int(time.time())
        cursor.execute("UPDATE users SET user_deleted_at = %s WHERE user_pk = %s", (user_deleted_at, user_pk))

        if cursor.rowcount != 1:
            return make_response("Failed to delete user", 400)

        db.commit()  # Commit the transaction

        # Send the account deletion email
        try:
            x.send_account_deletion_email(user_data["user_email"], user_deleted_at)
        except Exception as email_ex:
            print(f"Error sending deletion email: {email_ex}")

        # Log out the user if they deleted their own account
        if not is_admin and current_user["user_pk"] == user_pk:
            session.pop("user", None)

        # Return the toast message
        toast = render_template("___toast.html", message="User deleted successfully")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""

    except Exception as ex:
        print(f"Error occurred: {ex}")
        if "db" in locals():
            db.rollback()
        return make_response("An error occurred while processing your request.", 500)
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



##############################
# @app.delete("/items/delete/<item_pk>")
# def item_delete(item_pk):
#     try:
#         # Ensure user is logged in
#         user = session.get("user")
#         if not user: 
#             return redirect(url_for("view_login"))
#         # if not session.get("user", ""): 
#         #     return redirect(url_for("view_login"))
        
#         # Check if user has appropriate permissions (e.g., restaurant role)
#         if "restaurant" not in user.get("roles") and "admin" not in user.get("roles"):
#             return redirect(url_for("view_login"))
#         # if not "restaurant" in session.get("user").get("roles"):
#         #     return redirect(url_for("view_login"))

#         # Validate the item primary key
#         item_pk = x.validate_uuid4(item_pk)
#         item_deleted_at = int(time.time())
#         ic(f"item_deleted_at set to: {item_deleted_at}")

#         db, cursor = x.db()
#         cursor.execute("""
#             UPDATE items 
#             SET item_deleted_at = %s 
#             WHERE item_pk = %s
#         """, (item_deleted_at, item_pk))

#         if cursor.rowcount != 1:
#             x.raise_custom_exception("Cannot delete item", 400)
#         ic(f"Rows affected: {cursor.rowcount}")  # Log how many rows were updated

#         # Commit the transaction
#         db.commit()

#         # Log successful delete
#         ic("Item successfully deleted from database")

#         # Return a template with a success message
#         toast = render_template("___toast.html", message="Item deleted")
#         return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""

#     except Exception as ex:
#         # Log the exception for debugging
#         ic(f"Error occurred: {ex}")

#         # Rollback transaction if something goes wrong
#         if "db" in locals(): db.rollback()
#         # Handle custom application exceptions
#         if isinstance(ex, x.CustomException): 
#             return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        

#         # Handle MySQL-specific errors
#         if isinstance(ex, x.mysql.connector.Error):
#             ic(f"MySQL Error: {ex}")
#             return "<template>Database error</template>", 500

#         # Generic error response
#         return "<template>System under maintenance</template>", 500  

#     finally:
#         # Ensure database resources are released
#         if "cursor" in locals(): cursor.close()
#         if "db" in locals(): db.close()
@app.delete("/items/delete/<item_pk>")
def item_delete(item_pk):
    try:
        # Ensure user is logged in
        user = session.get("user")
        if not user: 
            return redirect(url_for("view_login"))
        
        # Check if user has appropriate permissions (e.g., restaurant or admin role)
        if "restaurant" not in user.get("roles") and "admin" not in user.get("roles"):
            return redirect(url_for("view_login"))

        # Validate the item primary key
        item_pk = x.validate_uuid4(item_pk)
        item_deleted_at = int(time.time())
        ic(f"item_deleted_at set to: {item_deleted_at}")

        db, cursor = x.db()

        # Fetch item details for email
        cursor.execute("SELECT item_title, item_user_fk FROM items WHERE item_pk = %s", (item_pk,))
        item_data = cursor.fetchone()
        if not item_data:
            return f"""<template mix-target="#toast" mix-bottom>Item not found</template>""", 404
        
        # Perform the soft delete
        cursor.execute("""
            UPDATE items 
            SET item_deleted_at = %s 
            WHERE item_pk = %s
        """, (item_deleted_at, item_pk))

        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot delete item", 400)
        ic(f"Rows affected: {cursor.rowcount}")  # Log how many rows were updated

        # Commit the transaction
        db.commit()
        ic("Item successfully deleted from database")

        # Send the deletion email notification
        try:
            item_owner_email = item_data["item_user_fk"]  # Replace with actual owner email logic
            x.send_account_deletion_email(item_owner_email, item_deleted_at)
        except Exception as email_ex:
            print(f"Error sending deletion email: {email_ex}")

        # Return a template with a success message
        toast = render_template("___toast.html", message="Item deleted")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""

    except Exception as ex:
        # Log the exception for debugging
        ic(f"Error occurred: {ex}")

        # Rollback transaction if something goes wrong
        if "db" in locals(): db.rollback()
        # Handle custom application exceptions
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        

        # Handle MySQL-specific errors
        if isinstance(ex, x.mysql.connector.Error):
            ic(f"MySQL Error: {ex}")
            return "<template>Database error</template>", 500

        # Generic error response
        return "<template>System under maintenance</template>", 500  

    finally:
        # Ensure database resources are released
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
##############################
##############################

def _________BRIDGE_________(): pass

##############################
##############################
##############################


##############################
@app.get("/verify/<verification_key>")
@x.no_cache
def verify_user(verification_key):
    try:
        ic(verification_key)
        verification_key = x.validate_uuid4(verification_key)
        user_verified_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users 
                SET user_verified_at = %s 
                WHERE user_verification_key = %s"""
        cursor.execute(q, (user_verified_at, verification_key))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot verify account", 400)
        db.commit()
        return redirect(url_for("view_login", message="User verified, please login"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()  

############## RESET KEY ############
@app.get("/reset-password/<reset_key>")
@x.no_cache
def get_reset_password(reset_key):
    reset_key= x.validate_uuid4(reset_key)
    db, cursor = x.db()
    
    cursor.execute(""" SELECT user_pk
                    FROM users WHERE
                    reset_key = %s""", (reset_key,))
    user = cursor.fetchone()

    if user is None: 

        cursor.close()
        db.close()
        return "Error: no acces", 400
    # If the reset key is valid, render the reset_password.html page

    return render_template("reset_password.html", reset_key=reset_key, x=x, title="Reset Password")
