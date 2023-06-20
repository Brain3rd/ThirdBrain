from deta import Deta
import streamlit as st
from environment import load_env_variables, get_api_key


load_env_variables()
DETA_KEY = get_api_key("DETA_KEY")
deta = Deta(DETA_KEY)

db = deta.Base("users_db")


def insert_user(username, name, password):
    return db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    res = db.fetch()
    return res.items


def get_user(username):
    return db.get(username)


def update_user(username, updates):
    return db.update(updates, username)


def delete_user(username):
    return db.delete(username)
