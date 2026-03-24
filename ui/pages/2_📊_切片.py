"""切片可视化页面"""
import streamlit as st
import httpx

from ui.config_shared import (
    init_session_state,
    render_sidebar,
    render_feature_nav,
    DEFAULT_CONFIG,
)
from ui.components.chat_layout import build_minimal_page_css

st.set_page_config(page_title="切片可视化", page_icon="📊", layout="wide")

init_session_state()
st.title("📊 切片可视化")
st.markdown(build_minimal_page_css(), unsafe_allow_html=True)
with st.sidebar:
    render_feature_nav(container=st)
    st.divider()
    with st.expander("⚙️ 配置", expanded=False):
        render_sidebar(container=st, include_title=False)

try:
    with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=30.0) as client:
        response = client.get("/documents")

        if response.status_code == 200:
            data = response.json()
            docs = data["items"]

            if not docs:
                st.info("暂无文档，请先上传文件")
                st.stop()

            doc_options = {d["original_filename"]: d["id"] for d in docs}
            selected_doc = st.selectbox("选择文档", list(doc_options.keys()))

            if selected_doc:
                doc_id = doc_options[selected_doc]
                chunks_response = client.get(f"/chunks/{doc_id}")

                if chunks_response.status_code == 200:
                    chunks_data = chunks_response.json()
                    st.write(f"**切片总数:** {chunks_data['total']}")

                    for i, chunk in enumerate(chunks_data["chunks"]):
                        preview = chunk["content"][:500] + "..." if len(chunk["content"]) > 500 else chunk["content"]
                        with st.expander(f"切片 {i + 1} ({chunk['length']} 字符)"):
                            st.text_area(
                                "内容",
                                preview,
                                height=150,
                                key=f"chunk_{i}_{doc_id[:8]}",
                            )
                else:
                    st.warning("该文档尚未处理或无切片")
        else:
            st.warning("无法获取文档列表")

except Exception as e:
    st.error(f"无法连接到 API: {str(e)}")
