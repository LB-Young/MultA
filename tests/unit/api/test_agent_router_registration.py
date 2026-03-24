"""Agent 路由接入测试"""
from pathlib import Path


ROUTERS_INIT = Path(__file__).resolve().parents[3] / "src" / "api" / "routers" / "__init__.py"
API_MAIN = Path(__file__).resolve().parents[3] / "src" / "api" / "main.py"
AGENT_ROUTER = Path(__file__).resolve().parents[3] / "src" / "api" / "routers" / "agent.py"


def test_agent_router_file_exists_and_exposes_query_endpoint():
    """应新增 agent 路由文件并暴露 /agent/query。"""
    source = AGENT_ROUTER.read_text(encoding="utf-8")
    assert 'APIRouter(prefix="/agent"' in source
    assert '@router.post("/query"' in source
    assert '@router.get("/sessions"' in source
    assert '@router.post("/sessions"' in source
    assert '@router.get("/sessions/{session_id}"' in source
    assert '@router.delete("/sessions/{session_id}"' in source
    assert '@router.patch("/sessions/{session_id}"' in source
    assert "get_agent_session_repository" in source
    assert "get_agent_service" in source
    assert "AgentService" in source


def test_agent_router_is_exported_and_included_in_app():
    """agent 路由应在 routers 包导出并在主应用挂载。"""
    routers_source = ROUTERS_INIT.read_text(encoding="utf-8")
    main_source = API_MAIN.read_text(encoding="utf-8")

    assert "agent_router" in routers_source
    assert "app.include_router(agent_router)" in main_source
