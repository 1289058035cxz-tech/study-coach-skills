#!/usr/bin/env python3
"""Install both public skills locally, refusing to overwrite existing installs."""
import argparse
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('semester-study-coach', 'obsidian-review-coach')


def install(destination, dry_run=False):
    destination = destination.expanduser().resolve()
    for name in SKILLS:
        if not (ROOT / 'skills' / name / 'SKILL.md').is_file():
            raise ValueError(f'缺少发行文件：{name}/SKILL.md')
        target = destination / name
        if target.exists() or target.is_symlink():
            raise ValueError(f'已有安装，未覆盖：{target}。请先备份状态，再人工合并更新。')
    if dry_run:
        for name in SKILLS:
            print(f'计划安装：{destination / name}')
        return
    destination.mkdir(parents=True, exist_ok=True)
    installed = []
    try:
        with tempfile.TemporaryDirectory(prefix='.study-coach-install-', dir=destination) as stage:
            stage = Path(stage)
            for name in SKILLS:
                shutil.copytree(
                    ROOT / 'skills' / name, stage / name,
                    ignore=shutil.ignore_patterns('state', '__pycache__', '*.pyc', '*.lock'),
                )
            for name in SKILLS:
                target = destination / name
                if target.exists() or target.is_symlink():
                    raise ValueError(f'安装期间出现同名目录，已停止：{target}')
                (stage / name).rename(target)
                installed.append(target)
    except Exception:
        # Roll back only directories this invocation actually installed.
        for target in installed:
            shutil.rmtree(target)
        raise
    for target in installed:
        print(f'已安装：{target}')
    print('安装完成。重新打开会话并确认两个 skill 已被发现。')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path.home() / '.codex' / 'skills')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        install(args.dest, args.dry_run)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'错误：{exc}\n')


if __name__ == '__main__':
    main()
