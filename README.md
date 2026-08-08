# CAD Agent Tools

`cad-agent-tools` 是一个**本地可安装、按需启动的 stdio MCP 命令包**。它不是 HTTP 服务，不监听端口，也不需要后台常驻。

## v0.5.1 的推荐接入方式

先在运行 AIDT MCP 的 Windows 用户环境中安装一次：

```powershell
uv tool install --force --from "git+https://github.com/qzxhsp9/cad-agent-tools.git@v0.5.1" cad-agent-tools
uv tool update-shell
```

关闭并重新打开终端或 AIDT 本地运行器后，验证：

```powershell
cad-agent-tools --version
cad-agent-tools doctor
```

AIDT 只需添加：

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

这里没有 Python、虚拟环境或项目目录的绝对路径。AIDT 需要时启动命令，会话结束后进程退出。

## 当前工具

- `cad_runtime_probe`：报告包版本、命令解析结果、stdio 生命周期、运行环境、允许读取目录、任务目录和启动诊断日志位置。
- `cad_inspect_model`：对 STEP/STP/BREP/IGES/STL 做只读轻量检查，包括文件存在性、大小、SHA-256、格式头信息，以及 STEP/IGES/STL 的基础文本或二进制元数据。

当前版本仍明确标记 `NOT_ASSESSED`：装配结构、拓扑数量、B-Rep 有效性、自由边、容差及修复没有执行。

## AIDT 连接排查

```powershell
where.exe cad-agent-tools
cad-agent-tools --version
cad-agent-tools doctor
```

`doctor` 会显示：

- `entry_command_resolved`：AIDT 应能解析到的安装命令；
- `allowed_roots`：允许读取的目录及其存在、读写状态；
- `job_root_ready`：任务目录是否可写；
- `log_file`：stdio 启动事件日志。

如果 Inspector 可以连接、AIDT 一直显示“连接中”，删除旧的 `uvx` MCP 配置，确认 `cad-agent-tools` 已进入 AIDT 运行进程的 `PATH`，然后重新添加直接命令配置。

## 零配置目录策略

未提供环境变量时：

- 允许读取：MCP 进程当前工作目录和操作系统临时目录；
- 任务制品：当前用户的平台缓存目录；
- 启动诊断：当前用户的平台缓存目录。

只有 AIDT 将附件物化到其他目录时，才需要可选配置：

```json
{
  "env": {
    "CAD_AGENT_ALLOWED_ROOTS": "[\"C:/AIDT/workspace\"]"
  }
}
```

## CLI

```powershell
cad-agent-tools --version
cad-agent-tools doctor
cad-agent-tools inspect-file .\sample.step
cad-agent-tools mcp
```

不带子命令时等价于 `cad-agent-tools mcp`，立即进入 stdio MCP 循环。

## 开发检查

```powershell
python -m compileall -q src
$env:PYTHONPATH = "$PWD/src"
python -m pytest -q
uv build --no-sources
```

## 安全边界

- 只读，不修改原始 CAD 文件；
- 不执行用户提供的 Shell 命令；
- 默认只允许读取工作目录和系统临时目录；
- stdout 专用于 MCP JSON-RPC；普通诊断使用 stderr 或缓存目录日志；
- 不把轻量文件扫描表述为几何内核验证。
