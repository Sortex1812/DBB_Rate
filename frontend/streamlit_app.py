import streamlit as st
import requests
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

API_BASE = st.secrets.get("API_BASE", os.getenv("API_BASE", "http://localhost:8000"))

st.set_page_config(page_title="Schüler Feedback", layout="wide")

st.title("Schüler-Feedback App")

page = st.sidebar.selectbox("Seite", ["Feedback abgeben", "Auswertung (Lehrer)"])

if page == "Feedback abgeben":
    st.header("Schnelles, anonymes Feedback")
    with st.form("feedback_form"):
        subject = st.text_input("Fach / Thema", value="Mathe")
        mood = st.selectbox("Stimmung", ["😀", "🙂", "😐", "😕", "😞"])
        difficulty = st.radio("Wie schwer war die Stunde?", ["leicht", "mittel", "schwer"])
        comment = st.text_area("Verbesserungsvorschlag (optional)")
        submitted = st.form_submit_button("Absenden")
    if submitted:
        payload = {
            "subject": subject,
            "mood": mood,
            "difficulty": difficulty,
            "comment": comment or None
        }
        try:
            resp = requests.post(f"{API_BASE}/feedback", json=payload, timeout=5)
            if resp.status_code in (200,201):
                st.success("Danke! Dein Feedback wurde anonym gesendet.")
            else:
                st.error(f"Fehler: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Fehler beim Senden: {e}")

else:
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
            st.write(f"- **{f['subject']}** — {f['difficulty']} — {f['mood']} — {f.get('comment') or ''}")

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
