\# PharmEasy Regional Pulse - Data Quality Report



\## Overview



This report documents the data-quality checks and cleaning actions applied to the PharmEasy Regional Pulse dataset.



The official raw dataset contains 2,159 rows. After removing 59 exact duplicate rows, the cleaned dataset contains 2,100 unique order records.



The required order schema is:



\- order\_id

\- order\_date

\- region

\- category

\- product

\- quantity

\- sales\_inr

\- profit\_inr



\## Data Quality Summary



| Data Quality Dimension | Issue Identified | Cleaning / Validation Action | Result |

|---|---|---|---|

| Accuracy | Missing category values could make product-category relationships inaccurate | Missing categories were restored using the product-to-category lookup | 48 missing category values were repaired and 0 remain |

| Completeness | Category and profit values were missing after duplicate removal | Category was imputed from the product lookup and profit was imputed using category mean profit margin | 48 missing category values and 94 missing profit values were reduced to 0 |

| Consistency | Raw region names contained inconsistent capitalization and whitespace variants | Region values were stripped and standardized to title case | 16 distinct raw region variants were standardized to 9 active canonical regions |

| Timeliness | The analysis requires the April-June 2026 reporting period | Order dates were checked as part of the generated reporting dataset | The dataset supports April, May, and June 2026 monthly analysis |

| Validity | Processing must stop when a required schema field is unavailable | The required 8-column schema was validated, and a deliberately broken copy without `profit\_inr` was tested | Valid data passed and the broken schema was blocked |

| Uniqueness | The raw dataset contained exact duplicate rows | Exact duplicates were removed before region normalization and imputation | 59 exact duplicates were removed, reducing 2,159 rows to 2,100 |

| Relevance | The analysis requires fields that support regional, monthly, category, sales, profit, quantity, and order analysis | The required order fields were retained for the regional performance workflow | The cleaned dataset supports the required analysis and dashboard |



\## Cleaning Sequence



The cleaning pipeline was applied in the following order:



1\. Validate the raw input schema.

2\. Remove exact duplicate rows.

3\. Strip whitespace from region values and standardize them to title case.

4\. Impute missing category values using the product-to-category lookup.

5\. Impute missing `profit\_inr` values using the mean category margin calculated from `profit\_inr / sales\_inr`.

6\. Validate the cleaned dataset.

7\. Test the schema validator against a deliberately broken copy.

8\. Save the cleaned dataset.



\## Validation Results



\### Raw Dataset



\- Raw row count: 2,159

\- Required schema status: validated

\- Required columns: 8

\- Missing required columns: none

\- Distinct raw region variants: 16



\### Duplicate Check



\- Exact duplicates removed: 59

\- Rows remaining after duplicate removal: 2,100

\- Clean order IDs are unique



\### Missing-Value Check



After duplicate removal and before imputation:



\- Missing category values: 48

\- Missing `profit\_inr` values: 94



After imputation:



\- Missing category values: 0

\- Missing `profit\_inr` values: 0



\### Region Standardization



The 16 distinct raw region variants were standardized to 9 active canonical regions:



\- Hyderabad

\- Warangal

\- Vijayawada

\- Visakhapatnam

\- Guntur

\- Nellore

\- Tirupati

\- Karimnagar

\- Bengaluru



Kurnool remains in `regions\_master.csv` as the tenth master region and intentionally has zero orders.



\## Schema Validation



The cleaned dataset passed validation against the required schema.



A deliberately broken copy was then created by removing the required `profit\_inr` column.



The validator correctly blocked the broken dataset because `profit\_inr` was missing.



This confirms that the pipeline does not silently continue when a required field is unavailable.



\## Database Cross-Checks



The cleaned data was loaded into SQLite and produced the following verified results:



\- Regions in master table: 10

\- Orders in clean order table: 2,100

\- Duplicate `order\_id` values: 0

\- LEFT JOIN row count: 2,101

\- INNER JOIN row count: 2,100

\- Kurnool `COUNT(\*)`: 1

\- Kurnool `COUNT(order\_id)`: 0



The Kurnool result demonstrates the difference between counting the preserved master-region row and counting matched order records in a LEFT JOIN.



\## Conclusion



All seven required data-quality dimensions - accuracy, completeness, consistency, timeliness, validity, uniqueness, and relevance - are addressed by the cleaning and validation workflow.



The final cleaned dataset contains 2,100 order records, 9 active canonical order regions, no missing category values, no missing `profit\_inr` values, and a validated 8-column schema. The tenth master region, Kurnool, is preserved with zero orders for correct master-data reporting.

