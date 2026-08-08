# 发布到 PyPI

## 本地检查

```powershell
python -m compileall -q src
$env:PYTHONPATH = "$PWD/src"
python -m pytest -q
uv build --no-sources
```

## 发布

```powershell
$env:UV_PUBLISH_TOKEN = "pypi-..."
uv publish
Remove-Item Env:UV_PUBLISH_TOKEN
```

更适合长期项目的方式是配置 PyPI Trusted Publisher，让 GitHub Actions 使用 OIDC 发布。

## 安装与验证

```powershell
uv tool install --force cad-agent-tools==0.5.1
uv tool update-shell
cad-agent-tools --version
cad-agent-tools doctor
```

AIDT 仍使用直接命令配置：

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
