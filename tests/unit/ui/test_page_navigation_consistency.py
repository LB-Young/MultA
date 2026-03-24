"""页面导航与样式一致性测试"""
from pathlib import Path


UPLOAD_PAGE = Path(__file__).resolve().parents[3] / "ui" / "pages" / "1_📤_上传.py"
CHUNKS_PAGE = Path(__file__).resolve().parents[3] / "ui" / "pages" / "2_📊_切片.py"
AGENT_PAGE = Path(__file__).resolve().parents[3] / "ui" / "pages" / "4_🤖_Agent.py"


def test_upload_page_keeps_custom_feature_nav_and_collapsed_config_panel():
    """上传页应使用自定义功能导航并保留折叠配置区。"""
    source = UPLOAD_PAGE.read_text(encoding="utf-8")

    assert "render_feature_nav(container=st)" in source
    assert "st.subheader(\"🧭 应用\")" not in source
    assert "with st.expander(\"⚙️ 配置\", expanded=False):" in source


def test_chunks_page_keeps_custom_feature_nav_and_collapsed_config_panel():
    """切片页应使用自定义功能导航并保留折叠配置区。"""
    source = CHUNKS_PAGE.read_text(encoding="utf-8")

    assert "render_feature_nav(container=st)" in source
    assert "st.subheader(\"🧭 应用\")" not in source
    assert "with st.expander(\"⚙️ 配置\", expanded=False):" in source


def test_agent_page_keeps_custom_feature_nav_and_collapsed_config_panel():
    """Agent 页应使用自定义功能导航并保留折叠配置区。"""
    source = AGENT_PAGE.read_text(encoding="utf-8")

    assert "render_feature_nav(container=st)" in source
    assert "st.subheader(\"🧭 应用\")" not in source
    assert "st.subheader(\"💬 会话\")" in source
    assert 'client.get("/agent/sessions")' in source
    assert 'client.post("/agent/sessions", params={"title": "新对话"})' in source
    assert "with st.expander(\"⚙️ 配置\", expanded=False):" in source
    assert "st.chat_input(" in source
    assert 'client.post("/agent/query", json=payload)' in source


def test_shared_feature_nav_order_is_qa_agent_upload_chunks():
    """功能导航顺序应为：知识问答 -> Agent -> 上传文件 -> 切片可视化。"""
    config_source = (
        Path(__file__).resolve().parents[3] / "ui" / "config_shared.py"
    ).read_text(encoding="utf-8")

    idx_qa = config_source.index('ui.page_link("pages/3_❓_问答.py", label="知识问答")')
    idx_agent = config_source.index('ui.page_link("pages/4_🤖_Agent.py", label="Agent")')
    idx_upload = config_source.index('ui.page_link("pages/1_📤_上传.py", label="上传文件")')
    idx_chunks = config_source.index('ui.page_link("pages/2_📊_切片.py", label="切片可视化")')
    assert idx_qa < idx_agent < idx_upload < idx_chunks
