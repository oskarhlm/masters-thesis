INFO_QUERY = """
WITH geometry_info AS (
    SELECT
        f_table_name AS table_name,
        srid,
        type AS geometry_type
    FROM
        geometry_columns
),
column_info AS (
    SELECT
        table_name,
        column_name,
        data_type
    FROM
        information_schema.columns
),
table_comments AS (
    SELECT
        relname AS table_name,
        description AS table_description
    FROM
        pg_class c
    LEFT JOIN
        pg_namespace n ON c.relnamespace = n.oid
    LEFT JOIN
        pg_description d ON c.oid = d.objoid
    WHERE
        n.nspname = 'public' -- Specify the schema name if needed
        AND c.relkind = 'r' -- Only select tables
)
SELECT
    gi.table_name,
    tc.table_description,
    gi.srid,
    gi.geometry_type,
    jsonb_agg(jsonb_build_object('name', ci.column_name, 'type', ci.data_type)) AS properties
FROM
    geometry_info gi
JOIN
    column_info ci ON gi.table_name = ci.table_name
LEFT JOIN
    table_comments tc ON gi.table_name = tc.table_name
GROUP BY
    gi.table_name, tc.table_description, gi.srid, gi.geometry_type
"""
