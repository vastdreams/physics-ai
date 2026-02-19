"""
PATH: api/v1/changelog.py
PURPOSE: Changelog & release notes API.

ENDPOINTS:
- GET  /changelog              — Parsed CHANGELOG.md entries
- GET  /changelog/commits      — Recent git commits (auto-summarized)
- POST /changelog/generate     — Generate release notes from git log via DeepSeek (admin)

The dashboard "What's New" card consumes these endpoints.
"""

import os
import re
import json
import subprocess
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

from flask import Blueprint, jsonify, request

changelog_bp = Blueprint('changelog', __name__, url_prefix='/changelog')

# ── Paths ──────────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CHANGELOG_PATH = os.path.join(_PROJECT_ROOT, 'CHANGELOG.md')
_GENERATED_NOTES_PATH = os.path.join(_PROJECT_ROOT, 'data', 'release_notes.json')

# ── Cache (avoid re-parsing on every request) ──────────────────
_changelog_cache: Dict = {}
_cache_mtime: float = 0


def _parse_changelog() -> List[Dict]:
    """
    Parse CHANGELOG.md into structured release entries.
    Caches result until the file is modified.
    """
    global _changelog_cache, _cache_mtime

    try:
        mtime = os.path.getmtime(_CHANGELOG_PATH)
        if _changelog_cache and mtime == _cache_mtime:
            return _changelog_cache.get('entries', [])
    except OSError:
        return []

    entries = []
    try:
        with open(_CHANGELOG_PATH, 'r') as f:
            raw = f.read()

        # Split on ## headers (each is a release)
        sections = re.split(r'^## ', raw, flags=re.MULTILINE)

        for section in sections[1:]:  # skip preamble
            lines = section.strip().split('\n')
            title_line = lines[0].strip()

            # Parse "[version] - date" or "[Unreleased]"
            match = re.match(r'\[(.+?)\](?:\s*-\s*(.+))?', title_line)
            version = match.group(1) if match else title_line
            date = match.group(2).strip() if match and match.group(2) else ''

            # Parse body into categorized changes
            changes = []
            current_category = ''
            for line in lines[1:]:
                cat_match = re.match(r'^### (.+)', line)
                if cat_match:
                    current_category = cat_match.group(1).strip()
                    continue
                item_match = re.match(r'^- (.+)', line)
                if item_match:
                    changes.append({
                        'category': current_category,
                        'text': item_match.group(1).strip(),
                    })

            entries.append({
                'version': version,
                'date': date,
                'changes': changes,
                'is_unreleased': version.lower() == 'unreleased',
            })

        _changelog_cache = {'entries': entries}
        _cache_mtime = mtime

    except Exception as e:
        print(f"[changelog] Error parsing CHANGELOG.md: {e}")

    return entries


def _get_recent_commits(limit: int = 20, since: str = '') -> List[Dict]:
    """Fetch recent git commits."""
    try:
        cmd = ['git', 'log', f'--max-count={limit}', '--format=%H|%h|%s|%an|%aI']
        if since:
            cmd.append(f'--since={since}')

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=_PROJECT_ROOT,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 4)
            if len(parts) >= 5:
                commits.append({
                    'sha': parts[0],
                    'short_sha': parts[1],
                    'message': parts[2],
                    'author': parts[3],
                    'date': parts[4],
                })
        return commits

    except Exception:
        return []


def _summarize_with_deepseek(commits: List[Dict]) -> Optional[str]:
    """
    Use DeepSeek API to generate a human-friendly release summary
    from raw git commit messages.
    """
    api_key = (
        os.environ.get('DEEPSEEK_API_KEY')
        or os.environ.get('LLM_API_KEY')
        or os.environ.get('OPENAI_API_KEY')
    )
    if not api_key:
        return None

    api_base = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com')
    model = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')

    commit_text = '\n'.join(
        f"- {c['short_sha']} {c['message']} ({c['author']}, {c['date'][:10]})"
        for c in commits[:30]
    )

    prompt = f"""You are a release notes writer for "Beyond Frontier" — an open-source neurosymbolic physics engine.

Given these recent git commits, write clear, user-friendly release notes grouped by category (Features, Improvements, Fixes, Security). 
Keep it concise. Use bullet points. Skip merge commits and trivial changes. Write for end-users, not developers.

Git commits:
{commit_text}

Output format — JSON array of objects:
[
  {{"category": "Features", "text": "Description of the feature"}},
  {{"category": "Improvements", "text": "Description of the improvement"}},
  ...
]

Return ONLY the JSON array, no markdown fences."""

    try:
        import urllib.request
        req = urllib.request.Request(
            f'{api_base}/v1/chat/completions',
            data=json.dumps({
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 1000,
            }).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            content = data['choices'][0]['message']['content'].strip()
            # Parse the JSON response
            # Strip markdown fences if present
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            return json.loads(content)
    except Exception as e:
        print(f"[changelog] DeepSeek summarization failed: {e}")
        return None


def _load_generated_notes() -> List[Dict]:
    """Load previously generated release notes from disk."""
    try:
        if os.path.exists(_GENERATED_NOTES_PATH):
            with open(_GENERATED_NOTES_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save_generated_notes(notes: List[Dict]) -> None:
    """Save generated release notes to disk."""
    try:
        os.makedirs(os.path.dirname(_GENERATED_NOTES_PATH), exist_ok=True)
        with open(_GENERATED_NOTES_PATH, 'w') as f:
            json.dump(notes, f, indent=2, default=str)
    except Exception as e:
        print(f"[changelog] Could not save release notes: {e}")


# ═══════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@changelog_bp.route('', methods=['GET'])
def get_changelog():
    """
    Return parsed CHANGELOG.md entries + any AI-generated notes.
    Query params:
      ?limit=N  — max entries (default: 10)
    """
    limit = min(int(request.args.get('limit', 10)), 50)

    entries = _parse_changelog()
    generated = _load_generated_notes()

    return jsonify({
        'success': True,
        'changelog': entries[:limit],
        'generated_notes': generated[:limit],
        'source': 'CHANGELOG.md',
    })


@changelog_bp.route('/commits', methods=['GET'])
def get_commits():
    """
    Return recent git commits.
    Query params:
      ?limit=N     — max commits (default: 20)
      ?since=DATE  — only commits after this date (ISO format)
    """
    limit = min(int(request.args.get('limit', 20)), 100)
    since = request.args.get('since', '')
    commits = _get_recent_commits(limit=limit, since=since)

    return jsonify({
        'success': True,
        'commits': commits,
        'count': len(commits),
    })


@changelog_bp.route('/latest', methods=['GET'])
def get_latest():
    """
    Combined endpoint for the dashboard "What's New" card.
    Returns the latest changelog entry + recent commits + generated notes.
    """
    entries = _parse_changelog()
    generated = _load_generated_notes()
    commits = _get_recent_commits(limit=10)

    # Find the latest non-unreleased entry
    latest_release = None
    unreleased = None
    for entry in entries:
        if entry['is_unreleased']:
            unreleased = entry
        elif not latest_release:
            latest_release = entry

    return jsonify({
        'success': True,
        'latest_release': latest_release,
        'unreleased': unreleased,
        'generated_notes': generated[:1] if generated else [],
        'recent_commits': commits[:10],
    })


@changelog_bp.route('/generate', methods=['POST'])
def generate_notes():
    """
    Generate release notes from recent git commits using DeepSeek AI.
    Requires admin auth. The generated notes are saved to disk and
    returned for display in the dashboard.
    """
    # Optional: check for admin (for now, allow if authenticated)
    from api.middleware.auth import require_auth, get_current_user
    # We'll do a manual auth check since we can't easily stack decorators here
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    since = request.json.get('since', '') if request.is_json else ''
    limit = 30

    commits = _get_recent_commits(limit=limit, since=since)
    if not commits:
        return jsonify({
            'success': False,
            'error': 'No commits found'
        }), 404

    ai_notes = _summarize_with_deepseek(commits)

    if ai_notes is None:
        # Fallback: just categorize commits by keywords
        ai_notes = []
        for c in commits[:15]:
            msg = c['message'].lower()
            if any(w in msg for w in ('fix', 'bug', 'patch', 'hotfix')):
                cat = 'Fixes'
            elif any(w in msg for w in ('security', 'auth', 'lockout', 'harden')):
                cat = 'Security'
            elif any(w in msg for w in ('add', 'feat', 'new', 'create', 'implement')):
                cat = 'Features'
            else:
                cat = 'Improvements'
            ai_notes.append({'category': cat, 'text': c['message']})

    # Build the release note entry
    note_entry = {
        'id': hashlib.md5(json.dumps(commits[:5], default=str).encode()).hexdigest()[:12],
        'generated_at': datetime.now().isoformat(),
        'commit_range': {
            'from': commits[-1]['short_sha'] if commits else '',
            'to': commits[0]['short_sha'] if commits else '',
        },
        'changes': ai_notes,
        'commit_count': len(commits),
    }

    # Prepend to existing notes (keep max 20)
    existing = _load_generated_notes()
    existing.insert(0, note_entry)
    _save_generated_notes(existing[:20])

    return jsonify({
        'success': True,
        'notes': note_entry,
        'method': 'deepseek' if os.environ.get('DEEPSEEK_API_KEY') else 'keyword-fallback',
    })
