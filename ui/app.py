"""Streamlit 主应用入口（默认跳转到问答页）。"""
import sys
from pathlib import Path

# 把项目根目录加入 Python path，使 ui/ 可作为模块导入
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from ui.config_shared import init_session_state

st.set_page_config(
    page_title="企业知识库 RAG 系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
st.switch_page("pages/3_❓_问答.py")
