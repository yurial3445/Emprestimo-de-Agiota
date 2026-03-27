# Emprestimo de Agiota

Sistema de controle de empréstimos de itens. Usuários podem cadastrar itens, agendar empréstimos e registrar devoluções. O sistema garante que um item não seja emprestado se já estiver em uso, e somente o usuário responsável pelo empréstimo pode registrar a devolução.

## 🏗️ Estrutura da aplicação

Arquivos principais:
- `manage.py` - ponto de entrada Flask.
- `app/__init__.py` - cria app, banco e migration.
- `app/models.py` - modelo de dados com 4 tabelas.
- `app/routes.py` - rotas REST com CRUD e regras de negócio.
- `config.py` - configurações (env e sqlite).
- `.env` - variáveis sensíveis (não versionadas).
- `requirements.txt` - dependências.
- `migrations/` - histórico de migrations Flask-Migrate.

## 📦 Modelo de dados

Tabelas e relacionamentos:

1. `users` (id, name, email, phone)
2. `categories` (id, name)
3. `items` (id, name, description, category_id, available)
4. `loans` (id, user_id, item_id, borrow_date, due_date, return_date, status)

Relacionamentos:
- `User` 1:N `Loan`
- `Category` 1:N `Item`
- `Item` 1:N `Loan`

## 🔁 Regras de negócio

- Empréstimo só pode ser criado se o item estiver `available=True`.
- Ao criar empréstimo, `item.available` vira `False`.
- Devolução requer `user_id` igual ao locatário original; `item.available` volta `True`.
- Delete de empréstimo em aberto também devolve item.

## 📍 Rotas

- `GET /health`
- Usuários: `GET/POST /users`, `GET/PUT/DELETE /users/<id>`
- Categorias: `GET/POST /categories`, `PUT/DELETE /categories/<id>`
- Itens: `GET/POST /items`, `PUT/DELETE /items/<id>`
- Empréstimos: `GET/POST /loans`, `GET /loans/<id>`, `DELETE /loans/<id>`
- Devolução: `POST /loans/<id>/return` com `{ "user_id": X }`

## ⚙️ Setup local

1. Criar virtualenv: `python -m venv venv`
2. Ativar: `venv\Scripts\activate` (Windows) ou `source venv/bin/activate` (Linux/Mac)
3. Instalar: `pip install -r requirements.txt`
4. Definir env: `.env` já criado (`DATABASE_URL=sqlite:///app.db`, `SECRET_KEY=...`)
5. Migrar banco:
   - `flask db init` (uma vez)
   - `flask db migrate -m "Initial migration"`
   - `flask db upgrade`
6. Iniciar:
   - `flask run` ou `python manage.py` ou `python run.py` (novo entrypoint)
7. Acessar frontend: `http://127.0.0.1:5000/`

## 🗂️ Estrutura de pastas organizada

- `app/` → código principal do backend (flask, modelos, rotas)
- `app/static/` ou `frontend/` → arquivos de UI estáticos (HTML, CSS, JS)
- `migrations/` → control history do banco
- `tests/` → testes automatizados
- `config.py`, `run.py`, `manage.py` → entrypoints e config
- `.env`, `.gitignore`, `requirements.txt`, `README.md` → config do ambiente

## 🧪 Teste rápido

- Criar usuário: `POST /users` {"name":"João","email":"joao@example.com"}
- Criar categoria: `POST /categories` {"name":"Ferramentas"}
- Criar item: `POST /items` {"name":"Martelo","category_id":1}
- Criar loan: `POST /loans` {"user_id":1,"item_id":1,"due_date":"2026-04-15T00:00:00"}
- Devolver: `POST /loans/1/return` {"user_id":1}

## 📌 Observações

- `venv/`, `.env` e `app.db` não são versionados pelo `.gitignore`.
- Banco criado via migrations e não com SQL manual.

