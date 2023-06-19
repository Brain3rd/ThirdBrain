import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
import math
import streamlit_authenticator as stauth
import database as db

TITLE = "Text Reader"
ABOUT = """
Welcome to the Text Reader App, a powerful tool designed for text reading and accessibility. Our app utilizes advanced AI text-to-speech features to bring written content to life.

With our Text Reader App, you can easily convert text into natural and expressive speech. Whether you have articles, documents, or even eBooks, our app empowers you to listen to your text-based content effortlessly. Enhance your reading experience, save time, and cater to diverse needs with our AI-powered text-to-speech capabilities.

Immerse yourself in the world of accessible information with the Text Reader App. Unlock the potential of AI to transform written content into engaging audio experiences. Start using our app today and embark on a new way of consuming text-based information.
    """

about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_icon="📙",
    page_title=TITLE,
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
    with st.sidebar:
        st.title(TITLE)
        st.markdown(ABOUT)
        add_vertical_space(2)
        st.write("💡 Note: API key required!")

    if "audio" not in st.session_state:
        st.session_state.audio = {}

    audiobook = st.selectbox(
        "Choose your book",
        list(st.session_state.audio.keys()),
    )

    # Create a button to play audiobook.
    if st.button(
        label="Read Book",  # name on the button
        help="Click to Read Book",  # hint text (on hover)
        key="read_audiobook",  # key to be used for the button
        type="primary",  # red default streamlit button
    ):
        selected_book = audiobook
        selected_file_content = st.session_state.audio[selected_book]

        # Perform the desired action with the selected book and its file content
        # For example, you can use text-to-speech to read the audiobook
        # or display the file content in another component

        # Display the images in columns with caption names
        image_urls = st.session_state.url[selected_book]
        num_images = len(image_urls)
        num_columns = 2  # Number of columns for the images
        num_rows = math.ceil(num_images / num_columns)

        col1, col2 = st.columns(2)  # Create two columns

        for i, url in enumerate(image_urls):
            # Determine the column to display the image based on the index
            if i % num_columns == 0:
                column = col1
            else:
                column = col2

            # Get the caption name from the image URL
            # caption = os.path.splitext(url.split("/")[-1])[0]

            # Display the image in the respective column with the caption name
            with column:
                st.image(url)

        # Display the text content
        st.write(selected_file_content)
