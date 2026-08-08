# 从 v0.4 迁移

直接升级到当前 v0.5.1：

1. 删除旧配置中的 Python、venv、`server.py`、固定数据目录和 Mock 后端路径；
2. 安装命令包：

```powershell
uv tool install --force --from "git+https://github.com/qzxhsp9/cad-agent-tools.git@v0.5.1" cad-agent-tools
uv tool update-shell
```

3. AIDT 使用：

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
