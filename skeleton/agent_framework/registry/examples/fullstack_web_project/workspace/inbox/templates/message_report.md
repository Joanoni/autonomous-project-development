<message_metadata>
from: {{sender_slug}}
to: {{recipient_slug}}
subject: {{subject}}
</message_metadata>

<task_report>

## Execution Summary
- **Status:** {{passed | failed | blocked}}
- **Actions Taken:** {{action_summary}}
- **Successes:** {{success_list}}
- **Failures & Blockers:** {{failure_details}}

<context_delta>

## State Changes
- **Modified Files:** {{file_list}}
- **Crucial Changes:** {{pivot_details}}

</context_delta>

</task_report>
