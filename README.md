Web scraping project using Scrapy

Collecting and cleaning real estate data by creating several spiders and corresponding pipelines.

May 2024

Contains two spiders, for two unique websites. 

Cleaned dataset is included for the apartments only.

September 2026

Re-scraped apartments for sale from 4zida. The site caps search results at 100 pages, so the spider splits the search into price bands until each fits under that cap. Halooglasi is now behind Cloudflare bot protection and is no longer scraped.

`clean_data.py` combines the 2024 data (`apartmentsdata.csv`) with the 2026 data (`apartmentsdata2026.csv`) into `apartments_dataset.csv`, adding a `year` column. It drops listings without a price or priced below 9,900 €, duplicates and implausible values, and recomputes price per m². `export_excel.py` (requires `openpyxl`) saves an Excel copy, `apartments_dataset.xlsx`, which opens correctly regardless of Excel's regional settings.
