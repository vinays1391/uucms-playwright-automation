# R&D POM conversion prompt

Record the R&D / Ph.D workflow step by step in the browser and convert the generated actions into maintainable page-object classes under `src/uucms/modules/research_development/pages` and workflow orchestration under `src/uucms/workflows/research_development`.

Checklist:
- identify each stage of the Ph.D lifecycle
- keep admission, synopsis, approval, progress, final report, symposium, and convocation logic separate
- store selectors and values in data-driven fixtures under `test_data/rnd`
- make success and validation assertions explicit
- keep generated recordings and videos out of tracked source files when they contain sensitive data
