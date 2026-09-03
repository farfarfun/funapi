# funapi

OpenAPI 相关的小工具集：根据 OpenAPI/Swagger 文档一键生成 Python API 客户端代码，并提供 OpenAPI v2 转 v3 的辅助函数。核心生成逻辑基于 [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) 封装。

## 安装

```bash
pip install funapi
```

## 用法示例

### 生成 API 客户端

```python
from funapi.generate import generate_api

# 根据 OpenAPI 文档 URL 生成客户端代码
generate_api(url="https://example.com/openapi.json")

# 或者根据本地 OpenAPI 文档文件生成
generate_api(path="./openapi.json")
```

### OpenAPI v2 转 v3

```python
from funapi.convert import convert_openapi_v3

# 调用 https://converter.swagger.io 在线接口，将 v2 文档转换为 v3
convert_openapi_v3(
    openapi_filepath_ori="openapi-ori.json",
    openapi_filepath_v3="openapi-v3.json",
)
```

## 说明

- 没有命令行入口，需在 Python 代码中调用上述函数。
- `convert_openapi_v3` 依赖外部在线转换服务（converter.swagger.io），需要联网。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
