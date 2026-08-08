# 发布到 PyPI

## 1. 检查名称

正式上传前再次确认 `cad-agent-tools` 尚未被占用。包名以首次成功上传为准。

## 2. 本地检查

```powershell
uv sync --dev
uv run pytest
uv build --no-sources
```

## 3. 先发 TestPyPI（可选）

```powershell
$env:UV_PUBLISH_TOKEN = "pypi-..."
uv publish --publish-url https://test.pypi.org/legacy/
```

## 4. 发布正式 PyPI

```powershell
$env:UV_PUBLISH_TOKEN = "pypi-..."
uv publish
Remove-Item Env:UV_PUBLISH_TOKEN
```

更适合长期项目的方式是配置 PyPI Trusted Publisher，让 GitHub Actions 使用 OIDC 发布，不在仓库中保存长期 Token。

## 5. 发布后验证

```powershell
uvx cad-agent-tools@0.5.0 --version
```

然后把 `examples/aidt.pypi.json` 添加到 AIDT。
