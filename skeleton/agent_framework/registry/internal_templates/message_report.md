<message_metadata>
from: {{sender_slug}}
to: {{recipient_slug}}
subject: {{subject}}
</message_metadata>

<task_report>

## Execution Summary
- **Actions Taken:** {{action_1}}
- **Successes:** {{success_list}}
- **Failures & Blockers:** {{blockers}}
- **Technical Debt:** {{debt_details}}

<context_delta>

## State Changes
- **Modified Files:** {{file_list}}
- **Crucial Changes:** {{pivot_details}}

</context_delta>

</task_report>