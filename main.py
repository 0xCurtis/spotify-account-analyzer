import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = os.getenv("SCOPE")

def app():
    sp = spotipy.Spotify(auth=st.session_state["token_info"].get("access_token"))
    playlists = sp.current_user_playlists(limit=50)["items"]

    if playlists:
        playlist_data = []

        for playlist in playlists:
            playlist_id = playlist["id"]
            playlist_name = playlist["name"]
            total_duration_ms = 0
            tracks = sp.playlist_tracks(playlist_id, fields="items(track(duration_ms))")["items"]
            for track in tracks:
                total_duration_ms += track["track"]["duration_ms"]
            total_duration_hours = total_duration_ms / (1000 * 60 * 60)
            playlist_data.append([playlist_name, total_duration_hours])
        df = pd.DataFrame(playlist_data, columns=["Playlist", "Duration (hours)"])
        st.subheader("Your Playlist Durations")
        st.dataframe(df)
        st.subheader("Playlist Duration Bar Chart")
        df = df.sort_values(by="Duration (hours)", ascending=False)
        fig, ax = plt.subplots()
        ax.barh(df["Playlist"], df["Duration (hours)"], color="skyblue")
        ax.set_xlabel("Duration (hours)")
        ax.set_title("Playlist Duration Comparison")
        st.pyplot(fig)
    else:
        st.write("No playlists found.")


def login():
    st.write("You are not logged in.")   
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SCOPE,
                        cache_handler=spotipy.cache_handler.MemoryCacheHandler())
    auth_url = sp_oauth.get_authorize_url()
    st.write(f"Please [login to Spotify]({auth_url})")
    # Check for token after redirect
    token_code = st.query_params.get("code", None)
    if token_code and st.session_state.get("token_info", None) is None:
        token_info = sp_oauth.get_access_token(token_code)
        st.session_state["token_info"] = token_info
        st.query_params.pop("code")
        st.rerun()
    

def logout():
    st.session_state.pop("token_info", None)
    st.rerun()


if __name__ == "__main__":
    st.title("Spotify Login App")

    if st.session_state.get("token_info", None) is None:
        login()
    else:
        if st.query_params.get("code", None) is not None:
            st.query_params.pop("code")
        token_info = st.session_state["token_info"]
        f"{token_info}"
        sp = spotipy.Spotify(auth=token_info["access_token"])
        user_profile = sp.current_user()
        st.write(f"Welcome, {user_profile['display_name']}!")
        st.write("You are logged in!")
        app()
        if st.button("Logout"):
            logout()