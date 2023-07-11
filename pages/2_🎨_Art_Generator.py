from _artist import art_generator
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from environment import load_env_variables, get_api_key
import dropbox
from cloud import display_art_and_save_to_database
from database import fetch_all_art


TITLE = "Photo Artist"
ABOUT = """
    Welcome to Photo Artist, where creativity meets artificial intelligence. Our innovative platform harnesses the power of ChatGPT, Stable Diffusion, and DALL-E to create captivating art experiences.

    With Photo Artist, you can input your artistic ideas, and ChatGPT will generate a written textual representation of your vision. This unique collaboration between human imagination and AI algorithms brings your ideas to life in a new and exciting way.

    But that's not all. We go beyond words and venture into the realm of visuals. Through the integration of Stable Diffusion and DALL-E, our platform transforms those textual representations into breathtaking images. Prepare to be amazed as your artistic concepts materialize into stunning visuals.

    Unleash your creativity with Photo Artist and witness the synergy of AI and human imagination. Explore the possibilities, immerse yourself in the realm of art, and discover the beauty of AI-assisted creation. Start your artistic journey today and experience the magic of our platform.
    """
about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

IMAGE_FOLDER = "images"

st.set_page_config(
    page_icon="🎨",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

with st.sidebar:
    st.title(TITLE)
    st.markdown(ABOUT)
    add_vertical_space(1)
    st.write("💡 Note: API keys required!!")


if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    load_env_variables()
    # Dropbox keys
    APP_KEY = get_api_key("APP_KEY")
    APP_SECRET = get_api_key("APP_SECRET")
    DROPBOX_REFRESH_TOKEN = get_api_key("DROPBOX_REFRESH_TOKEN")
    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    )

    def art_form():
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""
        if "user_input_name" not in st.session_state:
            st.session_state.user_input_name = ""

        st.sidebar.markdown("Stable Diffusion Settings")

        size = st.sidebar.select_slider(
            "Image Size",
            (
                "896x512",
                "768x512",
                "683x512",
                "640x512",
                "512x512",
                "512x640",
                "512x683",
                "512x768",
                "512x896",
            ),
            value="512x512",
        )

        width, height = map(int, size.split("x"))

        samples = st.sidebar.slider("Samples", 0, 10, 2, 1)
        steps = st.sidebar.slider("Steps", 30, 100, 50, 1)
        engine = st.sidebar.selectbox(
            "Engine",
            (
                "stable-diffusion-v1-5",
                "stable-diffusion-512-v2-1",
                "stable-diffusion-768-v2-1",
                "stable-diffusion-xl-beta-v2-2-2",
            ),
            3,
        )

        with st.form("Art", clear_on_submit=True):
            st.session_state.user_input = st.text_area(
                "Submit a Description of an Art to Generate:",
                value="",
            )
            st.session_state.user_input_name = st.text_input(
                "**Name your Art:**",
                value="",
            )

            add_vertical_space(1)

            user_input_name_button = st.form_submit_button("Submit")

        if user_input_name_button:
            st.info(st.session_state.user_input)
            st.info(st.session_state.user_input_name)
            art_generator(
                st.session_state.user_input,
                st.session_state.user_input_name,
                width,
                height,
                engine,
                samples,
                steps,
            )
            display_art_and_save_to_database(1)
            st.experimental_rerun()

    # Run the app
    if __name__ == "__main__":
        art_form()
        fetch_all_art()
