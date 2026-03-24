"""UI 共享配置"""
import streamlit as st
import httpx

# 默认配置（远程 Tailscale 服务）
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "llm_url": "http://100.117.128.23:8000",
    "llm_model": "qwen3-5-4b",
    "llm_type": "openai",
    "embedding_url": "http://100.117.128.23:8001",
    "embedding_model": "qwen3-embedding-0.6b",
    "embedding_type": "openai",
    "reranker_url": "http://100.117.128.23:8002",
    "reranker_enabled": False,
}


def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    if "config_loaded" not in st.session_state:
        try:
            response = httpx.get(f"{DEFAULT_CONFIG['api_url']}/config", timeout=5.0)
            if response.status_code == 200:
                backend_config = response.json()
                DEFAULT_CONFIG.update(backend_config)
                st.session_state.config_loaded = True
        except:
            pass


def render_feature_nav(container=None):
    """渲染功能导航（按业务优先顺序）。"""
    ui = container or st.sidebar
    ui.page_link("pages/3_❓_问答.py", label="知识问答")
    ui.page_link("pages/4_🤖_Agent.py", label="Agent")
    ui.page_link("pages/1_📤_上传.py", label="上传文件")
    ui.page_link("pages/2_📊_切片.py", label="切片可视化")


def render_sidebar(container=None, include_title: bool = True):
    """渲染配置面板（默认渲染到侧边栏）"""
    ui = container or st.sidebar

    if include_title:
        ui.title("⚙️ 配置")

    # ========== LLM 配置 ==========
    ui.subheader("🤖 LLM 配置")
    llm_type = ui.selectbox(
        "API 类型", ["openai", "local"],
        index=0 if DEFAULT_CONFIG.get("llm_type") == "openai" else 1,
        key="llm_type",
    )
    llm_url = ui.text_input(
        "LLM API 地址",
        value=DEFAULT_CONFIG.get("llm_url", "http://localhost:11434"),
        placeholder="http://localhost:11434",
        key="llm_url",
    )
    llm_model = ui.text_input(
        "LLM 模型",
        value=DEFAULT_CONFIG.get("llm_model", "qwen3:8b"),
        key="llm_model",
    )

    # ========== Embedding 配置 ==========
    ui.subheader("📊 Embedding 配置")
    embedding_type = ui.selectbox(
        "API 类型", ["openai", "local"],
        index=0 if DEFAULT_CONFIG.get("embedding_type") == "openai" else 1,
        key="embedding_type",
    )
    embedding_url = ui.text_input(
        "Embedding API 地址",
        value=DEFAULT_CONFIG.get("embedding_url", "http://localhost:11434"),
        placeholder="http://localhost:11434",
        key="embedding_url",
    )
    embedding_model = ui.text_input(
        "Embedding 模型",
        value=DEFAULT_CONFIG.get("embedding_model", "nomic-embed-text"),
        key="embedding_model",
    )

    # ========== Reranker 配置 ==========
    ui.subheader("🎯 Reranker 配置")
    reranker_enabled = ui.checkbox(
        "启用精排",
        value=DEFAULT_CONFIG.get("reranker_enabled", False),
        key="reranker_enabled",
    )
    reranker_url = ui.text_input(
        "Reranker API 地址",
        value=DEFAULT_CONFIG.get("reranker_url", "http://localhost:8002"),
        placeholder="http://localhost:8002",
        key="reranker_url",
    )

    # ========== 切片配置 ==========
    ui.subheader("📝 切片配置")
    chunk_size = ui.number_input(
        "块大小", min_value=100, max_value=5000, value=500, step=50, key="chunk_size",
    )
    overlap = ui.number_input(
        "重叠大小", min_value=0, max_value=1000, value=50, step=10, key="overlap",
    )
    strategy = ui.selectbox(
        "切片策略", ["fixed_chars", "fixed_tokens"], key="strategy",
    )

    # ========== 保存配置 ==========
    if ui.button("💾 保存配置", type="primary"):
        try:
            with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=30.0) as client:
                response = client.post(
                    "/config",
                    json={
                        "llm_url": llm_url,
                        "llm_model": llm_model,
                        "llm_type": llm_type,
                        "embedding_url": embedding_url,
                        "embedding_model": embedding_model,
                        "embedding_type": embedding_type,
                        "reranker_enabled": reranker_enabled,
                        "reranker_url": reranker_url,
                    },
                )
                if response.status_code == 200:
                    ui.success("✅ 配置已保存并同步到后端")
                else:
                    ui.error(f"保存失败: {response.status_code}")
        except Exception as e:
            ui.error(f"保存失败: {str(e)}")

    return {
        "llm_url": llm_url,
        "llm_model": llm_model,
        "llm_type": llm_type,
        "embedding_url": embedding_url,
        "embedding_model": embedding_model,
        "embedding_type": embedding_type,
        "reranker_enabled": reranker_enabled,
        "reranker_url": reranker_url,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "strategy": strategy,
    }
