Return a code review summary in Russian using Markdown headings and lists when useful.

This is a summary of the review, not a rewritten Pull Request description.
Assume the reader can already see the PR title, description, changed files, and diff.
Provide only enough factual change context to make the review conclusions understandable.

Follow the project's Python API review guidelines for defect assessment.

Include these sections:

- **Итог:** briefly summarize the purpose of the reviewed changes and the overall result of the review.
  Keep the change overview at a high level and concise, normally 1–3 sentences.
  Group changes by purpose rather than listing files, methods, schemas, or tests one by one.
  Mention added tests only when they are central to understanding the PR.
  State whether verified defects were found.
  Do not use approval language, praise, or quality scores.

- **Найденные проблемы:** list only distinct, verified defects supported by the reviewed code and available context.
  For each finding, include the affected path and line when available, the concrete trigger,
  consequence, and smallest adequate fix.
  If no supported defects were found, state:
  "Подтверждённых дефектов в рассмотренных изменениях не обнаружено."
  Do not invent speculative risks or hypothetical failures to fill this section.

- **Влияние и риски:** include this section only when the reviewed changes have material effects or review-relevant risks
  that add information beyond the PR description.
  Explain interactions with existing clients, fixtures, schemas, assertions, shared framework code,
  configuration, or CI when relevant.
  Mention important unchanged shared behavior when it helps assess regression risk.
  Do not repeat the change overview from "Итог" or narrate the diff file by file.
  Omit this section when there is nothing material to add.

- **Проверено и ограничения:** identify the relevant changed and surrounding code actually inspected during the review.
  State material gaps caused by unavailable, missing, or truncated context.
  Explicitly distinguish code inspection from runtime verification.
  State when tests, CI behavior, external services, or the actual API contract were not executed or independently verified.
  Do not claim tests were run or behavior was verified without explicit evidence.

Make the level of detail proportional to the PR.
Prioritize verified findings and review conclusions over change narration.
Avoid repetition between sections.

Do not invent commit intent, API contracts, expected responses, test results, or behavior absent from the available context.
Do not report old defects that the Pull Request neither introduces nor materially affects.
Do not report hypothetical collisions based only on fixed test values; establish a concrete failure from available code.
If significant findings cannot all fit within the response budget, prioritize the most important ones and state that the list is incomplete.

Return the complete Markdown summary text, not JSON.
