import re
from datetime import datetime, timedelta

import streamlit as st
from supabase import create_client

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Flashcards", page_icon="✨", layout="centered")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------- HELPERS ----------------
def normalize_profile_code(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]", "", value)
    return value


def get_profile_id():
    uid = st.query_params.get("uid", "")
    if isinstance(uid, list):
        uid = uid[0] if uid else ""
    return uid


def set_profile_id(uid: str):
    st.query_params["uid"] = uid


def load_words(user_id: str):
    res = (
        supabase.table("flashcards_words")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at")
        .execute()
    )
    return res.data if res.data else []


def add_word(user_id: str, eng: str, rus: str):
    supabase.table("flashcards_words").insert({
        "user_id": user_id,
        "english": eng.strip(),
        "russian": rus.strip(),
        "interval": 1,
        "next_review": datetime.now().isoformat()
    }).execute()


def update_word(word_id: int, known: bool):
    res = (
        supabase.table("flashcards_words")
        .select("*")
        .eq("id", word_id)
        .single()
        .execute()
    )

    word = res.data
    if not word:
        return

    current_interval = int(word.get("interval", 1))
    new_interval = current_interval * 2 if known else 1
    next_review = datetime.now() + timedelta(days=new_interval)

    (
        supabase.table("flashcards_words")
        .update({
            "interval": new_interval,
            "next_review": next_review.isoformat()
        })
        .eq("id", word_id)
        .execute()
    )


def delete_word(word_id: int):
    supabase.table("flashcards_words").delete().eq("id", word_id).execute()


def get_due_words(words):
    now = datetime.now()
    result = []
    for word in words:
        try:
            review_time = datetime.fromisoformat(word["next_review"])
            if review_time <= now:
                result.append(word)
        except Exception:
            result.append(word)
    return result


# ---------------- SESSION ----------------
if "show_translation" not in st.session_state:
    st.session_state.show_translation = False


# ---------------- STYLES ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(233, 246, 238, 0.95) 0%, transparent 28%),
        radial-gradient(circle at top right, rgba(236, 244, 250, 0.92) 0%, transparent 24%),
        linear-gradient(180deg, #f5fbf7 0%, #eef7f1 50%, #edf5ef 100%);
    color: #1d1d1f;
}

.block-container {
    max-width: 920px;
    padding-top: 2.2rem;
    padding-bottom: 2.2rem;
}

hr {
    display: none !important;
}
[data-testid="stForm"] {
    border: none !important;
}

.hero {
    text-align: center;
    padding: 1.1rem 0 0.9rem 0;
    margin-bottom: 0.15rem;
}

.hero-title {
    font-size: 3.15rem;
    line-height: 1.03;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: #1d1d1f;
    margin-bottom: 0.35rem;
}

.hero-subtitle {
    font-size: 1.08rem;
    color: #66746c;
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.45;
}

.section-shell {
    background: rgba(255, 255, 255, 0.64);
    backdrop-filter: blur(14px);
    border-radius: 30px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(41, 63, 51, 0.05);
    border: none !important;
}

.section-title {
    font-size: 1.28rem;
    font-weight: 650;
    color: #1d1d1f;
    margin-bottom: 0.9rem;
    letter-spacing: -0.02em;
}

.flashcard-box {
    background: linear-gradient(135deg, #edf8f1 0%, #e8f2ec 100%);
    border-radius: 26px;
    padding: 34px 18px;
    text-align: center;
    margin-top: 6px;
    margin-bottom: 14px;
    border: none;
}

.flashcard-word {
    font-size: 2.65rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: #1d1d1f;
    margin-bottom: 0.35rem;
}

.flashcard-hint {
    color: #6a776f;
    font-size: 1rem;
    line-height: 1.45;
}

.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.stat-card {
    background: rgba(255, 255, 255, 0.72);
    border-radius: 22px;
    padding: 18px;
    border: none;
}

.stat-label {
    color: #6e7c73;
    font-size: 0.95rem;
    margin-bottom: 4px;
}

.stat-value {
    color: #1d1d1f;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.03em;
}

.word-item {
    background: rgba(255, 255, 255, 0.75);
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: none;
    color: #2a342e;
}

.word-item b {
    color: #1d1d1f;
}

.profile-box {
    background: rgba(255, 255, 255, 0.72);
    border-radius: 22px;
    padding: 16px 18px;
    margin-bottom: 14px;
    color: #4d5e54;
}

.stTextInput > label,
.stNumberInput > label {
    color: #4a5a51 !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.96) !important;
    color: #1d1d1f !important;
    border: 1px solid rgba(205, 221, 211, 0.95) !important;
    border-radius: 18px !important;
    padding: 0.86rem 1rem !important;
    font-size: 1rem !important;
    box-shadow: none !important;
}

.stTextInput > div > div > input:focus {
    border: 1px solid #a9c7b1 !important;
    box-shadow: 0 0 0 1px #a9c7b1 !important;
}

.stNumberInput > div > div > input {
    background: #f4faf6 !important;
    color: #24312a !important;
    border: 1px solid #d6e4da !important;
    border-radius: 16px !important;
    padding: 0.78rem 0.95rem !important;
}

.stFormSubmitButton > button,
.stButton > button {
    border-radius: 999px !important;
    border: none !important;
    padding: 0.74rem 1.24rem !important;
    font-weight: 650 !important;
    font-size: 0.98rem !important;
    box-shadow: none !important;
    transition: all 0.16s ease !important;
}

.stFormSubmitButton > button:hover,
.stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.02);
}

/* По умолчанию все кнопки мягко-голубые */
.stFormSubmitButton > button,
.stButton > button {
    background: linear-gradient(135deg, #d9ebfa 0%, #c7ddf2 100%) !important;
    color: #26445d !important;
}

/* Порядок кнопок stButton после выбора профиля:
1 = Показать перевод
2 = Знаю
3 = Не знаю
4 = Удалить выбранное слово
*/

/* Знаю */
div[data-testid="stButton"]:nth-of-type(2) > button {
    background: linear-gradient(135deg, #dcefdc 0%, #c9e2c9 100%) !important;
    color: #2f5a35 !important;
}

/* Не знаю */
div[data-testid="stButton"]:nth-of-type(3) > button {
    background: linear-gradient(135deg, #f0d7d7 0%, #e7c6c6 100%) !important;
    color: #6a3535 !important;
}

div[data-testid="stAlert"] {
    border-radius: 18px !important;
    border: none !important;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.35rem;
    }
    .stat-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div class="hero-title">Flashcards</div>
    <div class="hero-subtitle">
        Изучение английских слов через интервальные повторения
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- PROFILE ENTRY ----------------
user_id = get_profile_id()

if not user_id:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Создай свой профиль</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="profile-box">Придумай свой логин, чтобы входить в свои слова с любого устройства.</div>',
        unsafe_allow_html=True
    )

    with st.form("profile_form"):
        profile_code = st.text_input("Логин")
        submitted_profile = st.form_submit_button("Продолжить")

        if submitted_profile:
            profile_code = normalize_profile_code(profile_code)
            if profile_code:
                set_profile_id(profile_code)
                st.rerun()
            else:
                st.warning("Введи логин: только английские буквы, цифры, _ или -")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- PROFILE INFO ----------------
st.markdown(
    f'<div class="profile-box"><b>Текущий профиль:</b> {user_id}</div>',
    unsafe_allow_html=True
)

words = load_words(user_id)
due_words = get_due_words(words)

# ---------------- ADD WORD ----------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Добавить новое слово</div>', unsafe_allow_html=True)

with st.form("add_word_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        english = st.text_input("Английское слово", placeholder="Например: apple")

    with col2:
        russian = st.text_input("Перевод", placeholder="Например: яблоко")

    submitted = st.form_submit_button("Добавить слово")

    if submitted:
        if english.strip() and russian.strip():
            add_word(user_id, english, russian)
            st.success(f"Слово «{english.strip()}» добавлено.")
            st.rerun()
        else:
            st.warning("Заполни оба поля.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FLASHCARD ----------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Карточка для повторения</div>', unsafe_allow_html=True)

if due_words:
    current_word = due_words[0]

    st.markdown(f"""
    <div class="flashcard-box">
        <div class="flashcard-word">{current_word['english']}</div>
        <div class="flashcard-hint">Сначала вспомни перевод, потом проверь себя.</div>
    </div>
    """, unsafe_allow_html=True)

    top_c1, top_c2, top_c3 = st.columns([1, 1.15, 1])
    with top_c2:
        if st.button("Показать перевод", key="show_translation_btn"):
            st.session_state.show_translation = True

    if st.session_state.show_translation:
        st.info(f"Перевод: {current_word['russian']}")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Знаю", key="know_btn"):
            update_word(current_word["id"], True)
            st.session_state.show_translation = False
            st.success("Отлично. Интервал увеличен.")
            st.rerun()

    with c2:
        if st.button("Не знаю", key="dont_know_btn"):
            update_word(current_word["id"], False)
            st.session_state.show_translation = False
            st.warning("Слово отправлено на повторение.")
            st.rerun()
else:
    st.markdown("""
    <div class="flashcard-box">
        <div class="flashcard-word">На сегодня слов нет</div>
        <div class="flashcard-hint">Добавь новые слова или вернись позже.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STATS ----------------
words = load_words(user_id)
due_words = get_due_words(words)

st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Статистика</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-label">Всего слов</div>
        <div class="stat-value">{len(words)}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Доступно для повторения сейчас</div>
        <div class="stat-value">{len(due_words)}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- WORD LIST ----------------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Список слов</div>', unsafe_allow_html=True)

if words:
    for i, word in enumerate(words, start=1):
        next_review_display = word.get("next_review", "")
        if "T" in next_review_display:
            next_review_display = next_review_display.split("T")[0]

        st.markdown(
            f'<div class="word-item"><b>{i}. {word["english"]}</b> — {word["russian"]} | '
            f'интервал: {word.get("interval", 1)} дн. | следующее повторение: {next_review_display}</div>',
            unsafe_allow_html=True
        )

    delete_index = st.number_input(
        "Номер слова для удаления",
        min_value=1,
        max_value=len(words),
        step=1
    )

    if st.button("Удалить выбранное слово", key="delete_btn"):
        word_id = words[delete_index - 1]["id"]
        delete_word(word_id)
        st.warning("Слово удалено.")
        st.rerun()
else:
    st.write("Список пока пуст.")

st.markdown('</div>', unsafe_allow_html=True)
