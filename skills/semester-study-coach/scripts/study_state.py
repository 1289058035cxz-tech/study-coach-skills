#!/usr/bin/env python3
"""Local-only semester status and safe subject routing. Standard library only."""
import argparse
from contextlib import contextmanager
from datetime import date, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if os.name == 'nt':
    import msvcrt
else:
    import fcntl

DEFAULT_STATE = Path(__file__).resolve().parents[1] / 'state'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def state_lock(state):
    # Advisory lock: all cooperating writers use state/.write.lock.
    state.mkdir(parents=True, exist_ok=True)
    with (state / '.write.lock').open('a+b') as stream:
        if os.name == 'nt':
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b'\0')
                stream.flush()
            deadline = time.monotonic() + 30
            while True:
                stream.seek(0)
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise ValueError('等待状态写入锁超时，请稍后重试。')
                    time.sleep(0.05)
        else:
            fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def checked_zone(name):
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(
            '无法读取时区；请确认 IANA 时区名称，例如 Asia/Shanghai。'
            '若系统缺少时区数据，请运行 python -m pip install tzdata。'
        ) from exc


def init_state(state, args):
    start = date.fromisoformat(args.week1_start)
    if args.total_weeks < 1:
        raise ValueError('total_weeks 必须是正整数。')
    zone = checked_zone(args.timezone)
    root = absolute_path(args.vault_root)
    end = date.fromisoformat(args.term_end) if args.term_end else None
    if end and end < start:
        raise ValueError('学期末不能早于学期起点。')
    config = {
        'schema_version': 1,
        'week1_start': start.isoformat(), 'total_weeks': args.total_weeks,
        'timezone': args.timezone,
        'confirmed_term_end': end.isoformat() if end else None,
        'default_vault_root': str(root),
        'basis': args.source or '用户首次配置；校历准确性以用户提供信息为准',
        'configured_on': datetime.now(zone).date().isoformat(),
    }
    with state_lock(state):
        # A partial or existing setup must be inspected, never silently reset.
        if (state / 'semester.json').exists() or (state / 'subjects.json').exists():
            raise ValueError('已有全部或部分配置，拒绝覆盖；请读取现有配置后修复，或使用新的 --state-dir。')
        atomic_json(state / 'semester.json', config)
        atomic_json(state / 'subjects.json', {'schema_version': 1, 'subjects': []})
    return {'result': 'initialized', 'state_dir': str(state),
            'note': '仅初始化学期配置与空注册表；未创建课程、笔记仓库或学习证据。'}


def local_today(config):
    return datetime.now(checked_zone(config['timezone'])).date()


def find_subject(registry, name):
    hits = [s for s in registry['subjects']
            if name == s['name'] or name == s['id'] or name in s.get('aliases', [])]
    if len(hits) > 1:
        raise ValueError('学科存在多个候选，先修复注册表或确认学科。')
    return hits[0] if hits else None


def compute_status(config, today, subject=None):
    start = date.fromisoformat(config['week1_start'])
    weeks = config['total_weeks']
    if not isinstance(weeks, int) or isinstance(weeks, bool) or weeks < 1:
        raise ValueError('total_weeks 必须是正整数。')
    elapsed = (today - start).days
    week = elapsed // 7 + 1
    estimated_end = start + timedelta(days=weeks * 7 - 1)
    confirmed = config.get('confirmed_term_end')
    exam = subject.get('exam_date') if subject else None
    target = date.fromisoformat(exam or confirmed) if (exam or confirmed) else estimated_end
    target_kind = '学科考试日' if exam else ('已确认学期末' if confirmed else '预计学期末（非考试日期）')
    phase = '学期开始前' if elapsed < 0 else ('已超过估计终点，需核实学期状态' if today > estimated_end else '学期内')
    result = {
        'today': today.isoformat(), 'timezone': config['timezone'],
        'week': week if elapsed >= 0 else None, 'total_weeks': weeks,
        'week_basis': config.get('basis'), 'phase': phase,
        'final_week_start': (start + timedelta(weeks=weeks-1)).isoformat(),
        'estimated_term_end': estimated_end.isoformat(),
        'target_date': target.isoformat(), 'target_kind': target_kind,
        'days_until_target': (target-today).days,
        'time_elapsed_percent': round(max(0, min(1, elapsed/(weeks*7))) * 100, 1),
        'progress_warning': '时间已过比例不是课程覆盖率或知识掌握率；负倒计时表示日期已过。',
    }
    if subject:
        result['subject'] = subject['name']
        result['vault_path'] = subject['vault_path']
        result['notes_root'] = subject['notes_root']
        result['vault_exists'] = Path(subject['vault_path']).is_dir()
        result['notes_root_exists'] = Path(subject['notes_root']).is_dir()
        result['exam_date_source'] = subject.get('exam_date_source')
    return result


def safe_name(name):
    if (not name or name != name.strip() or name in ('.', '..')
            or any(c in '/\\<>:"|?*' or ord(c) < 32 for c in name)
            or name.startswith('.') or name.endswith('.')
            or len(name.encode('utf-8')) > 200):
        raise ValueError('学科名称不能安全用于仓库文件夹；请确认可用名称。')
    return name


def absolute_path(raw):
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise ValueError('请使用绝对路径。')
    return path.resolve()


def empty_profile(subject):
    return {'subject_id': subject['id'], 'subject_name': subject['name'],
            'updated_on': None, 'preferences': [],
            'coverage': {'last_session': None, 'classroom_boundary': None, 'taught_topics': []},
            'topics': [], 'next_review': []}


def register_subject(state, config, args):
    name = safe_name(args.name)
    # Serialize routing changes, including profile initialization.
    with state_lock(state):
        registry = load(state / 'subjects.json')
        existing = find_subject(registry, name)
        if args.command == 'create-subject':
            if existing:
                if not Path(existing['vault_path']).is_dir() or not Path(existing['notes_root']).is_dir():
                    raise ValueError('已登记路径失效，请修复路径，不创建第二个仓库。')
                return {'result': 'already_registered', 'subject': existing}
            root = absolute_path(config['default_vault_root'])
            vault = root / name
            # Refuse existing directories, files, and symlinks (including broken ones).
            if vault.exists() or vault.is_symlink():
                raise ValueError('同名路径已存在；先核实归属，再使用 register。')
            root.mkdir(parents=True, exist_ok=True)
            vault.mkdir(exist_ok=False)
            (vault / '.obsidian').mkdir()
            notes = vault
            source = '首次学习时创建的学科仓库'
        else:
            vault = absolute_path(args.vault)
            notes = absolute_path(args.notes_root) if args.notes_root else vault
            if not vault.is_dir() or not notes.is_dir():
                raise ValueError('仓库或笔记目录不存在；register 不创建目录。')
            if not notes.is_relative_to(vault):
                raise ValueError('notes_root 必须位于 vault_path 内，且不能通过符号链接逃逸。')
            if existing and (existing['vault_path'] != str(vault) or existing['notes_root'] != str(notes)) and not args.replace:
                raise ValueError('该科已有不同路径；确认迁移意图后才可使用 --replace。')
            source = args.source or '已核实的现有学科仓库'
        today = local_today(config).isoformat()
        subject = dict(existing) if existing else {
            'id': 'subject-' + hashlib.sha256(name.encode('utf-8')).hexdigest()[:12],
            'name': name, 'aliases': [], 'exam_date': None,
            'exam_date_source': None, 'registered_on': today,
        }
        subject.update(vault_path=str(vault), notes_root=str(notes), source=source)
        profile_path = state / 'subjects' / subject['id'] / 'profile.json'
        if not profile_path.exists():
            atomic_json(profile_path, empty_profile(subject))
        if existing:
            registry['subjects'][registry['subjects'].index(existing)] = subject
        else:
            registry['subjects'].append(subject)
        atomic_json(state / 'subjects.json', registry)
        return {'result': 'registered', 'subject': subject,
                'profile_path': str(profile_path),
                'note': '仅登记路径与初始画像；未生成知识笔记，也未修改 Obsidian 应用注册配置。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, default=DEFAULT_STATE)
    commands = parser.add_subparsers(dest='command', required=True)
    initialize = commands.add_parser('init', help='首次配置；不覆盖已有状态')
    initialize.add_argument('--week1-start', required=True, help='第 1 周起点 YYYY-MM-DD')
    initialize.add_argument('--total-weeks', type=int, required=True)
    initialize.add_argument('--timezone', required=True, help='IANA 时区，如 Asia/Shanghai')
    initialize.add_argument('--vault-root', required=True, help='默认笔记根目录的绝对路径')
    initialize.add_argument('--term-end', help='已确认的学期末 YYYY-MM-DD；未知则不传')
    initialize.add_argument('--source', help='校历来源或推定依据')
    status = commands.add_parser('status')
    status.add_argument('--subject')
    status.add_argument('--today', help='历史查询/测试日期 YYYY-MM-DD；正常使用不传')
    register = commands.add_parser('register')
    register.add_argument('--name', required=True)
    register.add_argument('--vault', required=True)
    register.add_argument('--notes-root')
    register.add_argument('--replace', action='store_true')
    register.add_argument('--source')
    create = commands.add_parser('create-subject')
    create.add_argument('--name', required=True)
    args = parser.parse_args()
    try:
        state = args.state_dir.expanduser().resolve()
        if args.command == 'init':
            print(json.dumps(init_state(state, args), ensure_ascii=False, indent=2))
            return
        if not (state / 'semester.json').is_file() or not (state / 'subjects.json').is_file():
            raise ValueError('尚未完成首次配置，请先执行 init；参数见 references/setup.md。')
        config = load(state / 'semester.json')
        if args.command == 'status':
            registry = load(state / 'subjects.json')
            subject = find_subject(registry, args.subject) if args.subject else None
            if args.subject and subject is None:
                raise ValueError('该学科尚未登记，请先定位现有仓库或创建新仓库。')
            today = date.fromisoformat(args.today) if args.today else local_today(config)
            result = compute_status(config, today, subject)
        else:
            result = register_subject(state, config, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'错误：{exc}\n')


if __name__ == '__main__':
    main()
