"""
cycle/inbox_router.py — Steps 4, 5

  4. Move messages: archive inbox/unread/ then promote inbox/draft/ → inbox/unread/.
  5. Scan inbox/unread/message.md and return the next recipient slug (or status).

Public entry point:
  run(base_dir) -> str
    Returns one of:
      "user"         — unread/message.md exists and to: user
      "{agent-slug}" — unread/message.md exists and to: {slug}
      "empty"        — no unread/message.md or no to: field
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Step 4 — Move messages (archive unread/, promote draft/ → unread/)
# ---------------------------------------------------------------------------

def _parse_metadata_to_field(message_path: Path) -> tuple[str | None, str | None]:
    """Return (from, to) from a message's <message_metadata> block, or (None, None)."""
    try:
        content = message_path.read_text(encoding="utf-8")
    except OSError:
        return None, None

    meta_match = re.search(
        r"<message_metadata>(.*?)</message_metadata>", content, re.DOTALL | re.IGNORECASE
    )
    if not meta_match:
        return None, None

    block = meta_match.group(1)
    from_match = re.search(r"^from\s*:\s*(.+)$", block, re.MULTILINE | re.IGNORECASE)
    to_match = re.search(r"^to\s*:\s*(.+)$", block, re.MULTILINE | re.IGNORECASE)

    sender = from_match.group(1).strip() if from_match else None
    recipient = to_match.group(1).strip() if to_match else None
    return sender, recipient


def archive_unread(base_dir: Path) -> None:
    """
    Move the entire contents of inbox/unread/ into a new timestamped folder
    inside inbox/read/.  Folder name pattern: YYYYMMDD_HHMMSS_{from}_{to}
    """
    unread_dir = base_dir / "agent_framework/inbox/unread"
    read_dir = base_dir / "agent_framework/inbox/read"

    if not unread_dir.exists():
        return

    contents = [p for p in unread_dir.iterdir()]
    if not contents:
        return

    # Treat a lone .gitkeep as an empty directory — nothing to archive
    if len(contents) == 1 and contents[0].name == ".gitkeep":
        return

    # Try to read sender/recipient from the existing unread message
    unread_message = unread_dir / "message.md"
    sender, recipient = _parse_metadata_to_field(unread_message)
    sender = sender or "unknown"
    recipient = recipient or "unknown"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"{timestamp}_{sender}_{recipient}"
    archive_path = read_dir / archive_name
    archive_path.mkdir(parents=True, exist_ok=True)

    for item in contents:
        shutil.move(str(item), str(archive_path / item.name))


def move_draft_to_unread(base_dir: Path) -> None:
    """Move all files from inbox/draft/ into inbox/unread/."""
    draft_dir = base_dir / "agent_framework/inbox/draft"
    unread_dir = base_dir / "agent_framework/inbox/unread"

    if not draft_dir.exists():
        return

    contents = [p for p in draft_dir.iterdir()]
    if not contents:
        return

    unread_dir.mkdir(parents=True, exist_ok=True)

    for item in contents:
        shutil.move(str(item), str(unread_dir / item.name))


def promote_messages(base_dir: Path) -> None:
    """Archive current unread/ then move draft/ → unread/ (if draft has content)."""
    draft_dir = base_dir / "agent_framework/inbox/draft"

    # Only act if there is something in draft/
    if not draft_dir.exists() or not any(draft_dir.iterdir()):
        return

    archive_unread(base_dir)
    move_draft_to_unread(base_dir)


# ---------------------------------------------------------------------------
# Step 5 — Scan inbox
# ---------------------------------------------------------------------------

def read_to_field(message_path: Path) -> str | None:
    try:
        content = message_path.read_text(encoding="utf-8")
    except OSError:
        return None

    meta_match = re.search(
        r"<message_metadata>(.*?)</message_metadata>", content, re.DOTALL | re.IGNORECASE
    )
    if not meta_match:
        return None

    to_match = re.search(r"^to\s*:\s*(.+)$", meta_match.group(1), re.MULTILINE | re.IGNORECASE)
    if not to_match:
        return None

    return to_match.group(1).strip()


def scan_inbox(base_dir: Path) -> str:
    message_path = base_dir / "agent_framework/inbox/unread/message.md"

    if not message_path.exists():
        return "empty"

    recipient = read_to_field(message_path)
    if not recipient:
        return "empty"

    return recipient  # "user" or agent slug


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(base_dir: Path) -> str:
    """
    Execute steps 4 and 5.
    Returns the recipient slug, "user", or "empty".
    """
    promote_messages(base_dir)
    return scan_inbox(base_dir)
