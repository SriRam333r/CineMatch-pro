import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os
import random
def read_director_note():
    # PASTE YOUR NOTEPAD FILE PATH HERE
    # Example: r"C:\Users\Admin\Desktop\note.txt"
    file_path = r"C:\Users\hp\Desktop\dmw.txt"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception:
        return "Note file not found. Please check the file path in the code."

# --- 1. CONFIG & CINEMATIC CSS ---
st.set_page_config(page_title="CineMatch Pro", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        color: #ffffff;
    }
    .movie-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e50914;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #e50914 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(20, 20, 20, 0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING (DWH Logic) ---
@st.cache_data
def load_data():
    folder = "dwm movie recomd"
    movies = pd.read_csv(os.path.join(folder, 'movies.csv'))
    # Loading 200,000 rows for the Fact Table
    ratings = pd.read_csv(os.path.join(folder, 'ratings.csv'), nrows=200000)
    return pd.merge(ratings, movies, on='movieId')

df = load_data()

# --- 3. DATA MINING ENGINE ---
@st.cache_resource
def get_engine_data(_df):
    # Transformation into User-Item Matrix
    matrix = _df.pivot_table(index='title', columns='userId', values='rating').fillna(0)
    # Mining relationships via Cosine Similarity
    sim = cosine_similarity(matrix)
    return matrix, pd.DataFrame(sim, index=matrix.index, columns=matrix.index)

movie_matrix, sim_df = get_engine_data(df)

# --- 4. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'username' not in st.session_state: st.session_state.username = ""
if 'watchlist' not in st.session_state: st.session_state.watchlist = set()
if 'movie_choice' not in st.session_state: st.session_state.movie_choice = movie_matrix.index[0]
if 'gen_choice' not in st.session_state: st.session_state.gen_choice = []

# --- 5. CALLBACK FUNCTIONS ---
def add_to_watchlist(title):
    st.session_state.watchlist.add(title)
    st.toast(f"🍿 Added {title} to Watch Later!")
def read_notepad_file():
    # Replace this with the actual path to your .txt file"C:\Users\hp\Desktop\dmw.txt"
    file_path = r"C:\Users\hp\Desktop\dmw.txt"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Note file not found. Check the file path in the code!"

def logout():
    st.session_state.page = 'login'
    st.session_state.watchlist = set()
    st.rerun()

# --- 6. PAGE LOGIC ---

# PAGE: LOGIN SCREEN
if st.session_state.page == 'login':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("# ")
        # BIG CINEMATIC TITLE
        st.markdown("""
        <h1 style='text-align: center; color: #e50914; font-size: 60px; font-family: "Arial Black", Gadget, sans-serif; text-shadow: 2px 2px 4px #000000;'>
        🎬 CineMatch Pro
        </h1>
        <p style='text-align: center; color: #ffffff; font-size: 20px; font-style: italic;'>
        Where Data Science Meets the Big Screen
        </p>
        <hr style="border: 1px solid #e50914;">
        """, unsafe_allow_html=True)
        
        st.image("https://cdn-icons-png.flaticon.com/512/2503/2503508.png", width=80)
        u_name = st.text_input("Enter your name to begin:")
        if st.button("Enter the Cinema 🎟️"):
            if u_name:
                st.session_state.username = u_name
                st.session_state.page = 'main'
                st.rerun()
            else:
                st.error("Please enter a name!")

# PAGE: MAIN APP
else:
    with st.sidebar:
        st.title(f"🍿 {st.session_state.username}")
        # 4: Dashboard Metrics
        m1, m2 = st.columns(2)
        m1.metric("Watchlist", len(st.session_state.watchlist))
        m2.metric("Engine", "Active", delta="100%")
        
        st.markdown("---")
        st.markdown("---")
        st.subheader("Watch Later")
        if st.session_state.watchlist:
            for movie in list(st.session_state.watchlist):
                st.write(f"✅ {movie}")
        else:
            st.info("Your list is empty.")
        st.markdown("---")
        if st.button("Logout"):
            logout()
    tab1, tab2, tab3 = st.tabs(["🔍 Similar Movies", "🧪 Genre Mixer", "📜 Director's Note"])
    #tab1, tab2 = st.tabs(["🔍 Similar Movies", "🧪 Genre Mixer"])

    # TAB 1: COLLABORATIVE FILTERING (MINING)
    with tab1:
        if st.button("🔀 Shuffle Suggestions"):
            st.session_state.movie_choice = random.choice(movie_matrix.index.tolist())
            st.rerun()
            
        m_idx = movie_matrix.index.get_loc(st.session_state.movie_choice)
        selected = st.selectbox("If you liked...", movie_matrix.index, index=m_idx)


        
        if st.button("Find Gems"):
            recs = sim_df[selected].sort_values(ascending=False).iloc[1:11]
            for title, score in recs.items():
                c1, c2 = st.columns([5, 1])
                with c1:
                    match_pct = int(score * 100)
                    st.markdown(f'<div class="movie-card"><b>{title}</b><br><span style="color:#00ff00;">{match_pct}% Match Score</span></div>', unsafe_allow_html=True)
                    # 2: Visual Progress Bar
                    st.progress(score)
                with c2:
                    st.button("➕", key=f"t1_{title}", help="Add to Watch Later", on_click=add_to_watchlist, args=(title,))
            with c1:
                    match_pct = int(score * 100)
                    st.markdown(f'<div class="movie-card"><b>{title}</b><br><span style="color:#00ff00;">{match_pct}% Match Score</span></div>', unsafe_allow_html=True)
                    # 2: Visual Progress Bar
                    st.progress(score)

    # TAB 2: DATA ANALYTICS (GENRE MIX)
    with tab2:
        st.subheader("The Genre Mixer")
        all_genres = sorted(list(set([g for genres in df['genres'].str.split('|') for g in genres if g != "(no genres listed)"])))
        
        if st.button("🔀 Shuffle Genres"):
            st.session_state.gen_choice = random.sample(all_genres, 2)
            st.rerun()
            
        selected_genres = st.multiselect("Pick up to 3 genres:", all_genres, default=st.session_state.gen_choice, max_selections=3)
        
        if st.button("Search Mix"):
            query = df.copy()
            for g in selected_genres:
                query = query[query['genres'].str.contains(g)]
            
            if not query.empty:
                top = query.groupby('title')['rating'].agg(['mean', 'count'])
                top = top[top['count'] > 5].sort_values(by='mean', ascending=False).head(7)
                
                for title, row in top.iterrows():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        approval = int((row['mean'] / 5) * 100)
                        st.markdown(f'<div class="movie-card"><b>{title}</b><br><span style="color:#ffcc00;">★ {approval}% Approval</span></div>', unsafe_allow_html=True)
                        # 2: Visual Progress Bar
                        st.progress(row['mean'] / 5) 
                    with c2:
                        st.button("➕", key=f"t2_{title}", help="Add to Watch Later", on_click=add_to_watchlist, args=(title,))
                        
                            # --- DIRECTOR'S HIDDEN NOTE ---
    with tab3:
            st.subheader("🎬 Director's Cut: Secret Notes")
            st.write("Click the button below to load the latest developer notes directly from the source file.")
            
            # This button triggers the file read
            if st.button("📖 Read Notepad Note"):
                note_content = read_director_note()
                st.markdown(f"""
                    <div style="background-color: rgba(229, 9, 20, 0.2); 
                                padding: 20px; 
                                border-radius: 15px; 
                                border: 1px dashed #e50914; 
                                margin-top: 15px;
                                color: white;
                                font-size: 18px;
                                font-style: italic;">
                        "{note_content}"
                    </div>
                """, unsafe_allow_html=True)