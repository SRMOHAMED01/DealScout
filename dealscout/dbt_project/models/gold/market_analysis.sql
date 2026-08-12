-- market_analysis.sql — Analyse sectorielle (Palier C.1)
-- À IMPLÉMENTER : agrégation par secteur.
--
-- Colonnes attendues :
--   sector, number_of_companies, average_growth, investment_volume

select
    sector,
    count(*) as number_of_companies,
    avg(growth) as average_growth,
    sum(funding) as investment_volume
from {{ ref('company_360') }}
group by sector
