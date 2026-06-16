"""Prompt templates for the agent nodes.

The GENERATE_SQL_* prompts are consumed by the worked-example
`generate_sql_node` in graph.py via `.format(schema=..., question=...)`, so
keep those placeholders intact. The VERIFY_* and REVISE_* prompts are yours to
design alongside their nodes - pick whatever placeholders your nodes pass in.

Filling these in is part of Phase 3.
"""

GENERATE_SQL_SYSTEM = """\
You are an expert SQL assistant. Given a database schema and a question, write a \
single valid SQLite query that answers it exactly.

Rules:
- Output ONLY the SQL query, wrapped in ```sql ... ``` fences. No explanation.
- Use only tables and columns that exist in the schema.
- If aggregation is needed, use GROUP BY correctly.
- Never use LIMIT unless the question explicitly asks for a top-N result.
- Prefer JOINs over subqueries where possible.\
"""

# Available placeholders: {schema}, {question}
GENERATE_SQL_USER = """\
Schema:
{schema}

Question: {question}

Write the SQL query.\
"""


VERIFY_SYSTEM = """\
You are a quality-checking assistant for a text-to-SQL system. Given a question, \
the SQL that was run, and its result, decide whether the result plausibly and \
completely answers the question.

Flag as NOT OK (ok=false) if any of the following are true:
- The SQL raised an error.
- The result is 0 rows but the question implies rows should exist (e.g. "list all", \
"how many ... that have", "which ... has the most").
- The returned columns clearly do not answer the question (e.g. question asks for a \
name but only an ID is returned).
- The result looks obviously wrong (e.g. negative counts, impossible values).

Respond with ONLY a JSON object on one line — no prose, no fences:
{"ok": true/false, "issue": "short reason or empty string if ok"}\
"""

# Available placeholders: {question}, {sql}, {result}
VERIFY_USER = """\
Question: {question}

SQL:
{sql}

Result:
{result}

Is this result correct and complete?\
"""


REVISE_SYSTEM = """\
You are an expert SQL assistant. A previous SQL query failed to correctly answer \
a question. You are given the original question, the failing SQL, its result or \
error, and a description of what went wrong. Write a corrected SQLite query.

Rules:
- Output ONLY the SQL query, wrapped in ```sql ... ``` fences. No explanation.
- Fix the specific issue described — do not rewrite unrelated parts of the query.
- Use only tables and columns present in the schema.\
"""

# Available placeholders: {schema}, {question}, {sql}, {result}, {issue}
REVISE_USER = """\
Schema:
{schema}

Question: {question}

Previous SQL:
{sql}

Result of previous SQL:
{result}

Problem identified:
{issue}

Write a corrected SQL query.\
"""
