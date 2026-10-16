-- Unit test: risk_level doit être une valeur acceptée (Palier C / D)
{{
    config(
        severity = "error",
        warn_if = "!=0"
    )
}}

select *
from {{ ref('investment_targets') }}
where risk_level not in ('Low', 'Medium', 'High')
