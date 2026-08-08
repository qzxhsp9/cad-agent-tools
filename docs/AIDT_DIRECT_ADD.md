# AIDT 直接添加：v0.5.1

## 1. 安装本地命令包

在实际运行 AIDT MCP 子进程的 Windows 用户环境中执行：

```powershell
uv tool install --force --from "git+https://github.com/qzxhsp9/cad-agent-tools.git@v0.5.1" cad-agent-tools
uv tool update-shell
```

然后关闭并重新打开终端或 AIDT 本地运行器。

验证：

```powershell
where.exe cad-agent-tools
cad-agent-tools --version
cad-agent-tools doctor
```

## 2. AIDT 配置

删除旧的 `uvx` 配置，添加：

```json
{
  "mcpServers": {
    "cad-agent-tools": {
      "command": "cad-agent-tools",
      "args": []
    }
  }
}
```

此配置不会在线安装依赖，因此 MCP 初始化速度更稳定。

## 3. 验收

工具列表应出现：

```text
cad_runtime_probe
cad_inspect_model
```

先调用 `cad_runtime_probe`，检查：

```text
package.version = 0.5.1
package.entry_command_resolved != null
package.transport = stdio
package.network_service = false
configuration.job_root_ready = true
```

## 4. 连接失败时

依次执行：

```powershell
where.exe cad-agent-tools
cad-agent-tools --version
cad-agent-tools doctor
```

然后查看 `doctor` 返回的 `configuration.log_file`。如果命令在新终端可见、AIDT 仍不可见，说明 AIDT 运行进程还继承着旧 `PATH`，需要重启对应本地运行器或宿主进程后重新添加 MCP。
