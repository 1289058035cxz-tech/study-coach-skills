# 首次配置与迁移

公开发行版不含 `state/`，不预设校历、学科、笔记路径或能力结论。

## 首次使用

先询问尚未提供的必要信息，可以一次问清：第 1 周从哪一天开始、总周数、时区、默认笔记根目录。用户有现成 Obsidian 仓库时优先复用；默认笔记根目录只用于之后明确需要新建仓库的情况，不会在初始化时创建。

不知道精确校历时可以记录用户认可的估计及其依据。关键字段尚不能确定时，继续当前对话的学习，不编造值，也不声称已持久化。用户要求不保存时，不运行初始化或其他写入。

确认参数后运行（替换大写占位参数，不照搬示例日期）：

```sh
python3 "SKILL_ROOT/scripts/study_state.py" init --week1-start "YYYY-MM-DD" --total-weeks N --timezone "IANA_TIMEZONE" --vault-root "ABSOLUTE_NOTES_ROOT"
python3 "SKILL_ROOT/scripts/study_state.py" status
```

Windows 可以使用 `python` 替换 `python3`，路径使用当地绝对路径。时区例如 `Asia/Shanghai` 或 `America/New_York`，以用户实际时区为准。若缺少时区数据，安装仓库根目录 `requirements.txt` 中的 `tzdata`，或运行 `python -m pip install tzdata`。

已确认学期末可附加 `--term-end "YYYY-MM-DD"`，来源可附加 `--source "用户提供的校历依据"`。学科考试日保存在学科注册项中，不通过学期末参数冒充。

`init` 只生成 `state/semester.json`、空的 `state/subjects.json` 与写入锁；不创建学科或画像。任何一份配置已经存在就拒绝覆盖，包括上次仅写入一部分的情况。此时先检查已有文件，保留内容并修复，不通过删除状态来重试。

## 学科登记

现有仓库用 `register`，已存在的课程子目录可通过 `--notes-root` 指定；只有确认没有对应仓库时才用 `create-subject`。具体命令见 [memory-and-notes.md](memory-and-notes.md)。

初始学科画像为未知。仓库目录、总纲或教材存在都不能作为已掌握证据。

## 状态与备份

状态仍放在安装后的 `semester-study-coach/state/`，由两个 skill 共用。手动写入时从该 skill 的 `scripts/study_state.py` 导入 `state_lock` 与 `atomic_json`，锁内读取、合并、原子替换。保存测验进度时先写会话，再更新引用这些证据的画像。

正常更新 skill 只替换方法文件，保留完整 `state/`。本仓库的安装工具遇到已安装目录会停止；迁移前先备份旧目录，再人工合并，不把旧状态提交到公共仓库。新学期应存档旧配置，再根据用户要求调整，保留有效的历史能力证据。

初始化工具支持 `--state-dir`，该参数必须放在子命令前：

```sh
python3 "SKILL_ROOT/scripts/study_state.py" --state-dir "ABSOLUTE_STATE_DIR" status
```

这个选项供测试或显式迁移使用。正常调用两个 skill 时保持默认位置，否则还需同步修改两者的状态定位约定。
