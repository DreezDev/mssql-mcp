"""
MCP Server custom para SQL Server (BAIC)
Usa pyodbc + FreeTDS (TDS_Version=8.0)
"""

import os
import re
import json
import pyodbc
from mcp.server.fastmcp import FastMCP

# ── Modo solo lectura ──────────────────────────────────────────────────────────
# Poner READ_ONLY=false en el entorno para permitir escritura (no recomendado).
READ_ONLY: bool = os.getenv("READ_ONLY", "true").strip().lower() != "false"

# Palabras clave que mutan datos — bloqueadas cuando READ_ONLY=true
_WRITE_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|EXEC|EXECUTE|MERGE|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

# ── Configuración de conexión ──────────────────────────────────────────────────
MSSQL_SERVER   = os.getenv("MSSQL_SERVER")
MSSQL_PORT     = os.getenv("MSSQL_PORT")
MSSQL_DB       = os.getenv("MSSQL_DB")
MSSQL_USER     = os.getenv("MSSQL_USER")
MSSQL_PWD      = os.getenv("MSSQL_PWD")

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={MSSQL_SERVER},{MSSQL_PORT};"
    f"DATABASE={MSSQL_DB};"
    f"UID={MSSQL_USER};"
    f"PWD={MSSQL_PWD};"
    "TrustServerCertificate=yes;"
    "Encrypt=no;"
)

def get_connection() -> pyodbc.Connection:
    return pyodbc.connect(CONNECTION_STRING, timeout=10)


# ── Servidor MCP ───────────────────────────────────────────────────────────────
mcp = FastMCP("BAIC SQL Server MCP")


# ── Tool: ejecutar query SELECT ────────────────────────────────────────────────
@mcp.tool()
def execute_query(sql: str, max_rows: int = 200) -> str:
    """
    Ejecuta una consulta SQL de solo lectura (SELECT) contra la base de datos SQL Server.
    Devuelve los resultados como JSON.

    Args:
        sql:      La consulta SQL a ejecutar (solo SELECT).
        max_rows: Máximo de filas a retornar (default 200, máximo 1000).
    """
    # ── Validación modo READ_ONLY ──────────────────────────────────────────────
    if READ_ONLY:
        if _WRITE_KEYWORDS.search(sql):
            blocked = _WRITE_KEYWORDS.findall(sql)
            return json.dumps({
                "error": "Operación bloqueada: el servidor está en modo solo lectura (READ_ONLY=true).",
                "keywords_detectadas": list(set(kw.upper() for kw in blocked)),
            })

    sql_clean = sql.strip().upper()
    if not sql_clean.startswith("SELECT") and not sql_clean.startswith("WITH"):
        return json.dumps({"error": "Solo se permiten consultas SELECT o WITH (CTE)."})

    max_rows = min(max_rows, 1000)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchmany(max_rows)
        result = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tool: listar tablas ────────────────────────────────────────────────────────
@mcp.tool()
def list_tables(schema: str = "dbo") -> str:
    """
    Lista todas las tablas del esquema indicado en la base de datos.

    Args:
        schema: Esquema a consultar (default: 'dbo').
    """
    sql = f"""
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{schema}'
        ORDER BY TABLE_NAME
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tool: describir columnas de una tabla ──────────────────────────────────────
@mcp.tool()
def describe_table(table_name: str, schema: str = "dbo") -> str:
    """
    Devuelve la estructura (columnas, tipos, nulabilidad) de una tabla.

    Args:
        table_name: Nombre de la tabla.
        schema:     Esquema de la tabla (default: 'dbo').
    """
    sql = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
          AND TABLE_SCHEMA = '{schema}'
        ORDER BY ORDINAL_POSITION
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tool: listar stored procedures ────────────────────────────────────────────
@mcp.tool()
def list_stored_procedures(schema: str = "dbo") -> str:
    """
    Lista los stored procedures disponibles en el esquema indicado.

    Args:
        schema: Esquema a consultar (default: 'dbo').
    """
    sql = f"""
        SELECT
            ROUTINE_SCHEMA,
            ROUTINE_NAME,
            ROUTINE_TYPE,
            CREATED,
            LAST_ALTERED
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA = '{schema}'
          AND ROUTINE_TYPE = 'PROCEDURE'
        ORDER BY ROUTINE_NAME
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tool: listar schemas ───────────────────────────────────────────────────────
@mcp.tool()
def list_schemas() -> str:
    """
    Lista todos los schemas disponibles en la base de datos actual.
    """
    sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA ORDER BY SCHEMA_NAME"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = [row[0] for row in cursor.fetchall()]
        conn.close()
        return json.dumps(rows, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Arrancar el servidor ───────────────────────────────────────────────────────
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
