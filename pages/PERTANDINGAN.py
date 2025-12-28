import streamlit as st
import pandas as pd
from gsheets import ws
from datetime import datetime

st.set_page_config(page_title="Pertandingan", layout="wide")
st.title("⚽ Input Pertandingan")

players_ws = ws("players")
matches_ws = ws("matches")

# =========================
# Helper
# =========================
def safe_int(val):
    try:
        return int(val)
    except:
        return 0

# =========================
# Load Data
# =========================
players_df = pd.DataFrame(players_ws.get_all_records())
matches_df = pd.DataFrame(matches_ws.get_all_records())

if players_df.empty:
    st.warning("Belum ada data pemain.")
    st.stop()

players = sorted(players_df["name"].tolist())

# =========================
# Form Input
# =========================
st.subheader("➕ Tambah Pertandingan")

with st.form("match_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        p1 = st.selectbox("Pemain 1", players)
        g1 = st.number_input("Gol Pemain 1", min_value=0, step=1)

    with col2:
        p2 = st.selectbox("Pemain 2", players, index=1 if len(players) > 1 else 0)
        g2 = st.number_input("Gol Pemain 2", min_value=0, step=1)

    season = st.text_input("Season", value="2025")
    submit = st.form_submit_button("✅ Simpan Pertandingan")

# =========================
# Submit Logic
# =========================
if submit:
    if p1 == p2:
        st.error("Pemain tidak boleh sama")
        st.stop()

    if g1 > g2:
        r1, r2 = "W", "L"
    elif g1 < g2:
        r1, r2 = "L", "W"
    else:
        r1 = r2 = "D"

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Simpan ke matches tanpa screenshot
    matches_ws.append_row([
        p1, p2,
        f"{g1}-{g2}",
        f"{r1}-{r2}",
        season,
        time_now
    ])

    # =========================
    # Update Player Stats
    # =========================
    def update_player(name, gf, ga, res):
        row = players_df[players_df["name"] == name].iloc[0]
        idx = players_df.index[players_df["name"] == name][0] + 2

        MP = safe_int(row["MP"]) + 1
        W = safe_int(row["W"])
        D = safe_int(row["D"])
        L = safe_int(row["L"])
        Poin = safe_int(row["Poin"])
        GD = safe_int(row["GD"]) + (gf - ga)
        Streak = safe_int(row["Streak"])

        if res == "W":
            W += 1
            Poin += 3
            Streak = Streak + 1 if Streak >= 0 else 1
        elif res == "D":
            D += 1
            Poin += 1
            Streak = 0
        else:
            L += 1
            Streak = Streak - 1 if Streak <= 0 else -1

        players_ws.update(
            f"B{idx}:H{idx}",
            [[MP, W, D, L, Poin, GD, Streak]]
        )

    update_player(p1, g1, g2, r1)
    update_player(p2, g2, g1, r2)

    st.success("Pertandingan berhasil disimpan")
    st.toast("Statistik pemain diperbarui", icon="✅")

# =========================
# Riwayat Pertandingan
# =========================
st.divider()
st.subheader("📜 Riwayat Pertandingan")

if not matches_df.empty:
    st.dataframe(matches_df.sort_values("time", ascending=False), use_container_width=True)
else:
    st.info("Belum ada pertandingan")
