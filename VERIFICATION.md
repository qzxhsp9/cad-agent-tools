# Verification Report

版本：`cad-agent-tools 0.5.0`

已执行：

- `pytest`：4/4 通过；
- `compileall`：通过；
- `setuptools` sdist 构建：通过；
- 通用 Wheel `py3-none-any` 构建：通过；
- 在全新虚拟环境中使用 `--no-deps` 安装 Wheel：通过；
- `cad-agent-tools --version`：通过；
- `cad-agent-tools inspect-file sample.step`：通过；
- 结果状态为 `partial`，STEP 头信息和 SHA-256 正常，`network_service=false`；
- Wheel 元数据包含入口 `cad-agent-tools` 和运行依赖 `mcp>=2.0,<3.0`。

说明：当前执行环境的内部 Python 镜像尚未同步 MCP SDK 2.0，因此没有在本容器内完成真实 MCP Host 握手；MCP 接口依据官方 2.0 `MCPServer`、`@mcp.tool()` 和 `run(transport="stdio")` API 编写。请在可访问公开 PyPI 的 Windows/AIDT 环境用 Inspector 做最终协议回归。
