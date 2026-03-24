"""文件上传页面"""
import streamlit as st
import httpx
import time

from ui.config_shared import (
    init_session_state,
    render_sidebar,
    render_feature_nav,
    DEFAULT_CONFIG,
)
from ui.components.chat_layout import build_minimal_page_css

SUPPORTED_TYPES = ["txt", "md", "json", "docx", "pdf", "xlsx", "pptx"]


# ══════════════════════════════════════════════════════════
def _show_results(results: dict):
    """展示上传结果汇总"""
    ok = len(results["success"])
    fail = len(results["failed"])
    if ok:
        st.success(f"✅ 成功 {ok} 个" + (f"，失败 {fail} 个" if fail else ""))
        with st.expander(f"📋 成功详情 ({ok} 个)"):
            for r in results["success"]:
                chunks = r.get("chunk_count", "-")
                st.markdown(f"- `{r.get('path', r.get('name'))}` — {chunks} 切片")
    if fail:
        st.error(f"❌ 以下 {fail} 个文件处理失败:")
        for r in results["failed"]:
            path = r.get("path", r.get("name", ""))
            st.markdown(f"- **{path}**: {r.get('error', '')}")


def _render_file_upload(config: dict):
    """单个/多个文件上传"""
    uploaded_files = st.file_uploader(
        "选择文件（支持多选）",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        help=f"支持格式: {', '.join(SUPPORTED_TYPES)}",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if uploaded_files:
            total_size = sum(f.size for f in uploaded_files)
            st.info(f"**待上传 {len(uploaded_files)} 个文件**\n共 {total_size / 1024:.1f} KB")
    with col2:
        start = st.button("🚀 上传并处理全部", type="primary", disabled=not uploaded_files)

    if start and uploaded_files:
        results = {"success": [], "failed": []}
        progress = st.progress(0, text="准备上传...")

        for i, f in enumerate(uploaded_files):
            progress.progress(
                (i + 0.5) / len(uploaded_files),
                text=f"处理 {i + 1}/{len(uploaded_files)}: {f.name}",
            )
            try:
                with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=300.0) as client:
                    upload_resp = client.post(
                        "/documents/upload",
                        files={"file": (f.name, f.getvalue())},
                    )
                    upload_resp.raise_for_status()
                    doc_id = upload_resp.json()["id"]

                    proc_resp = client.post(
                        f"/documents/{doc_id}/process",
                        json={
                            "chunk_size": config["chunk_size"],
                            "overlap": config["overlap"],
                            "strategy": config["strategy"],
                        },
                    )
                    if proc_resp.status_code == 200:
                        r = proc_resp.json()
                        results["success"].append({"name": f.name, "chunks": r.get("chunk_count", 0)})
                    else:
                        results["failed"].append({"name": f.name, "error": proc_resp.json().get("detail", "")})

            except Exception as e:
                results["failed"].append({"name": f.name, "error": str(e)})

        progress.progress(1.0, text="完成！")
        _show_results(results)
        time.sleep(0.5)
        st.rerun()


def _render_folder_upload(config: dict):
    """文件夹上传"""
    folder_path = st.text_input(
        "📁 文件夹路径",
        placeholder="/Users/liubaoyang/Documents/我的知识库",
        help="输入本地文件夹绝对路径，系统会递归扫描所有子文件夹",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        st.checkbox("上传后立即处理", value=True, key="folder_process")
    with col2:
        scan_btn = st.button("🔍 预览文件", disabled=not folder_path)

    if scan_btn and folder_path:
        try:
            with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=15.0) as client:
                resp = client.post(
                    "/documents/upload-folder",
                    json={
                        "folder_path": folder_path,
                        "dry_run": True,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.info(f"找到 **{data['total_found']}** 个支持的文件")
                    if data["total_found"] > 0:
                        with st.expander(f"📋 文件列表"):
                            for item in data.get("success", []):
                                st.text(f"  {item['path']}")
                elif resp.status_code == 400:
                    st.error(f"路径错误: {resp.json()['detail']}")
                else:
                    st.error(f"扫描失败: {resp.status_code}")
        except Exception as e:
            st.error(f"无法连接后端: {e}")

    if folder_path and st.button("🚀 开始上传并处理", type="primary"):
        with st.spinner("正在递归扫描和处理文件夹，请稍候..."):
            try:
                with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=600.0) as client:
                    resp = client.post(
                        "/documents/upload-folder",
                        json={
                            "folder_path": folder_path,
                            "chunk_size": config["chunk_size"],
                            "overlap": config["overlap"],
                            "strategy": config["strategy"],
                        },
                    )
                if resp.status_code == 200:
                    data = resp.json()
                    _show_results({
                        "success": data.get("success", []),
                        "failed": data.get("failed", []),
                    })
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"上传失败: {resp.json().get('detail', resp.status_code)}")
            except Exception as e:
                st.error(f"请求失败: {e}")


# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="文件上传", page_icon="📤", layout="wide")
init_session_state()
st.title("📤 文件上传")
st.markdown(build_minimal_page_css(), unsafe_allow_html=True)

with st.sidebar:
    render_feature_nav(container=st)
    st.divider()
    with st.expander("⚙️ 配置", expanded=False):
        config = render_sidebar(container=st, include_title=False)

mode = st.radio("上传方式", ["📄 单个/多个文件", "📁 文件夹"], horizontal=True)

if mode == "📄 单个/多个文件":
    _render_file_upload(config)
else:
    _render_folder_upload(config)

# ── 文件列表 ──────────────────────────────────────────────
st.markdown("---")
st.subheader("📁 已上传文件")

try:
    with httpx.Client(base_url=DEFAULT_CONFIG["api_url"], timeout=30.0) as client:
        response = client.get("/documents")
        if response.status_code == 200:
            data = response.json()
            if data["items"]:
                cols = st.columns(3)
                for idx, doc in enumerate(data["items"]):
                    with cols[idx % 3]:
                        status_icon = {
                            "uploaded": "📤",
                            "processing": "⚙️",
                            "processed": "✅",
                            "failed": "❌",
                        }.get(doc["status"], "❓")
                        st.markdown(f"**{status_icon} {doc['original_filename']}**")
                        st.caption(
                            f"状态: {doc['status']} · "
                            f"切片: {doc['chunk_count']} · "
                            f"{(doc['file_size'] or 0) / 1024:.1f} KB"
                        )
            else:
                st.info("暂无上传的文件")
        else:
            st.warning(f"无法获取文件列表: {response.status_code}")
except Exception as e:
    st.error(f"无法连接到 API: {str(e)}")
