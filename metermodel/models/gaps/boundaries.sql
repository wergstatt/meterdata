{{config(order_by = ('id', 'ts'))}}

/*
    As most timeseries do not contain gaps, or at least not of their full length, this
    is meant to reduce the size of data to be interpolated by exactly finding the
    boundaries of each "gap". This means, a single id can have multiple gaps.
    The idea is to carry the information of the bounds (current and next) through.

 */

select id, ts, neighbor(ts, 1) as next_ts, ec, neighbor(ec, 1) as next_ec
from {{ ref('clean_source_data') }}
where next_ts - ts > 60 * 60 -- fill gaps larger than one hours
  and neighbor(id, 1) = id
order by id, ts