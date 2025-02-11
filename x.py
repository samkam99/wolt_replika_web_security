from flask import request, make_response
from functools import wraps
import mysql.connector
import re
import os
import uuid
import time

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

UNSPLASH_ACCESS_KEY = 'YOUR_KEY_HERE'
ADMIN_ROLE_PK = "16fd2706-8baf-433b-82eb-8c7fada847da"
CUSTOMER_ROLE_PK = "c56a4180-65aa-42ec-a945-5fd21dec0538"
PARTNER_ROLE_PK = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
RESTAURANT_ROLE_PK = "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15"


# form to get data from input fields
# args to get data from the url
# values to get data from the url and from the form

class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)


##############################
def db():
    db = mysql.connector.connect(
        host="mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="company"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor


##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################

def allow_origin(origin="*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call the wrapped function
            response = make_response(f(*args, **kwargs))
            # Add Access-Control-Allow-Origin header to the response
            response.headers["Access-Control-Allow-Origin"] = origin
            # Optionally allow other methods and headers for full CORS support
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return decorated_function
    return decorator


##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise_custom_exception(error, 400)
    return user_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip() # None
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise_custom_exception(error, 400)
    return user_last_name

##############################
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email():
    error = "email invalid"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise_custom_exception(error, 400)
    return user_email

##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise_custom_exception(error, 400)
    return user_password

##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    error = f"invalid uuid4"
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise_custom_exception(error, 400)
    return uuid4

############################## ITEM VALIDATION ##############################
ITEM_TITLE_MIN = 2
ITEM_TITLE_MAX = 20
REGEX_ITEM_TITLE = f"^.{{{ITEM_TITLE_MIN},{ITEM_TITLE_MAX}}}$"
def validate_item_title():
    error = f"Item title {ITEM_TITLE_MIN} to {ITEM_TITLE_MAX} characters"
    item_title = request.form.get("item_title", "").strip()
    if not re.match(REGEX_ITEM_TITLE, item_title): raise_custom_exception(error, 400)
    return item_title

##############################
ITEM_DESCRIPTION_MIN = 2
ITEM_DESCRIPTION_MAX = 255
REGEX_ITEM_DESCRIPTION = f"^.{{{ITEM_DESCRIPTION_MIN},{ITEM_DESCRIPTION_MAX}}}$"
def validate_item_description():
    error = f"Item description {ITEM_DESCRIPTION_MIN} to {ITEM_DESCRIPTION_MAX} characters"
    item_description = request.form.get("item_description", "").strip()
    if not re.match(REGEX_ITEM_DESCRIPTION, item_description): raise_custom_exception(error, 400)
    return item_description

##############################
ITEM_PRICE_MIN = 1
ITEM_PRICE_MAX = 999.99
REGEX_ITEM_PRICE = "^([1-9]\d{0,2}|\d{1,3}\.\d{1,2})$" #the regex allows the numbers from 1-9, and 2 decimals. 1-3 numbers before the "." and 1-2 numbers after the "." the datatype in out database is DECIMAL (5,2) which means the same.
def validate_item_price():
    error = f" Item price from {ITEM_PRICE_MIN} to {ITEM_PRICE_MAX}"
    item_price = request.form.get("item_price", "").strip()
    if not re.match(REGEX_ITEM_PRICE, item_price): raise_custom_exception(error, 400)
    return item_price

##############################
# UPLOAD_ITEM_FOLDER = './static/images'
UPLOAD_ITEM_FOLDER = './static/dishes'
ALLOWED_ITEM_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "avif"}

def validate_item_images():
    if 'item_files' not in request.files:
        raise_custom_exception("item_files missing", 400)

    files = request.files.getlist('item_files')
    if not files:
        raise_custom_exception("No files Uploaded", 400)

    validated_files =[]

    for file in files:
        if file.filename == "":
            raise_custom_exception("one of the item_files has an invalid name", 400)

        file_extension = os.path.splitext(file.filename)[1][1:].lower() #get file extension
        if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS:
            raise_custom_exception(f"item_file '{file.filename} has an invalid extension", 400)

        #generate a unique filename
        filename = 'dish_' + str(uuid.uuid4()) + '.' + file_extension

        #add to the validated list
        validated_files.append((file, filename))
    
    return validated_files


# def validate_item_image():
#     if 'item_file' not in request.files: raise_custom_exception("item_file missing", 400)
#     file = request.files.get("item_file", "")
#     if file.filename == "": raise_custom_exception("item_file name invalid", 400)

#     if file:
#         ic(file.filename)
#         file_extension = os.path.splitext(file.filename)[1][1:]
#         ic(file_extension)
#         if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS: raise_custom_exception("item_file invalid extension", 400)
#         filename = str(uuid.uuid4()) + file_extension
#         return file, filename 


##############################
def send_verify_email(to_email, user_verification_key):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords


        # Email and password of the sender's Gmail account
        sender_email = "wolteksamen@gmail.com"
        password = "hkgr nsno teuw ujiq"  # If 2FA is on, use an App Password instead

        # Receiver email address
        receiver_email = "wolteksamen@gmail.com"
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "Wolt"
        message["To"] = receiver_email
        message["Subject"] = "Please verify your account"

        # Body of the email
        body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        return "email sent"
    
    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass

##############################

def send_recipt_email(cart):
    try:
        # Sender's email and password (use environment variables for sensitive info)
        sender_email = "wolteksamen@gmail.com"
        password = "hkgr nsno teuw ujiq"  # Use an App Password if 2FA is enabled

        # Receiver email address (this will still be your email for testing)
        receiver_email = "wolteksamen@gmail.com"

        # Create the email message
        message = MIMEMultipart()
        message["From"] = "Wolt"
        message["To"] = receiver_email
        message["Subject"] = "Thank you for your order with Wolt!"

        # Create the body of the email dynamically
        body = "<p>Thank you for your order! Here are the details:</p><ul>"

        # Loop through the cart to build the order details list
        for item in cart:
            body += f"<li>{item['item_title']} - {item['item_price']} kr</li>"
        
        body += "</ul><p>Your order has been received and is being processed. We will send you another update when it's shipped.</p>"

        # Attach the email body
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print("Email sent successfully!")
        return "Email sent"
    
    except Exception as ex:
        print("Error sending email:", ex)
        raise Exception("Cannot send email", 500)


###############################
def send_action_email(to_email, action, entity):
    """
    Send an email notification for an action (block/unblock) on an entity (user/item).

    :param to_email: The recipient email (e.g., admin)
    :param action: The action performed (e.g., 'blocked', 'unblocked')
    :param entity: The entity type (e.g., 'user', 'item')
    """
    try:
        sender_email = "wolteksamen@gmail.com" # Erstat med jeres egen email 
        password = "hkgr nsno teuw ujiq"  # Erstat med jeres egen  

        subject = f"{entity.capitalize()} {action.capitalize()}"
        body = f"The {entity} has been {action} successfully by the admin."

        # Email besked
        message = MIMEMultipart()
        message["From"] = "Wolt Admin"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        # Sender en email via Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())
        print(f"Email sent to {to_email}: {subject}")

    except Exception as ex:
        print(f"Error sending email: {ex}")


############ RESET KEY ############
def send_reset_email(to_email, reset_key):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords


        # Email and password of the sender's Gmail account
        sender_email = "wolteksamen@gmail.com"  # Erstat med jeres egen email 
        password = "hkgr nsno teuw ujiq"  # If 2FA is on, use an App Password instead # Erstat med jeres egen kode 

        # Receiver email address
        receiver_email = "wolteksamen@gmail.com"
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "Wolt"
        message["To"] = receiver_email
        message["Subject"] = "Reset your password"

        # Body of the email
        # body = f"""To reset your password, please <a href="http://127.0.0.1/reset-password/{reset_key}">click here</a>"""
        # message.attach(MIMEText(body, "html"))

        body = f"""To reset your password, please <a href="http://127.0.0.1/reset-password/{reset_key}">click here</a>"""
        message.attach(MIMEText(body, "html"))


        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        return "email sent"
    
    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass

def send_account_deletion_email(to_email, deleted_at):

    try:
        sender_email = "wolteksamen@gmail.com"
        password = "hkgr nsno teuw ujiq"  # Replace with your Gmail App Password

        # Receiver email address
        receiver_email = "wolteksamen@gmail.com"

        # Create the email message
        message = MIMEMultipart()
        message["From"] = "Your App Team"
        message["To"] = to_email
        message["Subject"] = "Your Account Has Been Deleted"

        # Body of the email
        body = f"""
        Hello,

        This is to confirm that your account was successfully deleted on 
        {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(deleted_at))}.
        
        If you did not request this deletion, please contact our support team immediately.

        Best regards,  
        Your App Team
        """
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print(f"Account deletion email sent successfully to {to_email}")
        return "Email sent successfully."

    except Exception as e:
        print(f"Error sending account deletion email: {e}")
        raise_custom_exception("Failed to send account deletion email", 500)