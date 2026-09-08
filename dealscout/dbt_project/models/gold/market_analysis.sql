-- market_analysis.sql — Analyse sectorielle agrégée (Palier C.1)

select
    sector,
    count(*) as number_of_companies,
    round(cast(avg(growth) as numeric), 2) as average_growth,
    round(cast(avg(financial_health) as numeric), 2) as average_financial_health,
    round(cast(sum(funding) as numeric), 2) as investment_volume,
    round(cast(avg(news_sentiment) as numeric), 3) as average_sentiment
from {{ ref('company_360') }}
group by sector
order by average_growth desc
