import os

import matplotlib.pyplot as plt
import requests
import streamlit as st
from wordcloud import WordCloud, STOPWORDS
from dotenv import load_dotenv
import stopwordsiso
import pandas as pd
import altair as alt

load_dotenv()

st.set_page_config(page_title="Schüler Feedback", layout="wide")

PORT = int(os.getenv("PORT", 8000))
API_BASE = os.getenv("API_BASE", f"http://localhost:{PORT}")

# ---------------------
# Login
# ---------------------
if "role" not in st.session_state:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        resp = requests.post(
            f"{API_BASE}/login", params={"username": username, "password": password}
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["role"] = data["role"]
            st.session_state["username"] = username
            st.rerun()
        elif resp.status_code == 401:
            st.error("Ungültige Login-Daten")
        else:
            st.error(f"Login-Fehler: {resp.status_code}")
    st.stop()  # stop execution until logged in

# ---------------------
# App Navigation
# ---------------------
st.title("Schüler-Feedback App")

role = st.session_state["role"]

if role == "student":
    st.header("Schnelles, anonymes Feedback")

    try:
        subjects = requests.get(f"{API_BASE}/subjects", timeout=30).json()
    except Exception as e:
        subjects = []
        st.error(f"Konnte Fächer nicht laden: {e}")

    if not subjects:
        st.warning("Keine Fächer gefunden.")
    else:
        subject = st.selectbox("Fach", subjects)

        try:
            teachers = requests.get(f"{API_BASE}/subjects/{subject}", timeout=30).json()
        except Exception as e:
            teachers = []
            st.error(f"Konnte Lehrer nicht laden: {e}")
        teacher = (
            st.selectbox("Lehrer", dict(teachers)["teachers"])
            if teachers
            else st.text_input("Lehrer (frei eingeben)")
        )

        mood = st.selectbox("Stimmung", ["😀", "🙂", "😐", "😕", "😞"])
        difficulty = st.radio(
            "Wie schwer war die Stunde?", ["leicht", "mittel", "schwer"]
        )
        comment = st.text_area("Verbesserungsvorschlag (optional)")
        submitted = st.button("Absenden")

        if submitted:
            payload = {
                "subject": subject,
                "teacher": teacher,
                "mood": mood,
                "difficulty": difficulty,
                "comment": comment or None,
            }
            try:
                resp = requests.post(f"{API_BASE}/feedback", json=payload, timeout=30)
                if resp.status_code in (200, 201):
                    st.success("Danke! Dein Feedback wurde anonym gesendet.")
                else:
                    st.error(f"Fehler: {resp.status_code} {resp.text}")
            except Exception as e:
                st.error(f"Fehler beim Senden: {e}")


elif role == "teacher":
    st.header("Auswertung")
    try:
        stats = requests.get(f"{API_BASE}/stats/{st.session_state["username"]}", params={"teacher": st.session_state["username"]}).json()
        st.subheader("Gesamt")
        st.metric("Feedbacks gesamt", stats.get("total", 0))

        difficulty_data = stats.get("by_difficulty", {})
        df_diff = pd.DataFrame(list(difficulty_data.items()), columns=["Schwierigkeit", "Anzahl"])

        if df_diff.empty:
            st.info("Noch keine Schwierigkeitsdaten verfügbar.")
        else:
            diff_chart = (
                alt.Chart(df_diff)
                .mark_bar()
                .encode(
                    x=alt.X("Schwierigkeit:N", axis=alt.Axis(labelAngle=0), title=None),  # Labels horizontal (0°)
                    y=alt.Y("Anzahl:Q", axis=alt.Axis(title=None)),
                    tooltip=["Schwierigkeit", "Anzahl"]
                )
                .configure_axisY(tickMinStep=1)
                .properties(height=300)
            )
            st.subheader("Schwierigkeit")
            st.altair_chart(diff_chart, use_container_width=True)

        mood_data = stats.get("by_mood", {})
        df_mood = pd.DataFrame(list(mood_data.items()), columns=["Stimmung", "Anzahl"])

        if df_mood.empty:
            st.info("Noch keine Stimmungsdaten verfügbar.")
        else:
            mood_chart = (
                alt.Chart(df_mood)
                .mark_bar()
                .encode(
                    x=alt.X("Stimmung:N", axis=alt.Axis(labelAngle=0, title=None)),  # Labels horizontal
                    y=alt.Y("Anzahl:Q", axis=alt.Axis(title=None)),
                    tooltip=["Stimmung", "Anzahl"]
                )
                .configure_axisY(tickMinStep=1)
            ).properties(height=300)
            st.subheader("Stimmung")
            st.altair_chart(mood_chart, use_container_width=True)


        st.subheader("Letzte Kommentare")
        feedbacks = requests.get(f"{API_BASE}/feedbacks/{st.session_state["username"]}", params={"teacher": st.session_state["username"], "limit": 50}).json()
        comments = [f["comment"] for f in feedbacks if f.get("comment")]
        for f in feedbacks[:5]:
            st.write(
                f"- **{f['subject']}** — {f['difficulty']} — {f['mood']} — {f.get('comment') or ''}"
            )

        if comments:
            st.subheader("Wordcloud der Kommentare")
            text = " ".join(comments).lower()
            german_sw = stopwordsiso.stopwords("de")
            stopwords = set(STOPWORDS).union(german_sw)
            wc = WordCloud(
                width=800,
                height=400,
                collocations=False,
                stopwords=stopwords,
                background_color="white"
            ).generate(text)
            fig, ax = plt.subplots(figsize=(10, 4.5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")

else:
    st.error("Unbekannte Rolle. Bitte erneut einloggen.")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
