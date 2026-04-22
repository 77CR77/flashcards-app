import streamlit as st
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "words.json"


def load_words():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_words(words):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(words, file, ensure_ascii=False, indent=4)


def get_due_words(words):
    now = datetime.now()
    due_words = []

    for word in words:
        try:
            review_time = datetime.strptime(word["next_review"], "%Y-%m-%d %H:%M:%S")
            if review_time <= now:
                due_words.append(word)
        except Exception:
            due_words.append(word)

    return due_words


def mark_word(words, current_word, known):
    for word in words:
        if (
            word["english"] == current_word["english"]
            and word["russian"] == current_word["russian"]
            and word["next_review"] == current_word["next_review"]
        ):
            current_interval = int(word.get("interval", 1))

            if known:
                word["interval"] = max(1, current_interval * 2)
            else:
                word["interval"] = 1

            next_review_date = datetime.now() + timedelta(days=word["interval"])
            word["next_review"] = next_review_date.strftime("%Y-%m-%d %H:%M:%S")
            break

    save_words(words)


def delete_word_by_index(words, index):
    if 0 <= index < len(words):
        del words[index]
        save_words(words)


st.set_page_config(
    page_title="Flashcards",
    page_icon="✨",
    layout="centered"
)

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

/* Убираем стандартные линии/отступы */
hr {
    display: none !important;
}
[data-testid="stForm"] {
    border: none !important;
}

/* Верх */
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

/* Секции */
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

/* Карточка слова */
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

/* Статистика */
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

/* Список слов */
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

/* Поля ввода */
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

/* Кнопки: база */
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

/* Все обычные кнопки — мягко-голубые */
.stFormSubmitButton > button,
.stButton > button {
    background: linear-gradient(135deg, #d9ebfa 0%, #c7ddf2 100%) !important;
    color: #26445d !important;
}

/*
Порядок stButton в приложении:
1 = Показать перевод
2 = Знаю
3 = Не знаю
4 = Удалить выбранное слово
*/

/* Знаю — мягко-зелёная */
div[data-testid="stButton"]:nth-of-type(2) > button {
    background: linear-gradient(135deg, #dcefdc 0%, #c9e2c9 100%) !important;
    color: #2f5a35 !important;
}

/* Не знаю — мягко-красная */
div[data-testid="stButton"]:nth-of-type(3) > button {
    background: linear-gradient(135deg, #f0d7d7 0%, #e7c6c6 100%) !important;
    color: #6a3535 !important;
}

/* Уведомления */
div[data-testid="stAlert"] {
    border-radius: 18px !important;
    border: none !important;
}

/* Мобильная версия */
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

st.markdown("""
<div class="hero">
    <div class="hero-title">Flashcards</div>
    <div class="hero-subtitle">
        Изучение английских слов через интервальные повторения
    </div>
</div>
""", unsafe_allow_html=True)

words = load_words()
due_words = get_due_words(words)

# ---------- ДОБАВЛЕНИЕ ----------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Добавить новое слово</div>', unsafe_allow_html=True)

with st.form("add_word_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        english = st.text_input(
            "Английское слово",
            placeholder="Например: apple"
        )

    with col2:
        russian = st.text_input(
            "Перевод",
            placeholder="Например: яблоко"
        )

    submitted = st.form_submit_button("Добавить слово")

    if submitted:
        if english.strip() and russian.strip():
            new_word = {
                "english": english.strip(),
                "russian": russian.strip(),
                "interval": 1,
                "next_review": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            words.append(new_word)
            save_words(words)
            st.success(f"Слово «{english.strip()}» добавлено.")
            st.rerun()
        else:
            st.warning("Заполни оба поля.")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- КАРТОЧКА ----------
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

    if "show_translation" not in st.session_state:
        st.session_state.show_translation = False

    top_c1, top_c2, top_c3 = st.columns([1, 1.15, 1])
    with top_c2:
        if st.button("Показать перевод", key="show_translation_btn"):
            st.session_state.show_translation = True

    if st.session_state.show_translation:
        st.info(f"Перевод: {current_word['russian']}")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Знаю", key="know_btn"):
            mark_word(words, current_word, True)
            st.session_state.show_translation = False
            st.success("Отлично. Интервал увеличен.")
            st.rerun()

    with c2:
        if st.button("Не знаю", key="dont_know_btn"):
            mark_word(words, current_word, False)
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

# ---------- СТАТИСТИКА ----------
words = load_words()
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

# ---------- СПИСОК СЛОВ ----------
st.markdown('<div class="section-shell">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Список слов</div>', unsafe_allow_html=True)

if words:
    for i, word in enumerate(words, start=1):
        next_review_short = word.get("next_review", "").split(" ")[0] if word.get("next_review") else "—"
        st.markdown(
            f'<div class="word-item"><b>{i}. {word["english"]}</b> — {word["russian"]} | '
            f'интервал: {word.get("interval", 1)} дн. | следующее повторение: {next_review_short}</div>',
            unsafe_allow_html=True
        )

    st.write("")
    delete_index = st.number_input(
        "Номер слова для удаления",
        min_value=1,
        max_value=len(words),
        step=1
    )

    if st.button("Удалить выбранное слово", key="delete_btn"):
        delete_word_by_index(words, delete_index - 1)
        st.warning("Слово удалено.")
        st.rerun()
else:
    st.write("Список пока пуст.")

st.markdown('</div>', unsafe_allow_html=True)