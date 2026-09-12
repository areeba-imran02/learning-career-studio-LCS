"""
Learning & Career Studio (LCS)
Intelligent Student Learning & Career Platform
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
import time
import re
from datetime import datetime, timedelta
from groq import Groq

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Learning & Career Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLOR SYSTEM
# ============================================================
COLORS = {
    "navy": "#182B49",
    "navy_dark": "#0F1B30",
    "purple": "#6C63FF",
    "purple_dark": "#4E46E5",
    "teal": "#19B5A5",
    "soft_pink": "#F8D7E8",
    "blush_pink": "#FCEAF3",
    "rose": "#E8A4C4",
    "rose_dark": "#D6427E",
    "pink_purple": "#D8B4E2",
    "soft_white": "#FAFBFE",
    "cool_lavender": "#F4F1FA",
    "very_light_pink": "#FFF7FA",
    "amber": "#E8A94C",
    "amber_dark": "#C97D1E",
    "cyan": "#33B7E8",
    "cyan_dark": "#1C8FBF",
    "success": "#1FAE6B",
    "danger": "#E24C6B",
}

# Category -> accent color, used for sidebar nav coloring + page headers
GROUP_COLORS = {
    "MAIN": COLORS["purple"],
    "LEARNING": COLORS["teal"],
    "CAREER": COLORS["rose_dark"],
    "PREPARATION": COLORS["amber_dark"],
    "INTELLIGENCE": COLORS["cyan_dark"],
}

# ============================================================
# NAVIGATION STRUCTURE
# ============================================================
NAV_STRUCTURE = {
    "MAIN": ["Dashboard", "My Profile"],
    "LEARNING": ["Study", "Roadmap", "Planner", "Subjects", "Notes", "Quizzes", "Mock Exams", "Progress"],
    "CAREER": ["Discover", "Skills", "Skill Gap", "Career Roadmap", "Projects", "Certifications"],
    "PREPARATION": ["CV Analyzer", "Job Matcher", "Internships", "Interview", "Readiness"],
    "INTELLIGENCE": ["Next Action", "Live Agent"],
}

PAGE_META = {
    "Dashboard": {"icon": "🏠", "subtitle": "Your learning and career journey at a glance.", "group": "MAIN"},
    "My Profile": {"icon": "🧑‍🎓", "subtitle": "This information powers personalization across LCS.", "group": "MAIN"},
    "Study": {"icon": "📘", "subtitle": "Structured explanations for any topic, on demand.", "group": "LEARNING"},
    "Roadmap": {"icon": "🗺️", "subtitle": "Your personalized, milestone-based study roadmap.", "group": "LEARNING"},
    "Planner": {"icon": "🗓️", "subtitle": "Plan, schedule and track your study tasks.", "group": "LEARNING"},
    "Subjects": {"icon": "📚", "subtitle": "Manage the subjects you are currently studying.", "group": "LEARNING"},
    "Notes": {"icon": "📝", "subtitle": "Keep organized notes for every subject and topic.", "group": "LEARNING"},
    "Quizzes": {"icon": "❓", "subtitle": "Test your knowledge with AI-generated quizzes.", "group": "LEARNING"},
    "Mock Exams": {"icon": "🧪", "subtitle": "Simulate a full, multi-topic exam experience.", "group": "LEARNING"},
    "Progress": {"icon": "📈", "subtitle": "Track how your learning is progressing over time.", "group": "LEARNING"},
    "Discover": {"icon": "🧭", "subtitle": "Discover careers that match your profile.", "group": "CAREER"},
    "Skills": {"icon": "🛠️", "subtitle": "Manage the skills you are building.", "group": "CAREER"},
    "Skill Gap": {"icon": "🔍", "subtitle": "Identify what's missing for your target career.", "group": "CAREER"},
    "Career Roadmap": {"icon": "🚀", "subtitle": "Your personalized path toward your career goal.", "group": "CAREER"},
    "Projects": {"icon": "💼", "subtitle": "Track portfolio projects that showcase your skills.", "group": "CAREER"},
    "Certifications": {"icon": "🎖️", "subtitle": "Track certifications you hold or plan to earn.", "group": "CAREER"},
    "CV Analyzer": {"icon": "📄", "subtitle": "Get instant AI feedback on your CV.", "group": "PREPARATION"},
    "Job Matcher": {"icon": "🎯", "subtitle": "See how well you match a job description.", "group": "PREPARATION"},
    "Internships": {"icon": "🏢", "subtitle": "Discover internships suited to your profile.", "group": "PREPARATION"},
    "Interview": {"icon": "🎤", "subtitle": "Practice live with an AI mock interviewer.", "group": "PREPARATION"},
    "Readiness": {"icon": "✅", "subtitle": "See exactly how career-ready you are right now.", "group": "PREPARATION"},
    "Next Action": {"icon": "⚡", "subtitle": "Your smartest next move, decided by LCS.", "group": "INTELLIGENCE"},
    "Live Agent": {"icon": "💬", "subtitle": "Chat live with your personal LCS AI agent.", "group": "INTELLIGENCE"},
}

# ============================================================
# GLOBAL THEME / CSS
# ============================================================
def build_nav_color_css():
    """Generates per-section coloring for the sidebar nav buttons based on NAV_STRUCTURE order."""
    rules = []
    idx = 1
    for group, items in NAV_STRUCTURE.items():
        start, end = idx, idx + len(items) - 1
        color = GROUP_COLORS[group]
        rules.append(f"""
        section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(n+{start}):nth-of-type(-n+{end}) > button {{
            border-left: 4px solid {color} !important;
            color: #EAF0FF !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(n+{start}):nth-of-type(-n+{end}) > button:hover {{
            background: linear-gradient(90deg, {color}55 0%, transparent 100%) !important;
            border-left: 4px solid {color} !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(n+{start}):nth-of-type(-n+{end}) > button[kind="primary"] {{
            background: linear-gradient(90deg, {color} 0%, {color}CC 100%) !important;
            border-left: 4px solid #FFFFFF !important;
            color: #FFFFFF !important;
            box-shadow: 0 3px 10px {color}66;
        }}
        """)
        idx = end + 1
    return "\n".join(rules)


def apply_theme():
    nav_css = build_nav_color_css()
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        :root {{
            --navy: {COLORS['navy']};
            --navy-dark: {COLORS['navy_dark']};
            --purple: {COLORS['purple']};
            --purple-dark: {COLORS['purple_dark']};
            --teal: {COLORS['teal']};
            --soft-pink: {COLORS['soft_pink']};
            --blush-pink: {COLORS['blush_pink']};
            --rose: {COLORS['rose']};
            --rose-dark: {COLORS['rose_dark']};
            --pink-purple: {COLORS['pink_purple']};
            --soft-white: {COLORS['soft_white']};
            --cool-lavender: {COLORS['cool_lavender']};
            --very-light-pink: {COLORS['very_light_pink']};
            --amber: {COLORS['amber']};
            --cyan: {COLORS['cyan']};
            --success: {COLORS['success']};
            --danger: {COLORS['danger']};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}

        .stApp {{
            background: radial-gradient(circle at top left, #F0EEFC 0%, var(--soft-white) 35%, var(--cool-lavender) 100%);
        }}

        /* ---------- SIDEBAR ---------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--navy) 0%, var(--navy-dark) 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }}
        section[data-testid="stSidebar"] * {{
            color: #EAF0FF !important;
        }}
        .lcs-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 6px 4px 14px 4px;
        }}
        .lcs-brand-badge {{
            width: 38px; height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--purple) 0%, var(--cyan) 100%);
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            box-shadow: 0 4px 14px rgba(108,99,255,0.45);
        }}
        .lcs-brand-title {{
            font-family: 'Poppins', sans-serif;
            font-weight: 800;
            font-size: 18px;
            letter-spacing: 0.5px;
            margin: 0;
        }}
        .lcs-brand-sub {{
            font-size: 11px;
            color: #A9B6D9 !important;
            margin: 0;
        }}

        .lcs-section-label {{
            color: #7C8DBF !important;
            font-size: 10.5px;
            letter-spacing: 1.4px;
            font-weight: 700;
            margin-top: 18px;
            margin-bottom: 6px;
            padding-left: 4px;
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            background-color: rgba(255,255,255,0.04);
            border: none;
            border-radius: 8px;
            margin-bottom: 4px;
            font-weight: 600;
            font-size: 14px;
            padding: 9px 14px;
            width: 100%;
            text-align: left;
            transition: all 0.15s ease-in-out;
        }}
        {nav_css}

        .lcs-sidebar-footer {{
            margin-top: 26px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.10);
            font-size: 11px;
            color: #7C8DBF !important;
            text-align: center;
            line-height: 1.5;
        }}

        /* ---------- TOP HEADER ---------- */
        .lcs-header {{
            background: linear-gradient(90deg, var(--navy) 0%, var(--purple-dark) 55%, var(--cyan) 100%);
            padding: 22px 32px;
            border-radius: 16px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 24px rgba(24,43,73,0.18);
            position: relative;
            overflow: hidden;
        }}
        .lcs-header::after {{
            content: "";
            position: absolute; inset: 0;
            background: radial-gradient(circle at 90% -20%, rgba(255,255,255,0.18), transparent 60%);
        }}
        .lcs-header-title {{
            font-family: 'Poppins', sans-serif;
            color: var(--soft-white);
            font-size: 30px;
            font-weight: 800;
            margin: 0;
            letter-spacing: 0.3px;
        }}
        .lcs-header-subtitle {{
            color: #E4D9F7;
            font-size: 13.5px;
            margin: 4px 0 0 0;
            font-weight: 500;
        }}
        .lcs-header-chip {{
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.35);
            color: #fff;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}

        /* ---------- HERO (Dashboard only) ---------- */
        .lcs-hero {{
            background: linear-gradient(120deg, var(--purple) 0%, var(--rose-dark) 50%, var(--amber) 100%);
            border-radius: 20px;
            padding: 34px 36px;
            margin-bottom: 24px;
            box-shadow: 0 14px 34px rgba(108,99,255,0.28);
            position: relative;
            overflow: hidden;
        }}
        .lcs-hero::before {{
            content: "";
            position: absolute; inset: 0;
            background: radial-gradient(circle at 85% 120%, rgba(255,255,255,0.25), transparent 55%);
        }}
        .lcs-hero-app-name {{
            font-family: 'Poppins', sans-serif;
            font-size: 44px;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            letter-spacing: 0.2px;
            text-shadow: 0 4px 18px rgba(0,0,0,0.15);
        }}
        .lcs-hero-tagline {{
            color: rgba(255,255,255,0.92);
            font-size: 15px;
            font-weight: 500;
            margin-top: 6px;
        }}
        .lcs-hero-welcome {{
            color: rgba(255,255,255,0.85);
            font-size: 13.5px;
            margin-top: 16px;
            font-weight: 600;
        }}

        /* ---------- PAGE HEADER BANNER ---------- */
        .lcs-page-banner {{
            border-radius: 14px;
            padding: 16px 22px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .lcs-page-banner-icon {{
            font-size: 26px;
            width: 46px; height: 46px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            background: rgba(255,255,255,0.55);
            flex-shrink: 0;
        }}
        .lcs-page-banner-title {{
            font-family: 'Poppins', sans-serif;
            font-size: 21px;
            font-weight: 700;
            margin: 0;
        }}
        .lcs-page-banner-subtitle {{
            font-size: 12.5px;
            margin: 2px 0 0 0;
            opacity: 0.85;
        }}

        /* ---------- METRICS ---------- */
        div[data-testid="stMetric"] {{
            background: linear-gradient(160deg, var(--soft-white) 0%, var(--cool-lavender) 100%);
            border: 1px solid rgba(108,99,255,0.15);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 4px 14px rgba(24, 43, 73, 0.07);
            transition: transform 0.15s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
        }}
        div[data-testid="stMetric"] label {{
            color: var(--navy) !important;
            font-weight: 600 !important;
        }}

        /* ---------- BUTTONS ---------- */
        .stButton > button {{
            background: linear-gradient(90deg, var(--purple) 0%, var(--purple-dark) 100%);
            color: var(--soft-white);
            border: none;
            border-radius: 9px;
            font-weight: 600;
            padding: 9px 18px;
            width: 100%;
            text-align: center;
            transition: all 0.15s ease;
            box-shadow: 0 3px 10px rgba(108,99,255,0.25);
        }}
        .stButton > button:hover {{
            background: linear-gradient(90deg, var(--teal) 0%, var(--cyan) 100%);
            color: var(--soft-white);
            transform: translateY(-1px);
            box-shadow: 0 5px 14px rgba(25,181,165,0.3);
        }}

        /* ---------- CARDS / BADGES ---------- */
        .lcs-card {{
            background-color: var(--soft-white);
            border: 1px solid var(--cool-lavender);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 3px 14px rgba(24, 43, 73, 0.06);
            margin-bottom: 16px;
            transition: box-shadow 0.15s ease;
        }}
        .lcs-card:hover {{
            box-shadow: 0 6px 20px rgba(24, 43, 73, 0.10);
        }}

        .lcs-nba-card {{
            background: linear-gradient(135deg, var(--blush-pink) 0%, var(--soft-pink) 60%, var(--pink-purple) 100%);
            border: 1px solid var(--rose);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 16px;
        }}

        .lcs-badge {{
            display: inline-block;
            background-color: var(--blush-pink);
            color: var(--rose-dark);
            border: 1px solid var(--rose);
            border-radius: 20px;
            padding: 4px 13px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }}
        .lcs-badge-purple {{
            display: inline-block;
            background-color: var(--cool-lavender);
            color: var(--purple-dark);
            border: 1px solid var(--pink-purple);
            border-radius: 20px;
            padding: 4px 13px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }}
        .lcs-badge-teal {{
            display: inline-block;
            background-color: var(--very-light-pink);
            color: var(--teal);
            border: 1px solid var(--teal);
            border-radius: 20px;
            padding: 4px 13px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }}
        .lcs-badge-amber {{
            display: inline-block;
            background-color: #FDF3E3;
            color: var(--amber);
            border: 1px solid var(--amber);
            border-radius: 20px;
            padding: 4px 13px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }}
        .lcs-badge-cyan {{
            display: inline-block;
            background-color: #E6F7FD;
            color: var(--cyan);
            border: 1px solid var(--cyan);
            border-radius: 20px;
            padding: 4px 13px;
            font-size: 12px;
            font-weight: 700;
            margin: 3px;
        }}

        .lcs-empty-state {{
            color: #6b7280;
            font-size: 14px;
            padding: 10px 0;
        }}

        div[data-testid="stTabs"] button {{
            font-weight: 600;
            color: var(--navy);
        }}

        /* ---------- LIVE CHAT PANEL ---------- */
        div[class*="st-key-chat_panel"], div[class*="st-key-chat_panel_page"] {{
            background: linear-gradient(165deg, var(--navy) 0%, var(--purple-dark) 55%, var(--cyan-dark, #1C8FBF) 100%);
            border-radius: 20px;
            padding: 16px 14px 10px 14px;
            box-shadow: 0 10px 28px rgba(24,43,73,0.28);
        }}
        .lcs-chat-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 6px 12px 6px;
            border-bottom: 1px solid rgba(255,255,255,0.15);
            margin-bottom: 8px;
        }}
        .lcs-chat-title {{
            color: #fff;
            font-weight: 700;
            font-size: 14.5px;
            margin: 0;
        }}
        .lcs-chat-status {{
            display: flex; align-items: center; gap: 6px;
            font-size: 11px;
            color: #B9F6D6;
            font-weight: 600;
        }}
        .lcs-dot {{
            width: 8px; height: 8px; border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 0 3px rgba(31,174,107,0.25);
            display: inline-block;
        }}
        div[class*="st-key-chat_panel"] [data-testid="stChatMessage"], div[class*="st-key-chat_panel_page"] [data-testid="stChatMessage"] {{
            background: rgba(255,255,255,0.92);
            border-radius: 12px;
        }}

        /* ---------- FOOTER ---------- */
        .lcs-footer {{
            margin-top: 34px;
            padding: 18px 10px 10px 10px;
            border-top: 1px solid rgba(24,43,73,0.10);
            text-align: center;
            color: #7A7F94;
            font-size: 12.5px;
        }}
        .lcs-footer b {{
            color: var(--navy);
        }}

        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def render_top_header():
    st.markdown(f"""
    <div class="lcs-header">
        <div>
            <p class="lcs-header-title"> Learning &amp; Career Studio</p>
            <p class="lcs-header-subtitle">Intelligent Student Learning &amp; Career Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero_banner():
    """Big, prominent app-name hero — shown only on the Dashboard (first page)."""
    profile = st.session_state.profile
    display_name = profile.get("name") or "Student"
    st.markdown(f"""
    <div class="lcs-hero">
        <p class="lcs-hero-app-name"> Learning &amp; Career Studio</p>
        <p class="lcs-hero-tagline">One intelligent platform for your learning journey and career growth.</p>
        <p class="lcs-hero-welcome"> Welcome back, {display_name} , here's where you stand today.</p>
    </div>
    """, unsafe_allow_html=True)


def render_page_banner(page_name):
    meta = PAGE_META.get(page_name, {"icon": "📄", "subtitle": "", "group": "MAIN"})
    color = GROUP_COLORS.get(meta["group"], COLORS["purple"])
    st.markdown(f"""
    <div class="lcs-page-banner" style="background: linear-gradient(90deg, {color}22 0%, {color}08 100%); border: 1px solid {color}44;">
        <div class="lcs-page-banner-icon" style="color:{color};">{meta['icon']}</div>
        <div>
            <p class="lcs-page-banner-title" style="color:{color};">{page_name}</p>
            <p class="lcs-page-banner-subtitle" style="color:{COLORS['navy']};">{meta['subtitle']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown(f"""
    <div class="lcs-footer">
        © {datetime.now().year} <b>Learning &amp; Career Studio (LCS)</b>. All rights reserved.<br>
        From classroom to career, study smarter, prepare sharper, succeed faster..
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# GROQ CLIENT SETUP
# ============================================================
GROQ_MODEL = "openai/gpt-oss-120b"

@st.cache_resource
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None

def call_groq(messages, temperature=0.4, max_tokens=1024):
    client = get_groq_client()
    if client is None:
        return "AI service is currently unavailable. Please configure the Groq API key in this environment."
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception:
        return "The AI service could not process this request right now. Please try again in a moment."

def call_groq_json(messages, temperature=0.3, max_tokens=1200):
    """
    Calls Groq and attempts to parse a JSON object from the response.
    Returns (parsed_dict_or_None, raw_text).
    """
    raw = call_groq(messages, temperature=temperature, max_tokens=max_tokens)
    cleaned = raw.strip()
    cleaned = re.sub(r"^```json", "", cleaned)
    cleaned = re.sub(r"^```", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned), raw
    except Exception:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0)), raw
            except Exception:
                return None, raw
        return None, raw

# ============================================================
# SESSION STATE / DATA MODEL
# ============================================================
def init_session_state():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "", "education_level": "", "institution": "", "program": "",
            "class_semester": "", "subjects": [], "skills": [], "interests": [],
            "certifications": [], "projects": [], "experience": "", "achievements": [],
            "career_goal": "", "preferred_industries": [], "preferred_work_type": "", "gpa": None,
        }

    if "study_data" not in st.session_state:
        st.session_state.study_data = {
            "topics": {},
            "quiz_history": [],
            "weak_topics": [],
            "roadmap": [],
            "notes": {},
            "planner": [],
        }

    if "career_data" not in st.session_state:
        st.session_state.career_data = {
            "matches": [], "skill_gaps": [], "roadmap": [], "projects": [], "certifications": [],
        }

    if "prep_data" not in st.session_state:
        st.session_state.prep_data = {
            "cv_analysis": None, "job_matches": [], "interview_history": [],
            "interview_active_question": None, "readiness_score": 0, "internships": [],
        }

    if "agent_context" not in st.session_state:
        st.session_state.agent_context = {"history": [], "language": "English"}

    if "rag_context" not in st.session_state:
        st.session_state.rag_context = {"documents": [], "chunks": []}

    if "study_workspace" not in st.session_state:
        st.session_state.study_workspace = {"subject": "", "topic": "", "content": None}


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="lcs-brand">
            <div class="lcs-brand-badge"></div>
            <div>
                <p class="lcs-brand-title">LCS</p>
                <p class="lcs-brand-sub">Learning &amp; Career Studio</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        for group_name, items in NAV_STRUCTURE.items():
            if group_name != "MAIN":
                st.markdown(f'<p class="lcs-section-label">{group_name}</p>', unsafe_allow_html=True)
            for item in items:
                is_active = st.session_state.current_page == item
                icon = PAGE_META.get(item, {}).get("icon", "•")
                if st.button(f"{icon}  {item}", key=f"nav_{item}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.current_page = item
                    st.rerun()

        st.markdown(f"""
        <div class="lcs-sidebar-footer">
            💬 Live Agent is on every page →<br>
            © {datetime.now().year} LCS. All rights reserved.
        </div>
        """, unsafe_allow_html=True)

def go_to_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# ============================================================
# UTILITIES
# ============================================================
def parse_csv_field(text_value):
    if not text_value:
        return []
    return [item.strip() for item in text_value.split(",") if item.strip()]

def list_to_csv(value_list):
    return ", ".join(value_list) if value_list else ""

def upsert_topic(subject, topic, status=None):
    """Add or update a topic entry in study_data.topics."""
    topics = st.session_state.study_data["topics"]
    if topic not in topics:
        topics[topic] = {
            "subject": subject,
            "status": status or "Learning",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    else:
        topics[topic]["subject"] = subject
        if status:
            topics[topic]["status"] = status
        topics[topic]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# ============================================================
# LOCAL DETERMINISTIC ANALYTICS (no LLM calls)
# ============================================================
STATUS_WEIGHTS = {
    "Not Started": 0, "Learning": 25, "Practicing": 50, "Needs Revision": 60, "Strong": 100,
}
STATUS_OPTIONS = list(STATUS_WEIGHTS.keys())

def compute_learning_progress():
    topics = st.session_state.study_data["topics"]
    if not topics:
        return 0
    values = [STATUS_WEIGHTS.get(t.get("status", "Not Started"), 0) for t in topics.values()]
    return round(sum(values) / len(values))

def compute_skill_strength():
    skills = st.session_state.profile.get("skills", [])
    if not skills:
        return 0
    return min(100, len(skills) * 12)

def compute_career_match_avg():
    matches = st.session_state.career_data.get("matches", [])
    if not matches:
        return 0
    return round(sum(m["match_pct"] for m in matches) / len(matches))

def compute_career_readiness():
    parts = [
        compute_learning_progress(),
        compute_skill_strength(),
        70 if st.session_state.prep_data.get("cv_analysis") else 0,
        70 if st.session_state.prep_data.get("interview_history") else 0,
    ]
    return round(sum(parts) / len(parts)) if parts else 0

def get_next_best_action():
    profile = st.session_state.profile
    weak = st.session_state.study_data.get("weak_topics", [])

    if not profile.get("name"):
        return {"title": "Complete Your Profile",
                "reason": "Setting up your profile lets LCS generate personalized study and career recommendations for you.",
                "action_label": "Complete Profile", "action_page": "My Profile"}
    if not profile.get("subjects"):
        return {"title": "Add Your Subjects",
                "reason": "Adding your current subjects helps LCS build a personalized study roadmap.",
                "action_label": "Add Subjects", "action_page": "Subjects"}
    if weak:
        topic = weak[0]
        return {"title": f"Strengthen {topic}",
                "reason": f"Your recent quiz performance shows that {topic}-related questions need more practice.",
                "action_label": "Practice Now", "action_page": "Quizzes"}
    if not st.session_state.career_data.get("matches"):
        return {"title": "Explore Career Matches",
                "reason": "Discover careers that align with your current skills, subjects, and interests.",
                "action_label": "Discover Careers", "action_page": "Discover"}
    return {"title": "Continue Your Learning Journey",
            "reason": "Keep building skills and projects to move closer to your career goal.",
            "action_label": "Go to Study", "action_page": "Study"}

def get_ranked_actions():
    """Returns a small ranked list of next-best actions (beyond just the single top one)."""
    profile = st.session_state.profile
    actions = []
    if not profile.get("name"):
        actions.append({"title": "Complete Your Profile", "reason": "Unlocks personalization across LCS.",
                         "action_label": "Complete Profile", "action_page": "My Profile", "icon": "🧑‍🎓"})
    if not profile.get("subjects"):
        actions.append({"title": "Add Your Subjects", "reason": "Powers your Study Workspace and Roadmap.",
                         "action_label": "Add Subjects", "action_page": "Subjects", "icon": "📚"})
    weak = st.session_state.study_data.get("weak_topics", [])
    if weak:
        actions.append({"title": f"Strengthen {weak[0]}", "reason": "Recent quiz results show this needs practice.",
                         "action_label": "Practice Now", "action_page": "Quizzes", "icon": "❓"})
    if not st.session_state.career_data.get("matches"):
        actions.append({"title": "Explore Career Matches", "reason": "See careers aligned with your profile.",
                         "action_label": "Discover Careers", "action_page": "Discover", "icon": "🧭"})
    if not st.session_state.prep_data.get("cv_analysis"):
        actions.append({"title": "Analyze Your CV", "reason": "Get instant AI feedback to improve it.",
                         "action_label": "Analyze CV", "action_page": "CV Analyzer", "icon": "📄"})
    if not st.session_state.prep_data.get("interview_history"):
        actions.append({"title": "Practice a Mock Interview", "reason": "Build confidence before real interviews.",
                         "action_label": "Start Interview", "action_page": "Interview", "icon": "🎤"})
    if not actions:
        actions.append({"title": "Keep Building Your Portfolio", "reason": "Add a new project or certification this week.",
                         "action_label": "Go to Projects", "action_page": "Projects", "icon": "💼"})
    return actions[:4]

# ============================================================
# LIVE AI AGENT (chat, shown on every page)
# ============================================================
def build_agent_system_prompt():
    profile = st.session_state.profile
    page = st.session_state.current_page
    context_bits = [
        f"Student name: {profile.get('name') or 'Not set'}",
        f"Education level: {profile.get('education_level') or 'Not set'}",
        f"Subjects: {list_to_csv(profile.get('subjects', [])) or 'None'}",
        f"Skills: {list_to_csv(profile.get('skills', [])) or 'None'}",
        f"Career goal: {profile.get('career_goal') or 'Not set'}",
        f"Currently viewing page: {page}",
    ]
    return (
        "You are the LCS Agent, a friendly, encouraging live assistant embedded inside the "
        "Learning & Career Studio platform. You help students with study questions, career "
        "guidance, and navigating the app. Keep answers concise (2-5 sentences unless asked for "
        "detail), practical, and supportive. Here is what you know about the current student:\n"
        + "\n".join(context_bits)
    )

def agent_reply(user_text):
    history = st.session_state.agent_context["history"]
    messages = [{"role": "system", "content": build_agent_system_prompt()}]
    for m in history[-8:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_text})
    return call_groq(messages, temperature=0.5, max_tokens=450)

def render_chat_panel(key_prefix="global", message_height=380):
    history = st.session_state.agent_context["history"]

    st.markdown("""
    <div class="lcs-chat-header">
        <p class="lcs-chat-title">💬 LCS Live Agent</p>
        <div class="lcs-chat-status"><span class="lcs-dot"></span>Online</div>
    </div>
    """, unsafe_allow_html=True)

    msg_box = st.container(height=message_height)
    with msg_box:
        if not history:
            st.chat_message("assistant").write(
                "Hi! I'm your LCS Agent! Ask me about a topic, your career path, or how to use this app."
            )
        for m in history:
            st.chat_message(m["role"]).write(m["content"])

    prompt = st.chat_input("Type a message...", key=f"chat_input_{key_prefix}")
    if prompt:
        history.append({"role": "user", "content": prompt})
        with st.spinner("LCS Agent is typing..."):
            reply = agent_reply(prompt)
        history.append({"role": "assistant", "content": reply})
        st.rerun()

    if history and st.button("🗑️ Clear Chat", key=f"clear_chat_{key_prefix}", use_container_width=True):
        st.session_state.agent_context["history"] = []
        st.rerun()

# ============================================================
# DASHBOARD PAGE
# ============================================================
def render_dashboard():
    render_hero_banner()

    learning_progress = compute_learning_progress()
    skill_strength = compute_skill_strength()
    career_match = compute_career_match_avg()
    career_readiness = compute_career_readiness()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Learning Progress", f"{learning_progress}%")
    k2.metric("Skill Strength", f"{skill_strength}%")
    k3.metric("Career Match", f"{career_match}%")
    k4.metric("Career Readiness", f"{career_readiness}%")

    st.write("")

    nba = get_next_best_action()
    st.markdown(f"""
    <div class="lcs-nba-card">
        <p class="lcs-section-label" style="color:{COLORS['navy']} !important;">NEXT BEST ACTION</p>
        <h3 style="margin-top:4px;">{nba['title']}</h3>
        <p style="color:{COLORS['navy']};">{nba['reason']}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(nba["action_label"], key="nba_action_button"):
        go_to_page(nba["action_page"])

    st.write("")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Study Progress")
        topics = st.session_state.study_data["topics"]
        if topics:
            status_counts = {}
            for t in topics.values():
                status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1
            fig = go.Figure(data=[go.Bar(
                x=list(status_counts.keys()), y=list(status_counts.values()), marker_color=COLORS["purple"]
            )])
            fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p class="lcs-empty-state">No study topics yet. Add subjects to start your roadmap.</p>', unsafe_allow_html=True)

        st.markdown("#### Weak Topics")
        weak = st.session_state.study_data.get("weak_topics", [])
        if weak:
            st.markdown("".join([f'<span class="lcs-badge">{w}</span>' for w in weak]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="lcs-empty-state">No weak topics detected yet. Complete a quiz to see results here.</p>', unsafe_allow_html=True)

        st.markdown("####  Recent Quiz Performance")
        quiz_history = st.session_state.study_data.get("quiz_history", [])
        if quiz_history:
            df = pd.DataFrame(quiz_history[-5:])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="lcs-empty-state">No quizzes attempted yet.</p>', unsafe_allow_html=True)

    with col_right:
        st.markdown("####  Career Matches")
        matches = st.session_state.career_data.get("matches", [])
        if matches:
            sorted_matches = sorted(matches, key=lambda m: m["match_pct"], reverse=True)[:5]
            fig = go.Figure(data=[go.Bar(
                x=[m["match_pct"] for m in sorted_matches], y=[m["career"] for m in sorted_matches],
                orientation="h", marker_color=COLORS["teal"]
            )])
            fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p class="lcs-empty-state">No career matches yet. Visit Discover to explore careers.</p>', unsafe_allow_html=True)

        st.markdown("####  Skill Gaps")
        gaps = st.session_state.career_data.get("skill_gaps", [])
        if gaps:
            for g in gaps[:3]:
                st.markdown(f"**{g['career']}**")
                st.markdown("".join([f'<span class="lcs-badge-purple">{s}</span>' for s in g["missing_skills"]]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="lcs-empty-state">No skill gap analysis yet.</p>', unsafe_allow_html=True)

        st.markdown("####  Study Roadmap")
        roadmap = st.session_state.study_data.get("roadmap", [])
        if roadmap:
            df = pd.DataFrame(roadmap)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="lcs-empty-state">Your personalized study roadmap will appear here.</p>', unsafe_allow_html=True)

        st.markdown("####  Career Roadmap")
        career_roadmap = st.session_state.career_data.get("roadmap", [])
        if career_roadmap:
            df = pd.DataFrame(career_roadmap)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="lcs-empty-state">Your career roadmap will appear here.</p>', unsafe_allow_html=True)

    st.markdown("####  Upcoming Goals")
    planner = st.session_state.study_data.get("planner", [])
    pending = [p for p in planner if p.get("status") != "Done"]
    if pending:
        df = pd.DataFrame(pending[:5])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">Set up your Study Planner to see upcoming goals here.</p>', unsafe_allow_html=True)

# ============================================================
# MY PROFILE PAGE
# ============================================================
EDUCATION_LEVELS = ["School", "College / Intermediate", "University"]
WORK_TYPES = ["Not Specified", "Remote", "Onsite", "Hybrid", "Internship", "Full-time", "Part-time", "Freelance"]

def render_profile_page():
    profile = st.session_state.profile

    with st.form("profile_form", clear_on_submit=False):
        st.markdown("#### Basic Information")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value=profile.get("name", ""))
            institution = st.text_input("School / College / University Name", value=profile.get("institution", ""))
            program = st.text_input("Degree / Program (if applicable)", value=profile.get("program", ""))
        with c2:
            education_level = st.selectbox(
                "Education Level", options=EDUCATION_LEVELS,
                index=EDUCATION_LEVELS.index(profile["education_level"]) if profile.get("education_level") in EDUCATION_LEVELS else 0
            )
            class_semester = st.text_input("Class / Grade / Semester", value=profile.get("class_semester", ""))
            gpa = st.text_input("GPA (optional)", value=str(profile.get("gpa")) if profile.get("gpa") else "")

        st.markdown("#### Academics & Skills")
        c3, c4 = st.columns(2)
        with c3:
            subjects = st.text_area("Subjects (comma-separated)", value=list_to_csv(profile.get("subjects", [])), height=80)
            skills = st.text_area("Skills (comma-separated)", value=list_to_csv(profile.get("skills", [])), height=80)
        with c4:
            interests = st.text_area("Interests (comma-separated)", value=list_to_csv(profile.get("interests", [])), height=80)
            certifications = st.text_area("Certifications (comma-separated)", value=list_to_csv(profile.get("certifications", [])), height=80)

        st.markdown("#### Experience & Achievements")
        c5, c6 = st.columns(2)
        with c5:
            projects = st.text_area("Projects (comma-separated)", value=list_to_csv(profile.get("projects", [])), height=80)
            experience = st.text_area("Experience (brief description)", value=profile.get("experience", ""), height=80)
        with c6:
            achievements = st.text_area("Achievements (comma-separated)", value=list_to_csv(profile.get("achievements", [])), height=80)

        st.markdown("#### Career Direction")
        c7, c8 = st.columns(2)
        with c7:
            career_goal = st.text_input("Career Goal", value=profile.get("career_goal", ""))
            preferred_industries = st.text_area("Preferred Industries (comma-separated)", value=list_to_csv(profile.get("preferred_industries", [])), height=80)
        with c8:
            preferred_work_type = st.selectbox(
                "Preferred Work Type", options=WORK_TYPES,
                index=WORK_TYPES.index(profile["preferred_work_type"]) if profile.get("preferred_work_type") in WORK_TYPES else 0
            )

        submitted = st.form_submit_button("💾 Save Profile")

        if submitted:
            st.session_state.profile = {
                "name": name.strip(), "education_level": education_level, "institution": institution.strip(),
                "program": program.strip(), "class_semester": class_semester.strip(),
                "subjects": parse_csv_field(subjects), "skills": parse_csv_field(skills),
                "interests": parse_csv_field(interests), "certifications": parse_csv_field(certifications),
                "projects": parse_csv_field(projects), "experience": experience.strip(),
                "achievements": parse_csv_field(achievements), "career_goal": career_goal.strip(),
                "preferred_industries": parse_csv_field(preferred_industries),
                "preferred_work_type": preferred_work_type, "gpa": gpa.strip() if gpa.strip() else None,
            }
            st.success("Profile saved successfully.")
            st.rerun()

    st.write("")
    render_profile_summary()

def render_profile_summary():
    profile = st.session_state.profile
    if not profile.get("name"):
        st.markdown('<p class="lcs-empty-state">No profile saved yet. Fill in the form above to get started.</p>', unsafe_allow_html=True)
        return

    st.markdown("#### Profile Summary")
    st.markdown(f"""
    <div class="lcs-card">
        <b>{profile['name']}</b><br>
        <span style="color:#6b7280;">{profile.get('education_level','')} — {profile.get('institution','')}</span><br>
        <span style="color:#6b7280;">{profile.get('program','')} {(' · ' + profile.get('class_semester','')) if profile.get('class_semester') else ''}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Subjects**")
        if profile.get("subjects"):
            st.markdown("".join([f'<span class="lcs-badge">{s}</span>' for s in profile["subjects"]]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="lcs-empty-state">Not added yet.</p>', unsafe_allow_html=True)

        st.markdown("**Skills**")
        if profile.get("skills"):
            st.markdown("".join([f'<span class="lcs-badge-purple">{s}</span>' for s in profile["skills"]]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="lcs-empty-state">Not added yet.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown("**Career Goal**")
        st.write(profile.get("career_goal") or "Not specified yet.")

        st.markdown("**Preferred Work Type**")
        st.write(profile.get("preferred_work_type") or "Not specified yet.")

# ============================================================
# STUDY WORKSPACE PAGE
# ============================================================
def build_topic_explanation_messages(subject, topic, education_level):
    system_prompt = (
        "You are an academic tutor inside an educational platform called Learning and Career Studio. "
        "Respond ONLY with a valid JSON object, no extra text, no markdown fences. "
        "The JSON must have exactly these keys: "
        '"explanation" (a clear, well-structured explanation string, 3 to 6 sentences), '
        '"key_concepts" (a list of 4 to 6 short strings), '
        '"examples" (a list of 2 to 4 short example strings). '
        "Keep the language appropriate for the given education level. Do not include emojis."
    )
    user_prompt = (
        f"Education Level: {education_level or 'Not specified'}\n"
        f"Subject: {subject}\n"
        f"Topic: {topic}\n\n"
        "Explain this topic clearly for a student studying it for the first time."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def render_study_page():
    profile = st.session_state.profile
    workspace = st.session_state.study_workspace

    profile_subjects = profile.get("subjects", [])

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if profile_subjects:
            subject_options = profile_subjects + ["Other (type below)"]
            selected_subject = st.selectbox("Subject", options=subject_options, key="study_subject_select")
            if selected_subject == "Other (type below)":
                subject = st.text_input("Enter Subject Name", key="study_subject_custom")
            else:
                subject = selected_subject
        else:
            subject = st.text_input("Subject", key="study_subject_custom_only", placeholder="e.g. Database Systems")

    with c2:
        topic = st.text_input("Topic", key="study_topic_input", placeholder="e.g. SQL JOIN Operations")

    with c3:
        education_level = st.selectbox(
            "Education Level", options=EDUCATION_LEVELS,
            index=EDUCATION_LEVELS.index(profile["education_level"]) if profile.get("education_level") in EDUCATION_LEVELS else 0,
            key="study_education_level"
        )

    generate_clicked = st.button("✨ Generate Explanation", key="generate_explanation_btn")

    if generate_clicked:
        if not subject or not topic:
            st.error("Please provide both a subject and a topic before generating an explanation.")
        else:
            with st.spinner("Preparing your explanation..."):
                messages = build_topic_explanation_messages(subject, topic, education_level)
                parsed, raw = call_groq_json(messages)
                if parsed:
                    workspace["content"] = parsed
                else:
                    workspace["content"] = {"explanation": raw, "key_concepts": [], "examples": []}
                workspace["subject"] = subject
                workspace["topic"] = topic
                upsert_topic(subject, topic, status="Learning")
            st.rerun()

    st.write("")

    if workspace.get("content"):
        content = workspace["content"]
        st.markdown(f'<span class="lcs-badge-teal">{workspace["subject"]} · {workspace["topic"]}</span>', unsafe_allow_html=True)
        st.write("")

        tab1, tab2, tab3 = st.tabs(["Explanation", "Key Concepts", "Examples"])
        with tab1:
            st.markdown(f'<div class="lcs-card">{content.get("explanation", "No explanation available.")}</div>', unsafe_allow_html=True)
        with tab2:
            concepts = content.get("key_concepts", [])
            if concepts:
                st.markdown("".join([f'<span class="lcs-badge-purple">{c}</span>' for c in concepts]), unsafe_allow_html=True)
            else:
                st.markdown('<p class="lcs-empty-state">No key concepts available.</p>', unsafe_allow_html=True)
        with tab3:
            examples = content.get("examples", [])
            if examples:
                for i, ex in enumerate(examples, 1):
                    st.markdown(f'<div class="lcs-card">{i}. {ex}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="lcs-empty-state">No examples available.</p>', unsafe_allow_html=True)

        st.write("")
        st.markdown("#### Update Topic Status")
        current_status = st.session_state.study_data["topics"].get(workspace["topic"], {}).get("status", "Learning")
        c_status, c_save = st.columns([2, 1])
        with c_status:
            new_status = st.selectbox(
                "Topic Status", options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 1,
                key="study_status_select"
            )
        with c_save:
            st.write("")
            st.write("")
            if st.button("Save Status", key="save_status_btn"):
                upsert_topic(workspace["subject"], workspace["topic"], status=new_status)
                st.success("Topic status updated.")
                st.rerun()
    else:
        st.markdown('<p class="lcs-empty-state">Select a subject and topic above, then click Generate Explanation to begin.</p>', unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Your Tracked Topics")
    topics = st.session_state.study_data["topics"]
    if topics:
        rows = [{"Topic": k, "Subject": v["subject"], "Status": v["status"], "Last Updated": v["last_updated"]} for k, v in topics.items()]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">No topics tracked yet.</p>', unsafe_allow_html=True)

# ============================================================
# SUBJECTS PAGE
# ============================================================
def render_subjects_page():
    profile = st.session_state.profile
    topics = st.session_state.study_data["topics"]

    with st.form("add_subject_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            new_subject = st.text_input("New Subject Name", placeholder="e.g. Data Structures", key="new_subject_input")
        with c2:
            st.write("")
            st.write("")
            add_clicked = st.form_submit_button("➕ Add Subject")

        if add_clicked:
            if not new_subject.strip():
                st.error("Please enter a subject name before adding.")
            elif new_subject.strip() in profile["subjects"]:
                st.warning("This subject has already been added.")
            else:
                profile["subjects"].append(new_subject.strip())
                st.success(f"Added subject: {new_subject.strip()}")
                st.rerun()

    st.write("")
    st.markdown("#### Your Subjects")

    if not profile.get("subjects"):
        st.markdown('<p class="lcs-empty-state">No subjects added yet. Use the form above to add your first subject.</p>', unsafe_allow_html=True)
        return

    for subject in list(profile["subjects"]):
        subject_topics = [t for t, v in topics.items() if v["subject"] == subject]
        strong_count = len([t for t in subject_topics if topics[t]["status"] == "Strong"])

        card_col, action_col = st.columns([5, 1])
        with card_col:
            st.markdown(f"""
            <div class="lcs-card">
                <b>{subject}</b><br>
                <span style="color:#6b7280; font-size:13px;">
                    {len(subject_topics)} topic(s) tracked · {strong_count} marked Strong
                </span>
            </div>
            """, unsafe_allow_html=True)
        with action_col:
            st.write("")
            if st.button("Remove", key=f"remove_subject_{subject}"):
                profile["subjects"].remove(subject)
                st.success(f"Removed subject: {subject}")
                st.rerun()

# ============================================================
# ROADMAP PAGE
# ============================================================
def render_roadmap_page():
    st.markdown("#### Auto-Generated From Your Topics")
    topics = st.session_state.study_data["topics"]
    if topics:
        rows = sorted(
            [{"Topic": k, "Subject": v["subject"], "Status": v["status"]} for k, v in topics.items()],
            key=lambda r: STATUS_WEIGHTS.get(r["Status"], 0)
        )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">Add subjects and study topics to auto-populate your roadmap.</p>', unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Add a Milestone")
    with st.form("add_roadmap_milestone", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            milestone = st.text_input("Milestone", placeholder="e.g. Finish Data Structures basics")
        with c2:
            target_date = st.date_input("Target Date", value=datetime.now() + timedelta(days=14))
        with c3:
            status = st.selectbox("Status", options=["Planned", "In Progress", "Done"])
        submitted = st.form_submit_button("➕ Add Milestone")
        if submitted:
            if not milestone.strip():
                st.error("Please enter a milestone description.")
            else:
                st.session_state.study_data["roadmap"].append({
                    "Milestone": milestone.strip(),
                    "Target Date": target_date.strftime("%Y-%m-%d"),
                    "Status": status,
                })
                st.success("Milestone added to your roadmap.")
                st.rerun()

    st.write("")
    st.markdown("#### Your Roadmap")
    roadmap = st.session_state.study_data.get("roadmap", [])
    if roadmap:
        st.dataframe(pd.DataFrame(roadmap), use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">No milestones added yet.</p>', unsafe_allow_html=True)

# ============================================================
# PLANNER PAGE
# ============================================================
def render_planner_page():
    with st.form("add_planner_task", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            task = st.text_input("Task", placeholder="e.g. Revise Chapter 4 for Physics")
        with c2:
            due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=3))
        with c3:
            priority = st.selectbox("Priority", options=["Low", "Medium", "High"], index=1)
        submitted = st.form_submit_button("➕ Add Task")
        if submitted:
            if not task.strip():
                st.error("Please enter a task description.")
            else:
                st.session_state.study_data["planner"].append({
                    "Task": task.strip(),
                    "Due Date": due_date.strftime("%Y-%m-%d"),
                    "Priority": priority,
                    "status": "Pending",
                })
                st.success("Task added to your planner.")
                st.rerun()

    st.write("")
    st.markdown("#### Your Tasks")
    planner = st.session_state.study_data.get("planner", [])
    if not planner:
        st.markdown('<p class="lcs-empty-state">No tasks yet. Add your first study task above.</p>', unsafe_allow_html=True)
        return

    for i, t in enumerate(planner):
        c1, c2, c3 = st.columns([4, 1, 1])
        badge_class = "lcs-badge-teal" if t["status"] == "Done" else "lcs-badge-amber"
        with c1:
            st.markdown(f"""
            <div class="lcs-card">
                <b>{t['Task']}</b><br>
                <span style="color:#6b7280; font-size:13px;">Due {t['Due Date']} · Priority: {t['Priority']}</span>
                <span class="{badge_class}">{t['status']}</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            if t["status"] != "Done" and st.button("Mark Done", key=f"planner_done_{i}"):
                st.session_state.study_data["planner"][i]["status"] = "Done"
                st.rerun()
        with c3:
            if st.button("Remove", key=f"planner_remove_{i}"):
                st.session_state.study_data["planner"].pop(i)
                st.rerun()

# ============================================================
# NOTES PAGE
# ============================================================
def render_notes_page():
    profile = st.session_state.profile
    notes = st.session_state.study_data["notes"]

    with st.form("add_note_form", clear_on_submit=True):
        c1, c2 = st.columns([1, 1])
        with c1:
            subject = st.selectbox("Subject", options=(profile.get("subjects") or ["General"]))
        with c2:
            title = st.text_input("Note Title", placeholder="e.g. Normalization Rules")
        body = st.text_area("Note Content", height=120, placeholder="Write your notes here...")
        submitted = st.form_submit_button("💾 Save Note")
        if submitted:
            if not title.strip() or not body.strip():
                st.error("Please provide both a title and note content.")
            else:
                notes.setdefault(subject, []).append({
                    "title": title.strip(), "body": body.strip(),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.success("Note saved.")
                st.rerun()

    st.write("")
    st.markdown("#### Your Notes")
    if not notes:
        st.markdown('<p class="lcs-empty-state">No notes yet. Add your first note above.</p>', unsafe_allow_html=True)
        return

    for subject, note_list in notes.items():
        st.markdown(f"**{subject}**")
        for i, n in enumerate(note_list):
            with st.expander(f"{n['title']} — {n['date']}"):
                st.write(n["body"])
                if st.button("Delete Note", key=f"del_note_{subject}_{i}"):
                    notes[subject].pop(i)
                    st.rerun()

# ============================================================
# QUIZZES PAGE
# ============================================================
def build_quiz_messages(subject, topic, difficulty):
    system_prompt = (
        "You are a quiz generator for an educational platform. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"questions": [{"question": str, "options": [str,str,str,str], '
        '"correct_index": int (0-3), "explanation": str}]}. Generate exactly 5 questions. '
        "Do not include emojis."
    )
    user_prompt = f"Subject: {subject}\nTopic: {topic}\nDifficulty: {difficulty}\nGenerate the quiz now."
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_quizzes_page():
    profile = st.session_state.profile

    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        subject = st.selectbox("Subject", options=(profile.get("subjects") or ["General"]), key="quiz_subject")
    with c2:
        topic = st.text_input("Topic", placeholder="e.g. Binary Trees", key="quiz_topic")
    with c3:
        difficulty = st.selectbox("Difficulty", options=["Easy", "Medium", "Hard"], key="quiz_difficulty")

    if st.button(" Generate Quiz", key="gen_quiz_btn"):
        if not topic:
            st.error("Please enter a topic.")
        else:
            with st.spinner("Building your quiz..."):
                messages = build_quiz_messages(subject, topic, difficulty)
                parsed, raw = call_groq_json(messages)
            if parsed and parsed.get("questions"):
                st.session_state.current_quiz = {"subject": subject, "topic": topic, "questions": parsed["questions"], "answers": {}}
            else:
                st.error("Could not generate a quiz right now. Please try again.")
            st.rerun()

    quiz = st.session_state.current_quiz
    if quiz:
        st.write("")
        st.markdown(f'<span class="lcs-badge-teal">{quiz["subject"]} · {quiz["topic"]}</span>', unsafe_allow_html=True)
        with st.form("quiz_form"):
            for i, q in enumerate(quiz["questions"]):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                choice = st.radio("Select an answer", options=list(range(len(q["options"]))),
                                   format_func=lambda idx, opts=q["options"]: opts[idx],
                                   key=f"quiz_q_{i}", label_visibility="collapsed")
                quiz["answers"][i] = choice
                st.write("")
            submit_quiz = st.form_submit_button("✅ Submit Quiz")

        if submit_quiz:
            total = len(quiz["questions"])
            correct = sum(1 for i, q in enumerate(quiz["questions"]) if quiz["answers"].get(i) == q["correct_index"])
            score_pct = round((correct / total) * 100) if total else 0
            st.session_state.study_data["quiz_history"].append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Subject": quiz["subject"], "Topic": quiz["topic"],
                "Score": f"{correct}/{total}", "Score %": score_pct,
            })
            if score_pct < 60:
                weak = st.session_state.study_data["weak_topics"]
                if quiz["topic"] not in weak:
                    weak.append(quiz["topic"])
            upsert_topic(quiz["subject"], quiz["topic"], status="Needs Revision" if score_pct < 60 else "Strong")

            st.success(f"You scored {correct}/{total} ({score_pct}%).")
            for i, q in enumerate(quiz["questions"]):
                is_correct = quiz["answers"].get(i) == q["correct_index"]
                icon = "✅" if is_correct else "❌"
                st.markdown(f"""
                <div class="lcs-card">
                    {icon} <b>Q{i+1}. {q['question']}</b><br>
                    <span style="color:#6b7280;">Correct answer: {q['options'][q['correct_index']]}</span><br>
                    <span style="color:#6b7280; font-size:13px;">{q.get('explanation','')}</span>
                </div>
                """, unsafe_allow_html=True)
            st.session_state.current_quiz = None

    st.write("")
    st.markdown("#### Quiz History")
    quiz_history = st.session_state.study_data.get("quiz_history", [])
    if quiz_history:
        st.dataframe(pd.DataFrame(quiz_history), use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">No quizzes attempted yet.</p>', unsafe_allow_html=True)

# ============================================================
# MOCK EXAMS PAGE
# ============================================================
def build_mock_exam_messages(subjects, education_level):
    system_prompt = (
        "You are a mock-exam generator for an educational platform. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"questions": [{"question": str, "options": [str,str,str,str], '
        '"correct_index": int (0-3), "subject": str}]}. Generate exactly 8 questions spread across '
        "the given subjects, appropriate to the education level. Do not include emojis."
    )
    user_prompt = f"Subjects: {list_to_csv(subjects)}\nEducation Level: {education_level}\nGenerate the mock exam now."
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_mock_exams_page():
    profile = st.session_state.profile
    subjects = profile.get("subjects", [])

    st.info(" Suggested time: 20 minutes · 8 questions across your subjects.")
    if "current_mock_exam" not in st.session_state:
        st.session_state.current_mock_exam = None

    if not subjects:
        st.markdown('<p class="lcs-empty-state">Add subjects in the Subjects page first to generate a mock exam.</p>', unsafe_allow_html=True)
        return

    if st.button("🧪 Generate Mock Exam", key="gen_mock_exam_btn"):
        with st.spinner("Assembling your mock exam..."):
            messages = build_mock_exam_messages(subjects, profile.get("education_level", ""))
            parsed, raw = call_groq_json(messages)
        if parsed and parsed.get("questions"):
            st.session_state.current_mock_exam = {"questions": parsed["questions"], "answers": {}}
        else:
            st.error("Could not generate a mock exam right now. Please try again.")
        st.rerun()

    exam = st.session_state.current_mock_exam
    if exam:
        with st.form("mock_exam_form"):
            for i, q in enumerate(exam["questions"]):
                st.markdown(f"**Q{i+1}. ({q.get('subject','General')}) {q['question']}**")
                choice = st.radio("Select an answer", options=list(range(len(q["options"]))),
                                   format_func=lambda idx, opts=q["options"]: opts[idx],
                                   key=f"mock_q_{i}", label_visibility="collapsed")
                exam["answers"][i] = choice
                st.write("")
            submit_exam = st.form_submit_button("✅ Submit Exam")

        if submit_exam:
            total = len(exam["questions"])
            correct = sum(1 for i, q in enumerate(exam["questions"]) if exam["answers"].get(i) == q["correct_index"])
            score_pct = round((correct / total) * 100) if total else 0
            st.session_state.study_data["quiz_history"].append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Subject": "Mock Exam", "Topic": "Multi-subject",
                "Score": f"{correct}/{total}", "Score %": score_pct,
            })
            st.success(f"Mock Exam complete — you scored {correct}/{total} ({score_pct}%).")
            st.session_state.current_mock_exam = None

# ============================================================
# PROGRESS PAGE
# ============================================================
def render_progress_page():
    quiz_history = st.session_state.study_data.get("quiz_history", [])
    topics = st.session_state.study_data.get("topics", {})

    k1, k2, k3 = st.columns(3)
    k1.metric("Topics Tracked", len(topics))
    k2.metric("Quizzes Taken", len(quiz_history))
    avg_score = round(sum(q.get("Score %", 0) for q in quiz_history) / len(quiz_history)) if quiz_history else 0
    k3.metric("Average Quiz Score", f"{avg_score}%")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Score Trend")
        if quiz_history:
            fig = go.Figure(data=[go.Scatter(
                x=[q["Date"] for q in quiz_history], y=[q.get("Score %", 0) for q in quiz_history],
                mode="lines+markers", line=dict(color=COLORS["purple"], width=3)
            )])
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p class="lcs-empty-state">Take a quiz to see your score trend.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Topic Status Breakdown")
        if topics:
            status_counts = {}
            for t in topics.values():
                status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1
            fig = go.Figure(data=[go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()),
                                          marker=dict(colors=[COLORS["purple"], COLORS["teal"], COLORS["rose"], COLORS["amber"], COLORS["cyan"]]))])
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p class="lcs-empty-state">Track topics to see your status breakdown.</p>', unsafe_allow_html=True)

# ============================================================
# DISCOVER (CAREER MATCHES) PAGE
# ============================================================
def build_career_discovery_messages(profile):
    system_prompt = (
        "You are a career guidance engine. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"careers": [{"career": str, "match_pct": int (0-100), "reason": str}]}. '
        "Suggest exactly 5 careers ranked by fit. Do not include emojis."
    )
    user_prompt = (
        f"Subjects: {list_to_csv(profile.get('subjects', []))}\n"
        f"Skills: {list_to_csv(profile.get('skills', []))}\n"
        f"Interests: {list_to_csv(profile.get('interests', []))}\n"
        f"Career Goal: {profile.get('career_goal') or 'Not specified'}\n"
        "Suggest careers that best match this student."
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_discover_page():
    profile = st.session_state.profile
    if not profile.get("skills") and not profile.get("subjects"):
        st.warning("Add some subjects, skills, or interests in My Profile for better career matches.")

    if st.button(" Find Career Matches", key="discover_btn"):
        with st.spinner("Analyzing your profile against career paths..."):
            messages = build_career_discovery_messages(profile)
            parsed, raw = call_groq_json(messages)
        if parsed and parsed.get("careers"):
            st.session_state.career_data["matches"] = [
                {"career": c["career"], "match_pct": c["match_pct"], "reason": c.get("reason", "")}
                for c in parsed["careers"]
            ]
            st.success("Career matches updated.")
        else:
            st.error("Could not generate career matches right now. Please try again.")
        st.rerun()

    st.write("")
    matches = st.session_state.career_data.get("matches", [])
    if matches:
        sorted_matches = sorted(matches, key=lambda m: m["match_pct"], reverse=True)
        for m in sorted_matches:
            st.markdown(f"""
            <div class="lcs-card">
                <b>{m['career']}</b>
                <span class="lcs-badge-teal">{m['match_pct']}% match</span><br>
                <span style="color:#6b7280; font-size:13px;">{m['reason']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="lcs-empty-state">Click "Find Career Matches" to discover careers suited to you.</p>', unsafe_allow_html=True)

# ============================================================
# SKILLS PAGE
# ============================================================
def render_skills_page():
    profile = st.session_state.profile

    with st.form("add_skill_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            new_skill = st.text_input("New Skill", placeholder="e.g. Python Programming")
        with c2:
            st.write("")
            st.write("")
            add_clicked = st.form_submit_button("➕ Add Skill")
        if add_clicked:
            if not new_skill.strip():
                st.error("Please enter a skill name.")
            elif new_skill.strip() in profile["skills"]:
                st.warning("This skill has already been added.")
            else:
                profile["skills"].append(new_skill.strip())
                st.success(f"Added skill: {new_skill.strip()}")
                st.rerun()

    st.write("")
    st.markdown(f"#### Skill Strength: {compute_skill_strength()}%")
    if profile.get("skills"):
        for skill in list(profile["skills"]):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f'<div class="lcs-card">🛠️ {skill}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("Remove", key=f"remove_skill_{skill}"):
                    profile["skills"].remove(skill)
                    st.rerun()
    else:
        st.markdown('<p class="lcs-empty-state">No skills added yet. Use the form above.</p>', unsafe_allow_html=True)

# ============================================================
# SKILL GAP PAGE
# ============================================================
def build_skill_gap_messages(career, profile):
    system_prompt = (
        "You are a career skills advisor. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"missing_skills": [str], "recommendations": [str]}. '
        "List 4-6 missing skills and 3-4 recommendations. Do not include emojis."
    )
    user_prompt = (
        f"Target career: {career}\n"
        f"Current skills: {list_to_csv(profile.get('skills', []))}\n"
        "Identify the skill gap for this student to become competitive for this career."
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_skill_gap_page():
    profile = st.session_state.profile
    matches = st.session_state.career_data.get("matches", [])
    career_options = [m["career"] for m in matches] + ["Other (type below)"]

    c1, c2 = st.columns([2, 1])
    with c1:
        if matches:
            selected = st.selectbox("Target Career", options=career_options)
            career = st.text_input("Enter Career Name", key="skillgap_custom") if selected == "Other (type below)" else selected
        else:
            career = st.text_input("Target Career", placeholder="e.g. Data Analyst")
    with c2:
        st.write("")
        st.write("")
        analyze_clicked = st.button("🔍 Analyze Skill Gap")

    if analyze_clicked:
        if not career:
            st.error("Please provide a target career.")
        else:
            with st.spinner("Analyzing your skill gap..."):
                messages = build_skill_gap_messages(career, profile)
                parsed, raw = call_groq_json(messages)
            if parsed:
                existing = [g for g in st.session_state.career_data["skill_gaps"] if g["career"] != career]
                existing.append({"career": career, "missing_skills": parsed.get("missing_skills", []),
                                  "recommendations": parsed.get("recommendations", [])})
                st.session_state.career_data["skill_gaps"] = existing
                st.success("Skill gap analysis complete.")
            else:
                st.error("Could not analyze skill gap right now.")
            st.rerun()

    st.write("")
    gaps = st.session_state.career_data.get("skill_gaps", [])
    if gaps:
        for g in gaps:
            st.markdown(f"**{g['career']}**")
            st.markdown("Missing skills:")
            st.markdown("".join([f'<span class="lcs-badge-purple">{s}</span>' for s in g["missing_skills"]]), unsafe_allow_html=True)
            if g.get("recommendations"):
                st.markdown("Recommendations:")
                for r in g["recommendations"]:
                    st.markdown(f"- {r}")
            st.write("")
    else:
        st.markdown('<p class="lcs-empty-state">Analyze a career above to see your skill gap.</p>', unsafe_allow_html=True)

# ============================================================
# CAREER ROADMAP PAGE
# ============================================================
def build_career_roadmap_messages(profile, gaps):
    system_prompt = (
        "You are a career roadmap planner. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"steps": [{"Step": str, "Timeframe": str, "Description": str}]}. '
        "Generate exactly 5 sequential steps. Do not include emojis."
    )
    missing = []
    for g in gaps:
        missing.extend(g.get("missing_skills", []))
    user_prompt = (
        f"Career Goal: {profile.get('career_goal') or 'Not specified'}\n"
        f"Current Skills: {list_to_csv(profile.get('skills', []))}\n"
        f"Missing Skills: {list_to_csv(missing)}\n"
        "Build a step-by-step roadmap toward this career goal."
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_career_roadmap_page():
    profile = st.session_state.profile
    gaps = st.session_state.career_data.get("skill_gaps", [])

    if not profile.get("career_goal"):
        st.warning("Set a Career Goal in My Profile for a more accurate roadmap.")

    if st.button(" Generate Career Roadmap"):
        with st.spinner("Building your career roadmap..."):
            messages = build_career_roadmap_messages(profile, gaps)
            parsed, raw = call_groq_json(messages)
        if parsed and parsed.get("steps"):
            st.session_state.career_data["roadmap"] = parsed["steps"]
            st.success("Career roadmap generated.")
        else:
            st.error("Could not generate a roadmap right now.")
        st.rerun()

    st.write("")
    roadmap = st.session_state.career_data.get("roadmap", [])
    if roadmap:
        st.dataframe(pd.DataFrame(roadmap), use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">Click "Generate Career Roadmap" above to build your path.</p>', unsafe_allow_html=True)

# ============================================================
# PROJECTS PAGE
# ============================================================
def render_projects_page():
    with st.form("add_project_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            name = st.text_input("Project Name", placeholder="e.g. Student Result Management System")
        with c2:
            status = st.selectbox("Status", options=["Planned", "In Progress", "Completed"])
        description = st.text_area("Description", height=80)
        skills_used = st.text_input("Skills Used (comma-separated)")
        submitted = st.form_submit_button("➕ Add Project")
        if submitted:
            if not name.strip():
                st.error("Please enter a project name.")
            else:
                st.session_state.career_data["projects"].append({
                    "name": name.strip(), "status": status, "description": description.strip(),
                    "skills": parse_csv_field(skills_used),
                })
                st.success("Project added.")
                st.rerun()

    st.write("")
    st.markdown("#### Your Portfolio Projects")
    projects = st.session_state.career_data.get("projects", [])
    if not projects:
        st.markdown('<p class="lcs-empty-state">No projects tracked yet. Add your first one above.</p>', unsafe_allow_html=True)
        return

    for i, p in enumerate(projects):
        c1, c2 = st.columns([5, 1])
        with c1:
            skills_html = "".join([f'<span class="lcs-badge-purple">{s}</span>' for s in p.get("skills", [])])
            st.markdown(f"""
            <div class="lcs-card">
                <b>{p['name']}</b> <span class="lcs-badge-teal">{p['status']}</span><br>
                <span style="color:#6b7280; font-size:13px;">{p.get('description','')}</span><br>
                {skills_html}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            if st.button("Remove", key=f"remove_project_{i}"):
                st.session_state.career_data["projects"].pop(i)
                st.rerun()

# ============================================================
# CERTIFICATIONS PAGE
# ============================================================
def render_certifications_page():
    with st.form("add_cert_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            name = st.text_input("Certification Name", placeholder="e.g. Google Data Analytics")
        with c2:
            provider = st.text_input("Provider", placeholder="e.g. Coursera")
        with c3:
            status = st.selectbox("Status", options=["Planned", "In Progress", "Earned"])
        submitted = st.form_submit_button("➕ Add Certification")
        if submitted:
            if not name.strip():
                st.error("Please enter a certification name.")
            else:
                st.session_state.career_data["certifications"].append({
                    "name": name.strip(), "provider": provider.strip(), "status": status,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                st.success("Certification added.")
                st.rerun()

    st.write("")
    certs = st.session_state.career_data.get("certifications", [])
    if certs:
        st.dataframe(pd.DataFrame(certs), use_container_width=True, hide_index=True)
    else:
        st.markdown('<p class="lcs-empty-state">No certifications tracked yet.</p>', unsafe_allow_html=True)

# ============================================================
# CV ANALYZER PAGE
# ============================================================
def build_cv_analysis_messages(cv_text):
    system_prompt = (
        "You are a CV/resume reviewer. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"score": int (0-100), "strengths": [str], "weaknesses": [str], "suggestions": [str]}. '
        "Do not include emojis."
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"CV Text:\n{cv_text}"}]

def render_cv_analyzer_page():
    cv_text = st.text_area("Paste your CV text here", height=220, placeholder="Paste the full text of your CV...")
    if st.button("📄 Analyze CV"):
        if not cv_text.strip():
            st.error("Please paste your CV text first.")
        else:
            with st.spinner("Analyzing your CV..."):
                messages = build_cv_analysis_messages(cv_text)
                parsed, raw = call_groq_json(messages)
            if parsed:
                st.session_state.prep_data["cv_analysis"] = parsed
                st.success("CV analysis complete.")
            else:
                st.error("Could not analyze your CV right now.")
            st.rerun()

    st.write("")
    analysis = st.session_state.prep_data.get("cv_analysis")
    if analysis:
        st.metric("CV Score", f"{analysis.get('score', 0)}/100")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ Strengths")
            for s in analysis.get("strengths", []):
                st.markdown(f"- {s}")
        with col2:
            st.markdown("#### ⚠️ Weaknesses")
            for w in analysis.get("weaknesses", []):
                st.markdown(f"- {w}")
        st.markdown("#### 💡 Suggestions")
        for s in analysis.get("suggestions", []):
            st.markdown(f"- {s}")
    else:
        st.markdown('<p class="lcs-empty-state">Paste your CV above and click Analyze CV.</p>', unsafe_allow_html=True)

# ============================================================
# JOB MATCHER PAGE
# ============================================================
def build_job_match_messages(job_description, profile):
    system_prompt = (
        "You are a job-fit analyzer. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"match_pct": int (0-100), "matching_skills": [str], "missing_skills": [str], "recommendation": str}. '
        "Do not include emojis."
    )
    user_prompt = (
        f"Candidate skills: {list_to_csv(profile.get('skills', []))}\n"
        f"Candidate subjects: {list_to_csv(profile.get('subjects', []))}\n"
        f"Job Description:\n{job_description}"
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_job_matcher_page():
    profile = st.session_state.profile
    job_title = st.text_input("Job Title", placeholder="e.g. Junior Data Analyst")
    job_description = st.text_area("Paste Job Description", height=180)

    if st.button("🎯 Match This Job"):
        if not job_description.strip():
            st.error("Please paste a job description first.")
        else:
            with st.spinner("Comparing job description to your profile..."):
                messages = build_job_match_messages(job_description, profile)
                parsed, raw = call_groq_json(messages)
            if parsed:
                st.session_state.prep_data["job_matches"].append({
                    "title": job_title or "Untitled Job", "match_pct": parsed.get("match_pct", 0),
                    "matching_skills": parsed.get("matching_skills", []),
                    "missing_skills": parsed.get("missing_skills", []),
                    "recommendation": parsed.get("recommendation", ""),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                st.success("Job match analysis complete.")
            else:
                st.error("Could not analyze this job right now.")
            st.rerun()

    st.write("")
    matches = st.session_state.prep_data.get("job_matches", [])
    if matches:
        for m in reversed(matches):
            st.markdown(f"""
            <div class="lcs-card">
                <b>{m['title']}</b> <span class="lcs-badge-teal">{m['match_pct']}% match</span><br>
                <span style="color:#6b7280; font-size:13px;">{m['recommendation']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="lcs-empty-state">Paste a job description above to see your match.</p>', unsafe_allow_html=True)

# ============================================================
# INTERNSHIPS PAGE
# ============================================================
def build_internship_messages(profile):
    system_prompt = (
        "You are an internship advisor. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"internships": [{"title": str, "field": str, "why_fit": str}]}. '
        "Suggest exactly 5 internship types. Do not include emojis."
    )
    user_prompt = (
        f"Subjects: {list_to_csv(profile.get('subjects', []))}\n"
        f"Skills: {list_to_csv(profile.get('skills', []))}\n"
        f"Career Goal: {profile.get('career_goal') or 'Not specified'}"
    )
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_internships_page():
    profile = st.session_state.profile
    if st.button("🏢 Suggest Internships"):
        with st.spinner("Finding internships suited to you..."):
            messages = build_internship_messages(profile)
            parsed, raw = call_groq_json(messages)
        if parsed and parsed.get("internships"):
            st.session_state.prep_data["internships"] = parsed["internships"]
            st.success("Internship suggestions ready.")
        else:
            st.error("Could not generate suggestions right now.")
        st.rerun()

    st.write("")
    internships = st.session_state.prep_data.get("internships", [])
    if internships:
        for i in internships:
            st.markdown(f"""
            <div class="lcs-card">
                <b>{i['title']}</b> <span class="lcs-badge-purple">{i.get('field','')}</span><br>
                <span style="color:#6b7280; font-size:13px;">{i.get('why_fit','')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="lcs-empty-state">Click "Suggest Internships" to get personalized options.</p>', unsafe_allow_html=True)

# ============================================================
# INTERVIEW PAGE
# ============================================================
def build_interview_question_messages(profile, history):
    system_prompt = (
        "You are conducting a mock interview. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"question": str}. Ask exactly one relevant interview question, '
        "considering the candidate's career goal and prior answers. Do not include emojis."
    )
    prior = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:]])
    user_prompt = f"Career Goal: {profile.get('career_goal') or 'General'}\nPrior Q&A:\n{prior or 'None yet'}"
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def build_interview_feedback_messages(question, answer):
    system_prompt = (
        "You are an interview coach. Respond ONLY with valid JSON, no extra text. "
        'JSON schema: {"feedback": str, "score": int (1-10)}. Give brief, constructive feedback. '
        "Do not include emojis."
    )
    user_prompt = f"Question: {question}\nCandidate Answer: {answer}"
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

def render_interview_page():
    profile = st.session_state.profile
    prep = st.session_state.prep_data

    if st.button("🎤 Start New Mock Interview"):
        with st.spinner("Preparing your first question..."):
            messages = build_interview_question_messages(profile, prep["interview_history"])
            parsed, raw = call_groq_json(messages)
        prep["interview_active_question"] = parsed.get("question") if parsed else raw
        st.rerun()

    active_q = prep.get("interview_active_question")
    if active_q:
        st.markdown(f'<div class="lcs-card"><b>Interviewer:</b> {active_q}</div>', unsafe_allow_html=True)
        answer = st.text_area("Your Answer", height=120, key="interview_answer_input")
        if st.button("Submit Answer"):
            if not answer.strip():
                st.error("Please type your answer first.")
            else:
                with st.spinner("Evaluating your answer..."):
                    fb_messages = build_interview_feedback_messages(active_q, answer)
                    fb_parsed, fb_raw = call_groq_json(fb_messages)
                feedback = fb_parsed.get("feedback") if fb_parsed else fb_raw
                score = fb_parsed.get("score", 0) if fb_parsed else 0
                prep["interview_history"].append({
                    "question": active_q, "answer": answer.strip(), "feedback": feedback, "score": score,
                })
                with st.spinner("Preparing your next question..."):
                    nq_messages = build_interview_question_messages(profile, prep["interview_history"])
                    nq_parsed, nq_raw = call_groq_json(nq_messages)
                prep["interview_active_question"] = nq_parsed.get("question") if nq_parsed else nq_raw
                st.rerun()
    else:
        st.markdown('<p class="lcs-empty-state">Click "Start New Mock Interview" to begin.</p>', unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Interview History")
    history = prep.get("interview_history", [])
    if history:
        for h in reversed(history):
            with st.expander(f"Q: {h['question'][:70]}..." if len(h['question']) > 70 else f"Q: {h['question']}"):
                st.write(f"**Your answer:** {h['answer']}")
                st.write(f"**Feedback:** {h['feedback']}")
                st.write(f"**Score:** {h['score']}/10")
    else:
        st.markdown('<p class="lcs-empty-state">No interview attempts yet.</p>', unsafe_allow_html=True)

# ============================================================
# READINESS PAGE
# ============================================================
def render_readiness_page():
    readiness = compute_career_readiness()

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness,
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": COLORS["purple"]},
               "steps": [
                   {"range": [0, 40], "color": "#FCEAF3"},
                   {"range": [40, 70], "color": "#F4F1FA"},
                   {"range": [70, 100], "color": "#E6F9F3"},
               ]},
        title={"text": "Career Readiness"}
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Learning Progress", f"{compute_learning_progress()}%")
    c2.metric("Skill Strength", f"{compute_skill_strength()}%")
    c3.metric("CV Analyzed", "Yes" if st.session_state.prep_data.get("cv_analysis") else "No")
    c4.metric("Interview Practiced", "Yes" if st.session_state.prep_data.get("interview_history") else "No")

    st.write("")
    st.markdown("#### Tips to Improve")
    tips = []
    if compute_learning_progress() < 60:
        tips.append("Keep marking study topics as 'Strong' by revising and taking quizzes.")
    if compute_skill_strength() < 60:
        tips.append("Add more skills to your profile as you learn them.")
    if not st.session_state.prep_data.get("cv_analysis"):
        tips.append("Run your CV through the CV Analyzer for instant feedback.")
    if not st.session_state.prep_data.get("interview_history"):
        tips.append("Practice at least one mock interview to build confidence.")
    if not tips:
        tips.append("You're in great shape — keep building projects and certifications!")
    for t in tips:
        st.markdown(f"- {t}")

# ============================================================
# NEXT ACTION PAGE
# ============================================================
def render_next_action_page():
    nba = get_next_best_action()
    st.markdown(f"""
    <div class="lcs-nba-card">
        <p class="lcs-section-label" style="color:{COLORS['navy']} !important;">TOP PRIORITY</p>
        <h3 style="margin-top:4px;">{nba['title']}</h3>
        <p style="color:{COLORS['navy']};">{nba['reason']}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(nba["action_label"], key="next_action_top_btn"):
        go_to_page(nba["action_page"])

    st.write("")
    st.markdown("#### More Suggested Actions")
    for i, action in enumerate(get_ranked_actions()):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"""
            <div class="lcs-card">
                <b>{action['icon']} {action['title']}</b><br>
                <span style="color:#6b7280; font-size:13px;">{action['reason']}</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            if st.button(action["action_label"], key=f"ranked_action_{i}"):
                go_to_page(action["action_page"])

# ============================================================
# LIVE AGENT PAGE (full page version)
# ============================================================
def render_live_agent_page():
    c1, c2 = st.columns([3, 1])
    with c2:
        lang = st.selectbox("Language", options=["English", "Urdu"],
                             index=["English", "Urdu"].index(st.session_state.agent_context.get("language", "English"))
                             if st.session_state.agent_context.get("language", "English") in ["English", "Urdu"] else 0)
        st.session_state.agent_context["language"] = lang
    with c1:
        st.caption("This is the same agent that follows you on every page via the right-side panel | expanded here for longer conversations.")

    with st.container(key="chat_panel_page"):
        render_chat_panel(key_prefix="full_page", message_height=480)

# ============================================================
# PAGE ROUTER
# ============================================================
PAGE_RENDERERS = {
    "Dashboard": render_dashboard,
    "My Profile": render_profile_page,
    "Study": render_study_page,
    "Roadmap": render_roadmap_page,
    "Planner": render_planner_page,
    "Subjects": render_subjects_page,
    "Notes": render_notes_page,
    "Quizzes": render_quizzes_page,
    "Mock Exams": render_mock_exams_page,
    "Progress": render_progress_page,
    "Discover": render_discover_page,
    "Skills": render_skills_page,
    "Skill Gap": render_skill_gap_page,
    "Career Roadmap": render_career_roadmap_page,
    "Projects": render_projects_page,
    "Certifications": render_certifications_page,
    "CV Analyzer": render_cv_analyzer_page,
    "Job Matcher": render_job_matcher_page,
    "Internships": render_internships_page,
    "Interview": render_interview_page,
    "Readiness": render_readiness_page,
    "Next Action": render_next_action_page,
    "Live Agent": render_live_agent_page,
}

def render_page(page_name):
    if page_name != "Dashboard":
        render_page_banner(page_name)
    renderer = PAGE_RENDERERS.get(page_name)
    if renderer:
        renderer()
    else:
        st.markdown(f'<span class="lcs-badge">{page_name}</span>', unsafe_allow_html=True)
        st.write("")
        st.markdown(
            f'<div class="lcs-card">The <b>{page_name}</b> module will be built in an upcoming development step.</div>',
            unsafe_allow_html=True
        )

# ============================================================
# MAIN APP
# ============================================================
def main():
    apply_theme()
    init_session_state()
    render_top_header()
    render_sidebar()

    client_status = get_groq_client()
    if client_status is None:
        st.warning("AI features are not yet active. Groq API key not detected in this session.")

    main_col, chat_col = st.columns([3, 1.05], gap="medium")

    with main_col:
        render_page(st.session_state.current_page)

    with chat_col:
        with st.container(key="chat_panel"):
            render_chat_panel(key_prefix="global", message_height=380)

    render_footer()

if __name__ == "__main__":
    main()
