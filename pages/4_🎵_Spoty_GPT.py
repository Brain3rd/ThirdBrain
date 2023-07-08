import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import _mixer as mix


TITLE = "Spoti Mixer"
ABOUT = """
        🎵 Spoty GPT

        Spoty GPT is an innovative AI-powered tool that seamlessly integrates ChatGPT with Spotify. With Spoty GPT, you can effortlessly create personalized playlists with just one click.

        ✨ Personalized Song Selection:
        Spoty GPT utilizes the power of ChatGPT to curate a tailored selection of songs based on your input. Whether it's a mood, genre, artist, or theme, our AI-driven model understands your preferences and handpicks songs to suit your unique taste.

        💾 Automatic Playlist Saving:
        Once the playlist is generated, Spoty GPT automatically saves it to your Spotify account. With just one click, you can enjoy your personalized playlist across all your devices and seamlessly integrate it into your music library.

        Discover new tracks, rediscover old favorites, and let Spoty GPT enhance your musical journey. Experience the power of AI-driven song selection and effortlessly create personalized playlists that match your mood and style.
    """
about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_icon="📚",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

with st.sidebar:
    st.title(TITLE)
    st.markdown(ABOUT)
    add_vertical_space(2)
    st.write("💡 API keys required!!")


if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    new_playlist = st.form("New Playlist")
    with new_playlist:
        playlist_description = st.text_area("Describe the playlist")
        playlist_songs = st.text_input("How many songs")
        playlist_name = st.text_input("Name your playlist")
        playlist_button = st.form_submit_button("Submit")
        if playlist_button:
            with st.spinner("Creating your playlist..."):
                new_playlist = mix.generate_playlist(
                    playlist_description, playlist_songs
                )
                mix.spotify_playlist(new_playlist, playlist_name)
                st.success("Playlist is ready!")
