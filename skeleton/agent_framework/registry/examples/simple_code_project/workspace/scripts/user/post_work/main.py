import os
import re


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


def main():
    base_dir = os.getcwd()
    draft_dir = os.path.join(base_dir, "agent_framework/inbox/draft")
    draft_message = os.path.join(draft_dir, "message.md")

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

    print(f"[Info] Message validated - from: '{draft_metadata['from']}', to: '{draft_metadata['to']}', subject: '{draft_metadata['subject']}'")
    print("--- Post-Work Routine Complete ---")


if __name__ == "__main__":
    main()
