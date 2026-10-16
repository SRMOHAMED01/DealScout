-- Unit test: company_360 company_id et name non nuls (Palier C)
{{
    config(
        severity = "error",
        warn_if = "!=0"
    )
}}

select *
from {{ ref('company_360') }}
where company_id is null
   or name is null
