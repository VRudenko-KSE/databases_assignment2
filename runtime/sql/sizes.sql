-- Copy the relevant measurements into your report's comparison tables.
-- Run in both configurations; for the INSERT table, also run after INSERT.
SELECT relation::text AS relation,
       pg_table_size(relation) AS table_bytes,
       pg_indexes_size(relation) AS index_bytes,
       pg_total_relation_size(relation) AS total_bytes
FROM unnest(ARRAY['mobility.events'::regclass, 'a2_write.events'::regclass]) AS t(relation)
ORDER BY relation::text;

-- Run this SELECT separately to see the cost of each index.
SELECT indrelid::regclass::text AS relation,
       indexrelid::regclass::text AS index_name,
       pg_relation_size(indexrelid) AS index_bytes
FROM pg_index
WHERE indrelid IN ('mobility.events'::regclass, 'a2_write.events'::regclass)
ORDER BY relation, index_name;
