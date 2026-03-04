# dreez-mssql-mcp

> A Model Context Protocol (MCP) server for **SQL Server** — built with read-only safety, pyodbc, and full compatibility with `uvx`.

[![PyPI version](https://img.shields.io/pypi/v/dreez-mssql-mcp)](https://pypi.org/project/dreez-mssql-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/dreez-mssql-mcp)](https://pypi.org/project/dreez-mssql-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Author](https://img.shields.io/badge/by-dreezdev-blue)](https://github.com/dreezdev)

---

## ✨ Features

- 🔍 **Execute read-only SQL queries** (SELECT / WITH)
- 🛡️ **READ_ONLY mode** — blocks any mutating SQL by default (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `MERGE`, `GRANT`, `REVOKE`)
- 📋 **List tables** in any schema
- 🔎 **Describe table columns** (types, nullability, defaults)
- 🗂️ **List schemas** in the database
- 📦 **List stored procedures**
- ⚡ Compatible with `uvx` — no global install needed

---

## 📦 Installation

### Using `uvx` (recommended — no install required)
```bash
uvx dreez-mssql-mcp
```

### Using `pip`
```bash
pip install dreez-mssql-mcp
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `MSSQL_SERVER` | ✅ | — | SQL Server hostname or IP |
| `MSSQL_PORT` | ✅ | — | SQL Server port (usually `1433`) |
| `MSSQL_DB` | ✅ | — | Database name |
| `MSSQL_USER` | ✅ | — | SQL Server username |
| `MSSQL_PWD` | ✅ | — | SQL Server password |
| `READ_ONLY` | ❌ | `true` | Set to `false` to allow write operations ⚠️ |

---

## 🔧 Client Configuration

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dreez-mssql": {
      "command": "uvx",
      "args": ["dreez-mssql-mcp"],
      "env": {
        "MSSQL_SERVER": "localhost",
        "MSSQL_PORT": "1433",
        "MSSQL_DB": "your_database",
        "MSSQL_USER": "your_user",
        "MSSQL_PWD": "your_password",
        "READ_ONLY": "true"
      }
    }
  }
}
```

### Cursor / VS Code

Edit `.cursor/mcp.json` or `.vscode/mcp.json`:

```json
{
  "servers": {
    "dreez-mssql": {
      "type": "stdio",
      "command": "uvx",
      "args": ["dreez-mssql-mcp"],
      "env": {
        "MSSQL_SERVER": "localhost",
        "MSSQL_PORT": "1433",
        "MSSQL_DB": "your_database",
        "MSSQL_USER": "your_user",
        "MSSQL_PWD": "your_password",
        "READ_ONLY": "true"
      }
    }
  }
}
```

---

## 🛠️ Available Tools

| Tool | Description |
|---|---|
| `execute_query(sql, max_rows?)` | Run a SELECT or WITH (CTE) query. Returns JSON. Max 1000 rows. |
| `list_tables(schema?)` | List all tables in a schema (default: `dbo`) |
| `describe_table(table_name, schema?)` | Get columns, types, and nullability for a table |
| `list_schemas()` | List all schemas in the current database |
| `list_stored_procedures(schema?)` | List stored procedures in a schema |

---

## 🛡️ READ_ONLY Mode

By default, `READ_ONLY=true`. Any query containing write keywords will be **blocked immediately** before reaching the database:

```json
{
  "error": "Operación bloqueada: el servidor está en modo solo lectura (READ_ONLY=true).",
  "keywords_detectadas": ["DELETE"]
}
```

Blocked keywords: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `EXECUTE`, `MERGE`, `REPLACE`, `GRANT`, `REVOKE`

> ⚠️ Set `READ_ONLY=false` only in controlled environments. It is strongly recommended to also use a SQL Server user with **read-only database permissions** as an extra safety layer.

---

## 🚀 Development

```bash
# Clone the repo
git clone https://github.com/dreezdev/dreez-mssql-mcp.git
cd dreez-mssql-mcp

# Install with uv
uv sync

# Run locally
uv run dreez-mssql-mcp
```

---

## 📋 Requirements

- Python >= 3.11
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- `pyodbc >= 5.0.0`
- `mcp[cli] >= 1.0.0`

---

## 📄 License

MIT © [dreezdev](https://github.com/dreezdev)

---

## 👤 Author

Made with ❤️ by **dreezdev**

- 🌐 Website: [dreez.dev](https://dreez.dev)
- 🐙 GitHub: [@dreezdev](https://github.com/dreezdev)
