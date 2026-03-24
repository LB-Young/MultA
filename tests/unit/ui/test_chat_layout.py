"""问答页布局样式测试"""
from ui.components.chat_layout import (
    build_bottom_docked_chat_css,
    build_chat_autoscroll_script,
    build_minimal_page_css,
    build_qa_sidebar_css,
)


def test_bottom_docked_chat_css_keeps_input_near_viewport_bottom():
    """输入栏应固定贴近页面底部，并为消息区提供可用空间。"""
    css = build_bottom_docked_chat_css()

    assert 'min-height: calc(100vh - 9rem);' not in css
    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {' not in css
    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-message-list-anchor) {' in css
    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) {' in css
    assert "max-height: calc(100vh - 15.5rem);" in css
    assert "overflow: hidden;" not in css
    assert "padding-bottom: 7rem;" in css
    assert "position: fixed;" in css
    assert "bottom: 1rem;" in css


def test_bottom_docked_chat_css_avoids_generic_sticky_vertical_blocks():
    """样式不应把所有包含锚点的 VerticalBlock 都设成 sticky。"""
    css = build_bottom_docked_chat_css()

    assert '[data-testid="stVerticalBlock"]:has(#qa-input-dock-anchor) {' not in css
    assert '[data-testid="stVerticalBlock"]:has(#qa-message-list-anchor) {' not in css


def test_bottom_docked_chat_css_uses_minimal_single_frame_chatbar():
    """输入栏应采用单层主容器，避免多重边框套娃。"""
    css = build_bottom_docked_chat_css()

    assert "--qa-input-bg:" in css
    assert "--qa-input-border:" in css
    assert "--qa-input-shadow:" in css
    assert "--qa-input-text:" in css
    assert "--qa-input-placeholder:" in css
    assert "--qa-send-text:" in css
    assert "@media (prefers-color-scheme: dark)" not in css
    assert "@media (prefers-color-scheme: light)" not in css
    assert "background: var(--qa-input-bg);" in css
    assert "border: 1px solid var(--qa-input-border);" in css
    assert "box-shadow: var(--qa-input-shadow);" in css
    assert "backdrop-filter: blur(2px);" in css
    assert "width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem)) !important;" in css
    assert "max-width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem)) !important;" in css
    assert "margin-left: auto !important;" in css
    assert "margin-right: auto !important;" in css
    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stForm"] {' in css
    assert "border: none !important;" in css
    assert "padding: 0 !important;" in css
    assert '[data-testid="stTextInputRootElement"] {' in css
    assert "border: none !important;" in css
    assert "box-shadow: none !important;" in css
    assert '[data-testid="stFormSubmitButton"] button {' in css
    assert "background: var(--primary-color, #1d4ed8);" in css
    assert "color: var(--qa-send-text);" in css


def test_bottom_docked_chat_css_centers_conversation_region():
    """聊天区应以最大宽度居中，而不是被锁在左侧列中。"""
    css = build_bottom_docked_chat_css()

    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-message-list-anchor)' in css
    assert '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor)' in css
    assert "max-width: 58rem;" in css
    assert "margin-left: auto;" in css
    assert "margin-right: auto;" in css
    assert "--qa-sidebar-offset: 15.75rem;" in css
    assert '[data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) {' in css
    assert "left: calc(50% + (var(--qa-sidebar-offset) / 2));" in css
    assert "transform: translateX(-50%);" in css
    assert "width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem));" in css
    assert "background: transparent;" in css
    assert "color: var(--qa-input-text) !important;" in css


def test_bottom_docked_chat_css_aligns_user_right_and_assistant_left():
    """用户消息应右对齐，助手消息应左对齐。"""
    css = build_bottom_docked_chat_css()

    assert '[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {' in css
    assert "flex-direction: row-reverse;" in css
    assert "flex: 0 0 auto;" in css
    assert "width: auto !important;" in css
    assert '[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {' in css
    assert "margin-left: auto;" in css
    assert '[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {' in css
    assert "margin-right: auto;" in css


def test_bottom_docked_chat_css_makes_message_region_scrollable():
    """消息区应支持独立滚动，便于自动滚到底部。"""
    css = build_bottom_docked_chat_css()

    assert "overflow-y: auto;" in css
    assert "scroll-behavior: smooth;" in css
    assert "min-height: 0;" in css


def test_chat_autoscroll_script_retries_and_falls_back_to_bottom_anchor():
    """自动滚动脚本应具备重试机制，并支持锚点回退。"""
    script = build_chat_autoscroll_script(7)

    assert "const nonce = 7;" in script
    assert "const maxAttempts = 8;" in script
    assert "setTimeout(() => runScroll(attempt + 1), 80);" in script
    assert "findScrollableAncestor" in script
    assert "bindSubmitAutoScroll" in script
    assert "bindGlobalSubmitAutoScroll" in script
    assert "parentDoc.addEventListener('keydown', onKeydown, true);" in script
    assert "parentDoc.addEventListener('click', onClick, true);" in script
    assert "form.addEventListener('submit', scheduleBurstScroll, true);" in script
    assert "submitBtn.addEventListener('click', scheduleBurstScroll, true);" in script
    assert "bindMessageMutationAutoScroll" in script
    assert "new MutationObserver(onMutate);" in script
    assert "bottomAnchor.scrollIntoView({ block: 'end', behavior: 'auto' });" in script


def test_minimal_page_css_reduces_global_blank_spacing():
    """全局样式应压缩页面顶部和分割线空白。"""
    css = build_minimal_page_css()

    assert '[data-testid="stMainBlockContainer"] {' in css
    assert "padding-top: 1.6rem;" in css
    assert "padding-bottom: 1rem;" in css
    assert '[data-testid="stAppViewContainer"] h1 {' in css
    assert '[data-testid="stMainBlockContainer"] [data-testid="stHeadingWithActionElements"] {' in css
    assert "padding-top: 0.45rem;" in css
    assert "margin-top: 0.55rem;" in css
    assert "line-height: 1.35;" in css
    assert "letter-spacing: normal;" in css
    assert "overflow: visible;" in css
    assert "font-size: 2.05rem;" in css


def test_sidebar_secondary_buttons_support_compact_single_line_cards():
    """会话按钮应为紧凑单行卡片。"""
    css = build_qa_sidebar_css()

    assert "white-space: nowrap;" in css
    assert "text-overflow: ellipsis;" in css
    assert "text-align: left;" in css
    assert "justify-content: flex-start;" in css
    assert "min-height: 2.1rem;" in css
