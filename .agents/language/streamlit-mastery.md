# Streamlit Mastery

## Principles
- **Separation of Concerns:** Keep data processing logic separated from UI rendering logic. Don't process massive dataframes directly inside a `st.write` or UI component.
- **State Management:** Use `st.session_state` properly to manage interactions, selections, and user configurations that should persist across reruns.
- **Performance & Caching:** 
  - Use `@st.cache_data` for functions that load data or do heavy pandas computations.
  - Use `@st.cache_resource` for database connections or machine learning models.
- **Responsiveness:** Make sure the dashboard uses layout elements effectively (`st.columns`, `st.container`, `st.expander`) to remain readable on different screen sizes.
- **Clean Reruns:** Ensure interactions don't cause unnecessary or expensive reruns.

## Best Practices
- Never mutate cached objects directly; return a copy if mutation is needed or use the `ttl` / `max_entries` parameters.
- Provide loading indicators (`st.spinner`) for long-running processes to enhance user experience.
