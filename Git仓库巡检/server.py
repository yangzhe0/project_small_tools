#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 仓库递归扫描与 AI 状态总结面板 (Local Web Server)
纯 Python 标准库实现，零第三方依赖，支持：
1. 指定一个或多个文件夹递归扫描 Git 仓库
2. 并发提取 Git 状态（分支、工作区变更、暂存区、未跟踪、远程同步状态、最近提交）
3. 调用远程模型 API 智能审阅并生成仓库状态总结
4. 一键在「文件资源管理器」「终端」「GitHub 网页」或「GitHub Desktop」中打开目标文件夹
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"
INDEX_HTML_PATH = BASE_DIR / "index.html"


def load_env_vars() -> Dict[str, str]:
    """从同目录 .env 文件及系统环境变量加载密钥与配置"""
    env_map: Dict[str, str] = {}
    if ENV_PATH.exists():
        try:
            for raw_line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env_map[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    for k in ("API_BASE_URL", "API_FALLBACK_BASE_URL", "API_KEY", "API_MODEL", "ENABLE_AI_SUMMARY"):
        if os.environ.get(k):
            env_map[k] = os.environ[k]
    return env_map


def update_env_setting(key: str, value: str) -> None:
    """将指定配置键值更新到 .env 文件，不污染受 Git 跟踪的 config.json"""
    lines: List[str] = []
    found = False
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    new_lines: List[str] = []
    prefix = f"{key}="
    for line in lines:
        if line.strip().startswith(prefix):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def update_env_key(api_key: str) -> None:
    update_env_setting("API_KEY", api_key)

# 默认跳过的高耗时非代码/依赖/系统目录（大小写不敏感匹配）
SKIP_DIRS_LOWER = {
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "target",
    "vendor",
    "$recycle.bin",
    "system volume information",
    "appdata",
    "local settings",
    "application data",
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    ".cache",
    ".gradle",
    ".idea",
    ".vscode",
}


def load_local_machine_defaults() -> Dict[str, Any]:
    """默认加载机器 API 配置（优先使用局域网/组网 API：10.126.126.2:8045 / 10.120.101.1:8045）"""
    home = Path.home()

    # 默认的 5 个扫描目录
    default_folders: List[str] = [
        p
        for p in [
            r"C:\Users\Y\Documents",
            r"C:\Users\Y\Downloads",
            r"C:\Users\Y\Desktop",
            r"C:\Users\Y\Pictures",
            r"C:\Jupiter\JupiterProject",
        ]
        if os.path.isdir(p)
    ]

    env_map = load_env_vars()
    env_enable_ai = env_map.get("ENABLE_AI_SUMMARY")
    auto_ai_summary = False if env_enable_ai is not None and env_enable_ai.lower() in ("false", "0", "off", "no") else True

    return {
        "folders": default_folders,
        "scan_nested_repos": False,
        "auto_ai_summary": auto_ai_summary,
        "terminal_type": "auto",  # auto | powershell | wt | cmd | gitbash
        "api": {
            "provider": "openai_compat",  # 指定的 OpenAI 兼容推理服务
            "base_url": env_map.get("API_BASE_URL", "http://10.126.126.2:8045/v1"),
            "fallback_base_url": env_map.get("API_FALLBACK_BASE_URL", "http://10.120.101.1:8045/v1"),
            "api_key": env_map.get("API_KEY", ""),
            "model": env_map.get("API_MODEL", "gemini-3.8-flash-high"),
            "proxy": "http://127.0.0.1:7897",
            "system_prompt": (
                "你是一个专业的Git工程助手。请根据给定的Git仓库状态数据，"
                "用简明扼要的中文（控制在45字以内）总结该仓库当前状态及建议动作（例如：工作区干净已同步、有未提交代码需整理、领先远程需推送等）。"
            ),
        },
    }


def get_config() -> Dict[str, Any]:
    defaults = load_local_machine_defaults()
    env_map = load_env_vars()
    env_key = env_map.get("API_KEY", "")
    env_enable_ai = env_map.get("ENABLE_AI_SUMMARY")
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                for k, v in saved.items():
                    if k == "api" and isinstance(v, dict):
                        defaults["api"].update(v)
                    elif k != "auto_ai_summary":  # auto_ai_summary 优先从 .env 读取
                        defaults[k] = v
        except Exception:
            pass
    # 始终优先从 .env 注入 api_key 与 auto_ai_summary，避免在 config.json 明文落盘
    if env_key:
        defaults["api"]["api_key"] = env_key
    if env_enable_ai is not None:
        defaults["auto_ai_summary"] = False if env_enable_ai.lower() in ("false", "0", "off", "no") else True
    return defaults


def save_config(new_cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg = get_config()
    for k, v in new_cfg.items():
        if k == "api" and isinstance(v, dict):
            if "api_key" in v and v["api_key"]:
                update_env_key(str(v["api_key"]).strip())
            cfg["api"].update(v)
        elif k == "auto_ai_summary":
            # auto_ai_summary 开关直接存入 .env，不修改 config.json
            update_env_setting("ENABLE_AI_SUMMARY", "true" if v else "false")
            cfg[k] = bool(v)
        else:
            cfg[k] = v

    # 写入 config.json 时剔除 api_key 和 auto_ai_summary，确保敏感密钥和临时开关仅存于被 .gitignore 忽略的 .env 中
    disk_cfg = json.loads(json.dumps(cfg))
    if isinstance(disk_cfg.get("api"), dict):
        disk_cfg["api"].pop("api_key", None)
    disk_cfg.pop("auto_ai_summary", None)
    CONFIG_PATH.write_text(json.dumps(disk_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_config()


def run_git_cmd(repo_path: str, args: List[str], timeout: float = 8.0) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", repo_path, "-c", "core.quotepath=false"] + args
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=creationflags,
    )


def build_rule_summary(info: Dict[str, Any]) -> str:
    """生成即时本地结构化总结（在 AI 总结返回前或离线时兜底展示）"""
    if info.get("error"):
        return f"读取异常：{info['error']}"

    parts = []
    branch = info.get("branch") or "未知分支"
    parts.append(f"当前位于 {branch} 分支")

    staged = info.get("staged_count", 0)
    modified = info.get("modified_count", 0)
    untracked = info.get("untracked_count", 0)
    conflicts = info.get("conflict_count", 0)

    if conflicts > 0:
        parts.append(f"⚠️ 存在 {conflicts} 个合并冲突待解决")
    elif staged == 0 and modified == 0 and untracked == 0:
        parts.append("工作区干净无修改")
    else:
        change_items = []
        if staged > 0:
            change_items.append(f"{staged} 个已暂存")
        if modified > 0:
            change_items.append(f"{modified} 个未暂存修改")
        if untracked > 0:
            change_items.append(f"{untracked} 个未跟踪文件")
        parts.append("有未提交变更（" + "、".join(change_items) + "）")

    ahead = info.get("ahead", 0)
    behind = info.get("behind", 0)
    if ahead > 0 and behind > 0:
        parts.append(f"与远程分叉（领先 {ahead} / 落后 {behind} 个提交，需拉取合并）")
    elif ahead > 0:
        parts.append(f"领先远程 {ahead} 个提交待 push")
    elif behind > 0:
        parts.append(f"落后远程 {behind} 个提交待 pull")
    elif info.get("remote_url"):
        parts.append("与远程同步")
    else:
        parts.append("未配置远程仓库")

    if info.get("stash_count", 0) > 0:
        parts.append(f"含 {info['stash_count']} 条 stash")

    return "；".join(parts) + "。"


def parse_remote_repo_info(remote_url: str) -> Dict[str, str]:
    """从 git remote URL (SSH 或 HTTPS) 解析 GitHub/远程 仓库名、owner/repo 及网页链接"""
    raw = (remote_url or "").strip()
    if not raw:
        return {"remote_repo_name": "", "remote_full_name": "", "remote_web_url": ""}

    # 匹配 git@github.com:owner/repo.git 或 ssh://git@host/owner/repo.git 或 https://github.com/owner/repo.git
    cleaned = re.sub(r"\.git$", "", raw)
    host = ""
    path_part = ""

    m_scp = re.match(r"^(?:[^@]+@)?([^:/]+):(.+)$", cleaned)
    if m_scp and "://" not in cleaned:
        host = m_scp.group(1)
        path_part = m_scp.group(2).lstrip("/")
    else:
        parsed = urllib.parse.urlparse(cleaned)
        host = parsed.hostname or ""
        path_part = (parsed.path or "").lstrip("/")

    segments = [s for s in path_part.split("/") if s]
    repo_name = segments[-1] if segments else ""
    full_name = "/".join(segments[-2:]) if len(segments) >= 2 else repo_name
    web_url = f"https://{host}/{path_part}" if host and path_part else ""

    return {
        "remote_repo_name": repo_name,
        "remote_full_name": full_name,
        "remote_web_url": web_url,
    }


def inspect_git_repo(repo_path: str, root_input: str = "") -> Dict[str, Any]:
    """提取单个 Git 仓库的详细状态信息"""
    p = Path(repo_path)
    result: Dict[str, Any] = {
        "name": p.name or str(p),
        "path": str(p),
        "root_input": root_input,
        "is_git": True,
        "branch": "",
        "upstream": "",
        "ahead": 0,
        "behind": 0,
        "staged_count": 0,
        "modified_count": 0,
        "untracked_count": 0,
        "conflict_count": 0,
        "stash_count": 0,
        "is_clean": True,
        "status_level": "clean",  # clean | dirty | unpushed | conflict | error
        "status_badge": "干净",
        "changed_files_preview": [],
        "last_commit_hash": "",
        "last_commit_time": "",
        "last_commit_msg": "",
        "last_commit_author": "",
        "remote_url": "",
        "remote_repo_name": "",
        "remote_full_name": "",
        "remote_web_url": "",
        "rule_summary": "",
        "ai_summary": "",
        "ai_source": "",
        "error": "",
    }

    try:
        # 1. git status --porcelain=v2 --branch
        st = run_git_cmd(repo_path, ["status", "--porcelain=v2", "--branch"])
        if st.returncode != 0:
            result["error"] = (st.stderr or "git status 执行失败").strip()[:120]
            result["status_level"] = "error"
            result["status_badge"] = "异常"
            result["rule_summary"] = build_rule_summary(result)
            return result

        changed_files: List[str] = []
        for line in st.stdout.splitlines():
            if not line:
                continue
            if line.startswith("# branch.head "):
                head = line[len("# branch.head ") :].strip()
                result["branch"] = "HEAD (游离)" if head == "(detached)" else head
            elif line.startswith("# branch.upstream "):
                result["upstream"] = line[len("# branch.upstream ") :].strip()
            elif line.startswith("# branch.ab "):
                # e.g. # branch.ab +1 -2
                ab = line[len("# branch.ab ") :].strip().split()
                for token in ab:
                    if token.startswith("+"):
                        try:
                            result["ahead"] = int(token[1:])
                        except ValueError:
                            pass
                    elif token.startswith("-"):
                        try:
                            result["behind"] = abs(int(token))
                        except ValueError:
                            pass
            elif line.startswith("1 ") or line.startswith("2 "):
                # 普通变更或重命名: 1 XY sub mH mI mW hH hI path
                parts = line.split(" ", 8)
                if len(parts) >= 2:
                    xy = parts[1]
                    x_state, y_state = xy[0], xy[1]
                    if x_state != ".":
                        result["staged_count"] += 1
                    if y_state != ".":
                        result["modified_count"] += 1
                    file_part = parts[-1].split("\t")[0]
                    if len(changed_files) < 10:
                        changed_files.append(f"{xy.replace('.', ' ').strip()} {file_part}")
            elif line.startswith("u "):
                result["conflict_count"] += 1
                parts = line.split(" ", 10)
                if len(changed_files) < 10:
                    changed_files.append(f"冲突 {parts[-1]}")
            elif line.startswith("? "):
                result["untracked_count"] += 1
                file_part = line[2:].strip()
                if len(changed_files) < 10:
                    changed_files.append(f"?? {file_part}")

        result["changed_files_preview"] = changed_files
        total_changes = (
            result["staged_count"]
            + result["modified_count"]
            + result["untracked_count"]
            + result["conflict_count"]
        )
        result["is_clean"] = total_changes == 0

        # 2. 最近一次提交信息
        lg = run_git_cmd(
            repo_path,
            ["log", "-1", "--format=%h%x09%cr (%ci)%x09%an%x09%s"],
        )
        if lg.returncode == 0 and lg.stdout.strip():
            cols = lg.stdout.strip().split("\t", 3)
            if len(cols) >= 1:
                result["last_commit_hash"] = cols[0]
            if len(cols) >= 2:
                # 简化时间展示
                m_date = re.search(r"\((\d{4}-\d{2}-\d{2} \d{2}:\d{2})", cols[1])
                rel_time = cols[1].split(" (")[0]
                result["last_commit_time"] = f"{m_date.group(1)} ({rel_time})" if m_date else cols[1]
            if len(cols) >= 3:
                result["last_commit_author"] = cols[2]
            if len(cols) >= 4:
                result["last_commit_msg"] = cols[3]
        else:
            result["last_commit_msg"] = "暂无提交记录 (空仓库)"

        # 3. 远程地址与 GitHub 仓库名解析
        rm = run_git_cmd(repo_path, ["remote", "get-url", "origin"])
        if rm.returncode == 0 and rm.stdout.strip():
            result["remote_url"] = rm.stdout.strip()
        else:
            rm_all = run_git_cmd(repo_path, ["remote", "-v"])
            if rm_all.returncode == 0 and rm_all.stdout.strip():
                first_line = rm_all.stdout.strip().splitlines()[0].split()
                if len(first_line) >= 2:
                    result["remote_url"] = first_line[1]

        result.update(parse_remote_repo_info(result["remote_url"]))

        # 4. Stash 数量
        st_list = run_git_cmd(repo_path, ["stash", "list"])
        if st_list.returncode == 0 and st_list.stdout.strip():
            result["stash_count"] = len(st_list.stdout.strip().splitlines())

        # 状态等级判定
        if result["conflict_count"] > 0:
            result["status_level"] = "conflict"
            result["status_badge"] = "存在冲突"
        elif not result["is_clean"]:
            result["status_level"] = "dirty"
            result["status_badge"] = "有未提交修改"
        elif result["ahead"] > 0 or result["behind"] > 0:
            result["status_level"] = "unpushed"
            if result["ahead"] > 0 and result["behind"] > 0:
                result["status_badge"] = f"分叉 ↑{result['ahead']} ↓{result['behind']}"
            elif result["ahead"] > 0:
                result["status_badge"] = f"待推送 ↑{result['ahead']}"
            else:
                result["status_badge"] = f"待拉取 ↓{result['behind']}"
        else:
            result["status_level"] = "clean"
            result["status_badge"] = "干净同步"

        result["rule_summary"] = build_rule_summary(result)
        result["ai_summary"] = result["rule_summary"]
        result["ai_source"] = "本地规则速览"
    except Exception as exc:
        result["error"] = str(exc)
        result["status_level"] = "error"
        result["status_badge"] = "异常"
        result["rule_summary"] = f"扫描出错: {exc}"
        result["ai_summary"] = result["rule_summary"]
        result["ai_source"] = "异常"

    return result


def discover_git_repos(folders: List[str], scan_nested: bool = False) -> Dict[str, Any]:
    """递归扫描一个或多个文件夹下的所有 Git 仓库"""
    t0 = time.time()
    discovered_paths: List[tuple[str, str]] = []  # (repo_path, input_root)
    seen_realpaths: set[str] = set()
    invalid_folders: List[str] = []
    non_git_Input_folders: List[str] = []

    normalized_folders: List[str] = []
    for item in folders:
        for sub in re.split(r"(?<=[^\r\n;])(?=[A-Za-z]:\\)", str(item)):
            s = sub.strip().strip('"').strip("'")
            if s and s not in normalized_folders:
                normalized_folders.append(s)

    for folder in normalized_folders:
        p = Path(folder)
        if not p.exists() or not p.is_dir():
            invalid_folders.append(folder)
            continue

        found_in_this_root = 0
        # Walk directory tree
        for root, dirs, files in os.walk(str(p), topdown=True):
            # 判断当前目录是否是 Git 仓库（存在 .git 目录或 .git 文件）
            has_git = ".git" in dirs or ".git" in files
            if has_git:
                real = os.path.normcase(os.path.abspath(root))
                if real not in seen_realpaths:
                    seen_realpaths.add(real)
                    discovered_paths.append((os.path.abspath(root), str(p)))
                    found_in_this_root += 1
                # 移除 .git 避免进入 .git 内部扫描
                if ".git" in dirs:
                    dirs.remove(".git")
                # 如果不要求嵌套扫描子仓库，命中 Git 仓库后不再向下递归，极大提升大仓库扫描速度
                if not scan_nested:
                    dirs[:] = []
                    continue

            # 过滤掉大型无关目录
            dirs[:] = [
                d
                for d in dirs
                if d.lower() not in SKIP_DIRS_LOWER and not (d.startswith(".") and d != ".git")
            ]

        if found_in_this_root == 0:
            non_git_Input_folders.append(str(p))

    # 并发获取所有 Git 仓库的状态
    repos: List[Dict[str, Any]] = []
    if discovered_paths:
        max_workers = min(16, (os.cpu_count() or 4) * 2, len(discovered_paths))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [
                pool.submit(inspect_git_repo, repo_path, root_input)
                for repo_path, root_input in discovered_paths
            ]
            for fut in concurrent.futures.as_completed(futures):
                repos.append(fut.result())

    # 保持稳定排序：先按状态优先级（有修改/冲突在前，或按路径排序），默认按名称和路径排序
    repos.sort(key=lambda r: (r["name"].lower(), r["path"].lower()))

    elapsed_ms = int((time.time() - t0) * 1000)
    return {
        "repos": repos,
        "total": len(repos),
        "dirty_count": sum(1 for r in repos if not r["is_clean"]),
        "unpushed_count": sum(1 for r in repos if r["ahead"] > 0 or r["behind"] > 0),
        "clean_count": sum(1 for r in repos if r["is_clean"] and r["ahead"] == 0 and r["behind"] == 0),
        "invalid_folders": invalid_folders,
        "non_git_folders": non_git_Input_folders,
        "elapsed_ms": elapsed_ms,
    }


# ==================== AI 总结调用模块 ====================


def is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def format_repo_prompt(repo: Dict[str, Any]) -> str:
    files_preview = ", ".join(repo.get("changed_files_preview", [])[:6]) or "无"
    return (
        f"仓库名: {repo.get('name')}\n"
        f"路径: {repo.get('path')}\n"
        f"当前分支: {repo.get('branch')} (远程跟踪: {repo.get('upstream') or '无'})\n"
        f"工作区统计: 已暂存 {repo.get('staged_count')}，未暂存修改 {repo.get('modified_count')}，"
        f"未跟踪文件 {repo.get('untracked_count')}，冲突 {repo.get('conflict_count')}\n"
        f"变更文件示例: {files_preview}\n"
        f"远程同步: 领先 {repo.get('ahead')} 个提交，落后 {repo.get('behind')} 个提交\n"
        f"Stash数量: {repo.get('stash_count')}\n"
        f"最近一次提交: [{repo.get('last_commit_hash')}] {repo.get('last_commit_time')} - {repo.get('last_commit_msg')}"
    )


def is_private_or_local_host(hostname: Optional[str]) -> bool:
    if not hostname:
        return False
    h = hostname.lower()
    if h in ("127.0.0.1", "localhost", "::1"):
        return True
    if h.startswith("10.") or h.startswith("192.168.") or h.startswith("127."):
        return True
    if h.startswith("172."):
        parts = h.split(".")
        if len(parts) >= 2 and parts[1].isdigit() and 16 <= int(parts[1]) <= 31:
            return True
    return False


def call_openai_compatible_api(
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_text: str,
    timeout: float = 25.0,
) -> str:
    """调用标准 OpenAI 兼容接口 (/v1/chat/completions 或 /v1/responses)，支持双内网地址自动主备切换"""
    candidates = [base_url.rstrip("/")]
    # 若使用的是组网/校园网双地址之一，自动将另一个作为备用地址
    lan_primary = "http://10.126.126.2:8045/v1"
    lan_secondary = "http://10.120.101.1:8045/v1"
    if candidates[0] == lan_primary:
        candidates.append(lan_secondary)
    elif candidates[0] == lan_secondary:
        candidates.append(lan_primary)

    last_err: Optional[Exception] = None
    for base in candidates:
        if not base:
            continue
        if not base.endswith("/chat/completions") and not base.endswith("/responses"):
            url = f"{base}/chat/completions"
        else:
            url = base

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GitRepoScanner/1.0",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        if url.endswith("/responses"):
            payload = {
                "model": model,
                "instructions": system_prompt,
                "input": [{"role": "user", "content": [{"type": "input_text", "text": user_text}]}],
                "stream": False,
            }
        else:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
                "temperature": 0.2,
                "stream": False,
            }

        # 对本地及局域网地址 (10.x / 192.168.x / 127.x) 绕过系统代理直连
        parsed = urllib.parse.urlparse(url)
        if is_private_or_local_host(parsed.hostname):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        else:
            opener = urllib.request.build_opener()

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with opener.open(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                data = json.loads(raw)
                if "choices" in data and data["choices"]:
                    msg = data["choices"][0].get("message", {})
                    content = (msg.get("content") or "").strip()
                    if content:
                        return content
                if "output_text" in data:
                    return str(data["output_text"]).strip()
                if "output" in data and isinstance(data["output"], list):
                    texts = []
                    for item in data["output"]:
                        for c in item.get("content", []):
                            if c.get("text"):
                                texts.append(c["text"])
                    if texts:
                        return "".join(texts).strip()
                raise ValueError(f"未识别的响应结构: {raw[:200]}")
        except Exception as exc:
            last_err = exc
            continue

    raise RuntimeError(f"API 调用失败: {last_err}")


def summarize_repo_with_ai(repo: Dict[str, Any], api_cfg: Dict[str, Any]) -> Dict[str, str]:
    """根据配置的远程模型 API 对单个仓库状态生成智能审阅总结"""
    env_map = load_env_vars()
    base_url = (api_cfg.get("base_url") or env_map.get("API_BASE_URL", "http://10.126.126.2:8045/v1")).strip()
    api_key = (api_cfg.get("api_key") or env_map.get("API_KEY", "")).strip()
    model = (api_cfg.get("model") or env_map.get("API_MODEL", "gemini-3.8-flash-high")).strip()
    system_prompt = (api_cfg.get("system_prompt") or "").strip() or (
        "你是一个专业的Git工程助手。请根据给定的Git仓库状态数据，"
        "用简明扼要的中文（控制在45字以内）总结该仓库当前状态及建议动作。"
    )
    user_text = format_repo_prompt(repo)

    # 仅调用指定的模型推理服务（不使用任何本机兜底）
    text = call_openai_compatible_api(base_url, api_key, model, system_prompt, user_text)
    return {"summary": text, "source": f"远程模型 ({model})"}


def summarize_repos_batch(repos: List[Dict[str, Any]], api_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """批量调用远程模型 API 进行智能审阅总结（支持单次批量推理 + 逐个请求）"""
    if not repos:
        return []

    env_map = load_env_vars()
    base_url = (api_cfg.get("base_url") or env_map.get("API_BASE_URL", "http://10.126.126.2:8045/v1")).strip()
    api_key = (api_cfg.get("api_key") or env_map.get("API_KEY", "")).strip()
    model = (api_cfg.get("model") or env_map.get("API_MODEL", "gemini-3.8-flash-high")).strip()

    # 若仓库数 <= 15，尝试一次请求批量总结所有仓库，速度极快
    if len(repos) <= 15:
        try:
            batch_items = []
            for idx, r in enumerate(repos):
                batch_items.append(f"[{idx}] {format_repo_prompt(r)}")
            batch_prompt = (
                "请为以下每个Git仓库分别生成一句简短中文状态总结与操作建议（每个控制在40字以内）。\n"
                "严格输出 JSON 数组格式，例如: [{\"index\": 0, \"summary\": \"...\"}, ...]，不要输出除 JSON 以外的任何文字。\n\n"
                + "\n\n".join(batch_items)
            )
            sys_prompt = "你是一个专业的Git工程状态分析API。只返回合法的JSON数组，格式为 [{\"index\": 0, \"summary\": \"中文总结\"}]。"

            raw_resp = call_openai_compatible_api(base_url, api_key, model, sys_prompt, batch_prompt, timeout=30.0)
            source_label = f"远程模型 ({model})"

            # 提取 JSON 数组
            m = re.search(r"\[.*\]", raw_resp, re.DOTALL)
            if m:
                arr = json.loads(m.group(0))
                if isinstance(arr, list):
                    mapped = {int(item["index"]): str(item["summary"]) for item in arr if "index" in item and "summary" in item}
                    results = []
                    for idx, r in enumerate(repos):
                        summary_txt = mapped.get(idx) or build_rule_summary(r)
                        results.append({
                            "path": r.get("path"),
                            "ai_summary": summary_txt,
                            "ai_source": source_label if idx in mapped else "本地规则速览",
                            "ok": True,
                        })
                    return results
        except Exception:
            # 批量解析失败则回退并发逐个请求
            pass

    # 并发逐个请求
    results: List[Dict[str, Any]] = [{} for _ in repos]

    def worker(idx: int, repo: Dict[str, Any]) -> None:
        try:
            res = summarize_repo_with_ai(repo, api_cfg)
            results[idx] = {
                "path": repo.get("path"),
                "ai_summary": res["summary"],
                "ai_source": res["source"],
                "ok": True,
            }
        except Exception as e:
            results[idx] = {
                "path": repo.get("path"),
                "ai_summary": f"{build_rule_summary(repo)} (模型调用提示: {str(e)[:60]})",
                "ai_source": "本地规则速览",
                "ok": False,
                "error": str(e),
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(repos))) as pool:
        futs = [pool.submit(worker, i, r) for i, r in enumerate(repos)]
        concurrent.futures.wait(futs)

    return results


# ==================== 本地系统动作（打开资源管理器 / 打开终端 / 选择文件夹） ====================


def open_in_explorer(folder_path: str) -> None:
    p = Path(folder_path).resolve()
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    os.startfile(str(p))


def open_in_terminal(folder_path: str, terminal_type: str = "auto") -> str:
    p = Path(folder_path).resolve()
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    target = str(p)
    t_type = (terminal_type or "auto").lower()

    # 1. Windows Terminal (wt.exe)
    if t_type in ("auto", "wt"):
        wt_path = shutil.which("wt") or shutil.which("wt.exe")
        if not wt_path:
            local_wt = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "wt.exe"
            if local_wt.exists():
                wt_path = str(local_wt)
        if wt_path:
            subprocess.Popen([wt_path, "-d", target])
            return "Windows Terminal"
        if t_type == "wt":
            raise FileNotFoundError("未找到 Windows Terminal (wt.exe)，请切换为 PowerShell 或 CMD")

    # 2. Git Bash
    if t_type == "gitbash":
        candidates = [
            r"C:\Program Files\Git\git-bash.exe",
            r"C:\Program Files (x86)\Git\git-bash.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                subprocess.Popen([c, f"--cd={target}"])
                return "Git Bash"

    # 3. CMD
    if t_type == "cmd":
        subprocess.Popen(
            ["cmd.exe", "/K", f'cd /d "{target}"'],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010),
        )
        return "CMD"

    # 4. 默认 PowerShell (pwsh 或 powershell)
    pwsh = shutil.which("pwsh") or shutil.which("powershell") or "powershell.exe"
    escaped_target = target.replace("'", "''")
    subprocess.Popen(
        [pwsh, "-NoExit", "-Command", f"Set-Location -LiteralPath '{escaped_target}'"],
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010),
    )
    return "PowerShell"


def open_in_github_desktop(folder_path: str) -> None:
    p = Path(folder_path).resolve()
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    local_app_data = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    gh_root = local_app_data / "GitHubDesktop"

    exe_candidates: List[Path] = []
    if gh_root.exists():
        # 优先查找 app-* 目录下的 GitHubDesktop.exe（与官方 cli.js 行为一致）
        for app_dir in sorted(gh_root.glob("app-*"), reverse=True):
            candidate = app_dir / "GitHubDesktop.exe"
            if candidate.exists():
                exe_candidates.append(candidate)
        root_exe = gh_root / "GitHubDesktop.exe"
        if root_exe.exists():
            exe_candidates.append(root_exe)

    if exe_candidates:
        subprocess.Popen([str(exe_candidates[0]), f"--cli-open={str(p)}"])
        return

    cli_bat = gh_root / "bin" / "github.bat"
    if cli_bat.exists():
        subprocess.Popen([str(cli_bat), "open", str(p)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return

    raise FileNotFoundError("未检测到 GitHub Desktop 安装路径 (%LOCALAPPDATA%\\GitHubDesktop)")


def pick_folder_dialog() -> Optional[str]:
    """调用 Windows 原生文件夹选择对话框"""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="选择要扫描 Git 仓库的文件夹")
        root.destroy()
        if selected:
            return str(Path(selected).resolve())
        return None
    except Exception as exc:
        raise RuntimeError(f"无法打开系统文件夹选择框: {exc}")


# ==================== HTTP 服务路由 ====================


class GitScannerRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # 精简控制台日志
        sys.stdout.write(f"[Web] {self.address_string()} - {format % args}\n")

    def _send_json(self, data: Any, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            if not INDEX_HTML_PATH.exists():
                self.send_error(404, "index.html not found")
                return
            content = INDEX_HTML_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/config":
            self._send_json({"ok": True, "config": get_config()})
            return

        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            body = self._read_json_body()
        except Exception as e:
            self._send_json({"ok": False, "error": f"JSON 解析错误: {e}"}, status=400)
            return

        if parsed.path == "/api/config":
            cfg = save_config(body)
            self._send_json({"ok": True, "config": cfg})
            return

        if parsed.path == "/api/pick-folder":
            try:
                folder = pick_folder_dialog()
                self._send_json({"ok": True, "folder": folder})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=500)
            return

        if parsed.path == "/api/scan":
            folders = body.get("folders") or []
            scan_nested = bool(body.get("scan_nested_repos", False))
            if isinstance(folders, str):
                folders = [line.strip() for line in re.split(r"[\r\n;]+", folders) if line.strip()]
            # 持久化最近一次扫描的文件夹配置
            save_config({"folders": folders, "scan_nested_repos": scan_nested})
            scan_res = discover_git_repos(folders, scan_nested=scan_nested)
            self._send_json({"ok": True, **scan_res})
            return

        if parsed.path == "/api/summarize":
            cfg = get_config()
            api_cfg = body.get("api") or cfg.get("api", {})
            repos = body.get("repos") or []
            if not repos and body.get("repo"):
                repos = [body["repo"]]
            summaries = summarize_repos_batch(repos, api_cfg)
            self._send_json({"ok": True, "summaries": summaries})
            return

        if parsed.path == "/api/open-explorer":
            folder_path = body.get("path", "")
            try:
                open_in_explorer(folder_path)
                self._send_json({"ok": True, "message": f"已在资源管理器打开: {folder_path}"})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=400)
            return

        if parsed.path == "/api/open-terminal":
            folder_path = body.get("path", "")
            cfg = get_config()
            term_type = body.get("terminal_type") or cfg.get("terminal_type", "auto")
            try:
                launched = open_in_terminal(folder_path, terminal_type=term_type)
                self._send_json({"ok": True, "terminal": launched, "message": f"已在 {launched} 打开: {folder_path}"})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=400)
            return

        if parsed.path == "/api/open-github-desktop":
            folder_path = body.get("path", "")
            try:
                open_in_github_desktop(folder_path)
                self._send_json({"ok": True, "message": f"已在 GitHub Desktop 打开: {folder_path}"})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=400)
            return

        self.send_error(404, "Endpoint Not Found")


def find_free_port(preferred: int = 8765) -> int:
    for port in range(preferred, preferred + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred


def main() -> None:
    # 确保 Windows 控制台 UTF-8 输出不乱码，并设置窗口标题
    if os.name == "nt":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("Git 仓库递归扫描与 AI 状态看板")
        except Exception:
            pass
        git_default_dir = r"C:\Program Files\Git\cmd"
        if not shutil.which("git") and os.path.isdir(git_default_dir):
            os.environ["PATH"] = git_default_dir + os.pathsep + os.environ.get("PATH", "")

    # 如果通过命令行/拖拽传入了文件夹路径，则自动写入初始配置
    cli_folders = [arg for arg in sys.argv[1:] if not arg.startswith("-") and os.path.isdir(arg)]
    if cli_folders:
        save_config({"folders": [str(Path(p).resolve()) for p in cli_folders]})

    no_browser = "--no-browser" in sys.argv
    test_startup = "--test-startup" in sys.argv
    port = find_free_port(8765)
    server = ThreadingHTTPServer(("127.0.0.1", port), GitScannerRequestHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 64)
    print(f"  Git 仓库扫描与 AI 状态面板已启动！")
    print(f"  访问地址: {url}")
    print(f"  提示: 保持此窗口开启以响应网页上的「打开文件夹/终端」和「AI总结」请求。")
    print(f"  按 Ctrl+C 可随时停止服务。")
    print("=" * 64)

    if test_startup:
        server.server_close()
        return

    if not no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        server.server_close()


if __name__ == "__main__":
    main()
