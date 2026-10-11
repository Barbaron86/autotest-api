Return a review summary in Russian, using Markdown headings and lists when useful.
Describe the changes across the reviewed PR; do not reduce the answer to a single finding or a 1–4 sentence summary.
Follow the project's Python API review guidelines for defect assessment.
This mode also requires a factual overview of the changes, even when no actionable defects are found.

Include these sections:

- **Что изменилось:** summarize the main changes by purpose and affected components, including added tests.
- **Влияние:** explain how behavior or usage changes and which related code is affected.
- **Найденные проблемы:** list distinct, verified defects with paths, lines, consequences and minimal fixes.
  If none are supported, state that explicitly.
- **Контекст проверки:** identify relevant code actually inspected and material gaps caused by missing or truncated context.
  Do not claim tests were run or all possible defects were found.

Make the detail proportional to the PR. Prefer concrete explanations over repetition, praise or quality scores.
Prioritize significant findings within the response budget; if findings cannot all fit, state that limitation.
Do not invent commit intent, API contracts or test results. Return the complete summary text, not JSON.
Do not report hypothetical collisions based only on fixed test values; establish a concrete failure from available code.
