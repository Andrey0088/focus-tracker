# Aplicativo Registro de Estudos

Este é um aplicativo simples de linha de comando para registrar suas sessões de estudo.

## Funcionalidades

- Registrar novas sessões de estudo (matéria, duração, notas).
- Visualizar todos os registros de estudo.
- Ver um resumo do tempo total de estudo e por matéria.

## Como Executar

1.  **Pré-requisitos:**
    Certifique-se de ter o Python 3.6 ou superior instalado.

2.  **Instalar dependências:**
    ```bash
    pip install colorama
    ```

3.  **Estrutura do Projeto:**
    Crie a seguinte estrutura de pastas e arquivos:

    ```
    study_tracker/
    ├── main.py
    ├── study_records.py
    ├── utils.py
    └── README.md
    ```
    Copie o conteúdo dos códigos fornecidos para os respectivos arquivos.

4.  **Executar o Aplicativo:**
    Navegue até a pasta `study_tracker` no seu terminal e execute:

    ```bash
    python main.py
    ```

## Estrutura para Futura Expansão

O aplicativo foi projetado com uma separação clara entre:

-   `study_records.py`: Contém a lógica de negócios e manipulação de dados (leitura/escrita em CSV/JSON). Esta parte é agnóstica à interface e pode ser facilmente reutilizada.
-   `utils.py`: Contém funções utilitárias, principalmente para a interface do console.
-   `main.py`: Lida com a interação do usuário na linha de comando.

**Para futuras expansões (ex: interface web, desktop):**

-   Você pode criar um novo arquivo `gui_app.py` (para uma interface gráfica com PyQt, Tkinter, Kivy) ou `web_app.py` (para uma interface web com Flask, Django) que importaria e utilizaria as funções de `study_records.py` para acessar e manipular os dados, mantendo a mesma base de dados (CSV/JSON).
-   A persistência de dados em CSV/JSON facilita a migração para bancos de dados mais robustos (SQLite, PostgreSQL) no futuro, se necessário.