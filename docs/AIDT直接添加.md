# AIDT 直接添加

## 方案 A：PyPI（推荐）

包发布后，在 AIDT 的“工具管理 → MCP → 添加 MCP 工具”粘贴：

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

AIDT 所在运行机只需要具备 `uvx` 并可访问包仓库。无需手工创建 venv、查找 Python、复制 `server.py`、启动服务或写本地安装路径。

## 方案 B：GitHub 源码直接运行

仓库创建并推送后可以先用：

```json
{
  "mcpServers": {
    "cad-agent-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/qzxhsp9/cad-agent-tools.git@main",
        "cad-agent-tools"
      ]
    }
  }
}
```

此方案同样没有本地路径，但依赖 AIDT 运行机可以访问 GitHub。

## 私有包仓库

```json
{
  "mcpServers": {
    "cad-agent-tools": {
      "command": "uvx",
      "args": ["cad-agent-tools@0.5.0"],
      "env": {
        "UV_INDEX_URL": "https://python-packages.example.com/simple"
      }
    }
  }
}
```

凭据应由平台密钥管理或运行环境注入，不要写入共享 JSON。

## 首次测试

1. 调用 `cad_runtime_probe`；
2. 检查 `network_service=false`、`transport=stdio`；
3. 上传 STEP 文件；
4. 调用 `cad_inspect_model`；
5. 当前版本应返回 `partial`，并明确列出几何检查为 `NOT_ASSESSED`。
