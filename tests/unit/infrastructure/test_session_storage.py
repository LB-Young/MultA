"""会话存储回归测试"""
from datetime import datetime

from src.domain.entities.query import ConversationSession
from src.infrastructure.storage.session_storage import SessionRepository, get_agent_session_repository


def test_list_sessions_can_be_called_repeatedly_without_type_errors(tmp_path):
    """list_sessions 不应在重复调用时触发 fromisoformat 类型错误。"""
    repo = SessionRepository(str(tmp_path / "sessions.json"))
    session = ConversationSession(title="重复调用测试")
    session.add_user_message("hello")
    repo.create_session(session)

    first = repo.list_sessions()
    second = repo.list_sessions()

    assert len(first) == 1
    assert len(second) == 1
    assert isinstance(second[0].created_at, datetime)
    assert isinstance(second[0].updated_at, datetime)


def test_get_session_can_be_called_repeatedly_without_type_errors(tmp_path):
    """get_session 不应在重复调用时触发 fromisoformat 类型错误。"""
    repo = SessionRepository(str(tmp_path / "sessions.json"))
    session = ConversationSession(title="重复读取测试")
    session.add_assistant_message("ok")
    repo.create_session(session)

    first = repo.get_session(session.id)
    second = repo.get_session(session.id)

    assert first is not None
    assert second is not None
    assert first.id == second.id
    assert isinstance(second.created_at, datetime)


def test_relative_storage_path_is_resolved_from_project_root(monkeypatch):
    """相对路径应基于项目根目录解析，而非运行时 cwd。"""
    repo = SessionRepository("data/sessions.json")
    assert repo._storage_path.name == "sessions.json"
    assert repo._storage_path.parent.name == "data"
    assert repo._storage_path.is_absolute()


def test_env_session_storage_path_overrides_default(tmp_path, monkeypatch):
    """应允许通过环境变量覆盖会话存储路径。"""
    override_path = tmp_path / "custom_sessions.json"
    monkeypatch.setenv("SESSION_STORAGE_PATH", str(override_path))
    repo = SessionRepository()
    assert repo._storage_path == override_path
    monkeypatch.delenv("SESSION_STORAGE_PATH", raising=False)


def test_agent_session_repository_uses_dedicated_storage_file():
    """Agent 会话应使用独立持久化文件，避免和知识问答混用。"""
    repo = get_agent_session_repository()
    assert repo._storage_path.name == "agent_sessions.json"
