with baseline as (
    select id, ts
    from {{ ref('clean_and_partitioned_source_data') }}

    union all

    select id, ts
    from {{ ref('interpolation_long_intervals') }}

    union all

    select id, ts
    from {{ ref('interpolation_short_intervals') }}
)

select id
from baseline
where id = neighbor(id, 1)
  and ts = neighbor(ts, 1)
