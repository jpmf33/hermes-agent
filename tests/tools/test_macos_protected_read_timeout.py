"""Regression tests for macOS protected-folder read stalls."""

from tools.file_operations import (
    ExecuteResult,
    ShellFileOperations,
    _is_macos_tcc_protected_path,
)


def test_protected_path_detection_is_lexical():
    assert _is_macos_tcc_protected_path(
        "/Users/test/Documents/vault/AGENTS.md",
        home="/Users/test",
        platform="darwin",
    )
    assert not _is_macos_tcc_protected_path(
        "/Users/test/project/AGENTS.md",
        home="/Users/test",
        platform="darwin",
    )


def test_read_file_stops_after_protected_folder_probe_timeout(monkeypatch):
    class Env:
        is_local = True
        cwd = "/Users/test"

    file_ops = ShellFileOperations(Env())
    calls = []

    def timed_out(command, cwd=None, timeout=None, stdin_data=None):
        calls.append(timeout)
        return ExecuteResult(stdout="[Command timed out]", exit_code=124)

    monkeypatch.setattr("tools.file_operations.sys.platform", "darwin")
    monkeypatch.setattr("tools.file_operations._HOME", "/Users/test")
    monkeypatch.setattr(file_ops, "_exec", timed_out)

    result = file_ops.read_file("/Users/test/Documents/vault/AGENTS.md")

    assert "Full Disk Access" in (result.error or "")
    assert calls == [5]
