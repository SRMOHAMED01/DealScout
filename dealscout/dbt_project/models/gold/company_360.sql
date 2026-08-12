-- company_360.sql — Vue complète d'une entreprise (Palier C.1)
-- À IMPLÉMENTER : joindre companies + financial + news (Silver),
-- produire une ligne par entreprise avec toutes les infos consolidées.
--
-- Colonnes attendues :
--   company_id, name, sector, country, revenue, growth, employees,
--   funding, financial_health, news_sentiment

select
    c.company_id,
    c.name,
    -- TODO: joindre financial et news, calculer les colonnes ci-dessus
    1 as placeholder
from {{ source('silver', 'companies') }} c
