# Pandas & Data Processing Pro

## Principles
- **Vectorization First:** Always prefer vectorized operations over iterative loops (e.g., `iterrows`, `apply`). Loops in Pandas are slow and unoptimized.
- **Memory Efficiency:** Use appropriate dtypes. Downcast numerical types when possible, and use `category` types for columns with low cardinality.
- **Handling Missing Data:** Be explicit about handling NaN values. Use `fillna()` or `dropna()` based on the domain logic, and clearly document why a certain approach was taken.
- **Chaining:** Use method chaining where it makes the code more readable (e.g., using `pipe()`, `assign()`), but avoid excessively long chains that make debugging difficult.
- **Immutability:** Avoid `inplace=True`. It rarely provides performance benefits and often leads to confusing code. Reassign variables instead.

## Best Practices
- When filtering dataframes for Streamlit, make sure the filtered views are created efficiently to ensure fast UI updates.
- Use explicit column names instead of index positions.
