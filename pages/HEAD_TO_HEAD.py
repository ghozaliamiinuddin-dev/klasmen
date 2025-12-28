import streamlit as st
import pandas as pd
from gsheets import ws

st.set_page_config(page_title="Head-to-Head", layout="wide")
st.title("🤝 Head-to-Head")

# =========================
# Load Data
# =========================
matches_ws = ws("matches")
matches_df = pd.DataFrame(matches_ws.get_all_records())

players_ws = ws("players")
players_df = pd.DataFrame(players_ws.get_all_records())
players = sorted(players_df["name"].tolist())

if matches_df.empty:
    st.info("Belum ada pertandingan.")
    st.stop()

# =========================
# Pilih Pemain
# =========================
col1, col2, col3 = st.columns(3)
with col1:
    player1 = st.selectbox("Pemain 1", players)
with col2:
    player2 = st.selectbox("Pemain 2", [p for p in players if p != player1])
with col3:
    season_filter = st.text_input("Season (kosong = semua)", value="")

# =========================
# Filter Data
# =========================
df_filtered = matches_df[
    ((matches_df["p1"] == player1) & (matches_df["p2"] == player2)) |
    ((matches_df["p1"] == player2) & (matches_df["p2"] == player1))
]

if season_filter.strip():
    df_filtered = df_filtered[df_filtered["season"] == season_filter.strip()]

if df_filtered.empty:
    st.warning("Belum ada pertandingan antara kedua pemain ini.")
    st.stop()

# =========================
# Statistik
# =========================
stats = {
    player1: {"W":0, "D":0, "L":0, "GF":0, "GA":0},
    player2: {"W":0, "D":0, "L":0, "GF":0, "GA":0}
}

def parse_score(score):
    try:
        g1, g2 = map(int, score.split("-"))
        return g1, g2
    except:
        return 0,0

for _, row in df_filtered.iterrows():
    g1, g2 = parse_score(row["score"])
    if row["p1"] == player1:
        stats[player1]["GF"] += g1
        stats[player1]["GA"] += g2
        stats[player2]["GF"] += g2
        stats[player2]["GA"] += g1

        res1, res2 = row["result"].split("-")
        stats[player1]["W"] += 1 if res1=="W" else 0
        stats[player1]["D"] += 1 if res1=="D" else 0
        stats[player1]["L"] += 1 if res1=="L" else 0
        stats[player2]["W"] += 1 if res2=="W" else 0
        stats[player2]["D"] += 1 if res2=="D" else 0
        stats[player2]["L"] += 1 if res2=="L" else 0
    else:
        stats[player1]["GF"] += g2
        stats[player1]["GA"] += g1
        stats[player2]["GF"] += g1
        stats[player2]["GA"] += g2

        res2, res1 = row["result"].split("-")
        stats[player1]["W"] += 1 if res1=="W" else 0
        stats[player1]["D"] += 1 if res1=="D" else 0
        stats[player1]["L"] += 1 if res1=="L" else 0
        stats[player2]["W"] += 1 if res2=="W" else 0
        stats[player2]["D"] += 1 if res2=="D" else 0
        stats[player2]["L"] += 1 if res2=="L" else 0

# =========================
# Tampilkan Statistik dalam Card
# =========================
st.subheader(f"📊 Statistik Head-to-Head: {player1} vs {player2}")

col_a, col_b = st.columns(2)

def player_card(player_name, stat):
    st.markdown(
        f"""
        <div style="
            background-color: rgba(0,0,255,0.1);
            border-radius:15px;
            padding:15px;
            text-align:center;
            border:1px solid rgba(0,0,255,0.3);
            ">
            <h3>{player_name}</h3>
            <p>W: {stat['W']} | D: {stat['D']} | L: {stat['L']}</p>
            <p>GF: {stat['GF']} | GA: {stat['GA']}</p>
        </div>
        """, unsafe_allow_html=True
    )

with col_a:
    player_card(player1, stats[player1])

with col_b:
    player_card(player2, stats[player2])

# =========================
# Preview Matches
# =========================
st.subheader("📜 Daftar Pertandingan")

def render_ss(val):
    if isinstance(val, str) and val.startswith("data:"):
        return f'<img src="{val}" width="200">'
    return ""

matches_df_display = df_filtered.copy()
if "ss" in matches_df_display.columns:
    matches_df_display["ss"] = matches_df_display["ss"].apply(render_ss)
    st.write(matches_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.dataframe(matches_df_display.sort_values("time", ascending=False), use_container_width=True)
