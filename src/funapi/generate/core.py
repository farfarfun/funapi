import codecs
from pathlib import Path

from farlog import getLogger
from openapi_python_client import MetaType, generate
from openapi_python_client.config import Config, ConfigFile

logger = getLogger("funapi")


class GenerateApiError(ValueError):
    """生成 API 客户端过程中，参数或配置不合法时抛出。"""


def _process_config(
    *,
    url: str | None,
    path: Path | None,
    config_path: Path | None,
    meta_type: MetaType,
    file_encoding: str,
    overwrite: bool,
    output_path: Path | None,
) -> Config:
    """校验入参并构建 `openapi-python-client` 所需的 `Config`。

    Args:
        url: OpenAPI 文档的 URL，与 `path` 二选一。
        path: 本地 OpenAPI 文档路径，与 `url` 二选一。
        config_path: 自定义生成器配置文件路径，可选。
        meta_type: 生成客户端时使用的元信息类型（如 poetry/setup）。
        file_encoding: 读取 OpenAPI 文档时使用的编码。
        overwrite: 目标目录已存在时是否覆盖。
        output_path: 生成客户端代码的输出目录，可选。

    Returns:
        构建好的 `Config` 对象。

    Raises:
        GenerateApiError: `url`/`path` 同时提供或都未提供、`file_encoding`
            不是合法编码、或 `config_path` 指向的配置文件加载失败时抛出。
    """
    source: Path | str
    if url and not path:
        source = url
    elif path and not url:
        source = path
    elif url and path:
        raise GenerateApiError("Provide either --url or --path, not both")
    else:
        raise GenerateApiError("You must either provide --url or --path")

    try:
        codecs.getencoder(file_encoding)
    except LookupError as err:
        raise GenerateApiError(f"Unknown encoding: {file_encoding}") from err

    if not config_path:
        config_file = ConfigFile()
    else:
        try:
            config_file = ConfigFile.load_from_path(path=config_path)
        except Exception as err:
            raise GenerateApiError(
                f"Failed to load generator config from {config_path}: {err}"
            ) from err

    return Config.from_sources(
        config_file,
        meta_type,
        source,
        file_encoding,
        overwrite,
        output_path=output_path,
    )


def generate_api(
    url: str | None = None,
    path: Path | None = None,
    custom_template_path: Path | None = None,
    meta: MetaType = MetaType.POETRY,
    file_encoding: str = "utf-8",
    config_path: Path | None = None,
    overwrite: bool = False,
    output_path: Path | None = None,
) -> None:
    """根据 OpenAPI 文档生成一个新的 API 客户端库。

    Args:
        url: OpenAPI 文档的 URL，与 `path` 二选一。
        path: 本地 OpenAPI 文档路径，与 `url` 二选一。
        custom_template_path: 自定义模板目录路径，可选。
        meta_type: 生成客户端时使用的元信息类型，默认 `MetaType.POETRY`。
        file_encoding: 读取 OpenAPI 文档时使用的编码，默认 `"utf-8"`。
        config_path: 自定义生成器配置文件路径，可选。
        overwrite: 目标目录已存在时是否覆盖，默认 `False`。
        output_path: 生成客户端代码的输出目录，默认使用生成器的默认规则。

    Returns:
        None。生成的客户端代码直接写入 `output_path`（或默认输出目录）。

    Raises:
        GenerateApiError: 参数不合法或配置文件加载失败时抛出。
    """
    config = _process_config(
        url=url,
        path=path,
        config_path=config_path,
        meta_type=meta,
        file_encoding=file_encoding,
        overwrite=overwrite,
        output_path=output_path,
    )
    generate(
        custom_template_path=custom_template_path,
        config=config,
    )
