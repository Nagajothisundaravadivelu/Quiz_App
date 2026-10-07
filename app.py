import json
import html
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError


load_dotenv()
logging.basicConfig(level=logging.INFO)

MODEL = "gemini-3.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
DIFFICULTIES = ("Beginner", "Intermediate", "Advanced")
QUESTION_COUNTS = (3, 5, 8, 10)

st.set_page_config(page_title="Python Practice | Quiz Studio", page_icon="🐍", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #202b28;
        --muted: #77817b;
        --green: #236b51;
        --green-dark: #19533d;
        --mint: #e7f3ec;
        --line: #e9ece8;
        --paper: #fffefa;
        --orange: #e89d53;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        max-width: 100%;
        overflow-x: clip;
    }
    *, *::before, *::after { box-sizing: border-box; }
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { visibility: hidden; height: 0; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1140px;
        padding: 1.1rem 2rem 4rem;
    }
    [data-testid="stHorizontalBlock"] { width: 100%; min-width: 0; }
    [data-testid="column"] { min-width: 0 !important; }
    .brandbar {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 56px;
        margin-bottom: 4.2rem;
    }
    .brandbar::after {
        position: absolute;
        left: 50%;
        width: 100vw;
        bottom: -1.1rem;
        border-bottom: 1px solid #f0f1ed;
        content: "";
        transform: translateX(-50%);
    }
    .brand-lockup { display: flex; align-items: center; gap: 11px; font-weight: 800; }
    .brand-mark {
        display: grid;
        width: 34px;
        height: 34px;
        place-items: center;
        border-radius: 11px;
        background: var(--green);
        color: white;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .brand-name { color: var(--ink); font-size: 16px; }
    .brand-name span { color: var(--green); }
    .brand-status { color: #66736b; font-size: 12px; font-weight: 600; }
    .brand-status i {
        display: inline-block;
        width: 7px;
        height: 7px;
        margin-right: 8px;
        border-radius: 50%;
        background: #60a982;
        box-shadow: 0 0 0 3px #e8f4ec;
    }
    .st-key-hero-layout [data-testid="stHorizontalBlock"] { align-items: center; }
    .intro-copy { padding: 0 10px 34px 0; }
    .eyebrow, .step-label {
        color: var(--green);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.35px;
    }
    .eyebrow { margin-bottom: 20px; }
    .eyebrow span { margin-right: 6px; color: var(--orange); font-size: 14px; }
    .intro-title {
        margin: 0 0 18px;
        color: var(--ink);
        font-size: clamp(44px, 5.2vw, 68px);
        font-weight: 800;
        letter-spacing: -3.5px;
        line-height: 1.08;
    }
    .intro-description {
        max-width: 390px;
        margin: 0 0 30px;
        color: #727d76;
        font-size: 15px;
        line-height: 1.8;
    }
    .learning-note { display: flex; align-items: center; gap: 13px; color: #738078; font-size: 12px; line-height: 1.7; }
    .note-icon {
        display: grid;
        width: 38px;
        height: 38px;
        flex: 0 0 38px;
        place-items: center;
        border-radius: 12px;
        background: #f2f4e9;
        color: #73834f;
        font-size: 17px;
    }
    .learning-note strong { color: #35443b; }
    .decorative-code {
        margin: 42px 0 0 58%;
        color: #abc2b4;
        font-family: monospace;
        font-size: 11px;
        line-height: 2;
        opacity: .7;
        transform: rotate(-5deg);
    }
    .decorative-code span { margin-right: 10px; color: #d5b28e; }
    .st-key-builder-card {
        padding: 30px 32px 26px;
        border: 1px solid #eeefeb;
        border-radius: 20px;
        background: #fff;
        box-shadow: 0 22px 65px rgba(49, 68, 54, .075);
    }
    .card-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 26px; }
    .card-heading h2 { margin: 8px 0 0; color: var(--ink); font-size: 23px; letter-spacing: -.8px; }
    .python-badge {
        display: grid;
        width: 42px;
        height: 42px;
        place-items: center;
        border-radius: 14px;
        background: var(--mint);
        color: var(--green);
        font-size: 17px;
        font-weight: 800;
    }
    .st-key-builder-card [data-testid="stWidgetLabel"] p {
        margin-bottom: .45rem;
        color: #35413b;
        font-size: 12px;
        font-weight: 700;
    }
    .st-key-builder-card [data-testid="stTextInputRootElement"] {
        min-height: 47px;
        border: 1px solid #e6eae5 !important;
        border-radius: 9px;
        background: #fff !important;
        box-shadow: none;
    }
    .st-key-builder-card [data-testid="stTextInputRootElement"]:focus-within {
        border-color: #7aaa8c !important;
        box-shadow: 0 0 0 3px rgba(83, 145, 107, .12);
    }
    .st-key-builder-card [data-testid="stTextInput"] input {
        min-height: 45px;
        border: 0 !important;
        background: transparent !important;
        color: var(--ink) !important;
        font-size: 13px;
    }
    .st-key-builder-card [data-testid="stTextInput"] input::placeholder {
        color: #a8b0aa !important;
        opacity: 1;
    }
    .st-key-builder-card [data-testid="stSelectbox"] [role="group"] {
        min-height: 47px;
        border: 1px solid #e6eae5 !important;
        border-radius: 9px;
        background: #fff !important;
        color: var(--ink) !important;
        box-shadow: none;
    }
    .st-key-builder-card [data-testid="stSelectbox"] [role="group"]:focus-within {
        border-color: #7aaa8c !important;
        box-shadow: 0 0 0 3px rgba(83, 145, 107, .12);
    }
    .st-key-builder-card [data-testid="stSelectbox"] [role="combobox"] {
        min-height: 45px;
        border-color: #e6eae5;
        background: transparent !important;
        color: var(--ink) !important;
        font-size: 13px;
    }
    .st-key-builder-card [data-testid="stSelectbox"] button {
        color: #657269 !important;
    }
    .st-key-builder-card [data-testid="stFormSubmitButton"] button {
        min-height: 49px;
        border: 0;
        border-radius: 9px;
        background: var(--green);
        color: white;
        font-size: 13px;
        font-weight: 700;
    }
    .st-key-builder-card [data-testid="stFormSubmitButton"] button:hover {
        border: 0;
        background: var(--green-dark);
        color: white;
    }
    .form-footnote { margin: 13px 0 0; color: #9ba39d; font-size: 10px; text-align: center; }
    .form-footnote span { color: #d9a45e; }
    .st-key-scoreboard-card, .st-key-question-card {
        max-width: 680px;
        margin: 0 auto;
        padding: 28px 32px;
        border: 1px solid #eeefeb;
        border-radius: 20px;
        background: #fff;
        box-shadow: 0 22px 65px rgba(49, 68, 54, .075);
    }
    .scoreboard-content { width: 100%; min-width: 0; }
    .scoreboard-heading { margin-bottom: 1.5rem; text-align: center; }
    .scoreboard-kicker {
        margin-bottom: .55rem;
        color: var(--green);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.4px;
    }
    .scoreboard-heading h1 {
        margin: 0 0 .35rem;
        color: var(--ink);
        font-size: clamp(25px, 4vw, 34px);
        letter-spacing: -1px;
    }
    .scoreboard-heading p { margin: 0; color: var(--muted); font-size: 13px; overflow-wrap: anywhere; }
    .score-charts {
        display: grid;
        grid-template-columns: minmax(150px, .8fr) minmax(0, 1.2fr);
        gap: 1.25rem;
        align-items: center;
        width: 100%;
        margin-bottom: 1.25rem;
        padding: 1.25rem;
        border: 1px solid var(--line);
        border-radius: 15px;
        background: #fcfdfb;
    }
    .donut-panel { display: grid; justify-items: center; gap: .7rem; min-width: 0; }
    .score-donut {
        display: grid;
        width: clamp(112px, 16vw, 148px);
        aspect-ratio: 1;
        place-items: center;
        border-radius: 50%;
        background: conic-gradient(var(--green) var(--score-percent), #e7eee8 0);
    }
    .donut-center {
        display: grid;
        width: 74%;
        height: 74%;
        align-content: center;
        justify-items: center;
        border-radius: 50%;
        background: #fff;
    }
    .donut-value { color: var(--ink); font-size: 25px; font-weight: 800; line-height: 1.1; }
    .donut-caption { margin-top: 3px; color: var(--muted); font-size: 10px; }
    .chart-caption { color: var(--muted); font-size: 11px; font-weight: 600; text-align: center; }
    .bars-panel { display: grid; gap: 1.05rem; min-width: 0; }
    .bars-title { margin: 0; color: var(--ink); font-size: 13px; font-weight: 700; }
    .bar-row { display: grid; gap: .4rem; min-width: 0; }
    .bar-label { display: flex; justify-content: space-between; gap: .75rem; color: #58645c; font-size: 11px; }
    .bar-label strong { color: var(--ink); }
    .bar-track { width: 100%; height: 9px; overflow: hidden; border-radius: 99px; background: #e7eee8; }
    .bar-fill { height: 100%; min-width: 0; border-radius: inherit; background: #4f966a; }
    .bar-fill.needs-practice { background: #e4b56f; }
    .score-summary {
        margin: 0 0 1.25rem;
        padding: .85rem 1rem;
        border-radius: 10px;
        background: var(--mint);
        color: #355b45;
        font-size: 12px;
        line-height: 1.6;
        text-align: center;
    }
    .st-key-scoreboard-card [data-testid="stButton"] button {
        min-height: 46px;
        border: 0;
        border-radius: 9px;
        background: var(--green);
        color: white;
        font-size: 13px;
        font-weight: 700;
    }
    .st-key-scoreboard-card [data-testid="stButton"] button:hover {
        border: 0;
        background: var(--green-dark);
        color: white;
    }
    [data-testid="stMetric"] {
        padding: 1rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #fbfdfb;
    }
    [data-testid="stMetricLabel"] p { color: var(--muted); }
    [data-testid="stProgressBar"] > div > div { background: #73ad83; }
    @media (max-width: 760px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1.25rem 3rem; }
        .brandbar { margin-bottom: 2.5rem; }
        .intro-copy { padding: 0 0 1rem; }
        .intro-title { font-size: 48px; letter-spacing: -2.5px; }
        .decorative-code { display: none; }
        .st-key-builder-card { padding: 24px 20px; }
    }
    @media (max-width: 520px) {
        .st-key-hero-layout [data-testid="stHorizontalBlock"] { flex-direction: column; }
        .st-key-hero-layout [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .st-key-scoreboard-card { padding: 23px 17px; }
        .score-charts { grid-template-columns: minmax(0, 1fr); gap: 1.25rem; padding: 1rem; }
        .donut-panel { grid-template-columns: auto 1fr; justify-content: center; align-items: center; }
        .score-donut { width: 104px; }
        .chart-caption { text-align: left; }
    }
    @media (min-width: 761px) {
        .st-key-hero-layout [data-testid="column"] { min-width: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brandbar">
      <div class="brand-lockup">
        <span class="brand-mark">Py</span>
        <span class="brand-name">Python<span>Practice</span></span>
      </div>
      <span class="brand-status"><i></i>AI quiz studio</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def get_api_key():
    try:
        secret_key = st.secrets.get("GOOGLE_AI_STUDIO_API_KEY", "")
    except StreamlitSecretNotFoundError:
        secret_key = ""
    return str(secret_key or os.getenv("GOOGLE_AI_STUDIO_API_KEY", "")).strip()


def generate_quiz(topic, difficulty, question_count, api_key):
    prompt = "\n".join(
        [
            "Create a multiple-choice quiz for students learning core Python.",
            f"Topic: {topic.strip()}",
            f"Difficulty: {difficulty}",
            f"Number of questions: {question_count}",
            "Each question must have exactly four distinct answer options.",
            "Make the questions accurate, self-contained, and appropriate for the requested difficulty.",
            "Return only JSON matching this schema:",
            '{"title":"short quiz title","questions":[{"question":"...","options":["...","...","...","..."],"correctAnswer":0,"explanation":"..."}]}',
            "correctAnswer must be a zero-based integer index into options.",
        ]
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
        },
    }
    api_request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        parts = result["candidates"][0]["content"]["parts"]
        quiz = json.loads("".join(part.get("text", "") for part in parts))
    except HTTPError as error:
        logging.error("Google AI Studio request failed with HTTP %s", error.code)
        if error.code == 503:
            raise RuntimeError("Google AI Studio is temporarily busy. Please try again in a minute.") from error
        if error.code == 429:
            raise RuntimeError("Google AI Studio rate limit reached. Please wait and try again.") from error
        if error.code in {400, 401, 403}:
            raise RuntimeError("Google AI Studio rejected the request. Check your API key and API access.") from error
        raise RuntimeError("Google AI Studio could not generate the quiz. Please try again.") from error
    except (URLError, TimeoutError) as error:
        logging.error("Google AI Studio request failed: %s", error)
        raise RuntimeError("Quiz generation failed. Please check your connection and try again.") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        logging.error("Google AI Studio returned an invalid quiz response: %s", error)
        raise RuntimeError("The generated quiz was not in the expected format. Please try again.") from error

    if not is_valid_quiz(quiz, question_count):
        logging.error("Google AI Studio returned a quiz that failed validation.")
        raise RuntimeError("The generated quiz was not in the expected format. Please try again.")
    return quiz


def is_valid_quiz(quiz, expected_count):
    if (
        not isinstance(quiz, dict)
        or not isinstance(quiz.get("title"), str)
        or not isinstance(quiz.get("questions"), list)
        or len(quiz["questions"]) != expected_count
    ):
        return False

    for question in quiz["questions"]:
        if not isinstance(question, dict):
            return False
        options = question.get("options")
        answer = question.get("correctAnswer")
        if (
            not isinstance(question.get("question"), str)
            or not isinstance(options, list)
            or len(options) != 4
            or not all(isinstance(option, str) for option in options)
            or isinstance(answer, bool)
            or not isinstance(answer, int)
            or not 0 <= answer < len(options)
            or not isinstance(question.get("explanation"), str)
        ):
            return False
    return True


def reset_quiz():
    for key in ("quiz", "question_index", "score", "answered", "selected_answer", "complete"):
        st.session_state.pop(key, None)


def render_builder():
    api_key = get_api_key()
    if not api_key:
        st.warning("Add `GOOGLE_AI_STUDIO_API_KEY` to Streamlit Cloud Secrets before generating a quiz.")

    with st.container(key="hero-layout"):
        intro, builder = st.columns([0.94, 1.06], gap="large")
        with intro:
            st.markdown(
                """
                <section class="intro-copy">
                  <div class="eyebrow"><span>✳</span> LEARN BY DOING</div>
                  <h1 class="intro-title">Make Python<br>make sense.</h1>
                  <p class="intro-description">
                    Build a quick quiz around what you’re learning. Practise at your own
                    pace and get explanations that help concepts stick.
                  </p>
                  <div class="learning-note">
                    <span class="note-icon">⌘</span>
                    <span><strong>Small steps, real progress.</strong><br>One question at a time.</span>
                  </div>
                  <div class="decorative-code"><span>01</span> for idea in practice:<br>
                    <span>02</span> &nbsp;&nbsp;learn(idea)</div>
                </section>
                """,
                unsafe_allow_html=True,
            )
        with builder:
            with st.container(key="builder-card"):
                st.markdown(
                    """
                    <div class="card-heading">
                      <div><div class="step-label">YOUR LEARNING SESSION</div><h2>Create a quiz</h2></div>
                      <span class="python-badge">Py</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("quiz_builder"):
                    topic = st.text_input(
                        "What would you like to practise?",
                        placeholder="e.g. loops, lists, functions",
                        max_chars=100,
                    )
                    difficulty_column, count_column = st.columns(2, gap="small")
                    with difficulty_column:
                        difficulty = st.selectbox("Difficulty", DIFFICULTIES)
                    with count_column:
                        question_count = st.selectbox("Questions", QUESTION_COUNTS, index=1, format_func=lambda count: f"{count} questions")
                    submitted = st.form_submit_button(
                        "Create my quiz     →",
                        type="primary",
                        use_container_width=True,
                        disabled=not bool(api_key),
                    )
                    st.markdown(
                        '<p class="form-footnote"><span>✦</span> Made for curious Python learners</p>',
                        unsafe_allow_html=True,
                    )

                if not api_key:
                    st.caption("Configure the API key to enable quiz generation.")

    if submitted:
        if not 2 <= len(topic.strip()) <= 100:
            st.error("Enter a topic between 2 and 100 characters.")
            return
        try:
            with st.spinner("Creating your quiz…"):
                quiz = generate_quiz(topic, difficulty, question_count, api_key)
        except RuntimeError as error:
            st.error(str(error))
            return
        st.session_state.quiz = quiz
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected_answer = None
        st.session_state.complete = False
        st.rerun()


def render_question():
    quiz = st.session_state.quiz
    question_index = st.session_state.question_index
    total = len(quiz["questions"])
    question = quiz["questions"][question_index]

    st.button("← New quiz", on_click=reset_quiz)
    st.title(quiz["title"])
    st.progress(question_index / total, text=f"Question {question_index + 1} of {total}")
    st.caption(f"Score: {st.session_state.score} correct")
    st.subheader(question["question"])

    selected = st.radio(
        "Choose an answer",
        options=range(len(question["options"])),
        format_func=lambda index: question["options"][index],
        index=st.session_state.selected_answer,
        key=f"answer_{question_index}",
        label_visibility="collapsed",
        disabled=st.session_state.answered,
    )
    st.session_state.selected_answer = selected

    if not st.session_state.answered:
        if st.button(
            "Check answer",
            type="primary",
            use_container_width=True,
            disabled=selected is None,
        ):
            st.session_state.answered = True
            st.session_state.is_correct = selected == question["correctAnswer"]
            if st.session_state.is_correct:
                st.session_state.score += 1
            st.rerun()
    else:
        if st.session_state.is_correct:
            st.success(f"That's right! {question['explanation']}")
        else:
            correct_option = question["options"][question["correctAnswer"]]
            st.error(f"Not quite. The correct answer is **{correct_option}**. {question['explanation']}")

        button_label = "See my score" if question_index == total - 1 else "Next question"
        if st.button(button_label, type="primary", use_container_width=True):
            if question_index == total - 1:
                st.session_state.complete = True
            else:
                st.session_state.question_index += 1
                st.session_state.answered = False
                st.session_state.selected_answer = None
            st.rerun()


def render_scoreboard():
    quiz = st.session_state.quiz
    total = len(quiz["questions"])
    score = st.session_state.score
    percentage = round(score / total * 100)
    if percentage == 100:
        result_title = "Brilliant work!"
        result_message = "You got every question right. Keep up the great work!"
    elif percentage >= 50:
        result_title = "Nice work!"
        result_message = "You have a good start. Review the missed topics and keep practising."
    else:
        result_title = "Keep practising!"
        result_message = "Every question is a chance to learn. Try again and watch your score grow."

    correct_percent = score / total * 100
    practise_percent = (total - score) / total * 100
    safe_title = html.escape(quiz["title"])

    with st.container(key="scoreboard-card"):
        st.button("← New quiz", on_click=reset_quiz)
        st.markdown(
            f"""
            <section class="scoreboard-content">
              <header class="scoreboard-heading">
                <div class="scoreboard-kicker">QUIZ COMPLETE</div>
                <h1>{result_title}</h1>
                <p>{safe_title}</p>
              </header>
              <div class="score-charts">
                <div class="donut-panel">
                  <div class="score-donut" role="img" aria-label="Score: {percentage} percent correct"
                       style="--score-percent: {percentage}%">
                    <div class="donut-center">
                      <span class="donut-value">{percentage}%</span>
                      <span class="donut-caption">{score} of {total} correct</span>
                    </div>
                  </div>
                  <div class="chart-caption">Overall score</div>
                </div>
                <div class="bars-panel" role="img"
                     aria-label="Answer breakdown: {score} correct, {total - score} to practise">
                  <p class="bars-title">Answer breakdown</p>
                  <div class="bar-row">
                    <div class="bar-label"><span>Correct</span><strong>{score}</strong></div>
                    <div class="bar-track"><div class="bar-fill" style="width: {correct_percent:.2f}%"></div></div>
                  </div>
                  <div class="bar-row">
                    <div class="bar-label"><span>To practise</span><strong>{total - score}</strong></div>
                    <div class="bar-track"><div class="bar-fill needs-practice" style="width: {practise_percent:.2f}%"></div></div>
                  </div>
                </div>
              </div>
              <p class="score-summary">{result_message}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.button("Create another quiz", type="primary", use_container_width=True, on_click=reset_quiz)


if st.session_state.get("quiz"):
    if st.session_state.get("complete"):
        render_scoreboard()
    else:
        render_question()
else:
    render_builder()
