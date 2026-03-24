"""知识问答页面 — 多轮对话"""
import streamlit as st
import httpx
from streamlit.components.v1 import html as st_html

from ui.components.chat_layout import (
    build_bottom_docked_chat_css,
    build_chat_autoscroll_script,
    build_minimal_page_css,
    build_qa_sidebar_css,
)
from ui.config_shared import (
    init_session_state,
    render_sidebar,
    render_feature_nav,
    DEFAULT_CONFIG,
)

MAX_VISIBLE_SESSION_ITEMS = 5


def _session_title_one_line(session: dict, limit: int = 24) -> str:
    title = " ".join((session.get("title") or "新对话").split())
    if not title:
        title = "新对话"
    return title if len(title) <= limit else f"{title[:limit]}..."


def _load_session_messages(client: httpx.Client, session_id: str) -> bool:
    detail = client.get(f"/rag/sessions/{session_id}")
    if detail.status_code != 200:
        st.session_state["qa_messages"] = []
        return False

    payload = detail.json()
    st.session_state["qa_current_session"] = session_id
    st.session_state["qa_current_session_title"] = payload.get("title", "新对话")
    st.session_state["qa_messages"] = [
        {"role": m["role"], "content": m["content"]}
        for m in payload.get("messages", [])
    ]
    return True


def _create_session(client: httpx.Client) -> str | None:
    response = client.post("/rag/sessions", params={"title": "新对话"})
    if response.status_code != 200:
        return None
    data = response.json()
    sid = data["id"]
    st.session_state["qa_current_session"] = sid
    st.session_state["qa_current_session_title"] = data.get("title", "新对话")
    st.session_state["qa_messages"] = []
    return sid


def _render_message_content(msg: dict) -> None:
    if msg.get("is_error"):
        st.error(msg["content"])
    else:
        st.markdown(msg["content"])

    sources = msg.get("sources", [])
    if sources:
        with st.expander(f"📚 参考来源 ({len(sources)} 条)"):
            for i, src in enumerate(sources, 1):
                st.markdown(f"**{i}.** (相似度 `{src.get('score', 0):.3f}`)")
                st.text(src.get("content_preview", "")[:200])
                st.divider()

    retrieved_chunks = msg.get("retrieved_chunks")
    generation_time = msg.get("generation_time")
    if retrieved_chunks is not None and generation_time is not None:
        st.caption(
            f"检索 {retrieved_chunks} 个切片 · "
            f"生成耗时 {generation_time:.2f}s"
        )


def _session_button_label(session: dict, is_active: bool) -> str:
    prefix = "● " if is_active else ""
    return f"{prefix}{_session_title_one_line(session)}"


st.set_page_config(page_title="知识问答", page_icon="❓", layout="wide")

init_session_state()
st.title("❓ 知识问答")
st.markdown(build_minimal_page_css(), unsafe_allow_html=True)

# ── 初始化 ─────────────────────────────────────────
if "qa_messages" not in st.session_state:
    st.session_state["qa_messages"] = []
if "qa_current_session" not in st.session_state:
    st.session_state["qa_current_session"] = None
if "qa_current_session_title" not in st.session_state:
    st.session_state["qa_current_session_title"] = "新对话"
if "qa_pending_request" not in st.session_state:
    st.session_state["qa_pending_request"] = None
if "qa_pending_started" not in st.session_state:
    st.session_state["qa_pending_started"] = False
if "qa_scroll_nonce" not in st.session_state:
    st.session_state["qa_scroll_nonce"] = 0
if "qa_session_search" not in st.session_state:
    st.session_state["qa_session_search"] = ""
if "qa_rename_input" not in st.session_state:
    st.session_state["qa_rename_input"] = ""

st.markdown(build_qa_sidebar_css(), unsafe_allow_html=True)

# ── 左侧边栏：会话管理 + 分层配置 ──────────────────
with st.sidebar:
    render_feature_nav(container=st)
    st.divider()
    st.subheader("💬 会话")

    try:
        with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=10.0) as client:
            if st.button("➕ 新建会话", use_container_width=True, type="primary"):
                if _create_session(client):
                    st.rerun()

            sessions_response = client.get("/rag/sessions")
            sessions = sessions_response.json() if sessions_response.status_code == 200 else []

            if sessions:
                current_sid = st.session_state.get("qa_current_session")
                current_sessions = [s for s in sessions if s["id"] == current_sid]
                other_sessions = [s for s in sessions if s["id"] != current_sid]
                sessions = current_sessions + other_sessions

                current_title = current_sessions[0].get("title") if current_sessions else None
                if current_title:
                    st.session_state["qa_current_session_title"] = current_title

                if current_sid:
                    action_cols = st.columns([1, 1])
                    with action_cols[0]:
                        rename_clicked = st.button("✏️ 重命名", use_container_width=True)
                    with action_cols[1]:
                        delete_clicked = st.button("🗑 删除", use_container_width=True)

                    if rename_clicked:
                        st.session_state["qa_rename_input"] = st.session_state.get("qa_current_session_title", "新对话")

                    if delete_clicked:
                        sid = st.session_state["qa_current_session"]
                        client.delete(f"/rag/sessions/{sid}")
                        st.session_state["qa_current_session"] = None
                        st.session_state["qa_current_session_title"] = "新对话"
                        st.session_state["qa_messages"] = []
                        st.rerun()

                    if st.session_state.get("qa_rename_input"):
                        rename_cols = st.columns([3, 1])
                        with rename_cols[0]:
                            st.text_input(
                                "会话名称",
                                key="qa_rename_input",
                                label_visibility="collapsed",
                            )
                        with rename_cols[1]:
                            if st.button("保存", use_container_width=True):
                                sid = st.session_state["qa_current_session"]
                                new_title = st.session_state["qa_rename_input"].strip()
                                if new_title:
                                    update_resp = client.patch(
                                        f"/rag/sessions/{sid}",
                                        json={"title": new_title},
                                    )
                                    if update_resp.status_code == 200:
                                        st.session_state["qa_current_session_title"] = new_title
                                st.session_state["qa_rename_input"] = ""
                                st.rerun()

                session_search = st.text_input(
                    "搜索会话",
                    placeholder="按标题筛选",
                    key="qa_session_search",
                    label_visibility="collapsed",
                )
                query = session_search.strip().lower()
                if query:
                    sessions = [
                        session for session in sessions
                        if query in session.get("title", "").lower()
                    ]

                visible_sessions = sessions[:MAX_VISIBLE_SESSION_ITEMS]
                hidden_sessions = sessions[MAX_VISIBLE_SESSION_ITEMS:]

                for session in visible_sessions:
                    sid = session["id"]
                    is_active = sid == st.session_state.get("qa_current_session")
                    if st.button(
                        _session_button_label(session, is_active),
                        key=f"qa_session_btn_{sid}",
                        use_container_width=True,
                        disabled=is_active,
                    ):
                        if _load_session_messages(client, sid):
                            st.rerun()

                if hidden_sessions:
                    with st.expander(f"更多会话 ({len(hidden_sessions)})", expanded=False):
                        for session in hidden_sessions:
                            sid = session["id"]
                            is_active = sid == st.session_state.get("qa_current_session")
                            if st.button(
                                _session_button_label(session, is_active),
                                key=f"qa_session_btn_more_{sid}",
                                use_container_width=True,
                                disabled=is_active,
                            ):
                                if _load_session_messages(client, sid):
                                    st.rerun()
            else:
                st.caption("暂无会话记录，点击上方按钮开始。")
    except Exception:
        st.caption("会话服务暂不可用")

    st.divider()
    with st.expander("⚙️ 高级配置", expanded=False):
        st.caption("检索参数")
        top_k = st.slider("返回切片数", 1, 20, 5, key="qa_top_k")
        st.divider()
        render_sidebar(container=st, include_title=False)
        use_rerank = bool(st.session_state.get("reranker_enabled", DEFAULT_CONFIG.get("reranker_enabled", False)))

st.caption(f"当前会话：{st.session_state.get('qa_current_session_title', '新对话')}")

# ── 对话区域 ──────────────────────────────────────
st.markdown(build_bottom_docked_chat_css(), unsafe_allow_html=True)

messages_container = st.container()
pending_request = st.session_state.get("qa_pending_request")
with messages_container:
    st.markdown('<div id="qa-message-list-anchor"></div>', unsafe_allow_html=True)
    for msg in st.session_state["qa_messages"]:
        with st.chat_message(msg["role"]):
            _render_message_content(msg)

    if pending_request and not st.session_state.get("qa_pending_started", False):
        with st.chat_message("assistant"):
            st.caption("正在准备检索请求...")

    if pending_request and st.session_state.get("qa_pending_started", False):
        with st.chat_message("assistant"):
            pending_result_msg = None
            with st.spinner("正在检索和生成回答..."):
                try:
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state["qa_messages"][:-1]
                    ]
                    payload = {
                        "text": pending_request["text"],
                        "session_id": pending_request["session_id"],
                        "history": history,
                        "top_k": pending_request["top_k"],
                        "use_rerank": pending_request["use_rerank"],
                    }

                    with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=300.0) as client:
                        response = client.post("/rag/query", json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        active_sid = result.get("session_id") or pending_request["session_id"]
                        if active_sid:
                            st.session_state["qa_current_session"] = active_sid
                        answer_text = result["answer"]

                        pending_result_msg = {
                            "role": "assistant",
                            "content": answer_text,
                            "sources": result.get("sources", []),
                            "retrieved_chunks": result.get("retrieved_chunks"),
                            "generation_time": result.get("generation_time"),
                        }
                        st.session_state["qa_messages"].append(pending_result_msg)
                    else:
                        error = response.json()
                        pending_result_msg = {
                            "role": "assistant",
                            "content": f"查询失败: {error.get('detail', '未知错误')}",
                            "is_error": True,
                        }
                        st.session_state["qa_messages"].append(pending_result_msg)
                except Exception as e:
                    pending_result_msg = {
                        "role": "assistant",
                        "content": f"请求失败: {str(e)}",
                        "is_error": True,
                    }
                    st.session_state["qa_messages"].append(pending_result_msg)
                finally:
                    st.session_state["qa_pending_request"] = None
                    st.session_state["qa_pending_started"] = False
                    st.session_state["qa_scroll_nonce"] += 1
            if pending_result_msg:
                _render_message_content(pending_result_msg)

    st.markdown('<div id="qa-message-bottom-anchor"></div>', unsafe_allow_html=True)

st_html(build_chat_autoscroll_script(st.session_state["qa_scroll_nonce"]), height=0)

if pending_request and not st.session_state.get("qa_pending_started", False):
    st.session_state["qa_pending_started"] = True
    st.rerun()

input_container = st.container()
with input_container:
    st.markdown('<div id="qa-input-dock-anchor"></div>', unsafe_allow_html=True)
    with st.form("qa_input", clear_on_submit=True):
        cols = st.columns([6, 1])
        with cols[0]:
            prompt = st.text_input(
                "输入您的问题...",
                label_visibility="collapsed",
                key="qa_prompt_input",
                disabled=st.session_state.get("qa_pending_request") is not None,
            )
        with cols[1]:
            submitted = st.form_submit_button(
                "发送",
                use_container_width=True,
                disabled=st.session_state.get("qa_pending_request") is not None,
            )

if submitted and prompt:
    session_id = st.session_state.get("qa_current_session")
    if not session_id:
        try:
            with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=10.0) as client:
                session_id = _create_session(client)
        except Exception:
            session_id = None

    st.session_state["qa_messages"].append({"role": "user", "content": prompt})
    st.session_state["qa_pending_request"] = {
        "text": prompt,
        "session_id": session_id,
        "top_k": top_k,
        "use_rerank": use_rerank,
    }
    st.session_state["qa_pending_started"] = False
    st.session_state["qa_scroll_nonce"] += 1
    st.rerun()
