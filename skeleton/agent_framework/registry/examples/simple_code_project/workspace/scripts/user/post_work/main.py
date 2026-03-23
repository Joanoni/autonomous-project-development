import os
import re
import shutil
from datetime import datetime, timezone


REQUIRED_FIELDS = ["from", "to", "subject"]


def parse_metadata(message_path):
    """
    Parses metadata from the <message_metadata> block of a message.md file.

    Expected format:
        <message_metadata>
        from: sender-slug
        to: recipient-slug
        subject: some subject
        </message_metadata>

    Returns a dict with the found keys (lowercased).
    Raises ValueError if the block is missing or unreadable.
    """
    try:
        with open(message_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        raise ValueError(f"Cannot read message file: {exc}") from exc

    meta_match = re.search(
        r"<message_metadata>(.*?)</message_metadata>", content, re.DOTALL | re.IGNORECASE
    )
    if not meta_match:
        raise ValueError(
            "No <message_metadata>...</message_metadata> block found in draft/message.md"
        )

    metadata = {}
    for line in meta_match.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^([a-zA-Z_\-]+)\s*:\s*(.*)$", line)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            metadata[key] = value

    return metadata


def validate_metadata(metadata):
    """
    Validates that all required fields are present and non-empty.
    Returns a list of error strings (empty list = valid).
    """
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required field: '{field}'")
        elif not metadata[field]:
            errors.append(f"Required field '{field}' is empty")
    return errors


def archive_unread(base_dir, sender, recipient):
    """
    Moves the entire contents of inbox/unread/ into a new timestamped folder
    inside inbox/read/.  Folder name pattern: YYYYMMDD_HHMMSS_{from}_{to}
    """
    unread_dir = os.path.join(base_dir, "agent_framework/inbox/unread")
    read_dir = os.path.join(base_dir, "agent_framework/inbox/read")

    if not os.path.exists(unread_dir):
        print("[Info] unread/ is empty or does not exist — nothing to archive.")
        return

    contents = os.listdir(unread_dir)
    if not contents:
        print("[Info] unread/ is empty — nothing to archive.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    sender = sender or "unknown"
    recipient = recipient or "unknown"
    archive_name = f"{timestamp}_{sender}_{recipient}"
    archive_path = os.path.join(read_dir, archive_name)

    os.makedirs(archive_path, exist_ok=True)

    for item in contents:
        src = os.path.join(unread_dir, item)
        dst = os.path.join(archive_path, item)
        shutil.move(src, dst)

    print(f"[Success] Archived unread/ contents -> read/{archive_name}")


def move_draft_to_unread(base_dir):
    """
    Moves all files from inbox/draft/ into inbox/unread/.
    """
    draft_dir = os.path.join(base_dir, "agent_framework/inbox/draft")
    unread_dir = os.path.join(base_dir, "agent_framework/inbox/unread")

    os.makedirs(unread_dir, exist_ok=True)

    moved_count = 0
    for item in os.listdir(draft_dir):
        src = os.path.join(draft_dir, item)
        dst = os.path.join(unread_dir, item)
        shutil.move(src, dst)
        moved_count += 1

    print(f"[Success] Moved {moved_count} item(s) from draft/ to unread/.")


def main():
    base_dir = os.getcwd()
    draft_dir = os.path.join(base_dir, "agent_framework/inbox/draft")
    draft_message = os.path.join(draft_dir, "message.md")
    unread_dir = os.path.join(base_dir, "agent_framework/inbox/unread")
    unread_message = os.path.join(unread_dir, "message.md")

    print("--- Starting Post-Work Routine ---")

    # 1. Validate draft/message.md exists
    if not os.path.exists(draft_message):
        print("[Error] draft/message.md not found. Nothing to post.")
        print("        Create the message at agent_framework/inbox/draft/message.md and re-run.")
        return

    # 2. Parse and validate draft metadata
    try:
        draft_metadata = parse_metadata(draft_message)
    except ValueError as exc:
        print(f"[Error] {exc}")
        return

    errors = validate_metadata(draft_metadata)
    if errors:
        print("[Error] draft/message.md has invalid metadata. Fix the following and re-run:")
        for err in errors:
            print(f"        - {err}")
        return

    draft_sender = draft_metadata["from"]
    draft_recipient = draft_metadata["to"]

    print(f"[Info] Message validated - from: '{draft_sender}', to: '{draft_recipient}', subject: '{draft_metadata['subject']}'")

    # 3. Archive current unread/ contents using unread message metadata
    unread_sender = None
    unread_recipient = None
    if os.path.exists(unread_message):
        try:
            unread_metadata = parse_metadata(unread_message)
            unread_sender = unread_metadata.get("from")
            unread_recipient = unread_metadata.get("to")
        except ValueError:
            pass

    archive_unread(base_dir, unread_sender, unread_recipient)

    # 4. Move draft/ → unread/
    move_draft_to_unread(base_dir)

    print("--- Post-Work Routine Complete ---")


if __name__ == "__main__":
    main()
