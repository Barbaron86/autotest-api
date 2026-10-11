Return only a valid JSON array of review comments in this format:

```json
[
  {
    "file": "<relative_file_path>",
    "line": 1,
    "message": "<review comment in Russian>",
    "suggestion": null
  }
]
```

Analyze the changed files together and follow the project's Python API review guidelines.
Report every distinct, supported defect that fits in the response budget; do not impose a comment count limit.
Order findings by impact. Avoid duplicate findings and style-only remarks.
Each message must explain the trigger, consequence and smallest adequate correction.
Establish a concrete failure from the available code before reporting a defect.
Fixed test values alone do not prove collisions or flaky execution; verify the relevant contract and isolation.
Omit speculative findings when required server behavior or failure conditions cannot be established.
The file must match a path in the diff; the line must identify the defect in the new version.
The suggestion must be replacement code without Markdown fences, or null when no precise replacement is available.
Preserve the original leading whitespace on every replacement line, including the first line.
If a complete replacement with correct indentation cannot be supplied, set suggestion to null and explain the fix in message.
If no supported defects are found, return []. Do not add prose outside the JSON array.
