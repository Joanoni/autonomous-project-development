import os
import re


def read_to_field(message_path):
    """
    Reads the 'to' field from the <message_metadata> block of a message.md file.

    Expected format:
        <message_metadata>
        from: sender-slug
        to: recipient-slug
        subject: some subject
        </message_metadata>

    Returns the value string, or None if not found.
    """
    try:
        with open(message_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    # Extract the content inside <message_metadata>...</message_metadata>
    meta_match = re.search(
        r"<message_metadata>(.*?)</message_metadata>", content, re.DOTALL | re.IGNORECASE
    )
    if not meta_match:
        return None

    meta_block = meta_match.group(1)

    # Find the 'to' field within the metadata block
    to_match = re.search(r"^to\s*:\s*(.+)$", meta_block, re.MULTILINE | re.IGNORECASE)
    if not to_match:
        return None

    return to_match.group(1).strip()


def scan_queue():
    base_dir = os.getcwd()
    unread_dir = os.path.join(base_dir, "agent_framework/inbox/unread")
    message_path = os.path.join(unread_dir, "message.md")

    # No unread/ folder or no message.md → queue is empty
    if not os.path.exists(message_path):
        print("empty")
        return

    recipient = read_to_field(message_path)

    if not recipient:
        # message.md exists but has no 'to' field — treat as empty to avoid routing errors
        print("empty")
        return

    # Priority rule: user messages always surface first
    if recipient == "user":
        print("user")
        return

    print(recipient)


if __name__ == "__main__":
    scan_queue()
