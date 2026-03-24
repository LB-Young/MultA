"""问答页结构回归测试"""
from pathlib import Path


CHAT_PAGE = Path(__file__).resolve().parents[3] / "ui" / "pages" / "3_❓_问答.py"


def test_submitted_messages_use_in_stream_pending_request_flow():
    """提交后应先显示用户消息，再在同一消息流中渲染处理中间态。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert '"qa_pending_request" not in st.session_state' in source
    assert 'st.session_state["qa_pending_request"] = None' in source
    assert 'pending_request = st.session_state.get("qa_pending_request")' in source
    assert '"qa_pending_started" not in st.session_state' in source
    assert 'st.session_state["qa_pending_started"] = False' in source
    assert "processing_container = st.container()" not in source
    assert source.index('if pending_request and not st.session_state.get("qa_pending_started", False):') < source.index('st.markdown(\'<div id="qa-message-bottom-anchor"></div>\', unsafe_allow_html=True)')
    assert 'st.session_state["qa_messages"].append({"role": "user", "content": prompt})' in source
    assert 'st.session_state["qa_pending_request"] = {' in source
    assert 'if pending_request and not st.session_state.get("qa_pending_started", False):' in source
    assert 'st.session_state["qa_pending_started"] = True' in source
    assert 'if pending_request and st.session_state.get("qa_pending_started", False):' in source
    assert "st.rerun()" in source
    assert "if pending_request:\n    st.rerun()" not in source


def test_chat_page_injects_bottom_anchor_and_autoscroll_script():
    """消息区应包含底部锚点和自动滚底脚本。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert 'st.markdown(\'<div id="qa-message-bottom-anchor"></div>\', unsafe_allow_html=True)' in source
    assert 'st_html(' in source
    assert 'build_chat_autoscroll_script(' in source


def test_chat_page_has_compact_session_and_config_sections():
    """问答页侧栏应包含会话区和分层配置区，不重复应用导航。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "render_feature_nav(container=st)" in source
    assert "st.subheader(\"🧭 应用\")" not in source
    assert "st.subheader(\"💬 会话\")" in source
    assert "st.subheader(\"⚡ 快捷参数\")" not in source
    assert 'st.caption("检索参数")' in source
    assert 'top_k = st.slider("返回切片数", 1, 20, 5, key="qa_top_k")' in source
    assert 'use_rerank = st.checkbox(' not in source
    assert 'use_rerank = bool(st.session_state.get("reranker_enabled", DEFAULT_CONFIG.get("reranker_enabled", False)))' in source
    assert "with st.expander(\"⚙️ 高级配置\", expanded=False):" in source
    assert "render_sidebar(container=st, include_title=False)" in source


def test_chat_page_renders_history_session_list_instead_of_selectbox():
    """历史会话应使用列表式展示，不应继续使用 selectbox。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "st.selectbox(" not in source
    assert "for session in visible_sessions:" in source
    assert "st.button(" in source
    assert "qa_session_btn_" in source
    assert "_session_preview(" not in source
    assert "_session_button_label(" in source
    assert "进入会话" not in source
    assert "visible_sessions = sessions[:MAX_VISIBLE_SESSION_ITEMS]" in source
    assert 'with st.expander(f"更多会话 ({len(hidden_sessions)})", expanded=False):' in source


def test_chat_page_supports_session_search_and_pin_current_session():
    """会话区应支持搜索，并将当前会话置顶。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "session_search = st.text_input(" in source
    assert '"搜索会话",' in source
    assert "query in session.get(\"title\", \"\").lower()" in source
    assert "current_sessions = [s for s in sessions if s[\"id\"] == current_sid]" in source
    assert "sessions = current_sessions + other_sessions" in source


def test_chat_page_supports_renaming_current_session():
    """当前会话应提供重命名入口，并调用会话更新接口。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert "✏️ 重命名" in source
    assert "client.patch(" in source
    assert 'f"/rag/sessions/{sid}"' in source


def test_chat_page_places_rename_delete_under_new_session():
    """重命名/删除操作应在新建按钮下方并保持紧凑。"""
    source = CHAT_PAGE.read_text(encoding="utf-8")

    assert source.index('st.button("➕ 新建会话"') < source.index('st.button("✏️ 重命名"')
    assert source.index('st.button("✏️ 重命名"') < source.index('st.button("🗑 删除"')
