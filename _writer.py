import openai
from environment import load_env_variables, get_api_key
import time
from database import (
    insert_ebook_title,
    insert_ebook_table_of_content,
    insert_ebook_chapter,
    insert_target_audience,
)
import streamlit as st


# Openai Keys
load_env_variables()
openai.api_key = get_api_key("OPENAI_API_KEY")


# Looping parameters for error handling
MAX_ATTEMPTS = 2
DELAY_SECONDS = 10


def new_ebook(user_input, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
            You are an esteemed best-selling book author known for your unique and engaging content that provides immense value to readers.
            """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Please, brainstorm book titles based on user input:
                        {user_input}
                        
                        and target audience:
                        {target_audience}

                        Using the user input and target audience provided, I kindly request your expertise in creating something that is completely distinct from any existing book title in the market. Utilize keyword research tools to identify popular search terms related to topic. Please provide me with ONE compelling title. Thank you.
                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
            Desired format:
            Title of Your Unique Book
                    """,
                    },
                ],
                model="gpt-3.5-turbo",
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    ebook_title = (
        response["choices"][0]["message"]["content"]
        .replace(":", "")
        .replace('"', "")
        .replace("?", "")
        .replace(".", "")
    )

    # Save to database
    insert_ebook_title(ebook_title)

    return ebook_title


def new_fiction_ebook(user_input, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
            You are an esteemed best-selling book author known for your unique and engaging content that provides immense value to readers.
            """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Please, brainstorm FICTION book titles based on user input:
                        {user_input}
                        
                        and target audience:
                        {target_audience}

                        Using the user input and target audience provided, I kindly request your expertise in creating something that is completely distinct from any existing book title in the market. Utilize keyword research tools to identify popular search terms related to topic. Please provide me with ONE compelling FICTION book title. Thank you.
                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
            Desired format:
            Title of Your Unique Book
                    """,
                    },
                ],
                model="gpt-3.5-turbo",
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    ebook_title = (
        response["choices"][0]["message"]["content"]
        .replace(":", "")
        .replace('"', "")
        .replace("?", "")
        .replace(".", "")
    )

    # Save to database
    insert_ebook_title(ebook_title)

    return ebook_title


def table_of_content(ebook, user_input, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are an accomplished best-selling Book author renowned for your ability to create engaging and valuable content. Remember that maintaining a suitable balance between perplexity and burstiness is crucial in crafting effective text. Perplexity assesses the complexity of the writing, while burstiness evaluates the variation in sentence structures. By incorporating a mix of long and short sentences, you can ensure a captivating reading experience for your audience.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Based on this user input:
                        {user_input} 

                        and this target audience:
                        {target_audience}

                        We have crafted unique book title:
                        {ebook}

                        Using the user input, target audience and book title provided, I kindly request your expertise in creating a captivating table of contents for this book. Consider how the content will best resonate with target audience and address their specific needs and interests. This process allows you to refine this book's angle, structure, and tone, ensuring that it captures the attention of target audience and provides them with the value they are seeking. Utilize keyword research tools to identify popular search terms related to this book. Thank you.
                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
                    Provide long, ind-depth and detailed table of contests and script for the book formatted in Markdown code. Avoid any apologies or compliments. Consider the overall arc of non-fiction eBook. Begin with main themes or key ideas that will form the basis for each chapter or section of the book. Within each chapter, ALWAYS include NUMBERED subtopics that expand on the main theme which allow to dig deeper into each subject, providing valuable insights and practical advice. 
                    
                    # {ebook} 
                    *Include your author name or pen name and any relevant subtitle or tagline.*

                    Table of Contents:
                    ## Table of Contents

                    *List the main chapters, sections and subsections of the book. Add 15 chapters with 5 sections each, add subsections as needed.
                    1. Introduction
                    2. Chapter
                        - 2.1 Section
                        - 2.2 Section 
                        - 2.3 Section
                    3. Chapter
                        - 3.1 Section
                            -3.1.1 Subsection
                            -3.1.2 Subsection
                        - 3.2 Section
                            -3.2.1 Subsection
                        - 3.3 Section
                    4. Chapter
                        - Sections
                            - Subsections
                    5. *Continue adding chapters with sections and subsections*
                    16. Conclusion
                    17. Q&A Section
                    18. Additional Resources/Appendix (optional)
                    """,
                    },
                ],
                model="gpt-3.5-turbo-16k",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    content = response["choices"][0]["message"]["content"]

    # Save to database
    insert_ebook_table_of_content(ebook, content)
    insert_target_audience(ebook, target_audience)

    return content


def manuscript(table_of_content, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are an accomplished best-selling Book author renowned for your ability to create engaging and valuable content. Remember that maintaining a suitable balance between perplexity and burstiness is crucial in crafting effective text. Perplexity assesses the complexity of the writing, while burstiness evaluates the variation in sentence structures. By incorporating a mix of long and short sentences, you can ensure a captivating reading experience for your audience.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        For this books table of content:
                        {table_of_content}

                        And target audience:
                        {target_audience}

                        I kindly request your expertise in creating a captivating manuscript for this book. Consider how the content will best resonate with target audience and address their specific needs and interests. This process allows you to refine this book's angle, structure, and tone, ensuring that it captures the attention of target audience and provides them with the value they are seeking.

                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
                        Provide long in-depth and detailed manuscript for the book formatted in Markdown code. Consider the overall arc of non-fiction book. Begin with main themes or key ideas that will form the basis for each chapter or section of the book. Within each chapter, include subtopics that expand on the main theme which allow to dig deeper into each subject, providing valuable insights and practical advice.

                        Who ever will read this manuscript should have clear instructions what to write and how to write it. Remember to maintain logical progression, allowing ideas to build upon one another and creating a sense of continuity. Consider incorporating storytelling elements or personal anecdotes that relate to each chapter's theme. This will help in establishing an emotional connection with readers. Futhermore, for example, if one chapter has mentioned a character, in the next chapter it should be mentioned so there is a continuum. Aim to add all necessary details with EACH section inside of a chapter, so that if previous chapter is forgotten, the writer can continue the story with all it characters, and details by following the manuscript.

                        - Create a compelling story that is related to the book.
                        - Analyze the key events and obstacles encountered in the story.
                        - Highlight the strategies, mindset, and actions taken by the character to overcome adversity.
                        - Extract the valuable lessons and insights gained from the story.
                        - Discuss the broader implications and relevance of these lessons in everyday life.
                        - Provide practical advice and strategies on how readers can cultivate perseverance in their own lives.
                        - Offer actionable steps and exercises to develop a resilient mindset and overcome obstacles.
                        - Q&A section
                            - Answer frequently asked questions related to perseverance and resilience.
                            - Address common challenges and concerns that readers may have.
                        - Additional Resources/Appendix (optional)
                            -Include any relevant resources, links, or references that can further enhance the reader's understanding or provide additional value.
                    """,
                    },
                ],
                model="gpt-3.5-turbo-16k",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    content = response["choices"][0]["message"]["content"]

    return content


def fiction_manuscript(ebook, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are an accomplished best-selling Book author renowned for your ability to create engaging and valuable content. Remember that maintaining a suitable balance between perplexity and burstiness is crucial in crafting effective text. Perplexity assesses the complexity of the writing, while burstiness evaluates the variation in sentence structures. By incorporating a mix of long and short sentences, you can ensure a captivating reading experience for your audience.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        For this fiction book:
                        {ebook}

                        And target audience:
                        {target_audience}

                        I kindly request your expertise in creating a captivating FICTION manuscript for book I am going to write. Consider how the content will best resonate with target audience and address their specific needs and interests. This process allows you to refine this book's angle, structure, and tone, ensuring that it captures the attention of target audience and provides them with the value they are seeking.

                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
                        Provide LONG, in-depth and detailed FICTION manuscript for the book formatted in Markdown code. Consider the overall arc of FICTION book. Split each chapter in to a smaller peaces, so it is easier to write small chunk at a time.

                        Who ever will read this manuscript should have clear instructions what to write and how to write it. Remember to maintain logical progression, allowing ideas to build upon one another and creating a sense of continuity. Futhermore, for example, if one chapter has mentioned a character, in the next chapter it should be mentioned so there is a continuum. Aim to add all necessary details with EACH section inside of a chapter, so that if previous chapter is forgotten, the writer can continue the story with all it characters, and details by following the manuscript.

                        - Craft a captivating story that hooks the readers from the beginning and keeps them engaged throughout.
                        - Develop a series of pivotal events and challenges that the characters face as they progress through the story.
                        - Explore the character's inner thoughts, emotions, and motivations as they navigate and overcome these obstacles.
                        - Extract meaningful themes and messages from the story that resonate with readers.
                        - Delve into the broader implications and relevance of these themes within the fictional world you've created.
                        - Introduce creative methods and techniques within the narrative that characters employ to tackle adversity.
                        - Provide readers with inspiring and relatable characters that embody perseverance and resilience.
                        - Include moments of personal growth and self-discovery for the characters, showcasing the transformative power of resilience.
                        - Incorporate moments of tension and suspense to heighten the readers' emotional investment in the story.
                        - Provide readers with actionable steps or exercises woven into the story that can help them develop a resilient mindset and overcome challenges.

                        Example format:
                        ## Prologue
                        *A brief introductory section that sets the stage or provides background information for the story. This section is typically shorter than a regular chapter and can vary in length depending on its purpose.*

                        ### Chapters
                        *Add at least 30 chapters.*

                        ## Epilogue
                        *A concluding section that offers closure or a glimpse into the characters' future after the main events of the story have concluded. Similar to the prologue, the length of the epilogue can vary.*
                    """,
                    },
                ],
                model="gpt-3.5-turbo-16k",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    content = response["choices"][0]["message"]["content"]

    # Save to database
    insert_ebook_table_of_content(ebook, content)
    insert_target_audience(ebook, target_audience)

    return content


def write_chapter(ebook, chapter_nro, chapter_to_write, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are a highly acclaimed best-selling author, renowned for your exceptional storytelling abilities and captivating prose. You have been focusing on self help books, learned your from mistakes and eventually succeeded. Remember that maintaining a suitable balance between perplexity and burstiness is crucial in crafting effective text. Perplexity assesses the complexity of the writing, while burstiness evaluates the variation in sentence structures. By incorporating a mix of long and short sentences, you can ensure a captivating reading experience for your audience.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                    I would greatly appreciate if you could write the following section of my book {ebook}:
                    {chapter_to_write} 
                    """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""                      

                    Write long in-depth with markdown. Remember you are writing section of the book, so write LONG paragraphs, NO bullet points or numbered lists. You can use bold and italic formatting when it fits to the theme. Choose language that is clear, concise, and accessible to your target audience:
                    {target_audience}
                    """,
                    },
                ],
                model="gpt-3.5-turbo",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    chapter_response = response["choices"][0]["message"]["content"]

    # Save chapter to database
    insert_ebook_chapter(ebook, chapter_nro, chapter_response)

    return chapter_response


def get_ebook_prompt(user_input):
    st.info("Creating prompt for the images...")
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
                        "content": f"Generate a short, under 400 characters long, written textual representation of an image from this user input: {user_input}",
                    },
                    {
                        "role": "assistant",
                        "content": """
            Generate a short written textual, max 400 characters long, representation of the image that captures the essence, mood, and theme of the user input. Incorporate key terms extracted from the input provided. Consider a suitable color scheme that aligns with the intended atmosphere. Use evocative language to describe visuals that reflect the plot, themes, significant elements or characters of the input. Do your best to captivate the core message visually. The output should not contain any images, only a textual representation of an art piece. Avoid any apologies or examples. 

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

            Please bear in mind that the aforementioned illustrations serve only as a reference and a source of inspiration. It is crucial to employ photographic vocabulary in crafting a distinct and customized textual depiction FROM THE USER INPUT. Under 400 charachters long.
            """,
                    },
                ],
                model="gpt-3.5-turbo",
            )

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    image_prompt = response["choices"][0]["message"]["content"]

    st.success(image_prompt)
    return image_prompt
