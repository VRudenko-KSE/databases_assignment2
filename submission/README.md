# Submission guide

Submit your own SQL, one report, and readable before/after plans for R1–R4 and INSERT.
A convenient set is `workload.sql`, `indexes.sql`, `insert.sql`, and a report with embedded plans or clearly
labelled attachments. These starters are optional; use any clear file arrangement.

Use Google Docs, Word, Markdown, PDF, or another readable report format. If useful, start from `report.md`.
Record hypotheses before experiments and retain them when adding findings. For Google Docs, export a PDF
so the Moodle submission is stable.

Before submitting, check that your report includes:

- Your profile, workload priorities, original predictions, and any deviations affecting the measurements.
- Five baseline/indexed plan comparisons, a paired measurement table, and causal explanations.
- Actual-result correctness reasoning and both INSERT before/after row-count checks.
- Table/index size comparisons, individual index sizes, and composite-column-order reasoning.
- A counterexample, retain/reject recommendation, drawback, and changed-demand scenario.

Put all SQL, report, and supporting plans in one ZIP archive and check that it opens correctly. No particular
folder tree is required. Do not include the database data, containers, runtime files, or local passwords.
Submit through the Moodle activity in the course announcement.

If the submission includes AI-generated content, include `AI_DISCLOSURE.md`: tool, date, original prompts,
affected files/passages, and how you checked and revised the output. Follow the assignment's allowed/prohibited-use
policy; disclosure does not make prohibited assistance permissible.

See [the assignment](../assignment.md) for the complete requirements, marking, and deadlines.
