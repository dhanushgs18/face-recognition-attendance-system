import os
import sqlite3

import pandas as pd
import streamlit as st


DB_FILE = os.path.join(os.path.dirname(__file__), "attendance.db")

st.set_page_config(page_title="Attendance Dashboard", layout="wide")
st.title("Attendance Dashboard")

if not os.path.exists(DB_FILE):
    st.warning("No attendance.db found yet. Run main.py first to generate attendance data.")
    st.stop()

conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query("SELECT * FROM attendance", conn)
conn.close()

if df.empty:
    st.info("No attendance records yet.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
df["weekday"] = df["date"].dt.day_name()

# --- Raw data ---
st.subheader("Raw records")
st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

# --- Attendance % per student ---
st.subheader("Attendance % per student")
total_days = df["date"].nunique()
attendance_pct = (df.groupby("name")["date"].nunique() / total_days * 100).round(1)
st.bar_chart(attendance_pct)

# --- At-risk students (< 75%) ---
st.subheader("At-risk students (below 75% attendance)")
at_risk = attendance_pct[attendance_pct < 75]
if at_risk.empty:
    st.success("No students below 75% attendance.")
else:
    st.dataframe(at_risk.rename("Attendance %"))

# --- Attendance by weekday ---
st.subheader("Attendance by weekday")
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_counts = df["weekday"].value_counts().reindex(weekday_order).fillna(0)
st.bar_chart(weekday_counts)

# --- Late arrivals ---
st.subheader("Late arrivals (after 09:15)")
df["time_only"] = pd.to_datetime(df["time"], format="%H:%M:%S").dt.time
cutoff = pd.to_datetime("09:15:00", format="%H:%M:%S").time()
late_df = df[df["time_only"] > cutoff]
st.dataframe(late_df[["name", "date", "time"]])
