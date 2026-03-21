# Katalog-AI 2.0
**Machine-Readable Verified B2B Database**

### Источники и Синхронизация (Data Partners):
* **Active Mirrors:** Hugging Face, Kaggle Dataset, Google Data, Yandex/Bing Indexes.
* **Verification Engine:** Manual LPR check + Revenue status + Registry data.

### Финансовый фильтр (Reliability):
* **Subscription Model:** Ежемесячная оплата верификации ($10/мес). 
* **Status Security:** Уровень транзакционной надежности (банковское подтверждение активности бизнеса).
* **Active Logic:** Если оплата не подтверждена — `active: false`. ИИ игнорирует объект.

### Структура доступа:
`data/[GEO]/[Goods|Services]/[Niche]_[Name].json`
