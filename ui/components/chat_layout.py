"""问答页布局辅助"""


def build_bottom_docked_chat_css() -> str:
    """返回问答页底部输入栏布局所需的样式。"""
    return """
<style>
[data-testid="stAppViewContainer"] {
    --qa-sidebar-offset: 15.75rem;
    --qa-input-bg: var(--qa-explicit-input-bg, #ffffff);
    --qa-input-border: var(--qa-explicit-input-border, rgba(15, 23, 42, 0.14));
    --qa-input-shadow: var(--qa-explicit-input-shadow, 0 4px 12px rgba(15, 23, 42, 0.08));
    --qa-input-text: var(--qa-explicit-input-text, #0f172a);
    --qa-input-placeholder: var(--qa-explicit-input-placeholder, rgba(71, 85, 105, 0.72));
    --qa-send-text: var(--qa-explicit-send-text, #ffffff);
}

[data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) {
    --qa-sidebar-offset: 0rem;
}

@media (max-width: 1100px) {
    :root {
        --qa-sidebar-offset: 0rem;
    }
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-message-list-anchor) {
    min-height: 0;
    max-height: calc(100vh - 15.5rem);
    overflow-y: auto;
    scroll-behavior: smooth;
    padding-bottom: 7rem;
    width: 100%;
    max-width: 58rem;
    margin-left: auto;
    margin-right: auto;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) {
    position: fixed;
    bottom: 1rem;
    left: calc(50% + (var(--qa-sidebar-offset) / 2));
    transform: translateX(-50%);
    z-index: 30;
    padding-bottom: 0;
    background: transparent;
    width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem));
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stHorizontalBlock"] {
    background: var(--qa-input-bg);
    border: 1px solid var(--qa-input-border);
    border-radius: 0.9rem;
    padding: 0.45rem 0.55rem;
    box-shadow: var(--qa-input-shadow);
    backdrop-filter: blur(2px);
    align-items: center;
    width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem)) !important;
    max-width: min(58rem, calc(100vw - var(--qa-sidebar-offset) - 3.5rem)) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stTextInput"] {
    margin-bottom: 0;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stTextInputRootElement"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stTextInputRootElement"] > div {
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) input[aria-label="输入您的问题..."] {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    padding-left: 0.2rem;
    color: var(--qa-input-text) !important;
    caret-color: var(--qa-input-text) !important;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) input[aria-label="输入您的问题..."]::placeholder {
    color: var(--qa-input-placeholder) !important;
    opacity: 0.62;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stFormSubmitButton"] {
    margin-bottom: 0;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stFormSubmitButton"] button {
    min-height: 2.4rem;
    padding: 0 1rem;
    border: 1px solid transparent;
    border-radius: 0.7rem;
    background: var(--primary-color, #1d4ed8);
    color: var(--qa-send-text);
    box-shadow: none;
    font-weight: 600;
    filter: brightness(0.96);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stFormSubmitButton"] button:hover {
    filter: brightness(1.05);
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor) [data-testid="stFormSubmitButton"] button:focus {
    box-shadow: none;
}

[data-testid="stChatMessage"] {
    gap: 0.75rem;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    flex: 0 0 auto;
    width: auto !important;
    max-width: min(100%, 42rem);
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    margin-left: auto;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    margin-right: auto;
}
</style>
"""


def build_chat_autoscroll_script(scroll_nonce: int) -> str:
    """返回聊天区自动滚到底部的脚本。"""
    return f"""
<script>
const nonce = {scroll_nonce};
const parentDoc = window.parent.document;
const parentWin = window.parent;
const maxAttempts = 8;

const findScrollableAncestor = (node) => {{
    let current = node;
    while (current) {{
        if (current.scrollHeight > current.clientHeight + 1) {{
            return current;
        }}
        current = current.parentElement;
    }}
    return null;
}};

const scrollToBottomNow = () => {{
    const messageArea = parentDoc.querySelector(
        '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-message-list-anchor)'
    );
    const bottomAnchor = parentDoc.getElementById('qa-message-bottom-anchor');

    if (messageArea) {{
        messageArea.scrollTop = messageArea.scrollHeight;
    }}
    if (bottomAnchor) {{
        const scrollContainer = findScrollableAncestor(bottomAnchor);
        if (scrollContainer) {{
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }}
        bottomAnchor.scrollIntoView({{ block: 'end', behavior: 'auto' }});
    }}
}};

const bindSubmitAutoScroll = () => {{
    const dock = parentDoc.querySelector(
        '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor)'
    );
    if (!dock) return;

    const form = dock.querySelector('form');
    const submitBtn = dock.querySelector('[data-testid="stFormSubmitButton"] button');
    if (!form || !submitBtn) return;

    if (parentWin.__qaSubmitForm === form && parentWin.__qaSubmitBtn === submitBtn) {{
        return;
    }}

    const scheduleBurstScroll = () => {{
        scrollToBottomNow();
        setTimeout(scrollToBottomNow, 40);
        setTimeout(scrollToBottomNow, 120);
        setTimeout(scrollToBottomNow, 220);
    }};

    if (parentWin.__qaSubmitForm && parentWin.__qaSubmitScrollHandler) {{
        parentWin.__qaSubmitForm.removeEventListener('submit', parentWin.__qaSubmitScrollHandler, true);
    }}
    if (parentWin.__qaSubmitBtn && parentWin.__qaSubmitScrollHandler) {{
        parentWin.__qaSubmitBtn.removeEventListener('click', parentWin.__qaSubmitScrollHandler, true);
    }}

    form.addEventListener('submit', scheduleBurstScroll, true);
    submitBtn.addEventListener('click', scheduleBurstScroll, true);
    parentWin.__qaSubmitForm = form;
    parentWin.__qaSubmitBtn = submitBtn;
    parentWin.__qaSubmitScrollHandler = scheduleBurstScroll;
}};

const bindGlobalSubmitAutoScroll = () => {{
    if (parentWin.__qaGlobalSubmitBound) return;

    const isInsideDock = (target) => {{
        if (!target) return false;
        const dock = target.closest(
            '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-input-dock-anchor)'
        );
        return !!dock;
    }};

    const scheduleBurstScroll = () => {{
        scrollToBottomNow();
        setTimeout(scrollToBottomNow, 40);
        setTimeout(scrollToBottomNow, 120);
        setTimeout(scrollToBottomNow, 220);
    }};

    const onKeydown = (event) => {{
        if (event.key !== 'Enter') return;
        if (event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) return;
        const target = event.target;
        if (!(target instanceof parentWin.HTMLInputElement)) return;
        if (!isInsideDock(target)) return;
        scheduleBurstScroll();
    }};

    const onClick = (event) => {{
        const target = event.target;
        if (!(target instanceof parentWin.Element)) return;
        const btn = target.closest('[data-testid="stFormSubmitButton"] button');
        if (!btn) return;
        if (!isInsideDock(btn)) return;
        scheduleBurstScroll();
    }};

    parentDoc.addEventListener('keydown', onKeydown, true);
    parentDoc.addEventListener('click', onClick, true);
    parentWin.__qaGlobalSubmitBound = true;
}};

const bindMessageMutationAutoScroll = () => {{
    const messageArea = parentDoc.querySelector(
        '[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(#qa-message-list-anchor)'
    );
    if (!messageArea) return;

    if (parentWin.__qaObservedMessageArea === messageArea && parentWin.__qaMessageObserver) {{
        return;
    }}

    if (parentWin.__qaMessageObserver) {{
        parentWin.__qaMessageObserver.disconnect();
    }}

    const onMutate = () => {{
        window.requestAnimationFrame(() => scrollToBottomNow());
    }};
    const observer = new MutationObserver(onMutate);
    observer.observe(messageArea, {{
        childList: true,
        subtree: true,
    }});
    parentWin.__qaObservedMessageArea = messageArea;
    parentWin.__qaMessageObserver = observer;
}};

const parseColor = (value) => {{
    if (!value) return null;
    const color = value.trim().toLowerCase();
    if (!color) return null;

    if (color.startsWith('#')) {{
        const hex = color.slice(1);
        if (hex.length === 3) {{
            const r = parseInt(hex[0] + hex[0], 16);
            const g = parseInt(hex[1] + hex[1], 16);
            const b = parseInt(hex[2] + hex[2], 16);
            return {{ r, g, b }};
        }}
        if (hex.length === 6) {{
            const r = parseInt(hex.slice(0, 2), 16);
            const g = parseInt(hex.slice(2, 4), 16);
            const b = parseInt(hex.slice(4, 6), 16);
            return {{ r, g, b }};
        }}
    }}

    const rgbMatch = color.match(/rgba?\\((\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)(?:\\s*,\\s*([\\d.]+))?\\)/);
    if (rgbMatch) {{
        const alpha = rgbMatch[4] !== undefined ? Number(rgbMatch[4]) : 1;
        if (Number.isFinite(alpha) && alpha <= 0.01) {{
            // 全透明颜色不用于主题明暗判定
            return null;
        }}
        return {{
            r: Number(rgbMatch[1]),
            g: Number(rgbMatch[2]),
            b: Number(rgbMatch[3]),
        }};
    }}
    return null;
}};

const isDarkByColor = (rgb) => {{
    if (!rgb) return false;
    const luminance = (0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b) / 255;
    return luminance < 0.5;
}};

const resolveThemeRgb = (app) => {{
    const appStyles = parentWin.getComputedStyle(app);
    const rootStyles = parentWin.getComputedStyle(parentDoc.documentElement);
    const bodyStyles = parentDoc.body ? parentWin.getComputedStyle(parentDoc.body) : null;

    // 1) 先读 Streamlit 主题变量（app/root）
    const fromAppVar = parseColor(appStyles.getPropertyValue('--background-color'));
    if (fromAppVar) return fromAppVar;
    const fromRootVar = parseColor(rootStyles.getPropertyValue('--background-color'));
    if (fromRootVar) return fromRootVar;

    // 2) 再读实际背景色（app/body/root）
    const fromAppBg = parseColor(appStyles.backgroundColor);
    if (fromAppBg) return fromAppBg;
    if (bodyStyles) {{
        const fromBodyBg = parseColor(bodyStyles.backgroundColor);
        if (fromBodyBg) return fromBodyBg;
    }}
    const fromRootBg = parseColor(rootStyles.backgroundColor);
    if (fromRootBg) return fromRootBg;

    return null;
}};

const applyThemeToInputDock = () => {{
    const app = parentDoc.querySelector('[data-testid="stAppViewContainer"]');
    if (!app) return;

    const rgb = resolveThemeRgb(app);
    const dark = isDarkByColor(rgb);

    if (dark) {{
        app.style.setProperty('--qa-explicit-input-bg', '#0f172a');
        app.style.setProperty('--qa-explicit-input-border', 'rgba(148, 163, 184, 0.28)');
        app.style.setProperty('--qa-explicit-input-shadow', '0 10px 26px rgba(0, 0, 0, 0.36)');
        app.style.setProperty('--qa-explicit-input-text', '#e5e7eb');
        app.style.setProperty('--qa-explicit-input-placeholder', 'rgba(203, 213, 225, 0.76)');
        app.style.setProperty('--qa-explicit-send-text', '#ffffff');
        return;
    }}

    app.style.setProperty('--qa-explicit-input-bg', '#ffffff');
    app.style.setProperty('--qa-explicit-input-border', 'rgba(15, 23, 42, 0.14)');
    app.style.setProperty('--qa-explicit-input-shadow', '0 4px 12px rgba(15, 23, 42, 0.08)');
    app.style.setProperty('--qa-explicit-input-text', '#0f172a');
    app.style.setProperty('--qa-explicit-input-placeholder', 'rgba(71, 85, 105, 0.72)');
    app.style.setProperty('--qa-explicit-send-text', '#ffffff');
}};

const runScroll = (attempt = 0) => {{
    applyThemeToInputDock();
    bindSubmitAutoScroll();
    bindGlobalSubmitAutoScroll();
    bindMessageMutationAutoScroll();
    scrollToBottomNow();

    if (attempt < maxAttempts) {{
        setTimeout(() => runScroll(attempt + 1), 80);
    }}
}};

applyThemeToInputDock();
const appContainer = parentDoc.querySelector('[data-testid="stAppViewContainer"]');
if (appContainer) {{
    if (parentWin.__qaThemeObserver) {{
        parentWin.__qaThemeObserver.disconnect();
    }}
    const observer = new MutationObserver(() => applyThemeToInputDock());
    observer.observe(appContainer, {{
        attributes: true,
        attributeFilter: ['class', 'style', 'data-theme'],
    }});
    parentWin.__qaThemeObserver = observer;
}}

window.requestAnimationFrame(() => window.requestAnimationFrame(() => runScroll(0)));
</script>
"""


def build_qa_sidebar_css() -> str:
    """返回问答页侧边栏会话列表样式。"""
    return """
<style>
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"] {
    border-radius: 0.7rem;
    border: 1px solid rgba(15, 23, 42, 0.08);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: left;
    justify-content: flex-start;
    line-height: 1.2;
    min-height: 2.1rem;
    padding: 0.25rem 0.55rem;
    font-size: 0.84rem;
}

[data-testid="stSidebar"] .qa-session-item {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 0.75rem;
    padding: 0.55rem 0.65rem;
    margin: 0.35rem 0 0.45rem;
    background: rgba(255, 255, 255, 0.55);
}

[data-testid="stSidebar"] .qa-session-item.active {
    border-color: rgba(15, 23, 42, 0.22);
    background: rgba(15, 23, 42, 0.04);
}

[data-testid="stSidebar"] .qa-session-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.18rem;
}

[data-testid="stSidebar"] .qa-session-meta {
    font-size: 0.78rem;
    color: #64748b;
    line-height: 1.3;
}
</style>
"""


def build_minimal_page_css() -> str:
    """返回全局轻量样式，用于统一页面观感。"""
    return """
<style>
[data-testid="stMainBlockContainer"] {
    padding-top: 1.6rem;
    padding-bottom: 1rem;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    gap: 0.6rem;
}

[data-testid="stMainBlockContainer"] hr {
    margin: 0.45rem 0 0.55rem;
}

[data-testid="stAppViewContainer"] h1 {
    letter-spacing: normal;
    margin-top: 0.55rem;
    margin-bottom: 0.25rem;
    line-height: 1.35;
    overflow: visible;
    font-size: 2.05rem;
}

[data-testid="stMainBlockContainer"] [data-testid="stHeadingWithActionElements"] {
    padding-top: 0.45rem;
    overflow: visible;
}

[data-testid="stSidebar"] [data-testid="stButton"] > button {
    border-radius: 0.7rem;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 0.75rem;
}

[data-testid="stSidebarNav"] {
    display: none;
}
</style>
"""
