# 更新已有 GitHub 仓库与发布版本

当前源码版本为 **v0.2.1**，本次更新笔记复习教练。仓库版本以根目录 `VERSION` 为准，各 skill 的 `metadata.version` 表示各自组件版本：复习教练为 0.2.1，课程带学教练保留 0.2.0。本次无需新建仓库或重新初始化学习状态。

## 上传本次版本补充文件

前一批复习规则已在 main 提交 `edeb395` 中。这次增量包以该提交为基准，仅补齐版本号、更新记录和发布文案；须合并到原仓库，不能单独安装。

1. 解压 `study-coach-skills-v0.2.1-release-update.zip`。
2. 在原仓库根目录选择 **Add file → Upload files**。
3. 上传解压后这一层中的 `VERSION`、`README.md`、`CHANGELOG.md`、`docs/`、`skills/`，保持原路径，不上传 ZIP 或外层包装目录。
4. 审阅修改列表，提交标题可用 `Release v0.2.1: improve review workflow and notes`。
5. 提交后查看 **Actions** 中对应提交的检查结果；若使用 PR，在检查通过后合并，再为包含这次更新的提交创建 Release。

已有本地仓库也可合并补充文件后审阅 diff，再提交与推送。若仓库已有后续编辑，先合并这些编辑，不用旧副本覆盖。未改动的 `.gitignore`、CI、辅助脚本及其他文件保留原样。

## 上传前检查

在合并后的仓库根目录运行：

```sh
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
git diff --check
```

Windows 将 `python3` 换成 `python`。测试使用临时目录及虚构数据，不初始化真实课程状态。增量包通过对照基准检查，但 GitHub Actions 的实际结果须在上传后查看。

## 创建 v0.2.1 Release

1. 打开 **Releases → Draft a new release**。
2. 标签填写并创建 **v0.2.1**，Target 选择包含这次版本补充的 main 提交。
3. 标题填写 **v0.2.1 · 小组复习、规范答案与笔记分离**。
4. 描述复制 [v0.2.1 Release 文案](RELEASE-v0.2.1.md)。
5. 审阅后点击 **Publish release**。GitHub 会为标签提供源码下载；本次增量包只用于更新，不能作为完整安装包附件。

更新源码与创建 GitHub Release 是两个操作。版本文件和说明已按本次正式版本准备；准备文件不代表已经代替仓库所有者提交、打标签或点击发布。

## 已安装用户更新

先备份本地相关文件。前一批更新涉及 `obsidian-review-coach` 的 `SKILL.md`、`agents/openai.yaml`、`references/assessment.md` 和 `references/integration.md`；此次版本补充仅再次更新该组件 `SKILL.md` 的版本信息。已应用前一批更新时，只需同步新版入口。

完整保留 `semester-study-coach/state/` 和其他个人文件，无需初始化或迁移画像。重新打开会话后读取新版 skill；后续实际整理按知识笔记与独立教练索引的分工执行，更新文件本身不自动迁移旧笔记。

仓库许可沿用 [MIT](../LICENSE)。上版说明保留在 [v0.2.0 Release 文案](RELEASE-v0.2.0.md)，不要将上版标签用于本次新提交。
