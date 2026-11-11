#!/usr/bin/env python3
"""Check public packaging and local Markdown links without third-party modules."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('semester-study-coach', 'obsidian-review-coach')


def check(root=ROOT):
    errors = []
    for name in ('README.md', 'LICENSE', '.gitignore', 'CHANGELOG.md',
                 'requirements.txt', '.github/workflows/checks.yml'):
        if not (root / name).is_file():
            errors.append(f'缺少文件：{name}')
    ignored = {'.git', '.venv'}
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if any(part in ignored for part in rel.parts):
            continue
        if 'state' in rel.parts or '__pycache__' in rel.parts or path.suffix in ('.pyc', '.lock'):
            errors.append(f'不应发布运行数据：{rel}')
        if not path.is_file() or path.suffix not in ('.md', '.yaml', '.yml', '.json', '.py', '.txt'):
            continue
        text = path.read_text(encoding='utf-8')
        # Deliberately scoped: detect concrete home paths, not generic documentation paths.
        if re.search(r'/Users/(?!\*|<)[A-Za-z0-9_.-]+/|[A-Za-z]:[\\/]Users[\\/][A-Za-z0-9_.-]+[\\/]', text):
            errors.append(f'发现个人主目录路径：{rel}')
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
                target = target.strip().strip('<>')
                if not target or target.startswith(('#', 'https://', 'http://', 'mailto:')):
                    continue
                local = unquote(target.split('#', 1)[0])
                if not (path.parent / local).exists():
                    errors.append(f'无效本地链接：{rel} → {target}')
    for name in SKILLS:
        entry = root / 'skills' / name / 'SKILL.md'
        if not entry.is_file():
            errors.append(f'缺少 skill 入口：{name}')
            continue
        text = entry.read_text(encoding='utf-8')
        front = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if not front:
            errors.append(f'入口缺少 YAML frontmatter：{name}')
            continue
        if not re.search(rf'^name: {re.escape(name)}$', front[1], re.M):
            errors.append(f'入口名称与目录不匹配：{name}')
        if not re.search(r'^description: \S', front[1], re.M):
            errors.append(f'入口缺少描述：{name}')
        ui = root / 'skills' / name / 'agents' / 'openai.yaml'
        if not ui.is_file() or f'${name}' not in ui.read_text(encoding='utf-8'):
            errors.append(f'界面元数据缺失或未引用自身 skill：{name}')
    return errors


if __name__ == '__main__':
    problems = check()
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        sys.exit(1)
    print('发布检查通过：两个 skill 的结构、内部链接及已知个人数据检查均通过。')
