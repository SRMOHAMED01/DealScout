-- Unit test: market_analysis sector unique et non nul (Palier C)
{{
    config(
        severity = "error",
        warn_if = "!=0"
    )
}}

select sector, count(*) as nb
from {{ ref('market_analysis') }}
where sector is null
group by sector

union all

select sector, count(*) as nb
from {{ ref('market_analysis') }}
group by sector
having count(*) > 1
