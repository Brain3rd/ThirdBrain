import streamlit as st
import streamlit_authenticator as stauth
import database as db


TITLE = "Book Summarizer - Third Brain"
ABOUT = """
    Welcome to Third Brain, your one-stop destination for self-development AI tools. Our website offers a wide range of powerful applications developed using Python and Streamlit. Whether you're looking to enhance your productivity, boost your creativity, or improve your personal growth, we've got you covered. Explore our collection of innovative AI tools designed to assist you on your journey towards self-improvement. With a perfect blend of cutting-edge technology and user-friendly interfaces, Third Brain is here to empower you on your path to success. Start your self-development journey today with our intuitive and transformative AI tools. 
    """
about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_title="Third Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""


users = db.fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]


authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords, "thirdbrain", "chocolate", cookie_expiry_days=20
)

name, st.session_state.authentication_status, username = authenticator.login(
    "Login", "main"
)


if st.session_state.authentication_status == False:
    st.error("Username / Password is Incorrect!")

if st.session_state.authentication_status == None:
    st.warning("Please enter you username and password")

if st.session_state.authentication_status:
    authenticator.logout("Logout", "sidebar")

    st.write("# Welcome to Third Brain with ChatGPT and other AI tools. 👋")

    st.sidebar.success("Select an App Above.")

    st.markdown(ABOUT)
