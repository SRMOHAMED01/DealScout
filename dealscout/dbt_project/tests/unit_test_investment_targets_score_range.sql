-- Unit test: m_and_a_score doit être compris entre 0 et 100 (Palier C / D)
{{
    config(
        severity = "error",
        warn_if = "!=0"
    )
}}

select *
from {{ ref('investment_targets') }}
where m_and_a_score < 0
   or m_and_a_score > 100
