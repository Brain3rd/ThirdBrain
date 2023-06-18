import os
import openai
from typing import List
import time
import requests
import base64
import dropbox
import streamlit as st
import environment as env


# Openai Keys
env.load_env_variables()
openai.api_key = env.get_api_key("OPENAI_API_KEY")


# Stable.ai Keys
api_host = os.getenv("API_HOST", "https://api.stability.ai")
url = f"{api_host}/v1/user/account"
engine_id = "stable-diffusion-v1-5"
api_key = env.get_api_key("STABILITY_API_KEY")
if api_key is None:
    raise Exception("Missing Stability API key.")


# Dropbox Keys
APP_KEY = env.get_api_key("APP_KEY")
APP_SECRET = env.get_api_key("APP_SECRET")
DROPBOX_REFRESH_TOKEN = env.get_api_key("DROPBOX_REFRESH_TOKEN")


dbx = dropbox.Dropbox(
    app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
)


# Looping parameters for error handling
MAX_ATTEMPTS = 2
DELAY_SECONDS = 10


def read_file_contents():
    try:
        # List all files and folders in the /books folder of Dropbox
        result = dbx.files_list_folder("/images", recursive=True)
        entries = result.entries
    except dropbox.exceptions.AuthError as e:
        # Handle authentication error
        # st.error(f"Dropbox authentication failed: {e}")
        return

    # Filter out folders from the entries
    folders = [
        entry for entry in entries if isinstance(entry, dropbox.files.FolderMetadata)
    ]

    all_folders = set()  # Use a set to store unique folder names

    for folder in folders:
        folder_name = os.path.basename(folder.path_display).replace("_", " ")
        if folder_name != "images":
            all_folders.add(folder_name)  # Add the folder name to the set

    return list(all_folders)


all_images = read_file_contents()


def get_image_prompt(user_input):
    st.sidebar.info("Creating prompt for the images...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
            As a seasoned artist and photographer, you possess extensive expertise and skill honed over the years. Your journey has been filled with invaluable experiences, where you've embraced failures as valuable lessons and triumphed in your pursuit of capturing breathtaking visuals. 
            """,
                    },
                    {
                        "role": "user",
                        "content": f"Generate a short, under 400 characters long, written textual representation of an art piece using keywords from the user input: {user_input}",
                    },
                    {
                        "role": "assistant",
                        "content": """
            Generate a short written textual representation of the art piece that captures the essence, mood, and theme of the user input. Incorporate key terms extracted from the provided input. Consider a suitable color scheme that aligns with the intended atmosphere. Use evocative language to describe visuals that reflect the plot, themes, or significant elements of the input. The output should not contain any images, only a textual representation of an art piece. Avoid any apologies or examples.

            Here are 10 great examples of textual representation of art pieces that you can learn from:

            1. Capture a vibrant street photograph of a bustling cityscape at night. Emphasize the colorful neon lights and the energy of the urban environment. Use long exposure techniques to create light trails and convey a sense of movement. Experiment with different angles and perspectives to capture a unique composition. Urban cityscape, Futuristic architecture, Dynamic motion blur, Vibrant street art.

            2. Take a breathtaking landscape photo of a serene mountain range at sunrise. Highlight the majestic peaks and the soft, warm glow of the rising sun. Incorporate elements of nature, such as trees or a flowing river, to add depth and interest to the composition. Use a wiSde-angle lens to capture the expansive beauty of the scene. Atmospheric landscape, Tranquil seascape, Serene mountainscapes, Subtle morning mist.

            3. Create an artistic still life photograph featuring a bouquet of colorful flowers in a vintage vase. Experiment with lighting techniques to create dramatic shadows and highlights. Play with composition and depth of field to draw attention to specific flowers or details. Aim for a visually striking image that evokes emotions. Detailed botanicals, Bold pop art, Subtle pastel tones, Whimsical illustrations.

            4. Capture a candid moment of joy and laughter between friends in a natural outdoor setting. Aim to convey the warmth and connection shared among them. Use natural light and a shallow depth of field to create a soft, dreamy atmosphere. Look for genuine expressions and interactions to capture the essence of friendship. Captivating wildlife, Emotional storytelling, Playful patterns, Nostalgic memories.

            5. Take a captivating wildlife photograph showcasing the beauty and grace of a wild animal in its natural habitat. Pay attention to details such as the animal's fur, feathers, or scales. Capture the animal in action or at rest, conveying its unique characteristics and behavior. Use a telephoto lens for close-up shots and a fast shutter speed to freeze motion.  Captivating wildlife, Expressive emotions, Dynamic action, Whimsical creatures.

            6. Create a striking abstract photograph using unconventional objects and textures. Look for interesting patterns, shapes, or colors in your surroundings. Experiment with different angles, lighting, and compositions to create a visually intriguing image that sparks curiosity and imagination. Abstract geometric, Subtle monochrome, Whimsical illustrations, Organic textures.

            7. Capture a powerful black and white portrait of an elderly person with wrinkles and weathered features. Aim to convey their life story and wisdom through their expression and character. Utilize dramatic lighting techniques and strong contrasts to add depth and intensity to the image. Focus on capturing the essence of their unique personality. Dramatic portrait, Haunting beauty, Expressive emotions, Mysterious shadows.

            8. Take a conceptual photograph that symbolizes freedom and exploration. Use props or elements that represent adventure and discovery. Experiment with composition and lighting to create a visually compelling image that inspires a sense of wanderlust and possibility. Conceptual symbolism, Ethereal fantasy, Dynamic action, Mystical forests.

            9. Create an ethereal, dreamlike photograph featuring a dancer in motion. Utilize flowing fabrics, soft lighting, and long exposure techniques to capture the grace and fluidity of the dance. Aim to convey a sense of beauty, movement, and emotion in the image. Whimsical creatures, Surreal dreamscape, Expressive emotions, Dynamic motion blur.

            10. Capture a unique architectural photograph that highlights the symmetry, lines, and textures of a modern building. Look for interesting angles and perspectives to showcase the building's design and aesthetics. Experiment with different lighting conditions to create a mood that complements the architecture. Futuristic architecture, Industrial urban, Architectural symmetry, Dramatic city skylines.

            Please bear in mind that the aforementioned illustrations serve as a reference and a source of inspiration. It is crucial to employ ARTISTIC and PHOTOGRAPHIC vocabulary in crafting a distinct and customized textual depiction that aligns with the user input and themes.

            """,
                    },
                ],
                model="gpt-3.5-turbo",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    image_prompt = response["choices"][0]["message"]["content"]

    st.sidebar.success(image_prompt)
    return image_prompt


def create_dalle_image(prompt):
    st.sidebar.info("Drawing DALL-E image...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            dalle_data = openai.Image.create(
                prompt=prompt,
                n=2,
                size="512x512",
                response_format="b64_json",  # Get image data instead of url
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    # Return url instead of b64_json
    # image_url = image_response["data"][0]["url"]

    st.sidebar.success("DALL-E image created!")
    return dalle_data


def create_stable_image(prompt):
    st.sidebar.info("Drawing Stable image...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                f"{api_host}/v1/generation/{engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "text_prompts": [{"text": f"{prompt}"}],
                    "cfg_scale": 7,
                    "clip_guidance_preset": "FAST_BLUE",
                    "height": 512,
                    "width": 512,
                    "samples": 2,
                    "steps": 50,
                },
            )

            if response.status_code != 200:
                stable_data = "No stability book"
                st.sidebar.error("Stable not in a drawing mood today")
                raise Exception("Non-200 response: " + str(response.text))
            else:
                stable_data = response.json()

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle the specific exception (if known) or catch all exceptions
            st.sidebar.error(
                f"Attempt {attempt} failed. Waiting a bit and trying again..."
            )

        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    st.sidebar.success("Stable image created!")

    return stable_data


def save_all(image_name, image_prompt, dalle_data, stability_data):
    dalle_arts = []
    stable_arts = []

    try:
        # Create a new folder for the book in Dropbox
        folder_path = f"/images/{image_name}"

        # Check if the folder already exists
        try:
            dbx.files_get_metadata(folder_path)
        except dropbox.exceptions.ApiError as e:
            if (
                isinstance(e.error, dropbox.files.GetMetadataError)
                and e.error.is_path()
                and e.error.get_path().is_not_found()
            ):
                # Folder does not exist, create it
                dbx.files_create_folder(folder_path)
            else:
                # Unexpected error, raise it
                raise e

        # Save image prompt to txt file
        art_path = f"{folder_path}/{image_name}.txt"
        data_to_txt = f"Image prompt: {image_prompt}"
        dbx.files_upload(data_to_txt.encode("utf-8"), art_path)

        # Save DALL-E images to png
        for i, image in enumerate(dalle_data["data"]):
            image_path = f"{folder_path}/{image_name}_dalle_{i}.png"
            image_data = base64.b64decode(image["b64_json"])
            dbx.files_upload(image_data, image_path)
            dalle_arts.append(image_data)

        # Save Stability images to png
        if stability_data != "No stability art":
            for i, image in enumerate(stability_data["artifacts"]):
                image_path = f"{folder_path}/{image_name}_stability_{i}.png"
                image_data = base64.b64decode(image["base64"])
                dbx.files_upload(image_data, image_path)
                stable_arts.append(image_data)

    except Exception as e:
        # Handle the specific exception (if known) or catch all exceptions
        st.sidebar.error(f"An error occurred while saving to Dropbox: {str(e)}")

    return dalle_arts, stable_arts


def art_gerator(art_input, art_name):
    if "dalle_art" not in st.session_state:
        st.session_state.dalle_art = ""
    if "stable_art" not in st.session_state:
        st.session_state.stable_art = ""
    if "art_expander" not in st.session_state:
        st.session_state.art_expander = ""

    art_prompt = get_image_prompt(art_input)
    dalle_art = create_dalle_image(art_prompt)
    stable_art = create_stable_image(art_prompt)

    st.session_state.dalle_art, st.session_state.stable_art = save_all(
        art_name, art_prompt, dalle_art, stable_art
    )

    st.session_state.art_expander = st.expander(art_name)
    with st.session_state.art_expander:
        # Display DALL-E images
        for image_data in st.session_state.dalle_art:
            st.image(image_data)

        # Display stability images
        for image_data in st.session_state.stable_art:
            st.image(image_data)

        st.title(art_name)
        st.write(art_prompt)

    st.sidebar.success("Art Generated!")
