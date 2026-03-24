"""Agent 页面（模型直答）"""
import httpx
import streamlit as st

from ui.components.chat_layout import build_minimal_page_css
from ui.config_shared import (
    DEFAULT_CONFIG,
    init_session_state,
    render_feature_nav,
    render_sidebar,
)

st.set_page_config(page_title="Agent", page_icon="🤖", layout="wide")
init_session_state()
st.title("🤖 Agent")
st.caption("该模式直接调用模型回答，不走知识库检索。")
st.markdown(build_minimal_page_css(), unsafe_allow_html=True)

if "agent_messages" not in st.session_state:
    st.session_state["agent_messages"] = []
if "agent_current_session" not in st.session_state:
    st.session_state["agent_current_session"] = None
if "agent_current_session_title" not in st.session_state:
    st.session_state["agent_current_session_title"] = "新对话"
if "agent_session_search" not in st.session_state:
    st.session_state["agent_session_search"] = ""
if "agent_rename_input" not in st.session_state:
    st.session_state["agent_rename_input"] = ""


def _load_agent_session_messages(client: httpx.Client, session_id: str) -> bool:
    detail = client.get(f"/agent/sessions/{session_id}")
    if detail.status_code != 200:
        st.session_state["agent_messages"] = []
        return False
    payload = detail.json()
    st.session_state["agent_current_session"] = session_id
    st.session_state["agent_current_session_title"] = payload.get("title", "新对话")
    st.session_state["agent_messages"] = [
        {"role": m["role"], "content": m["content"]}
        for m in payload.get("messages", [])
    ]
    return True


def _create_agent_session(client: httpx.Client) -> str | None:
    response = client.post("/agent/sessions", params={"title": "新对话"})
    if response.status_code != 200:
        return None
    data = response.json()
    sid = data["id"]
    st.session_state["agent_current_session"] = sid
    st.session_state["agent_current_session_title"] = data.get("title", "新对话")
    st.session_state["agent_messages"] = []
    return sid

with st.sidebar:
    render_feature_nav(container=st)
    st.divider()
    st.subheader("💬 会话")
    try:
        with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=10.0) as client:
            if st.button("➕ 新建会话", use_container_width=True, type="primary"):
                if _create_agent_session(client):
                    st.rerun()

            sessions_response = client.get("/agent/sessions")
            sessions = sessions_response.json() if sessions_response.status_code == 200 else []
            if sessions:
                current_sid = st.session_state.get("agent_current_session")
                current_sessions = [s for s in sessions if s["id"] == current_sid]
                other_sessions = [s for s in sessions if s["id"] != current_sid]
                sessions = current_sessions + other_sessions

                if current_sid:
                    action_cols = st.columns([1, 1])
                    with action_cols[0]:
                        rename_clicked = st.button("✏️ 重命名", use_container_width=True, key="agent_rename_btn")
                    with action_cols[1]:
                        delete_clicked = st.button("🗑 删除", use_container_width=True, key="agent_delete_btn")
                    if rename_clicked:
                        st.session_state["agent_rename_input"] = st.session_state.get("agent_current_session_title", "新对话")
                    if delete_clicked:
                        sid = st.session_state["agent_current_session"]
                        client.delete(f"/agent/sessions/{sid}")
                        st.session_state["agent_current_session"] = None
                        st.session_state["agent_current_session_title"] = "新对话"
                        st.session_state["agent_messages"] = []
                        st.rerun()

                    if st.session_state.get("agent_rename_input"):
                        rename_cols = st.columns([3, 1])
                        with rename_cols[0]:
                            st.text_input(
                                "会话名称",
                                key="agent_rename_input",
                                label_visibility="collapsed",
                            )
                        with rename_cols[1]:
                            if st.button("保存", use_container_width=True, key="agent_rename_save_btn"):
                                sid = st.session_state["agent_current_session"]
                                new_title = st.session_state["agent_rename_input"].strip()
                                if new_title:
                                    update_resp = client.patch(
                                        f"/agent/sessions/{sid}",
                                        json={"title": new_title},
                                    )
                                    if update_resp.status_code == 200:
                                        st.session_state["agent_current_session_title"] = new_title
                                st.session_state["agent_rename_input"] = ""
                                st.rerun()

                session_search = st.text_input(
                    "搜索会话",
                    placeholder="按标题筛选",
                    key="agent_session_search",
                    label_visibility="collapsed",
                )
                query = session_search.strip().lower()
                if query:
                    sessions = [
                        session for session in sessions
                        if query in session.get("title", "").lower()
                    ]

                for session in sessions[:5]:
                    sid = session["id"]
                    is_active = sid == st.session_state.get("agent_current_session")
                    label = f"{'● ' if is_active else ''}{session.get('title', '新对话')}"
                    if st.button(label, key=f"agent_session_btn_{sid}", use_container_width=True, disabled=is_active):
                        if _load_agent_session_messages(client, sid):
                            st.rerun()
            else:
                st.caption("暂无会话记录，点击上方按钮开始。")
    except Exception:
        st.caption("会话服务暂不可用")

    st.divider()
    with st.expander("⚙️ 配置", expanded=False):
        render_sidebar(container=st, include_title=False)

st.caption(f"当前会话：{st.session_state.get('agent_current_session_title', '新对话')}")

for msg in st.session_state["agent_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("输入你的问题（Agent 直答）...")
if prompt:
    session_id = st.session_state.get("agent_current_session")
    if not session_id:
        try:
            with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=10.0) as client:
                session_id = _create_agent_session(client)
        except Exception:
            session_id = None

    st.session_state["agent_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["agent_messages"][:-1]
                ]
                payload = {
                    "text": prompt,
                    "session_id": session_id,
                    "history": history,
                }
                with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=300.0) as client:
                    response = client.post("/agent/query", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    sid = data.get("session_id") or session_id
                    if sid:
                        st.session_state["agent_current_session"] = sid
                    answer = data.get("answer", "")
                    st.markdown(answer)
                    st.caption(f"生成耗时 {data.get('generation_time', 0):.2f}s")
                    st.session_state["agent_messages"].append({"role": "assistant", "content": answer})
                else:
                    detail = response.json().get("detail", "未知错误")
                    st.error(f"请求失败: {detail}")
                    st.session_state["agent_messages"].append({"role": "assistant", "content": f"请求失败: {detail}"})
            except Exception as e:
                st.error(f"请求失败: {e}")
                st.session_state["agent_messages"].append({"role": "assistant", "content": f"请求失败: {e}"})
