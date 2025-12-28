import streamlit as st
import pandas as pd
from gsheets import ws
from datetime import datetime

st.set_page_config(page_title="Dashboard eFootball", layout="wide")

# =========================
# LOAD DATA
# =========================
players_ws = ws("players")
matches_ws = ws("matches")

players_df = pd.DataFrame(players_ws.get_all_records())
matches_df = pd.DataFrame(matches_ws.get_all_records())

# Convert numeric columns
num_cols = ["MP","W","D","L","Poin","GD","Streak"]
for col in num_cols:
    if col in players_df.columns:
        players_df[col] = pd.to_numeric(players_df[col], errors='coerce').fillna(0).astype(int)

# Convert time column
if 'time' in matches_df.columns:
    matches_df['time'] = pd.to_datetime(matches_df['time'], errors='coerce')

# =========================
# TITLE
# =========================
st.title("🏆 Dashboard eFootball")

# =========================
# PAPAN PERINGKAT
# =========================
st.subheader("📊 Papan Peringkat")
players_rank = players_df.sort_values(by="Poin", ascending=False).reset_index(drop=True)
cols_per_row = 3
cols = st.columns(cols_per_row)
gradients = [
    "linear-gradient(135deg, #1d4ed8, #2563eb)",
    "linear-gradient(135deg, #059669, #10b981)",
    "linear-gradient(135deg, #b91c1c, #ef4444)",
    "linear-gradient(135deg, #7c3aed, #8b5cf6)",
    "linear-gradient(135deg, #f97316, #fb923c)",
]

for i, r in players_rank.iterrows():
    col = cols[i % cols_per_row]
    gradient = gradients[i % len(gradients)]
    with col:
        st.markdown(
            f"""
            <div style='
                background: {gradient};
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
                color: white;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
                transition: transform 0.3s;
            '>
                <h3 style='text-align:center;'>{r['name']}</h3>
                <div style='display:grid; grid-template-columns: repeat(2, 1fr); gap:5px;'>
                    <div>MP:</div><div>{r['MP']}</div>
                    <div>W:</div><div>{r['W']}</div>
                    <div>D:</div><div>{r['D']}</div>
                    <div>L:</div><div>{r['L']}</div>
                    <div>Poin:</div><div>{r['Poin']}</div>
                    <div>GD:</div><div>{r['GD']}</div>
                    <div>Streak:</div><div>{r['Streak']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

# =========================
# GRAFIK PERFORMA & STREAK
# =========================
st.subheader("📈 Grafik Performa")
if not players_df.empty:
    st.line_chart(players_df.set_index("name")["Poin"])
    st.bar_chart(players_df.set_index("name")["Streak"])

# =========================
# RIWAYAT PERTANDINGAN
# =========================
st.subheader("📋 Riwayat Pertandingan")
if matches_df.empty:
    st.info("Belum ada pertandingan yang tercatat.")
else:
    matches_df = matches_df.sort_values(by="time", ascending=False).reset_index(drop=True)
    for idx, r in matches_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
            col1.markdown(f"**{r['p1']}** vs **{r['p2']}**")
            col2.markdown(f"Score: {r['score']}")
            col3.markdown(f"Result: {r['result']}")
            col4.markdown(f"Season: {r['season']}")
            if r['ss']:
                col5.image(r['ss'], width=80)
            # Tombol hapus
            if col5.button("❌ Hapus", key=f"del_{idx}"):
                row_idx = matches_ws.find(r['p1']).row
                matches_ws.delete_rows(row_idx)
                st.warning("Pertandingan dihapus!")

