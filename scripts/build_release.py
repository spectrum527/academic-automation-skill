#!/usr/bin/env python3
"""Build reproducible, source-only platform assets without credentials or caches."""
import argparse
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ('SKILL.md', 'README.md', 'README.zh-CN.md', 'LICENSE', 'AGENTS.md',
              'VERIFICATION.md', 'RELEASE_NOTES.md', 'LEGACY.md', 'package.json', 'package-lock.json', 'requirements-pdf.txt',
              'assets/logo.png', 'assets/readme-banner.png')


def source_files(root, target):
    files = [root / name for name in ROOT_FILES]
    for folder, suffixes in [('src/academic_automation', {'.py'}),
                             ('scripts', {'.py', '.js', '.sh'}),
                             ('references', {'.md'}), ('tests', {'.py', '.html', '.js'})]:
        for path in (root / folder).rglob('*'):
            if '__pycache__' in path.parts or not path.is_file() or path.suffix not in suffixes:
                continue
            if target == 'windows' and path.suffix == '.sh':
                continue
            files.append(path)
    for path in sorted(set(files)):
        if not path.is_file() or path.is_symlink() or root not in path.resolve().parents:
            raise ValueError('Missing or unsafe package source: ' + str(path))
        yield path.relative_to(root).as_posix(), path.read_bytes()


def add(archive, name, data, executable=False, skill_name='academic-automation'):
    info = zipfile.ZipInfo(skill_name + '/' + name, (2026, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def legacy_asset(root, output, ref):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args])
    commit = git('rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    skill = git('show', commit + ':SKILL.md')
    version = re.search(rb'version:\s*"([^"]+)"', skill).group(1).decode()
    if not re.fullmatch(r'1\.[0-9A-Za-z.-]+', version): raise ValueError('Legacy must be a version 1 Skill snapshot')
    # Frozen snapshots retain their original Skill name and payload bytes.
    name_match = re.search(rb'^name:[ \t]*([a-z0-9]+(?:-[a-z0-9]+)*)[ \t]*\r?$', skill, re.MULTILINE)
    if not name_match: raise ValueError('Legacy snapshot must declare a valid Skill name')
    skill_name = name_match.group(1).decode()
    names = git('ls-tree', '-r', '--name-only', commit).decode().splitlines()
    selected = [name for name in names if name in ('SKILL.md', 'README.md', 'README.zh-CN.md', 'LICENSE', 'AGENTS.md', 'VERIFICATION.md')
                or (Path(name).parts[0] in ('scripts', 'references', 'tests')
                    and Path(name).suffix in ('.py', '.js', '.sh', '.md', '.html'))]
    path = output / ('academic-automation-legacy-v' + version + '-macos.zip')
    with zipfile.ZipFile(path, 'w') as archive:
        payload = {}
        for name in selected:
            data = git('show', commit + ':' + name)
            payload[name] = hashlib.sha256(data).hexdigest()
            add(archive, name, data, name.endswith('.sh'), skill_name=skill_name)
        add(archive, 'LEGACY_SOURCE.json', json.dumps({'label': 'Legacy Version 1', 'version': version,
            'commit': commit, 'files_sha256': payload}, indent=2) + '\n', skill_name=skill_name)
        add(archive, 'INSTALL.md', (root / 'LEGACY.md').read_bytes(), skill_name=skill_name)
    return path


def build(root=ROOT, output=None, legacy_ref=None):
    root = Path(root).resolve(); output = Path(output or root / 'dist').resolve()
    version = re.search(r'version:\s*"([^"]+)"', (root / 'SKILL.md').read_text(encoding='utf-8')).group(1)
    if not re.fullmatch(r'[0-9A-Za-z.-]+', version):
        raise ValueError('Invalid release version')
    output.mkdir(parents=True, exist_ok=True)
    hashes, artifacts = [], []
    for target in ('windows', 'macos'):
        path = output / ('academic-automation-v' + version + '-' + target + '.zip')
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in source_files(root, target):
                add(archive, name, data, name.endswith('.sh'))
            backend = 'extension' if target == 'windows' else 'apple-events'
            add(archive, 'platform.json', json.dumps({'platform': target, 'default_backend': backend,
                'version': version, 'validation': 'preview; see VERIFICATION.md'}, indent=2) + '\n')
            if target == 'windows':
                add(archive, 'academic.cmd', '@echo off\r\nwhere py >nul 2>nul\r\nif errorlevel 1 (\r\n  python "%~dp0scripts\\academic.py" %*\r\n) else (\r\n  py -3 "%~dp0scripts\\academic.py" %*\r\n)\r\nexit /b %errorlevel%\r\n')
            else:
                add(archive, 'academic.command', '#!/bin/sh\nexec python3 "$(dirname "$0")/scripts/academic.py" "$@"\n', True)
            instructions = (root / 'references' / ('install-' + target + '.md')).read_text(encoding='utf-8')
            # INSTALL.md is at the package root, one level above its source.
            instructions = re.sub(r'\]\(([^)]+)\)', lambda match: '](' + (
                match[1] if re.match(r'(?:[a-zA-Z][\w+.-]*:|/|#)', match[1])
                else 'references/' + match[1]) + ')', instructions)
            add(archive, 'INSTALL.md', instructions)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
        artifacts.append(path)
    if legacy_ref:
        path = legacy_asset(root, output, legacy_ref)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
        artifacts.append(path)
    (output / 'SHA256SUMS').write_text('\n'.join(hashes) + '\n', encoding='utf-8')
    return artifacts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output')
    parser.add_argument('--legacy-ref', help='Frozen v1 git commit to include as a macOS legacy asset')
    args = parser.parse_args()
    for artifact in build(output=args.output, legacy_ref=args.legacy_ref): print(artifact)
