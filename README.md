\# PharmEasy Regional Pulse



\## 1. Installation and End-to-End Run



PharmEasy Regional Pulse is an end-to-end analytics capstone covering deterministic synthetic data generation, data cleaning and quality controls, SQLite analysis, month-to-month regional metrics, CII narrative reporting, human review, audit logging, and a Streamlit + Plotly dashboard.



The analysis covers April, May, and June 2026.



From PowerShell in the project directory, install the required dependencies:



```powershell

py -m pip install -r requirements.txt

```



Run the complete pipeline from dataset generation through cleaning, database construction, SQL metrics, significance flagging, and report generation:



```powershell

py run\_pipeline.py

```



Launch the dashboard:



```powershell

py -m streamlit run app.py

```



The pipeline runs the project stages in this order:



`generate\_dataset.py` → `clean\_data.py` → `build\_db.py` → `queries.py` → `metrics\_engine.py` → `draft\_report.py`



No API key or paid service is required.



\## 2. Four-Artifact Cover Note



\### Headline Finding



Guntur sales increased from INR 78,000.00 in April 2026 to INR 173,308.20 in May 2026, a +122.19% month-to-month increase, before decreasing to INR 124,527.00 in June 2026.



\### Four Artifacts



1\. \*\*Streamlit dashboard — `app.py`\*\*  

&#x20;  Provides live exploration of regional sales, profit, orders, category performance, and monthly movements.



2\. \*\*CII narrative — embedded in the Streamlit dashboard\*\*  

&#x20;  Provides Context–Insight–Implication interpretation of the verified regional movements produced from the computed metrics.



3\. \*\*One-page memo — `memo.md`\*\*  

&#x20;  Provides the recommendation and supporting evidence for the flagship Guntur +122.19% April-to-May sales movement.



4\. \*\*Presentation storyline — `presentation\_storyline.md`\*\*  

&#x20;  Provides the structured storyline and responses used to explain and defend the finding in a live discussion.



\### Recommended Review Order



Review the four artifacts in this order:



1\. Streamlit dashboard (`app.py`)

2\. CII narrative embedded in the dashboard

3\. One-page recommendation memo (`memo.md`)

4\. Presentation storyline (`presentation\_storyline.md`)



This order moves from interactive evidence to interpretation, recommendation, and live communication.



\### Unverified Assumption



\[HIGH] No external cause for Guntur's 122.19% April-to-May sales increase has been verified by the current dataset; any explanation involving promotion, demand, inventory, or another operational event remains an unverified hypothesis.



\## Data Quality Summary



The raw dataset contains 2,159 rows, including 59 exact duplicate rows.



After deduplication, the clean analytical dataset contains 2,100 orders.



Missing category and profit values are imputed by the cleaning pipeline, region names are normalized to canonical values, and the clean schema is validated before downstream analysis.



\## Metric Rule



Month-on-month percentage change is calculated as:



`(current month - previous month) / previous month \* 100`



Division by zero returns 0.



A region is operationally flagged when:



`abs(change) > 8`



The 8% threshold is a fixed operational-alert business rule and is not a statistical-significance test.



\## Human Review and Reliability



Generated narrative is subject to a human review gate before downstream use.



`review\_gate\_v1()` accepts only:



\- `approve`

\- `edit`

\- `reject`



Only `approve` allows downstream use. Review actions are recorded in `audit\_log.jsonl`.



The reliability workflow is:



\*\*Safety Check → Validation → Critique/Refine → Human Sign-off\*\*



\## Project Files



\- `generate\_dataset.py` — deterministic synthetic dataset generation

\- `clean\_data.py` — cleaning pipeline and schema validation

\- `pharmeasy\_orders\_raw.csv` — generated raw dataset

\- `pharmeasy\_orders\_clean.csv` — cleaned analytical dataset

\- `regions\_master.csv` — ten-region master table

\- `data\_quality\_report.md` — data-quality controls and fixes

\- `build\_db.py` — SQLite database construction

\- `pharmeasy.db` — generated SQLite database

\- `queries.py` — JOIN validation and SQL metrics

\- `metrics\_engine.py` — month-on-month calculations, operational flagging, and state persistence

\- `draft\_report.py` — `draft\_report\_v1()` CII narrative generator

\- `memo.md` — Guntur recommendation memo

\- `review\_gate.py` — human review gate

\- `audit\_log.jsonl` — review audit trail

\- `reliability\_checklist.md` — four-step reliability workflow

\- `app.py` — Streamlit + Plotly dashboard

\- `presentation\_storyline.md` — presentation storyline and pushback responses

\- `run\_pipeline.py` — end-to-end pipeline runner

\- `requirements.txt` — Python dependencies

