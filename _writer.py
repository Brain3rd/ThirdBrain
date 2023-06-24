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

                        Using the user input and target audience provided, I kindly request your expertise in creating something that is completely distinct from any existing book title in the market. Utilize keyword research tools to identify popular search terms related to topic. Please provide me with ONE compelling title.
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
            st.sidebar.error(
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

                        Using the user input, target audience and book title provided, I kindly request your expertise in creating a captivating table of contents for this book. Consider how the content will best resonate with target audience and address their specific needs and interests. This process allows you to refine this book's angle, structure, and tone, ensuring that it captures the attention of target audience and provides them with the value they are seeking. Utilize keyword research tools to identify popular search terms related to this book.
                        """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""
                    Provide detailed table of contents for the book formatted in Markdown code. Avoid any apologies or compliments. Consider the overall arc of non-fiction eBook. Begin with main themes or key ideas that will form the basis for each chapter or section of the book. Within each chapter, aim to include subtopics that expand on the main theme which allow to dig deeper into each subject, providing valuable insights and practical advice. Remember to maintain a logical progression wit the outline, allowing ideas to build upon one another and creating a sense of continuity. Futhermore, consider incorporating storytelling elements or personal anecdotes that relate to each chapter's theme. This will help in establishing an emotional connection with readers:
                    # {ebook} 
                    *Include your author name or pen name and any relevant subtitle or tagline.*

                    ## Table of Contents

                    List the main chapters, sections and subsections of the book. 
                    1. Introduction
                    2. Chapter
                        - 2.1 Section
                        - 2.2 Section 
                        - 2.3 Section
                    3. Chapter
                        - 3.1 Section
                            -3.1.1 Subsection
                            -3.1.2 Subsection
                            -3.1.3 Subsection
                        - 3.2 Section
                    4. Chapter
                        - Sections
                            - Subsections
                    5. ...
                    10. Conclusion

                    ## Introduction
                    *Begin with an engaging introduction that grabs the reader's attention and provides an overview of what your eBook will cover.*

                    ## Chapter 1
                    *Start with a clear heading that reflects the topic of the chapter.*
                    - Present your main ideas, arguments, or information related to the chapter's subject matter.
                    - Use bullet points, numbered lists or subsections to break down complex concepts or steps.

                    ## Chapter 2
                    *Repeat the structure used in the previous chapter for subsequent chapters or sections.*

                    ## Chapter 3
                    *Continue with the same structure if the Book has more chapters or sections.*

                    ## Conclusion
                    *Summarize the key points discussed in the Book.*
                    - Provide any final thoughts, recommendations, or calls to action.

                    ### Additional Resources/Appendix (optional)
                    *Include any relevant resources, links, or references that can further enhance the reader's understanding or provide additional value.*
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

    content = response["choices"][0]["message"]["content"]

    # Save to database
    insert_ebook_table_of_content(ebook, content)
    insert_target_audience(ebook, target_audience)

    return content


def write_chapter(ebook, chapter_nro, template, chapter_to_write, target_audience):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are a highly acclaimed best-selling author, renowned for your exceptional storytelling abilities and captivating prose. You have been focusing on self help books, learned your mistakes and enetually succeeded. It is crucial to maintain a perfect balance between perplexity and burstiness while crafting your content. Perplexity ensures the complexity of your text, while burstiness evaluates the variation in sentence structures. Remember that a compelling narrative incorporates a mix of sentence lengths, unlike machine-generated writing that can be uniform. Strive to achieve an optimal blend of both perplexity and burstiness to engage your readers effectively.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                    I present to you the meticulously crafted table of contents for the eBook you are writing now:
                    {template}

                    Now, I would greatly appreciate if you could write the following section of the book:
                    {chapter_to_write} 

                    Choose language that is clear, concise, and accessible to your target audience:
                    {target_audience}
                    """,
                    },
                    {
                        "role": "assistant",
                        "content": f"""                      
                    When crafting chapter titles, use markdown formatting to enhance their visual appeal. Employ the following format: ## Title, ### Subtitle. Feel free to use **bold** and *italic* when it fits the theme.

                    It is important to establish a seamless flow within your chapters, maintaining a novel-like structure that entices readers to delve deeper into your story, rather than selling picth for upcoming book. Avoid apologies or compliments. While your aim is to educate and provide valuable information, you also want to create a connection with your readers. Use language that is relatable and conversational, making your readers feel like they are having a conversation with a knowledgeable friend.

                    """,
                    },
                ],
                model="gpt-3.5-turbo-16k",
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

    chapter_response = response["choices"][0]["message"]["content"]

    # Save chapter to database
    insert_ebook_chapter(ebook, chapter_nro, chapter_response)

    return chapter_response
