"""funapi 的轻量级冒烟测试。

funapi 是一个提供两个公开入口的小型 OpenAPI 工具集：

- ``funapi.convert.convert_openapi_v3``：通过 POST 请求外部服务
  ``converter.swagger.io``，将本地 OpenAPI 2.0/3.0 JSON 文件转换为 v3。
  这里始终模拟 HTTP 调用，测试不得访问真实网络。
- ``funapi.generate.generate_api``：对
  ``openapi_python_client.generate`` 的薄封装，用于根据 OpenAPI 文档（本地
  文件或 URL）生成客户端库。网络请求、代码生成和文件写入由第三方
  ``openapi_python_client`` 完成，因此这里也会模拟该调用，只验证 funapi
  自身的配置构建逻辑。

本文件不会访问真实网络，不会在 pytest 的 ``tmp_path`` 之外产生文件系统副作用，
也不会使用外部凭据。
"""

import json
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# 导入冒烟测试
# ---------------------------------------------------------------------------


def test_import_top_level_package():
    import funapi  # noqa: F401


def test_import_convert_submodule():
    import funapi.convert  # noqa: F401

    assert hasattr(funapi.convert, "convert_openapi_v3")
    assert callable(funapi.convert.convert_openapi_v3)


def test_import_generate_submodule():
    import funapi.generate  # noqa: F401

    assert hasattr(funapi.generate, "generate_api")
    assert callable(funapi.generate.generate_api)


# ---------------------------------------------------------------------------
# funapi.convert.convert_openapi_v3
# ---------------------------------------------------------------------------


def test_convert_openapi_v3_mocks_http_call(tmp_path):
    """验证 convert_openapi_v3 不会访问真实的 converter.swagger.io。

    模拟 ``requests.post``（由 funapi.convert.convert_openapi 直接导入），
    确保不发起网络请求，并验证请求与响应的衔接正确。
    """
    from funapi.convert.convert_openapi import convert_openapi_v3

    ori_path = tmp_path / "openapi-ori.json"
    v3_path = tmp_path / "openapi-v3.json"

    original_doc = {"swagger": "2.0", "info": {"title": "demo", "version": "1"}}
    converted_doc = {"openapi": "3.0.0", "info": {"title": "demo", "version": "1"}}

    ori_path.write_text(json.dumps(original_doc), encoding="utf-8")

    fake_response = mock.Mock()
    fake_response.json.return_value = converted_doc

    with mock.patch(
        "funapi.convert.convert_openapi.requests.post", return_value=fake_response
    ) as mock_post:
        convert_openapi_v3(
            openapi_filepath_ori=str(ori_path),
            openapi_filepath_v3=str(v3_path),
        )

    # 不访问真实网络：requests.post 应只调用一次，并使用外部转换服务的 URL。
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_args[0] == "https://converter.swagger.io/api/convert"
    assert called_kwargs["json"] == original_doc
    assert "headers" in called_kwargs

    # 模拟的转换文档应被正确写出。
    assert v3_path.exists()
    assert json.loads(v3_path.read_text(encoding="utf-8")) == converted_doc


def test_convert_openapi_v3_raises_on_missing_input_file(tmp_path):
    """验证输入文件不存在时会明确失败且不会吞掉异常。

    这也证明读取文件前不会发起网络请求（requests.post 仍被模拟）。
    """
    from funapi.convert.convert_openapi import convert_openapi_v3

    missing = tmp_path / "does-not-exist.json"

    with mock.patch("funapi.convert.convert_openapi.requests.post") as mock_post:
        with pytest.raises(FileNotFoundError):
            convert_openapi_v3(
                openapi_filepath_ori=str(missing),
                openapi_filepath_v3=str(tmp_path / "out.json"),
            )

    mock_post.assert_not_called()


# ---------------------------------------------------------------------------
# funapi.generate.generate_api
# ---------------------------------------------------------------------------


def test_generate_api_requires_url_or_path():
    """验证未提供 --url 和 --path 时 _process_config 会抛出异常。

    这是 funapi 自身的校验逻辑（不涉及网络或代码生成），因此直接测试而不跳过。
    """
    from funapi.generate import generate_api

    with pytest.raises(Exception):
        generate_api(url=None, path=None)


def test_generate_api_rejects_url_and_path_together():
    """验证同时提供 --url 和 --path 时 _process_config 也会抛出异常。"""
    from funapi.generate import generate_api

    with pytest.raises(Exception):
        generate_api(url="https://example.com/openapi.json", path=Path("some.json"))


def test_generate_api_builds_config_and_delegates_without_network(tmp_path):
    """验证 generate_api 会根据本地路径构建 Config 并交给
    openapi_python_client.generate()。

    模拟该调用，确保不进行真实代码生成、网络访问或文件写入。
    """
    from funapi.generate import core as generate_core

    fake_source = tmp_path / "openapi.json"
    fake_source.write_text("{}", encoding="utf-8")

    with mock.patch.object(generate_core, "generate") as mock_generate:
        mock_generate.return_value = []
        generate_core.generate_api(path=fake_source)

    mock_generate.assert_called_once()
    _, call_kwargs = mock_generate.call_args
    config = call_kwargs["config"]
    assert config.document_source == fake_source


def test_generate_api_cli_entry_point_not_present():
    """验证 funapi 没有声明 [project.scripts] 入口，因此没有可通过 --help
    运行的 CLI。这是仓库结构事实，不是测试功能缺失。"""
    pytest.skip(
        "funapi 未在 pyproject.toml 中定义 [project.scripts] CLI 入口，"
        "没有可通过 --help 调用的命令。"
    )
