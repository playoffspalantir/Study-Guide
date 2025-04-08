# app.py

import streamlit as st
import google.generativeai as genai
import random
import re
from datetime import datetime

def ai_analysis(data, topic, question=None, answer=None):
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        if question and answer:
            response = model.generate_content((
                f"The user selected answer {answer} to the following question:\n\n"
                f"{question}\n\n"
                f"The topic is {topic}. Is this the correct answer? If not, explain why and give the correct one."
            ))
            return response.text if response else "No response text available."
        else:
            response = model.generate_content((
                f"Generate a multiple choice question on the topic: {topic}.\n"
                "Include 4 answer options labeled A to D.\n"
                "Clearly indicate the correct answer at the end using the format:\n\n"
                "'Answer: X'"
            ))
            return response.text if response else "No response text available."
    except Exception as e:
        return f"Analysis Error: {str(e)}"

def parse_question_and_answer(text):
    match = re.search(r'Answer:\s*([A-D])', text)
    correct = match.group(1) if match else None
    question_only = re.sub(r'Answer:\s*[A-D]', '', text).strip()
    return question_only, correct

def app():
    API_KEY = ""
    genai.configure(api_key=API_KEY)

    st.title("📊 Statistics Study App")

    # Topics
    topics = [
        "Descriptive Statistics & Data Summarization",
        "Probability & Distributions",
        "Hypothesis Testing Fundamentals",
        "Advanced Hypothesis Testing & Multiple Comparisons",
        "Regression Analysis",
        "Experimental Design",
        "Survival Analysis",
        "Ethical Considerations & Data Integrity",
        "Preparing Written Material",
        "Understanding and Interpreting Written Material",
        "Descriptive and Inferential Statistics",
        "Understanding and Interpreting Tabular Material",
        "Evaluating Conclusions in Light of Known Facts"
    ]

    # Init session states
    if 'question_log' not in st.session_state:
        st.session_state.question_log = []
    if 'topic_stats' not in st.session_state:
        st.session_state.topic_stats = {t: {'correct': 0, 'total': 0} for t in topics}
    if 'question_output' not in st.session_state:
        st.session_state.question_output = None
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'topic' not in st.session_state:
        st.session_state.topic = None

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📘 Generate Question")
        topic = st.selectbox("Select Topic or Random", ["Random"] + topics)
        if st.button("🎲 Generate Question"):
            with st.spinner("Thinking..."):
                if topic == "Random":
                    topic = random.choice(topics)
                full_output = ai_analysis("", topic)
                question, correct = parse_question_and_answer(full_output)
                st.session_state.topic = topic
                st.session_state.question_output = question
                st.session_state.correct_answer = correct
        if st.session_state.question_output:
            st.text_area("Question", value=st.session_state.question_output, height=350)

    with col2:
        st.subheader("✏️ Select Answer")
        answer = st.selectbox("Choose your answer:", ["A", "B", "C", "D"])
        if st.button("✅ Submit Answer"):
            correct = (answer == st.session_state.correct_answer)
            st.success(f"Your answer was: {answer}")
            if correct:
                st.info("✅ Correct!")
            else:
                st.warning(f"❌ Incorrect! Correct answer: {st.session_state.correct_answer}")

            # Log result
            st.session_state.topic_stats[st.session_state.topic]['total'] += 1
            if correct:
                st.session_state.topic_stats[st.session_state.topic]['correct'] += 1

            st.session_state.question_log.append({
                'timestamp': datetime.now().isoformat(),
                'topic': st.session_state.topic,
                'question': st.session_state.question_output,
                'selected_answer': answer,
                'correct': correct
            })

        if st.button("💡 Explain Answer"):
            with st.spinner("Analyzing your answer..."):
                explanation = ai_analysis("", st.session_state.topic, st.session_state.question_output, answer)
                st.text_area("Explanation", value=explanation, height=300)

    st.sidebar.subheader("📈 Your Study Focus")
    for topic, stats in st.session_state.topic_stats.items():
        if stats['total'] == 0:
            continue
        accuracy = stats['correct'] / stats['total']
        if accuracy < 0.6:
            st.sidebar.markdown(f"🔴 **{topic}** — {accuracy:.0%} accuracy")
        else:
            st.sidebar.markdown(f"🟢 {topic} — {accuracy:.0%} accuracy")

if __name__ == "__main__":
    app()
