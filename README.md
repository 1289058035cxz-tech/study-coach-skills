# 学期与复习教练 · Study Coach Skills

一组面向大学课程学习与笔记复习的中文 Codex skills：从课程资料出发，在题目中学会知识与解题方法，再用新情境检查能否独立运用。

它把“看过讲解”“提示后会做”“独立完成”“不同情境下稳定运用”分别记录，根据真实作答调整后续训练。默认中文，可按当次请求调整语言与节奏。

## 两个 skill

| Skill | 显示名称 | 适用场景 |
| --- | --- | --- |
| [`semester-study-coach`](skills/semester-study-coach/SKILL.md) | 学期学习教练 | 分析 PPT、作业、教材与课堂资料，以题带学、答疑、独立测试，并维护分学科进度和能力画像 |
| [`obsidian-review-coach`](skills/obsidian-review-coach/SKILL.md) | 笔记复习教练 | 根据已有笔记、易错点和历史表现，进行知识诊断、交错测验、批改和换情境复测 |

**建议一起安装。** 学期学习教练提供唯一的学科注册表、会话草稿和能力画像；笔记复习教练复用这些状态。后者缺少依赖时仍可基于用户提供的内容做当前对话练习，但不会声称保存了共享画像。

## 安装

需要可读取本地 skill 文件并执行 Python 的 Codex 环境，以及 Python 3.10 或更高版本。笔记整理面向本地 Obsidian Markdown 仓库；不要求安装 Obsidian 插件。

下载此仓库并解压，或克隆到本地。进入仓库根目录后运行：

```sh
python3 scripts/install.py
```

Windows 使用 `python` 替换 `python3`，并安装时区数据：

```powershell
python -m pip install -r requirements.txt
python scripts/install.py
```

安装工具默认复制到 `~/.codex/skills/`；这是本项目采用的本地安装目录。若环境使用其他 skill 目录，通过 `--dest` 指定：

```sh
python3 scripts/install.py --dest "/绝对路径/技能目录"
```

可以先加 `--dry-run` 查看计划。安装工具只复制这两个 skill，遇到任意同名目录就停止，并保留已有文件。安装后重新打开会话，确认两个 skill 已被发现。其他支持 `SKILL.md` 的工具可手动复制两个目录，具体兼容性尚未验证。

## 第一次使用

对 Codex 说：

> 使用 $semester-study-coach，帮我完成首次配置。请询问我的学期起点、总周数、时区和笔记根目录，再开始学习。

也可以把这些信息与课程名、现有笔记位置一起提供。配置未知时可先在当前对话学习，待信息齐全后再保存状态；不会套用作者的学期或示例日期。配置命令与迁移规则见 [首次配置](skills/semester-study-coach/references/setup.md)。

之后可以这样用：

```text
使用 $semester-study-coach 学习线性代数第二章。
这是我的教材章节和课堂笔记，先帮我找入手方法，讲完后留出答疑时间。
```

```text
使用 $obsidian-review-coach，复习我笔记中的矩阵与线性方程组。
这次直接测验，预计 30 分钟；题型和难度打散，提交后再批改。
```

```text
把今天已经讲过的内容、我的实际疑问和练习表现整理进这门课的 Obsidian 仓库。
```

更多使用方式见 [使用示例](examples/usage.md)。所有例子均为虚构请求，不包含真实学习记录。

## 学习记录与隐私

默认状态保存在安装后的 `semester-study-coach/state/`，包括学期配置、学科路径、会话草稿和能力画像。日常学习会在有意义的单元后保存检查点；用户明确要求不保存时，只在当前对话反馈。要求整理笔记后，才将对应内容归档到笔记仓库；首次建立课程总纲是课程规划的一部分。

发行版不含任何个人状态。`.gitignore` 排除了运行时状态、缓存和锁文件。更新或迁移前备份自己的 `state/`，不要把它上传到公共仓库。

本项目的辅助脚本只执行本地操作；实际发送给模型或连接工具的内容，仍受所用产品和账号的数据设置约束。建议只提供完成学习所需的材料。

## 能力边界

- 生成的题目、解答和诊断仍可能出错，应结合教材、课程材料和教师要求核对。
- 历史试卷不能保证本次考试范围，练习表现也不等于真实考试成绩。
- 会话接续依赖读取已保存文件，不代表后台监测或自动提醒。
- 文件锁实现覆盖 macOS/Linux 与 Windows；本次发布准备在 macOS 验证，其他平台交由仓库的 CI 验证。

## 开发与贡献

```sh
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
```

参见 [贡献说明](CONTRIBUTING.md)、[更新记录](CHANGELOG.md) 与 [发布指南](docs/PUBLISHING.md)。仓库内所有代码与教学流程文本采用 [MIT 许可证](LICENSE)；用户自行提供的教材、试卷和笔记不因使用本项目而改变授权。

项目名称：`study-coach-skills`。本项目是社区学习工作流，与 OpenAI 或 Obsidian 无隶属关系。
