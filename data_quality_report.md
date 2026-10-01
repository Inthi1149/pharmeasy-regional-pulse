\# PharmEasy Regional Pulse — Data Quality Report



\## Overview



This report documents the data-quality checks and cleaning actions applied to the PharmEasy Regional Pulse dataset.



The raw dataset contained 2,159 rows. After removing 59 exact duplicate rows, the final cleaned dataset contained 2,100 unique order records.



\## Data Quality Summary



| Data Quality Dimension | Issue Identified | Cleaning / Validation Action | Result |

|---|---|---|---|

| Accuracy | Region names appeared in inconsistent forms | Region values were mapped to approved canonical region names | Regional analysis uses standardized names |

| Completeness | 48 category values were missing | Missing categories were imputed using the product-to-category lookup | 0 missing category values remain |

| Completeness | 94 profit values were missing | Missing profit was imputed using the mean margin for the corresponding category | 0 missing profit values remain |

| Consistency | Region names used different capitalization, spacing, and aliases | Region values were stripped, converted for lookup, and mapped to canonical names | 9 active canonical regions remain |

| Timeliness | Orders must represent the required analysis period | Order dates were generated for April, May, and June 2026 | Dataset supports the required monthly comparison |

| Validity | Required fields must exist before processing | `validate\_schema()` checks the dataset against the required column list | Clean dataset returned `validated` |

| Uniqueness | Raw data contained duplicate order rows | Exact duplicates were removed before other cleaning operations | 59 exact duplicates removed |

| Relevance | Analysis requires order, region, product, category, sales, profit, and date information | Only fields relevant to the regional performance analysis were retained/generated | Dataset supports regional and category analysis |



\## Cleaning Sequence



The cleaning pipeline was applied in the following order:



1\. Validate the raw input schema.

2\. Remove exact duplicate rows.

3\. Normalize region names.

4\. Impute missing category values using the product-to-category lookup.

5\. Impute missing profit values using category mean margin.

6\. Validate the cleaned dataset.

7\. Test the schema validator against a deliberately broken copy.

8\. Save the cleaned dataset.



\## Validation Results



\### Raw Dataset



\- Raw row count: 2,159

\- Required schema status: `validated`

\- Missing required columns: none



\### Duplicate Check



\- Exact duplicates removed: 59

\- Rows remaining after duplicate removal: 2,100



\### Missing-Value Check



Before imputation:



\- Missing category values: 48

\- Missing profit values: 94



After imputation:



\- Missing category values: 0

\- Missing profit values: 0



\### Region Standardization



The raw region field contained inconsistent capitalization, spacing, and aliases.



After normalization, the order dataset contains 9 active canonical regions:



\- Hyderabad

\- Warangal

\- Vijayawada

\- Visakhapatnam

\- Guntur

\- Nellore

\- Tirupati

\- Karimnagar

\- Bengaluru



Kurnool remains in the region master data but intentionally has zero orders.



\## Schema Validation



The cleaned dataset passed the required schema validation:



`status = validated`



A deliberately broken copy of the dataset was created by removing the `profit` column.



The validator correctly returned:



`status = blocked\_schema`



with:



`missing\_columns = \['profit']`



This demonstrates that the pipeline blocks processing when a required field is unavailable.



\## Conclusion



The cleaning process improved the accuracy, completeness, consistency, timeliness, validity, uniqueness, and relevance of the dataset.



The final cleaned dataset contains 2,100 order records with standardized regional values, no missing category values, no missing profit values, and a validated schema. It is ready for loading into the SQLite database and for subsequent regional performance analysis.

