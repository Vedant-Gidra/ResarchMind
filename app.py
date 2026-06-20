import streamlit as st
import time
from agents import (
    build_researcher_agent,
    build_writer_chain,
)
from error_handling import normalize_llm_error


def _extract_last_message_content(step_name: str, result: dict) -> str:
    try:
        messages = result.get("messages", [])
        if not messages:
            raise ValueError("No messages returned.")
        content = messages[-1].content
        if not content:
            raise ValueError("Last message content is empty.")
        return content
    except Exception as exc:
        raise RuntimeError(f"{step_name} returned an invalid response format.") from exc


st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 900px; }

.hero {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span {
    color: #ff8c32;
}
.hero-sub {
    font-size: 1rem;
    font-weight: 300;
    color: #a09890;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 1.5rem 0;
}

.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.2rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 2.5rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}

.thinking-box {
    background: rgba(255,140,50,0.08);
    border: 1px solid rgba(255,140,50,0.25);
    border-radius: 12px;
    padding: 1.8rem;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}

.thinking-box::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: #ff8c32;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.thinking-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.8;
}

.thinking-message {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    color: #d8d3ca;
}

.thinking-dot {
    display: inline-block;
    width: 4px;
    height: 4px;
    background: #ff8c32;
    border-radius: 50%;
    margin-left: 0.3rem;
    animation: bounce 1.4s infinite;
}
.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 100% { transform: translateY(0); opacity: 1; }
    50% { transform: translateY(-4px); opacity: 0.5; }
}

.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
}

.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 2rem;
    letter-spacing: 0.08em;
}

.stSpinner > div { color: #ff8c32 !important; }
</style>
""", unsafe_allow_html=True)


for key in ("results", "running", "done", "error", "thinking"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key == "thinking":
            st.session_state[key] = []
        elif key == "error":
            st.session_state[key] = ""
        else:
            st.session_state[key] = False


st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        AI-powered research that searches the web and writes comprehensive reports on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


st.markdown('<div class="input-card">', unsafe_allow_html=True)
topic = st.text_input(
    "Research Topic",
    placeholder="e.g. AI Advacements In 2026",
    key="topic_input",
    label_visibility="visible",
)
run_btn = st.button("Run Research Pipeline", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.error = ""
        st.session_state.thinking = []
        st.rerun()


thinking_placeholder = st.empty()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = (st.session_state.topic_input or "").strip()

    st.markdown("""
    <script>
        const thinkingElement = document.querySelector('[data-testid="stVerticalBlock"]');
        if (thinkingElement) {
            setTimeout(() => {
                thinkingElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    </script>
    """, unsafe_allow_html=True)

    try:
        if not topic_val:
            raise ValueError("Research topic is empty. Please enter a valid topic.")

        thinking_messages = []

        thinking_messages.append(f"🔍 Searching for information about '{topic_val}'...")
        with thinking_placeholder.container():
            st.markdown(f"""
            <div class="thinking-box">
                <div class="thinking-title">Researcher Agent Thinking</div>
                <div class="thinking-message">{thinking_messages[-1]}<span class="thinking-dot"></span><span class="thinking-dot"></span><span class="thinking-dot"></span></div>
            </div>
            """, unsafe_allow_html=True)

        time.sleep(0.3)

        researcher_agent = build_researcher_agent()
        rr = researcher_agent.invoke({
            "messages": [("user", f"Find recent and relevant information about: {topic_val}")]
        })
        results["researcher"] = _extract_last_message_content("Researcher step", rr)
        st.session_state.results = dict(results)

        thinking_messages.append(f"✓ Found relevant sources about '{topic_val}'")
        thinking_messages.append("✍️ Analyzing findings and drafting report...")
        with thinking_placeholder.container():
            st.markdown(f"""
            <div class="thinking-box">
                <div class="thinking-title">Writer Agent Thinking</div>
                <div class="thinking-message">{thinking_messages[-1]}<span class="thinking-dot"></span><span class="thinking-dot"></span><span class="thinking-dot"></span></div>
            </div>
            """, unsafe_allow_html=True)

        time.sleep(0.3)

        writer_chain = build_writer_chain()
        writer_output = writer_chain.invoke({
            "topic": topic_val,
            "research": results["researcher"]
        })
        if not writer_output:
            raise RuntimeError("Writer produced an empty report.")
        results["writer"] = writer_output
        st.session_state.results = dict(results)

        thinking_messages.append("✓ Report generated successfully!")
        st.session_state.thinking = thinking_messages
        st.session_state.done = True
        st.session_state.error = ""

    except Exception as exc:
        st.session_state.error = normalize_llm_error(exc)
        st.session_state.done = False
    finally:
        st.session_state.running = False

    st.rerun()


r = st.session_state.results
err = st.session_state.error

if err:
    st.error(f"Pipeline failed: {err}")

if r and not st.session_state.running:
    thinking_placeholder.empty()

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <script>
        const resultsElement = document.getElementById('results');
        if (resultsElement) {
            setTimeout(() => {
                resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    </script>
    """, unsafe_allow_html=True)

    st.write('<div id="results"></div>', unsafe_allow_html=True)

    if "researcher" in r:
        with st.expander("Research Data", expanded=False):
            st.text(r["researcher"])

    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )


st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain and Groq · Built with Streamlit
</div>
""", unsafe_allow_html=True)
