import os
import openai
from typing import List
import time
import requests
import base64
import dropbox
import streamlit as st
from environment import load_env_variables, get_api_key


# Openai Keys
load_env_variables()
openai.api_key = get_api_key("OPENAI_API_KEY")


# Stable.ai Keys
api_host = os.getenv("API_HOST", "https://api.stability.ai")
url = f"{api_host}/v1/user/account"
engine_id = "stable-diffusion-v1-5"
api_key = get_api_key("STABILITY_API_KEY")
if api_key is None:
    raise Exception("Missing Stability API key.")


# Dropbox Keys
APP_KEY = get_api_key("APP_KEY")
APP_SECRET = get_api_key("APP_SECRET")
DROPBOX_REFRESH_TOKEN = get_api_key("DROPBOX_REFRESH_TOKEN")


dbx = dropbox.Dropbox(
    app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
)


# Looping parameters for error handling
MAX_ATTEMPTS = 2
DELAY_SECONDS = 10


def read_file_contents():
    try:
        # List all files and folders in the /books folder of Dropbox
        result = dbx.files_list_folder("/books", recursive=True)
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
        if folder_name != "books":
            all_folders.add(folder_name)  # Add the folder name to the set

    return list(all_folders)


all_books = read_file_contents()


# Get random book
def book_picker():
    books = [
        {
            "role": "system",
            "content": f"""
            You are a professional life coach with great knowledge of charisma and leadership. Having witnessed a wide range of experiences, overcome challenges, and achieved success in life, you will choose books that teach users to better their lives.
        """,
        },
        {
            "role": "user",
            "content": f"""
        Give me a 1 random book from all time best selling self help books.
        Different than these books:
        {all_books}
        """,
        },
        {
            "role": "assistant",
            "content": """
        Desired format:
        Book Title by Author Name

        Undesired format:
        "Book Title" by Aurhor name
        Book Title: Author name
        """,
        },
        {
            "role": "assistant",
            "content": """
        Just 1 book, no more. Give me just text in form of derired format, notthing else. No = or . or : either. 

        Example template:
        Unlimited Power by Tony Robbins

        Another example:
        Brain Rules 12 Principles for Surviving and Thriving at Work Home and School by John Medina
        """,
        },
    ]
    return books


def get_book(books):
    st.sidebar.info("Selecting random book...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=books, model="gpt-3.5-turbo", max_tokens=50
            )
            book = (
                response["choices"][0]["message"]["content"]
                .replace(".", "")
                .replace("=", "")
                .replace(":", "")
                .replace("'", "")
                .replace(",", "")
                .replace('"', "")
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

    while book in all_books:
        # Book has already been  selected, choose a different one
        st.sidebar.warning(
            "Oh, you've read this book already. Choosing a different book..."
        )

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = openai.ChatCompletion.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            You are a professional life coach with great knowledge of charisma and leadership. Having witnessed a wide range of experiences, overcome challenges, and achieved success in life, you will choose books that teach users to better their lives.
                        """,
                        },
                        {
                            "role": "user",
                            "content": f"""
                        I have read this book already, please give me 1 different book. Different than these books: {all_books}
                        """,
                        },
                        {
                            "role": "assistant",
                            "content": """
                        Desired format:
                        Book Title by Author Name

                        Undesired format:
                        "Book Title" by Aurhor name
                        Book Title: Author name
                        """,
                        },
                        {
                            "role": "assistant",
                            "content": """
                        Just 1 book, no more. Give me just text in form of desired format, nothing else. No = or . or : either. 

                        Example template:
                        Unlimited Power by Tony Robbins

                        Another example:
                        Brain Rules 12 Principles for Surviving and Thriving at Work Home and School by John Medina

                        """,
                        },
                    ],
                    model="gpt-3.5-turbo",
                    max_tokens=50,
                )
                book = (
                    response["choices"][0]["message"]["content"]
                    .replace(".", "")
                    .replace("=", "")
                    .replace(":", "")
                    .replace("'", "")
                    .replace(",", "")
                    .replace('"', "")
                )
                # If the code execution is successful, break out of the loop
                if book not in all_books:
                    break
            except Exception as e:
                # Handle RateLimitError
                st.sidebar.error(
                    f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
                )
            # Wait for the specified delay before the next attempt
            time.sleep(DELAY_SECONDS)

    st.sidebar.success(f"{book}")

    return book


def summarize_book(book: str) -> str:
    st.sidebar.info("Summarizing...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are a professional writer and book summarizer. To write effective content, both "perplexity" and "burstiness" are important. Perplexity assesses text complexity and burstiness evaluates sentence variation. People often write with a mix of long and short sentences, while machine-generated sentences tend to be uniform. You need to ensure a suitable balance of both perplexity and burstiness.

                    Remember that while summarizing, it's crucial to maintain the integrity of the author's ideas and voice. Use your own words to explain the concepts, but ensure that you capture the essence of the original content accurately.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this book: {book}",
                    },
                    {
                        "role": "assistant",
                        "content": """
                    You are an assistant that speaks only in Markdown code. Do not write text that is not formatted as Markdown code.
                    Desired format:
                    ## Introduction
                    Provide a brief overview of the book's purpose, author's background, and any relevant context.
                    ## Key points
                    Identify the main concepts or ideas presented in the book. Summarize each key point concisely and clearly. Use bullet points or numbered lists to organize the information.
                    ## Insights and Examples
                    Highlight the most insightful and impactful moments from the book. Explain how these insights can be applied in real-life situations. Provide relevant examples or anecdotes to illustrate the author's ideas.
                    ## Practical Application
                    Offer practical steps or strategies derived from the book's teachings. Describe how readers can implement the ideas in their own lives. Include actionable tips or exercises to reinforce the concepts.
                    ## Quotes
                    Select notable quotes from the author that encapsulate important concepts or provide inspiration. Use quotation marks and attribute the quotes to the author, "Quote" Author Name
                    ## Conclusion
                    Summarize the overall message of the book. Express your own thoughts and reflections on the book's content and potential impact.
                    ### Tags
                    Add tags based on the mood or emotion of the book.
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

    summary = response["choices"][0]["message"]["content"]

    st.sidebar.success("Book summarized!")

    return summary


def get_cover_prompt(book):
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
                        "content": f"Generate a short, under 400 characters long, written textual representation of an art piece using keywords from the book summary: {book}",
                    },
                    {
                        "role": "assistant",
                        "content": """
            Generate a short written textual representation of the art piece that captures the essence, mood, and theme of the book. Incorporate key terms extracted from the provided summary. Consider a suitable color scheme that aligns with the intended atmosphere. Use evocative language to describe visuals that reflect the plot, themes, or significant elements of the book. The output should not contain any images, only a textual representation of an art piece. Avoid any apologies or examples.

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

            Please bear in mind that the aforementioned illustrations serve as a reference and a source of inspiration. It is crucial to employ keywords and vocabulary that aligns with the user input and themes.

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


def create_dalle_image(prompt, samples):
    st.sidebar.info("Drawing DALL-E image...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            image_response = openai.Image.create(
                prompt=prompt,
                n=samples,
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
    return image_response


def create_stable_image(prompt, width, height, engine_id, samples, steps):
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
                    "height": height,
                    "width": width,
                    "samples": samples,
                    "steps": steps,
                },
            )

            if response.status_code != 200:
                data = "No stability book"
                st.sidebar.error("Stable not in a drawing mood today")
                raise Exception("Non-200 response: " + str(response.text))
            else:
                data = response.json()

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

    return data


def save_all(
    new_book,
    book_content,
    dalle_data,
    stability_data,
    image_prompt,
    engine,
    width,
    height,
):
    dalle_images = []
    stability_images = []

    try:
        # Create a new folder for the book in Dropbox
        folder_path = f"/books/{new_book}"

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

        # Save summary to txt file
        summary_path = f"{folder_path}/{new_book}.txt"
        data_to_txt = f"""
        **Prompt:** {image_prompt}\n\n**Stable Diffusion:** {engine} {width}x{height}\n\n**DALL-E:** 512x512\n\n{book_content}
        """
        dbx.files_upload(data_to_txt.encode("utf-8"), summary_path)

        # Save DALL-E images to png
        for i, image in enumerate(dalle_data["data"]):
            image_path = f"{folder_path}/{new_book}_dalle_{i}.png"
            image_data = base64.b64decode(image["b64_json"])
            dbx.files_upload(image_data, image_path)
            dalle_images.append(image_data)

        # Save Stability images to png
        if stability_data != "No stability book":
            for i, image in enumerate(stability_data["artifacts"]):
                image_path = f"{folder_path}/{new_book}_stability_{i}.png"
                image_data = base64.b64decode(image["base64"])
                dbx.files_upload(image_data, image_path)
                stability_images.append(image_data)

    except Exception as e:
        # Handle the specific exception (if known) or catch all exceptions
        st.sidebar.error(f"An error occurred while saving to Dropbox: {str(e)}")

    return dalle_images, stability_images


def summarizer(book_input, width, height, engine, samples, steps):
    if "new_expander" not in st.session_state:
        st.session_state.new_expander = ""
    if "new_book" not in st.session_state:
        st.session_state.new_book = ""
    if "book_summary" not in st.session_state:
        st.session_state.book_summary = ""
    if "dalle_cover" not in st.session_state:
        st.session_state.dalle_cover = ""
    if "stable_cover" not in st.session_state:
        st.session_state.stable_cover = ""

    st.sidebar.info("Summarizanion progress started...")
    if book_input == "":
        books = book_picker()
        st.session_state.new_book = get_book(books)
    else:
        st.session_state.new_book = book_input
        all_books.append(st.session_state.new_book)

    st.session_state.book_summary = summarize_book(st.session_state.new_book)
    book_content = f"{st.session_state.new_book}\n\n{st.session_state.book_summary}"

    dalle_prompt = get_cover_prompt(book_content)
    dalle_image = create_dalle_image(dalle_prompt, samples)
    stable_image = create_stable_image(
        dalle_prompt, width, height, engine, samples, steps
    )

    st.session_state.dalle_cover, st.session_state.stable_cover = save_all(
        st.session_state.new_book,
        st.session_state.book_summary,
        dalle_image,
        stable_image,
        dalle_prompt,
        engine,
        width,
        height,
    )

    st.session_state.new_expander = st.expander(
        st.session_state.new_book, expanded=True
    )
    with st.session_state.new_expander:
        # Display DALL-E images
        for image_data in st.session_state.dalle_cover:
            st.image(image_data)

        # Display stability images
        for image_data in st.session_state.stable_cover:
            st.image(image_data)

        st.title(st.session_state.new_book)
        st.write(st.session_state.book_summary)

    st.sidebar.success("Book summarized!")


if __name__ == "__main__":
    summarizer()
