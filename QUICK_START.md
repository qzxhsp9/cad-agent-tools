# v0.5.1：发布并接入 AIDT

## 发布源码标签

在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_v051.ps1
```

## 安装本地命令

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_aidt.ps1
```

关闭并重新打开终端或 AIDT 本地运行器。

## AIDT 配置

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

## 验证

```powershell
where.exe cad-agent-tools
cad-agent-tools --version
cad-agent-tools doctor
```

AIDT 工具列表应出现：

```text
cad_runtime_probe
cad_inspect_model
```
