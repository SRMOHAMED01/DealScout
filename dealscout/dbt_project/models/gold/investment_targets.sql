-- investment_targets.sql — Table de classement des cibles M&A (Palier C.1 / D)
-- Formule alignée sur scoring_engine/rules_scoring.py :
-- M&A Score = Growth*0.30 + Revenue*0.20 + Profitability*0.20
--           + Market*0.15 + Innovation*0.10 + International*0.05
-- Chaque composante est normalisée min-max [0,100] avant pondération.

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
),

-- Min-max bounds pour la normalisation de chaque composante
bounds as (
    select
        min(growth) as min_growth, max(growth) as max_growth,
        min(revenue) as min_revenue, max(revenue) as max_revenue,
        min(profit_margin) as min_profit_margin, max(profit_margin) as max_profit_margin,
        min(market_score) as min_market_score, max(market_score) as max_market_score,
        min(innovation_score) as min_innovation_score, max(innovation_score) as max_innovation_score,
        min(international_presence) as min_international_presence, max(international_presence) as max_international_presence
    from company_base
),

norm as (
    select
        cb.company_id,
        cb.name,
        cb.sector,
        cb.country,
        cb.revenue,
        cb.growth,
        cb.profit_margin,
        cb.financial_health,
        cb.market_score,
        cb.innovation_score,
        cb.international_presence,
        cb.news_sentiment,
        case when b.max_growth = b.min_growth then 50.0
             else round(((cb.growth - b.min_growth) / nullif(b.max_growth - b.min_growth, 0)) * 100.0, 2)
        end as norm_growth,
        case when b.max_revenue = b.min_revenue then 50.0
             else round(((cb.revenue - b.min_revenue) / nullif(b.max_revenue - b.min_revenue, 0)) * 100.0, 2)
        end as norm_revenue,
        case when b.max_profit_margin = b.min_profit_margin then 50.0
             else round(((cb.profit_margin - b.min_profit_margin) / nullif(b.max_profit_margin - b.min_profit_margin, 0)) * 100.0, 2)
        end as norm_profit_margin,
        case when b.max_market_score = b.min_market_score then 50.0
             else round(((cb.market_score - b.min_market_score) / nullif(b.max_market_score - b.min_market_score, 0)) * 100.0, 2)
        end as norm_market_score,
        case when b.max_innovation_score = b.min_innovation_score then 50.0
             else round(((cb.innovation_score - b.min_innovation_score) / nullif(b.max_innovation_score - b.min_innovation_score, 0)) * 100.0, 2)
        end as norm_innovation_score,
        case when b.max_international_presence = b.min_international_presence then 50.0
             else round(((cb.international_presence - b.min_international_presence) / nullif(b.max_international_presence - b.min_international_presence, 0)) * 100.0, 2)
        end as norm_international_presence
    from company_base cb
    cross join bounds b
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
    round(
        norm_growth * 0.30 +
        norm_revenue * 0.20 +
        norm_profit_margin * 0.20 +
        norm_market_score * 0.15 +
        norm_innovation_score * 0.10 +
        norm_international_presence * 0.05
    , 2) as m_and_a_score,
    case
        when financial_health < 40.0 or profit_margin < -10.0 then 'High'
        when financial_health < 65.0 then 'Medium'
        else 'Low'
    end as risk_level,
    case
        when round(norm_growth * 0.30 + norm_revenue * 0.20 + norm_profit_margin * 0.20 +
                   norm_market_score * 0.15 + norm_innovation_score * 0.10 + norm_international_presence * 0.05, 2) >= 85.0
            then 'Cible prioritaire'
        when round(norm_growth * 0.30 + norm_revenue * 0.20 + norm_profit_margin * 0.20 +
                   norm_market_score * 0.15 + norm_innovation_score * 0.10 + norm_international_presence * 0.05, 2) >= 60.0
            then 'À surveiller'
        else 'Faible priorité'
    end as recommendation
from norm
order by m_and_a_score desc
