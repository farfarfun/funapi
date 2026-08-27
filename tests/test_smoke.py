"""Lightweight smoke tests for funapi.

funapi is a small OpenAPI toolkit with two public entry points:

- ``funapi.convert.convert_openapi_v3`` -- converts a local OpenAPI 2.0/3.0
  JSON file to v3 by POSTing it to the external service
  ``converter.swagger.io``. The HTTP call is always mocked here -- these
  tests must never touch the real network.
- ``funapi.generate.generate_api`` -- thin wrapper around
  ``openapi_python_client.generate`` used to generate a client library from
  an OpenAPI document (local file or URL). The heavy lifting (network I/O,
  code generation, file writing) lives inside the third-party
  ``openapi_python_client`` package, so it is mocked out here too; we only
  smoke-test funapi's own config-building logic.

No real network, filesystem side effects outside of pytest's ``tmp_path``,
or external credentials are used anywhere in this file.
"""

import json
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Import smoke tests
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
    """convert_openapi_v3 must never hit the real converter.swagger.io.

    We patch ``requests.post`` (imported directly in
    funapi.convert.convert_openapi) so no network call is made, and assert
    the function wires the request/response together correctly.
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

    # No real network call: requests.post was called exactly once, and it
    # was called with the URL to the external converter service.
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_args[0] == "https://converter.swagger.io/api/convert"
    assert called_kwargs["json"] == original_doc
    assert "headers" in called_kwargs

    # The (mocked) converted document was written out correctly.
    assert v3_path.exists()
    assert json.loads(v3_path.read_text(encoding="utf-8")) == converted_doc


def test_convert_openapi_v3_raises_on_missing_input_file(tmp_path):
    """Sanity check the function fails loudly (no swallowed errors) when
    the input file doesn't exist -- this also proves no network call
    happens before the file is read (requests.post is still mocked)."""
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
    """_process_config raises if neither --url nor --path is given. This is
    funapi's own validation logic (no network/codegen involved), so it is
    exercised directly rather than skipped."""
    from funapi.generate import generate_api

    with pytest.raises(Exception):
        generate_api(url=None, path=None)


def test_generate_api_rejects_url_and_path_together():
    """_process_config also raises if both --url and --path are given."""
    from funapi.generate import generate_api

    with pytest.raises(Exception):
        generate_api(url="https://example.com/openapi.json", path=Path("some.json"))


def test_generate_api_builds_config_and_delegates_without_network(tmp_path):
    """generate_api should build a Config from a local path and hand off to
    openapi_python_client.generate(). We mock that call so no real code
    generation, network access, or file writing happens."""
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
    """funapi's pyproject.toml declares no [project.scripts] entry point,
    so there is no CLI to smoke test via --help. This is a repo-shape fact,
    not a functional gap in the tests."""
    pytest.skip(
        "funapi has no [project.scripts] CLI entry point defined in "
        "pyproject.toml; nothing to invoke with --help."
    )
