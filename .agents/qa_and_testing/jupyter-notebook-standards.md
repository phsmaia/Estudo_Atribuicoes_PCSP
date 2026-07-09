# Jupyter Notebook Standards

## Principles
- **Reproducibility:** A notebook should run from top to bottom without errors. Avoid out-of-order execution dependencies.
- **Clear Documentation:** Use Markdown cells to explain the "why", not just the "how". Document the data sources, assumptions, and conclusions for each section.
- **Clean Commits:** Clear all outputs before committing to version control, unless the output is explicitly required for demonstration purposes. Huge outputs (like inline datasets or large interactive charts) bloat the git repository.
- **Code Modularity:** If a block of code in a notebook becomes too large or is reused frequently, refactor it into a separate Python script (e.g., `data_processing.py`) and import it.

## Best Practices
- Use a consistent naming convention for notebooks (e.g., `01-data-cleaning.ipynb`).
- Keep the number of imports at the top of the notebook.
- Use `assert` statements or basic checks to ensure data integrity during exploratory analysis.
