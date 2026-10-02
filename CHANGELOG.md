# Changelog

本项目的版本记录遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 风格。

## [1.0.4]

### 新增

- `tests/` 补齐公开 API 的边界用例：转换服务非 2xx 响应、响应非法 JSON、连接异常、
  输入文件非法 JSON，以及生成器的非法编码、配置文件加载失败、URL/模板参数透传

### 修复

- `_process_config`/`convert_openapi_v3` 不再一律 `raise Exception`，改为携带上下文的领域异常
  （`GenerateApiError`、`OpenApiConvertError`）
- `convert_openapi_v3` 补上 HTTP 响应状态码与 JSON 解析校验，转换服务失败时不再当成功处理
- `convert_openapi_v3` 的 `requests.post` 补上连接/读取超时（5s/30s），不再可能无限期挂住
- `convert_openapi_v3` 捕获 `requests.RequestException` 与输入文件的 `json.JSONDecodeError`，
  转换为带请求 URL 和输入文件路径的 `OpenApiConvertError`，并用 `raise ... from` 保留原始异常

### 变更

- 日志入口从 `funutil.getLogger` 改为组织统一的 `farlog.getLogger`，移除 `funutil` 依赖
- `generate/core.py` 类型标注从 `typing.Optional`/`typing.Union` 改为 `X | None`/`A | B` 写法
- `pyproject.toml` 补全 `description`（此前是脚手架占位文案）、`license = "MIT"`，`funfake` 依赖补上版本下限

### 废弃

- 无

## [1.0.3]

### 新增

- OpenAPI 文档生成客户端代码、OpenAPI v2 转 v3 两个核心功能

### 修复

- 无

### 变更

- 无

### 废弃

- 无
