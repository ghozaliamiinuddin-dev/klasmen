import streamlit as st
import pandas as pd
from gsheets import ws
from datetime import datetime
import base64

st.set_page_config(page_title="Pertandingan", layout="wide")
st.title("⚽ Input Pertandingan & Upload Screenshot")

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

def upload_image(file):
    # Convert uploaded file to base64 string (Google Sheets friendly)
    if file:
        encoded = base64.b64encode(file.read()).decode("utf-8")
        return f"data:{file.type};base64,{encoded}"
    return ""

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
    col1, col2, col3 = st.columns(3)

    with col1:
        p1 = st.selectbox("Pemain 1", players)
        g1 = st.number_input("Gol Pemain 1", min_value=0, step=1)

    with col2:
        p2 = st.selectbox("Pemain 2", players, index=1 if len(players) > 1 else 0)
        g2 = st.number_input("Gol Pemain 2", min_value=0, step=1)

    with col3:
        season = st.text_input("Season", value="2025")
        ss_file = st.file_uploader("Upload Screenshot", type=["png","jpg","jpeg"])

    submit = st.form_submit_button("✅ Simpan Pertandingan", use_container_width=True)

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
    ss_data = upload_image(ss_file)

    # Simpan ke matches
    matches_ws.append_row([
        p1, p2,
        f"{g1}-{g2}",
        f"{r1}-{r2}",
        ss_data,
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
    # Tampilkan preview screenshot
    def render_ss(val):
        if isinstance(val, str) and val.startswith("data:"):
            return f'<img src="{val}" width="200">'
        return ""

    matches_df_display = matches_df.copy()
    if "ss" in matches_df_display.columns:
        matches_df_display["ss"] = matches_df_display["ss"].apply(render_ss)
        st.write(matches_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.dataframe(matches_df_display.sort_values("time", ascending=False), use_container_width=True)
else:
    st.info("Belum ada pertandingan")
