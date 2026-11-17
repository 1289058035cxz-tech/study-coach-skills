# 更新已有 GitHub 仓库与发布版本

当前已发布版本为 **v0.2.0**；笔记复习教练此次调整处于“未发布”状态，VERSION 暂不变。下列 v0.2.0 Release 步骤保留为历史版本操作参考。旧版更新记录为 v0.1.0。本次更新已有仓库，无需新建仓库或重新执行 `git init`。版本号保存在根目录 `VERSION`，学期学习教练的版本同时记录在其 `SKILL.md` 的 `metadata.version`；每次发布同步维护版本与 CHANGELOG。

## 本次复习教练增量更新（未发布）

更新包只含新增/修改文件，解压后把其中内容按原路径合并到现有仓库根目录；网页上传时拖入该层的文件与目录，不上传 ZIP 或外层包装目录。不要求本次包包含未修改的 VERSION、`.gitignore` 或 CI；保留仓库中原有文件。

本次 skill 文件为 `skills/obsidian-review-coach/SKILL.md`、`agents/openai.yaml`、`references/assessment.md`、`references/integration.md`（后三项相对该 skill 目录）；其余为同步的说明与验证记录。提交标题可用 `Improve review question groups and separate coach records`。审阅 diff、运行下列检查，再由仓库所有者提交并上传。本次准备不创建标签或发布新 Release。

本地已安装用户先备份对应四个文件，再按 skill 内相对路径更新 `obsidian-review-coach`；完整保留 `semester-study-coach/state/` 和其他个人文件。无需重新初始化、安装或迁移画像。规则更新不自动重整真实笔记，后续实际整理按新分工执行。

## 上传前检查

在仓库根目录运行：

```sh
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
```

Windows 将 `python3` 换成 `python`。测试只使用临时目录与虚构数据，不初始化真实课程状态。发行文件中保留 `.gitignore` 和 `.github/workflows/checks.yml`；它们用于排除运行状态与执行 CI，不能因文件名以点开头而漏传。

## 方法一：通过 GitHub 网页更新

1. 解压完整仓库包或增量文件包，找到包含 `README.md`、`CHANGELOG.md`、`VERSION`、`skills/` 的那一层。增量文件包只含本次新增/修改文件，必须合并进已有仓库，不能单独安装。
2. 打开已有仓库根页面，点击 **Add file → Upload files**。
3. 将该层里面的文件和文件夹拖入上传区，保持原路径；不要把外层包装目录或 ZIP 本身当源码上传。例如学期学习教练入口必须仍为 `skills/semester-study-coach/SKILL.md`。
4. 在上传列表确认同名文件按原路径更新；`.gitignore` 与 `.github/workflows/checks.yml` 必须在列表中。macOS Finder 可用 `Command + Shift + .` 显示隐藏项。若拖入后仍遗漏，使用 **Add file → Create new file** 分别填写这两个完整文件名并粘贴对应文件内容。
5. 提交标题使用 `Release v0.2.0: improve semester study workflow`。可提交到新的 `release/v0.2.0` 分支，再通过 Pull Request 合并；若界面允许且你选择直接提交到 `main`，同样先审阅改动路径。分支保护要求 PR 时按界面执行。
6. 在 **Code** 检查目录和版本，在 **Actions** 检查本次提交对应的 `Check release` 运行；若走 PR，则在通过检查后合并，并确认 `main` 对应检查通过。

`.gitignore` 不会自动取消已被 Git 跟踪的私人文件；本次发布包不含任何真实 `state/`。上传只使用准备好的公共文件，不复制个人 skill 安装目录。

## 方法二：通过 Git 或 GitHub Desktop 更新

克隆已有仓库，把增量包内容按原路径合并进去，查看 Changes/diff，再提交与推送。GitHub Desktop 使用 **Clone repository → Changes → Commit → Push origin**；不要选择创建第二个仓库。终端示例：

```sh
git clone https://github.com/1289058035cxz-tech/study-coach-skills.git
cd study-coach-skills
# 在这里合并增量包，保留 .git 和既有未更新文件
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
git diff --check
git status --short
git add README.md CHANGELOG.md VERSION .gitignore .github docs skills/semester-study-coach
git diff --cached --stat
git commit -m "Release v0.2.0: improve semester study workflow"
git push origin main
```

这些命令供仓库所有者审阅后执行，本文件不代表已经提交或推送。已有本地仓库时进入原目录，先处理自己的未提交改动并同步，不覆盖本地工作。

## 创建 v0.2.0 Release

源码已经进入 `main` 且该提交检查通过后：

1. 打开仓库的 **Releases → Draft a new release**。
2. 在标签处输入并创建 **v0.2.0**，Target 选择包含更新的 `main` 提交。不要把新标签指向更新前的提交。
3. 标题填写 **v0.2.0 · 术语覆盖、规范答案与分段讲练**。
4. 描述复制 [本次 Release 文案](RELEASE-v0.2.0.md)。文案中的本地验证不等于 GitHub Actions 已经运行。
5. 可附上公开完整源码包作为附件；不要附增量包冒充完整安装包。GitHub 也会为标签提供源码下载。
6. 审阅后点击 **Publish release**；还没准备发布则保存草稿。若设置了不可变 Release，先完成附件与审阅再发布。

仓库许可沿用现有 MIT，保留 [LICENSE](../LICENSE)。不要重复创建旧版标签；如果之前只上传了源码、没有创建 v0.1.0 Release，可以直接为本次新提交发布 v0.2.0，无需补造历史发布记录。

## 已安装用户更新 skill

先备份本地已安装目录。将新版 `skills/semester-study-coach/` 的 `SKILL.md`、`agents/openai.yaml`、`references/teaching-workflow.md`、`references/memory-and-notes.md` 合并至本地同名位置；公开版首次配置文档和脚本沿用已有公开实现。本次不要求重新初始化或迁移画像，完整保留个人 `state/`。另一个 skill 无需更新。安装工具仍拒绝覆盖已有安装，不能通过删除状态来绕过。

发布包中不含个人状态；不要从更新包反向删除本地私有文件。重新打开会话并确认入口版本为 0.2.0，再使用实际课程验证新节奏。

## 官方操作参考

- [上传文件](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [管理 Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
