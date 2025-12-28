import streamlit as st
import pandas as pd
from gsheets import ws

st.set_page_config(page_title="Data Pemain", layout="wide")

players_ws = ws("players")

# =========================
# HELPER
# =========================
def to_python_value(val):
    if isinstance(val, (int, float, str)):
        return val
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return str(val)

# =========================
# LOAD DATA PEMAIN
# =========================
df = pd.DataFrame(players_ws.get_all_records())
num_cols = ["MP", "W", "D", "L", "Poin", "GD", "Streak"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# =========================
# TAMBAH PEMAIN
# =========================
st.title("👥 Data Pemain")
with st.expander("➕ Tambah Pemain"):
    name = st.text_input("Nama Pemain Baru")
    if st.button("Tambah"):
        if name.strip():
            players_ws.append_row([name,0,0,0,0,0,0,""])
            st.success(f"Pemain '{name}' ditambahkan!")

# =========================
# HAPUS PEMAIN
# =========================
with st.expander("❌ Hapus Pemain"):
    plist = players_ws.col_values(1)[1:]
    del_p = st.selectbox("Pilih Pemain untuk Dihapus", plist)
    if st.button("Hapus"):
        row_idx = players_ws.find(del_p).row
        players_ws.delete_rows(row_idx)
        st.warning(f"Pemain '{del_p}' dihapus!")

# =========================
# Papan Peringkat
# =========================
st.subheader("🏆 Papan Peringkat")
df_rank = df.sort_values(by="Poin", ascending=False).reset_index(drop=True)
for idx, r in df_rank.iterrows():
    medal = ""
    style = ""
    if idx == 0:
        medal = "🥇"
        style = "color: gold; font-weight:bold;"
    elif idx == 1:
        medal = "🥈"
        style = "color: silver; font-weight:bold;"
    elif idx == 2:
        medal = "🥉"
        style = "color: #cd7f32; font-weight:bold;"
    st.markdown(f"<p style='{style}'>{idx+1}. {r['name']} {medal} — Poin: {r['Poin']} | GD: {r['GD']} | Streak: {r['Streak']}</p>", unsafe_allow_html=True)

# =========================
# CARD PLAYER DENGAN EFEK HOVER
# =========================
st.subheader("🃏 Card Player")
cols_per_row = 3
cols = st.columns(cols_per_row)
gradients = [
    "linear-gradient(135deg, #1d4ed8, #2563eb)",
    "linear-gradient(135deg, #059669, #10b981)",
    "linear-gradient(135deg, #b91c1c, #ef4444)",
    "linear-gradient(135deg, #7c3aed, #8b5cf6)",
    "linear-gradient(135deg, #f97316, #fb923c)",
]

for i, r in df_rank.iterrows():
    col = cols[i % cols_per_row]
    gradient = gradients[i % len(gradients)]
    with col:
        # Card container dengan hover effect
        st.markdown(
            f"""
            <style>
            .card{i} {{
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
                background: {gradient};
                color: white;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            .card{i}:hover {{
                transform: scale(1.05);
                box-shadow: 5px 5px 20px rgba(0,0,0,0.5);
            }}
            </style>
            <div class="card{i}">
                <h3 style="text-align:center;">{r['name']}</h3>
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

        # Form edit nama di card
        with st.form(key=f"edit_form_{i}"):
            new_name = st.text_input("Nama", value=r['name'], key=f"name_{i}")
            submit = st.form_submit_button("Simpan Perubahan")
            if submit:
                row_idx = players_ws.find(r['name']).row
                row_values = [
                    to_python_value(new_name),
                    to_python_value(r["MP"]),
                    to_python_value(r["W"]),
                    to_python_value(r["D"]),
                    to_python_value(r["L"]),
                    to_python_value(r["Poin"]),
                    to_python_value(r["GD"]),
                    to_python_value(r["Streak"]),
                    ""  # kolom foto kosong
                ]
                players_ws.update(f"A{row_idx}:I{row_idx}", [row_values])
                st.success(f"Profil pemain '{new_name}' diperbarui!")
