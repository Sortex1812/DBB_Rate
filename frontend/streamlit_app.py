import os

import matplotlib.pyplot as plt
import requests
import streamlit as st
from wordcloud import WordCloud
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Schüler Feedback", layout="wide")

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

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
    # Student only has feedback form
    st.header("Schnelles, anonymes Feedback")

    # Load available subjects from backend
    try:
        subjects = requests.get(f"{API_BASE}/subjects", timeout=5).json()
    except Exception as e:
        subjects = []
        st.error(f"Konnte Fächer nicht laden: {e}")

    if not subjects:
        st.warning("Keine Fächer gefunden.")
    else:
        # Subject selection
        subject = st.selectbox("Fach", subjects)

        # Fetch teachers for selected subject
        try:
            teachers = requests.get(f"{API_BASE}/subjects/{subject}", timeout=5).json()
        except Exception as e:
            teachers = []
            st.error(f"Konnte Lehrer nicht laden: {e}")
        teacher = (
            st.selectbox("Lehrer", dict(teachers)["teachers"])
            if teachers
            else st.text_input("Lehrer (frei eingeben)")
        )

        # Rest of feedback form
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
                resp = requests.post(f"{API_BASE}/feedback", json=payload, timeout=5)
                if resp.status_code in (200, 201):
                    st.success("Danke! Dein Feedback wurde anonym gesendet.")
                else:
                    st.error(f"Fehler: {resp.status_code} {resp.text}")
            except Exception as e:
                st.error(f"Fehler beim Senden: {e}")


elif role == "teacher":
    # Teacher only has dashboard
    st.header("Auswertung")
    try:
        stats = requests.get(f"{API_BASE}/stats").json()
        st.subheader("Gesamt")
        st.metric("Feedbacks gesamt", stats.get("total", 0))

        st.subheader("Schwierigkeit")
        st.bar_chart(data=stats.get("by_difficulty", {}))

        st.subheader("Stimmung")
        st.bar_chart(data=stats.get("by_mood", {}))

        st.subheader("Letzte Kommentare")
        feedbacks = requests.get(f"{API_BASE}/feedbacks?limit=50").json()
        comments = [f["comment"] for f in feedbacks if f.get("comment")]
        for f in feedbacks[:20]:
            st.write(
                f"- **{f['subject']}** — {f['difficulty']} — {f['mood']} — {f.get('comment') or ''}"
            )

        if comments:
            st.subheader("Wordcloud der Kommentare")
            text = " ".join(comments)
            wc = WordCloud(width=800, height=400, collocations=False).generate(text)
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
