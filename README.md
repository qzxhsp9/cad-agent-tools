# CAD Agent Tools

`cad-agent-tools` 是一个可发布到 PyPI 或公司私有 Python 包仓库的**本地 stdio MCP 命令包**。

AIDT 通过 `uvx` 按需获取并启动它：

```json
{
  "mcpServers": {
    "cad-agent-tools": {
      "command": "uvx",
      "args": ["cad-agent-tools@0.5.0"]
    }
  }
}
```

没有 Python 绝对路径，没有虚拟环境路径，没有固定 CAD 目录，没有 HTTP 地址或端口。进程由 MCP Host 在需要时启动，会话结束后退出。

## 当前能力

- `cad_runtime_probe`：报告包版本、stdio 生命周期、运行环境、自动工作目录和缓存目录。
- `cad_inspect_model`：对 STEP/STP/BREP/IGES/STL 做只读轻量检查：文件存在性、大小、SHA-256、格式头信息，以及 STEP/IGES/STL 的基础文本或二进制元数据。
- 明确标记 `NOT_ASSESSED`：装配结构、拓扑数量、B-Rep 有效性、自由边、容差及修复目前没有执行。

## 零配置目录策略

未提供环境变量时：

- 允许读取：MCP 进程当前工作目录和操作系统临时目录；
- 任务制品：由标准库规则放入当前用户的平台缓存目录；
- 不依赖 `D:/CADCases` 或 `D:/CADAgentJobs`。

只有当 AIDT 把附件放在其他目录时，才需要可选配置：

```json
{
  "env": {
    "CAD_AGENT_ALLOWED_ROOTS": "[\"C:/AIDT/workspace\",\"C:/Users/me/AppData/Local/Temp\"]"
  }
}
```

## 本地开发

```powershell
uv sync --dev
uv run pytest
uv run cad-agent-tools --version
uv run cad-agent-tools inspect-file .\sample.step
```

## 构建与发布

```powershell
uv build --no-sources
uv publish
```

发布后即可在 AIDT 中使用上方 `uvx` 配置。发布前可用本地 Wheel 测试，但本地测试天然需要一个 Wheel 路径；正式使用不需要。

## 安全边界

- 只读，不修改原始 CAD 文件；
- 不执行用户提供的 Shell 命令；
- 默认仅允许读取工作目录和系统临时目录；
- stdout 专用于 MCP JSON-RPC，普通日志写入 stderr；
- 不把轻量文件扫描错误表述为几何内核验证。
