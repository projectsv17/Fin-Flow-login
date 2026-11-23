
import streamlit as st
import bcrypt
import mysql.connector
from mysql.connector import Error, IntegrityError

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Fin Flow AI",
    page_icon="",
    layout="centered"
)


# --------------------------------
# MYSQL CONNECTION
# --------------------------------

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )


# --------------------------------
# CREATE USERS TABLE
# --------------------------------

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


# --------------------------------
# REGISTER USER
# --------------------------------

def register_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            """,
            (username, hashed_password)
        )

        connection.commit()
        return True, "Registration successful!"

    except IntegrityError:
        return False, "Username already exists!"

    finally:
        cursor.close()
        connection.close()


# --------------------------------
# LOGIN USER
# --------------------------------

def verify_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = %s",
            (username,)
        )

        result = cursor.fetchone()

        if result is None:
            return False, "Username not found!"

        stored_password = result[0].encode("utf-8")

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password
        ):
            return True, "Login successful!"

        return False, "Incorrect password!"

    finally:
        cursor.close()
        connection.close()


# --------------------------------
# DATABASE INITIALIZATION
# --------------------------------

try:
    initialize_database()

except Error as e:
    st.error(f"Database connection error: {e}")
    st.stop()


# --------------------------------
# SESSION INITIALIZATION
# --------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "guest" not in st.session_state:
    st.session_state.guest = False


# --------------------------------
# APPLICATION TITLE
# --------------------------------

st.title("FIN FLOW AI")
st.caption("Your Daily Finance Partner")

st.divider()


# --------------------------------
# DASHBOARD
# --------------------------------

if st.session_state.logged_in:

    st.success(
        f"Welcome, {st.session_state.username}!"
    )

    if st.session_state.guest:
        st.info("You are using Fin Flow AI as a Guest.")

    st.subheader("Your Financial Dashboard")

    st.write(
        "Your financial management journey starts here!"
    )

    st.info(
        "Personal details and expense analysis "
        "will be added in the next development step."
    )

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.guest = False

        st.rerun()


# --------------------------------
# LOGIN AND REGISTRATION
# --------------------------------

else:

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    # LOGIN
    with login_tab:

        st.subheader("User Login")

        with st.form("login_form"):

            username = st.text_input(
                "Username",
                placeholder="Enter your username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:

                if not username or not password:
                    st.warning("Please enter username and password.")

                else:
                    try:
                        success, message = verify_user(
                            username.strip(),
                            password
                        )

                        if success:

                            st.session_state.logged_in = True
                            st.session_state.username = username.strip()
                            st.session_state.guest = False

                            st.success(message)
                            st.rerun()

                        else:
                            st.error(message)

                    except Error as e:
                        st.error(f"Database error: {e}")


    # REGISTRATION
    with register_tab:

        st.subheader("Create New Account")

        with st.form("register_form"):

            new_username = st.text_input(
                "Create Username"
            )

            new_password = st.text_input(
                "Create Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Register",
                use_container_width=True
            )

            if register_button:

                if not new_username.strip() or not new_password:
                    st.warning(
                        "Please enter username and password."
                    )

                elif new_password != confirm_password:
                    st.error("Passwords do not match!")

                elif len(new_password) < 8:
                    st.warning(
                        "Password must contain at least 8 characters."
                    )

                else:

                    try:
                        success, message = register_user(
                            new_username.strip(),
                            new_password
                        )

                        if success:
                            st.success(
                                message + " Now login using your account."
                            )
                        else:
                            st.error(message)

                    except Error as e:
                        st.error(f"Database error: {e}")


    st.divider()

    # GUEST LOGIN

    st.subheader("Try Fin Flow AI")

    if st.button(
        "👤 Login as Guest",
        use_container_width=True
    ):

        st.session_state.logged_in = True
        st.session_state.username = "Guest User"
        st.session_state.guest = True

        st.rerun()

    st.caption(
        "Guest access does not require registration."
    )
