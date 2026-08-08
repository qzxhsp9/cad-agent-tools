# 从 v0.5.0 迁移到 v0.5.1

v0.5.0 推荐 AIDT 直接运行 `uvx`，首次启动需要下载、构建和创建隔离环境，可能超过 AIDT 的 MCP 初始化等待时间。

v0.5.1 改为：

```text
安装一次 → PATH 中得到 cad-agent-tools → AIDT 直接启动
```

## 安装更新

```powershell
uv tool install --force --from "git+https://github.com/qzxhsp9/cad-agent-tools.git@v0.5.1" cad-agent-tools
uv tool update-shell
```

## 删除旧配置

```json
{
  "command": "uvx",
  "args": [
    "--from",
    "git+https://github.com/qzxhsp9/cad-agent-tools.git@v0.5.0",
    "cad-agent-tools"
  ]
}
```

## 添加新配置

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

## 新增诊断能力

```powershell
cad-agent-tools doctor
```

并在 `cad_runtime_probe` 中返回命令解析、目录状态和启动日志位置。
