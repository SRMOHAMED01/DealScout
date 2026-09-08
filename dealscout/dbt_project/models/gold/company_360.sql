-- company_360.sql — Vue 360 consolidée d'une entreprise (Palier C.1)
-- Jointure des couches Silver (companies, financial, news)

with companies as (
    select
        company_id,
        name,
        sector,
        country,
        city,
        employees,
        founded_year,
        age_years,
        international_presence,
        innovation_score,
        market_score
    from {{ source('silver', 'companies') }}
),

financial as (
    select
        company_id,
        revenue,
        growth_yoy as growth,
        profit_margin,
        ebitda_margin,
        debt,
        cash,
        market_cap,
        funding_total as funding,
        funding_rounds,
        financial_health_score as financial_health
    from {{ source('silver', 'financial') }}
),

news as (
    select
        company_id,
        news_sentiment_score as news_sentiment,
        mentions_count,
        latest_headline
    from {{ source('silver', 'news') }}
)

select
    c.company_id,
    c.name,
    c.sector,
    c.country,
    c.city,
    c.employees,
    c.founded_year,
    c.age_years,
    coalesce(f.revenue, 0.0) as revenue,
    coalesce(f.growth, 0.0) as growth,
    coalesce(f.profit_margin, 0.0) as profit_margin,
    coalesce(f.ebitda_margin, 0.0) as ebitda_margin,
    coalesce(f.debt, 0.0) as debt,
    coalesce(f.cash, 0.0) as cash,
    coalesce(f.market_cap, 0.0) as market_cap,
    coalesce(f.funding, 0.0) as funding,
    coalesce(f.funding_rounds, 0) as funding_rounds,
    coalesce(f.financial_health, 50.0) as financial_health,
    c.international_presence,
    c.innovation_score,
    c.market_score,
    coalesce(n.news_sentiment, 0.0) as news_sentiment,
    coalesce(n.mentions_count, 0) as mentions_count,
    n.latest_headline
from companies c
left join financial f on c.company_id = f.company_id
left join news n on c.company_id = n.company_id
