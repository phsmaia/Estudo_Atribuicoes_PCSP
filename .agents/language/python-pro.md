# Python Pro Guidelines

- **Tipagem Estrita (Type Hinting):** Sempre utilize *type hints* para argumentos de funções e retornos (ex: `str`, `int`, `List`, `Dict`, `Optional`). A tipagem deve servir como documentação viva.
- **Recursos Modernos:** Prefira *list comprehensions*, *generators* e *context managers* (`with`) ao invés de loops excessivos e gerenciamento manual de recursos. Evite blocos `try/except` que capturam exceções genéricas.
- **Sinergia com Pydantic e SQLAlchemy:** Utilize ativamente o Pydantic para validação robusta de dados. Garanta que os modelos do SQLAlchemy (2.0+) declarem tipos estritos (como `Mapped[str]`).
- **Princípios SOLID:** Mantenha as funções curtas e focadas em uma única responsabilidade. Desacople a lógica de negócio das rotas do Streamlit.
- **Pragmatismo sobre Pedantismo:** Evite abstrações prematuras ou padrões de design corporativos pesados (ex: *Factories* complexas) onde uma função simples já é suficiente para resolver o problema.
