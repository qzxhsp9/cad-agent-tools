# Changelog

## 0.5.1 - 2026-08-08

- AIDT 推荐方式改为“安装一次，直接运行 `cad-agent-tools`”，不再由 AIDT 在初始化期间运行 `uvx` 在线构建。
- 新增 `cad-agent-tools doctor`，输出 PATH 命令解析、运行环境、允许目录、任务目录和日志位置。
- `cad_runtime_probe` 增加 `entry_command_resolved`、目录可读写状态和 `job_root_ready`。
- 新增启动事件日志；不向 MCP stdout 输出普通日志。
- 延迟加载文件检查模块，缩短 stdio MCP 初始化路径。
- 新增可靠的安装、升级、发布脚本和直接 AIDT 配置。

## 0.5.0 - 2026-08-08

- 建立标准 Python 包和 stdio MCP 入口。
- 默认允许读取当前工作目录和系统临时目录。
- 任务制品自动写入平台用户缓存目录。
- 新增 STEP、IGES、STL、BREP 的轻量文件元数据检查。
- 保持只读并明确标记所有未执行的几何内核检查。
