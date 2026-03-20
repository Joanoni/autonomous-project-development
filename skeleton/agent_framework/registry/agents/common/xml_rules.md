<do>

## What to do
- Use XML tags to delimit distinct sections with semantic names.
- Write content within tags using Markdown (lists, headers, bold, code blocks).
- Use code blocks fenced with language identifiers: ` ```python `, ` ```json `.
- Use `##`, `###` to subdivide long sections within a tag.
- Use lists (`-` or `1.`) for any enumerable content — never plain prose for lists.
- Use tables for comparisons and structured data.
- Use `{{placeholder}}` for values to be replaced at runtime.
- Keep tag names lowercase and snake_case: `<my_section>`.
- Add a blank line after the opening tag and before the closing tag.

</do>

<do_not>

## What not to do
- Do not use Markdown headers (#) as substitutes for XML tags — headers blend without clear boundaries.
- Do not mix multiple concerns within a single tag — one tag, one purpose.
- Do not use inline HTML within Markdown content — creates parsing ambiguity.
- Do not leave sections as unstructured prose when a list or table would be clearer.
- Do not use a root tag (wrapper) — wastes a nesting level without added value.
- Do not nest XML tags beyond two levels — deep nesting reduces readability.
- Do not use XML attributes for content belonging to the tag body.
- Do not indent content within XML tags — indentation breaks Markdown rendering and wastes tokens.

</do_not>

<formatting_rules>

## Formatting Rules

| Element | Use XML for | Use Markdown for |
|---|---|---|
| Section boundaries | ✅ | ❌ |
| Named semantics | ✅ | ❌ |
| Lists and enumerations | ❌ | ✅ |
| Code with language context | ❌ | ✅ |
| Bold / Italic emphasis | ❌ | ✅ |
| Tabular comparisons | ❌ | ✅ |
| Hierarchical data (2+ levels) | ✅ | ❌ |

</formatting_rules>