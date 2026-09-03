import json
from pathlib import Path

import requests
from farlog import getLogger
from funfake.headers import fake_header

logger = getLogger("funapi")


class OpenApiConvertError(RuntimeError):
    """调用 converter.swagger.io 转换 OpenAPI 文档失败时抛出。"""


def convert_openapi_v3(
    openapi_filepath_ori: str | Path = "openapi-ori.json",
    openapi_filepath_v3: str | Path = "openapi-v3.json",
) -> None:
    """调用 converter.swagger.io，把本地 OpenAPI v2 文档转换成 v3。

    Args:
        openapi_filepath_ori: 待转换的原始 OpenAPI（v2/v3）文档路径。
        openapi_filepath_v3: 转换结果写出的目标文件路径。

    Returns:
        None。转换结果直接写入 `openapi_filepath_v3`。

    Raises:
        FileNotFoundError: `openapi_filepath_ori` 不存在时抛出（内置行为）。
        OpenApiConvertError: 远程转换服务返回非 2xx 状态码，或返回内容不是
            合法 JSON 时抛出，错误信息携带请求的 URL 与输入文件路径。
    """
    url = "https://converter.swagger.io/api/convert"
    headers = fake_header()
    with open(openapi_filepath_ori, "r", encoding="utf-8") as f:
        original_doc = json.load(f)

    response = requests.post(url, json=original_doc, headers=headers)
    if not response.ok:
        raise OpenApiConvertError(
            f"调用 {url} 转换 {openapi_filepath_ori} 失败："
            f"HTTP {response.status_code} {response.text[:200]!r}"
        )

    try:
        converted_doc = response.json()
    except ValueError as err:
        raise OpenApiConvertError(
            f"调用 {url} 转换 {openapi_filepath_ori} 失败：响应不是合法 JSON"
        ) from err

    with open(openapi_filepath_v3, "w", encoding="utf-8") as f:
        f.write(json.dumps(converted_doc, indent=4, ensure_ascii=False))
    logger.success(f"converted success: {openapi_filepath_v3}")
