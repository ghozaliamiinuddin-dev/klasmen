import streamlit as st
import pandas as pd
from gsheets import ws

st.title("📊 Klasemen")

df = pd.DataFrame(ws("players").get_all_records())
df["WinRate"] = (df.W / df.MP * 100).fillna(0).round(1)

df = df.sort_values(
    ["Poin", "GD", "WinRate"],
    ascending=False
)

st.dataframe(df, width="stretch")

st.subheader("🥇 Badge Juara")
for i, r in df.head(3).iterrows():
    st.write(f"{r.name} – {'🥇🥈🥉'[list(df.index).index(i)]}")
