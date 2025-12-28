import streamlit as st
import pandas as pd
from gsheets import ws
from datetime import datetime

# =========================
# Load Sheets
# =========================
players_ws = ws("players")
matches_ws = ws("matches")

# =========================
# Helper Functions
# =========================
def reset_players_stats():
    """Reset semua statistik pemain ke 0."""
    all_players = players_ws.get_all_records()
    for idx, p in enumerate(all_players, start=2):  # baris pertama header
        players_ws.update(f"B{idx}:H{idx}", [[0,0,0,0,0,0,0]])

def recalc_player_stats():
    """Hitung ulang statistik pemain dari history pertandingan."""
    matches_df = pd.DataFrame(matches_ws.get_all_records())
    
    # Jika sheet kosong, hentikan
    if matches_df.empty:
        reset_players_stats()
        return
    
    # Pastikan ada kolom time
    if "time" not in matches_df.columns:
        matches_df["time"] = pd.Timestamp.now()
    
    reset_players_stats()  # reset dulu stats
    
    players_df = pd.DataFrame(players_ws.get_all_records())
    for idx, match in matches_df.iterrows():
        p1 = match['p1']
        p2 = match['p2']
        score = match['score']
        result = match.get('result','')
        if not score or '-' not in score:
            continue
        g1, g2 = map(int, score.split('-'))
        
        try:
            row_p1 = players_ws.find(p1).row
            row_p2 = players_ws.find(p2).row
        except:
            continue  # skip kalau pemain belum ada
        
        mp1, w1, d1, l1, poin1, gd1, streak1 = [int(x) if str(x).isdigit() else 0 for x in players_ws.row_values(row_p1)[1:8]]
        mp2, w2, d2, l2, poin2, gd2, streak2 = [int(x) if str(x).isdigit() else 0 for x in players_ws.row_values(row_p2)[1:8]]
        
        # Update stats
        mp1 +=1; mp2 +=1
        gd1 += g1 - g2; gd2 += g2 - g1
        
        if result == 'W':
            w1 +=1; l2 +=1; poin1 +=3
        elif result == 'D':
            d1 +=1; d2 +=1; poin1 +=1; poin2 +=1
        elif result == 'L':
            l1 +=1; w2 +=1; poin2 +=3
        
        players_ws.update(f"B{row_p1}:H{row_p1}", [[mp1,w1,d1,l1,poin1,gd1,streak1]])
        players_ws.update(f"B{row_p2}:H{row_p2}", [[mp2,w2,d2,l2,poin2,gd2,streak2]])

# =========================
# Sidebar Controls
# =========================
st.sidebar.title("Controls")
if st.sidebar.button("Hapus Semua Riwayat Pertandingan"):
    matches_ws.clear()
    reset_players_stats()
    st.success("Semua pertandingan dihapus, statistik pemain di-reset!")
    st.experimental_rerun()

# =========================
# Tampilkan Papan Peringkat
# =========================
st.subheader("📊 Papan Peringkat")
players_df = pd.DataFrame(players_ws.get_all_records())

if not players_df.empty:
    players_df = players_df.sort_values(by="Poin", ascending=False).reset_index(drop=True)
    cols_per_row = 3
    cols = st.columns(cols_per_row)
    gradients = [
        "linear-gradient(135deg, #1d4ed8, #2563eb)",
        "linear-gradient(135deg, #059669, #10b981)",
        "linear-gradient(135deg, #b91c1c, #ef4444)",
        "linear-gradient(135deg, #7c3aed, #8b5cf6)",
        "linear-gradient(135deg, #f97316, #fb923c)",
    ]

    for i, r in players_df.iterrows():
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
# Riwayat Pertandingan
# =========================
st.subheader("📋 Riwayat Pertandingan")
matches_df = pd.DataFrame(matches_ws.get_all_records())

if not matches_df.empty:
    if "time" not in matches_df.columns:
        matches_df["time"] = pd.Timestamp.now()
    
    matches_df = matches_df.sort_values(by="time", ascending=False).reset_index(drop=True)

    for idx, r in matches_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
            col1.markdown(f"**{r['p1']}** vs **{r['p2']}**")
            col2.markdown(f"Score: {r['score']}")
            col3.markdown(f"Result: {r['result']}")
            col4.markdown(f"Season: {r.get('season','-')}")
            if r.get('ss'):
                col5.image(r['ss'], width=80)
            if col5.button("❌ Hapus", key=f"del_{idx}"):
                row_idx = idx + 2  # karena header
                matches_ws.delete_rows(row_idx)
                recalc_player_stats()
                st.warning("Pertandingan dihapus dan stats diperbarui!")
               
