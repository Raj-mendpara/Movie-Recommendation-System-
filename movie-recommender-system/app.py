import streamlit as st
import pickle
import pandas as pd
import requests

# -------------------- CONFIG --------------------
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

# -------------------- Fetch Movie Poster (CACHED) --------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("poster_path"):
            # smaller image = faster load
            return "https://image.tmdb.org/t/p/w342/" + data["poster_path"]
        else:
            return PLACEHOLDER_POSTER

    except requests.exceptions.RequestException:
        return PLACEHOLDER_POSTER


# -------------------- Recommendation Function --------------------
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]]["movie_id"]

        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# -------------------- Load Data --------------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))


# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")

selected_movie_name = st.selectbox(
    "Select a movie",
    movies["title"].values
)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.markdown(
                f"<h4 style='text-align:center'>{names[idx]}</h4>",
                unsafe_allow_html=True
            )
            st.image(posters[idx], use_container_width=True)
