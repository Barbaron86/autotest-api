# Allure report action

Generates Allure reports on Java 17 with Allure CLI 2.44.0. The CLI archive is
verified against the SHA256 pinned in `action.yml`; the renderer is stored locally.

Check out the source repository before downloading artifacts. Before calling the
action, place raw results in `allure-results/` and prepare the existing Pages
workspace in `gh-pages/`.

```yaml
- name: Generate Allure report
  uses: ./.github/actions/allure-report
  with:
    subfolder: ${{ steps.report.outputs.subfolder }}
    report-name: ${{ steps.report.outputs.name }}
    keep-reports: "50"
```

| Input | Required | Default | Purpose |
| --- | --- | --- | --- |
| `subfolder` | Yes | | Pages target, such as `main` or `pr-18`. |
| `report-name` | Yes | | Name shown in report metadata. |
| `keep-reports` | No | `50` | Maximum number of report runs in the target. |

The publishable workspace is `allure-history/`. It preserves the prepared Pages
content and writes the report to `<subfolder>/<run_number>/`, a redirect in
`<subfolder>/index.html`, and history in `<subfolder>/last-history/`.

## Vendored renderer

`vendor/entrypoint.sh` is an unmodified copy from
[simple-elf/allure-report-action](https://github.com/simple-elf/allure-report-action/tree/385367cde61ac68c2568a117f7579f7f148dc459).

- Upstream revision: `385367cde61ac68c2568a117f7579f7f148dc459`.
- Script SHA256: `546fcbd0af297485622bb955778f19a29880c3ba6c60766894c91131e48ececf`.
- License: MIT; the original notice is in `vendor/LICENSE`.

The internal `INPUT_*` variables adapt this renderer's interface. The workflow
only supplies the three inputs above. Preserve the renderer's provenance and
check PR/main history and retention when updating it or the CLI.
