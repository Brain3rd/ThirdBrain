import environment as env
import openai
import json
import datetime
import spotipy
import streamlit as st


client_id = env.get_api_key("SPOTIFY_ID")
client_secret = env.get_api_key("SPOTIFY_SECRET")

if client_id == None or client_secret == None:
    raise ValueError(
        "Error: missing environment variables. Please check your env file."
    )


# Openai Keys
openai.api_key = env.get_api_key("OPENAI_API_KEY")


def generate_playlist(prompt, count):
    example_json = """
      [
          {"song": "Everybody Hurts", "artist": "R.E.M."},
          {"song": "Yesterday", "artist": "The Beatles"},
          {"song": "Tears in Heaven", "artist": "Eric Clapton"},
          {"song": "Hallelujah", "artist": "Jeff Buckley"},
          {"song": "Nothing Compares 2 U", "artist": "Sinead O'Connor"}
      ]
  """

    messages = [
        {
            "role": "system",
            "content": """
      You are a helpful playlist generating assistant.
      You should generate a list of songs and their artists according to a text prompt.
      You should return a JSON array, where each element follows this format: {"song": <song_title>, "asrtist": <artist_name>}
      """,
        },
        {
            "role": "user",
            "content": """
      Generate a playlist of 5 songs based on this prompt: super super sad songs
      """,
        },
        {
            "role": "assistant",
            "content": example_json,
        },
        {
            "role": "user",
            "content": f"""
      Generate a playlist of {count}songs based on this prompt: {prompt}
      """,
        },
        {
            "role": "assistant",
            "content": "Return just a JSON array, nothing else. No text before, no text after.",
        },
    ]

    response = openai.ChatCompletion.create(
        messages=messages, model="gpt-3.5-turbo", max_tokens=400
    )

    output = response["choices"][0]["message"]["content"]
    playlist = json.loads(output)
    st.success("ChatGPT has selected the songs!")
    return playlist


def spotify_playlist(playlist: json, playlist_name: str, popularity: int):
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="https://share.streamlit.io/brain3rd/thirdbrain/callback",
            scope="playlist-modify-private",
        )
    )

    current_user = sp.current_user()

    assert current_user is not None

    track_uris = []
    for item in playlist:
        artist, song = item["artist"], item["song"]
        # https://developer.spotify.com/documentation/web-api/reference/#/operations/search

        advanced_query = f"artist:({artist}) track:({song})"
        basic_query = f"{song} {artist}"

        for query in [advanced_query, basic_query]:
            st.info(f"Searching from Spotify: {query}")
            search_results = sp.search(
                q=query, limit=10, type="track"
            )  # , market=market)

            if (
                not search_results["tracks"]["items"]
                or search_results["tracks"]["items"][0]["popularity"] < popularity
            ):
                continue
            else:
                good_guess = search_results["tracks"]["items"][0]
                st.success(f"Found: {good_guess['name']} [{good_guess['id']}]")
                # print(f"FOUND USING QUERY: {query}")
                track_uris.append(good_guess["id"])
                break

        else:
            st.info(
                f"Queries {advanced_query} and {basic_query} returned no good results. Skipping."
            )

    created_playlist = sp.user_playlist_create(
        current_user["id"],
        public=False,
        name=f"{playlist_name} ({datetime.datetime.now().strftime('%c')})",
    )

    sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], track_uris)

    st.success(f"Created playlist: {created_playlist['name']}")
    st.success(created_playlist["external_urls"]["spotify"])


def get_user_playlists():
    sp = spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://127.0.0.1:9999",
            scope="playlist-read-private",
            open_browser=False,
        )
    )

    playlists = sp.current_user_playlists(limit=50)
    all_playlists = []

    while playlists:
        for playlist in playlists["items"]:
            all_playlists.append(playlist)
        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None

    return all_playlists
