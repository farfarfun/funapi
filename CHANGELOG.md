# Changelog

本项目的版本记录遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 风格。

## [1.0.4]

### Changed

- 日志入口从 `funutil.getLogger` 改为组织统一的 `farlog.getLogger`，移除 `funutil` 依赖
- `generate/core.py` 类型标注从 `typing.Optional`/`typing.Union` 改为 `X | None`/`A | B` 写法
- `pyproject.toml` 补全 `description`（此前是脚手架占位文案）、`license = "MIT"`，`funfake` 依赖补上版本下限

### Fixed

- `_process_config`/`convert_openapi_v3` 不再一律 `raise Exception`，改为携带上下文的领域异常
  （`GenerateApiError`、`OpenApiConvertError`）
- `convert_openapi_v3` 补上 HTTP 响应状态码与 JSON 解析校验，转换服务失败时不再当成功处理

## [1.0.3]

### Added

- OpenAPI 文档生成客户端代码、OpenAPI v2 转 v3 两个核心功能
