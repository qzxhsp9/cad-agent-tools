# Verification Report

版本：`cad-agent-tools 0.5.1`

已执行：

- `pytest`：6/6 通过；
- `compileall`：通过；
- 通用 Wheel `py3-none-any` 构建：通过；
- sdist 构建：通过；
- 在全新虚拟环境中使用 `--no-deps` 安装 Wheel：通过；
- `cad-agent-tools --version`：输出 `0.5.1`；
- `cad-agent-tools doctor --compact`：返回结构化 JSON，`network_service=false`、`transport=stdio`、`job_root_ready=true`；
- 启动事件 JSONL 写入测试：通过；
- Wheel 元数据包含入口 `cad-agent-tools` 和运行依赖 `mcp>=2.0,<3.0`。

说明：当前构建容器的内部 Python 镜像没有同步 `mcp` 包，因此未在本容器内重新执行真实 MCP Host 握手。v0.5.1 保留了已在 MCP Inspector 中验证成功的 `MCPServer`、两个工具装饰器和 stdio 入口；本次重点修改为直接安装命令、启动诊断和延迟加载。
