# GitHub 发布指南

## 名称与简介

- 仓库名称：`study-coach-skills`
- 中文名称：学期与复习教练
- GitHub 简介：`中文 Codex 学习与复习 skills：以题带学、新情境混合测验、证据驱动的能力画像与 Obsidian 笔记整理。`
- Topics：`codex`、`agent-skills`、`study`、`learning`、`obsidian`、`chinese`
- 首版标签：`v0.1.0`
- Release 标题：`v0.1.0 · 学期与复习教练`
- 许可证：MIT，版权署名使用项目贡献者，不要求公开真实姓名。

名称是项目选定名称，未声称已经查询或保留 GitHub 仓库名。仓库名位于你自己的账号或组织下；如已有同名仓库，可改为 `study-review-coach-skills`，两个 skill 的英文名称无需改动。

## 发布前检查

在仓库根目录运行：

```sh
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
```

首次发布不运行真实课程训练、不初始化自己的 `state/`。检查脚本会拒绝个人状态、缓存与运行产物；它不是通用秘密扫描工具，新增文件仍需自行审阅。

## 建立仓库并上传

1. 在 GitHub 新建名为 `study-coach-skills` 的 Public 仓库。仓库简介使用上面的文案；README、许可证和忽略文件已包含，不必让 GitHub 重复生成。
2. 将本项目整个目录作为仓库根目录。推荐使用 Git 或 GitHub Desktop 上传，确保 `.gitignore` 和 `.github/workflows/checks.yml` 也被包含。
3. 首次提交信息可用 `Prepare initial public release`。不要把上层目录、原始私人 skills 或发布压缩包一起提交。
4. 推送后在 Actions 查看 Linux、macOS、Windows 的实际结果；有失败则修复后再发布。自动测试未验证模型真实教学质量，也不代表所有宿主工具已兼容。

若熟悉 Git，可以在本目录内执行以下命令；`你的用户名` 应替换为实际账号。远端仓库须已创建且为空：

```sh
git init -b main
git add .
git status --short
git commit -m "Prepare initial public release"
git remote add origin "https://github.com/你的用户名/study-coach-skills.git"
git push -u origin main
```

## 发布首版

在仓库 Releases 中创建 `v0.1.0`，目标选择已检查通过的 `main` 提交。可复制以下说明：

> 学期与复习教练的首个公开版本，包含 `semester-study-coach` 与 `obsidian-review-coach`。支持课程资料分析、以题带学、答疑、新情境混合测验，以及共享的分学科能力画像和按需 Obsidian 整理。发行版不含个人学习状态，首次使用会引导配置。安装方法见 README。

实际跨平台结果以本次 Actions 为准；不要把未运行的平台写成已验证。GitHub 会提供源码下载，不必上传私人配置或额外运行产物。

## 发布后的维护

从公共仓库维护方法文件，把真实学习状态留在本地。修复后更新 `CHANGELOG.md`；提供复现例子时使用虚构数据。安装工具会拒绝覆盖已有安装，更新时先备份 `state/`，再审阅并合并新方法文件。
