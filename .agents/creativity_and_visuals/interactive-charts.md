# Interactive Charts (Plotly/Altair)

## Principles
- **Visual Consistency:** Maintain a consistent color palette across all visualizations in the dashboard. Use colors that match the application theme and avoid aggressive or hard-to-read combinations.
- **Clarity Over Complexity:** Keep visualizations clean. Don't overload a single chart with too many dimensions. If it gets too complex, split it into multiple charts.
- **Informative Tooltips:** Interactive charts should provide clear and concise tooltips. Avoid dumping raw JSON or unformatted numbers; format currencies, percentages, and dates nicely.
- **Responsiveness:** Ensure charts scale correctly within the Streamlit layout without causing horizontal scrolling unless explicitly intended.

## Best Practices
- Provide titles and axis labels for every chart.
- Ensure legends are visible and positioned correctly without overlapping data.
- Optimize plotting functions to not block the main UI thread with heavy calculations; do the calculations beforehand in Pandas.
