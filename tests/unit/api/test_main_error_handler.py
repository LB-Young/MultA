"""主应用异常处理测试"""
from pathlib import Path


MAIN_FILE = Path(__file__).resolve().parents[3] / "src" / "api" / "main.py"


def test_general_error_handler_uses_request_debug_flag_instead_of_logger_level_compare():
    """异常处理不应比较 logger.level 与整数，避免 method/int 类型错误。"""
    source = MAIN_FILE.read_text(encoding="utf-8")

    assert "logger.level <= 10" not in source
    assert '{"trace": str(exc)} if request.app.debug else {}' in source
