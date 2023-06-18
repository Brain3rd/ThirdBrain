from dotenv import load_dotenv
import os
import streamlit as st


def load_env_variables():
    if os.path.isfile(".env"):
        load_dotenv(".env")


def get_api_key(api_key):
    load_env_variables()
    if api_key in os.environ:
        api_key = os.environ[api_key]
    else:
        api_key = st.secrets[api_key]
    return api_key
