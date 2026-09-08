-- investment_targets.sql — Table de classement des cibles M&A (Palier C.1 / D)

with company_base as (
    select
        company_id,
        name,
        sector,
        country,
        revenue,
        growth,
        profit_margin,
        financial_health,
        market_score,
        innovation_score,
        international_presence,
        news_sentiment
    from {{ ref('company_360') }}
)

select
    company_id,
    name,
    sector,
    country,
    revenue,
    growth,
    financial_health,
    news_sentiment,
    -- Normalized weighted M&A formula
    round(
        cast(
            (growth * 0.30) +
            (least(revenue / 1000000.0, 100.0) * 0.20) +
            (greatest(profit_margin + 20.0, 0.0) * 0.20) +
            (market_score * 0.15) +
            (innovation_score * 0.10) +
            (international_presence * 0.05)
        as numeric), 2
    ) as m_and_a_score,
    case
        when financial_health < 40.0 or profit_margin < -10.0 then 'High'
        when financial_health < 65.0 then 'Medium'
        else 'Low'
    end as risk_level,
    case
        when (growth * 0.30) + (market_score * 0.15) >= 30.0 then 'Cible prioritaire'
        when (growth * 0.30) + (market_score * 0.15) >= 15.0 then 'À surveiller'
        else 'Faible priorité'
    end as recommendation
from company_base
