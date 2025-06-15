# NHLDraftSimulator-
ML model that predicts upcoming draft based on historical prospect data and current career data from those prospects 

# Phase 1 - Webscraping and Aquiring Data

Data Source (for 2025 prospects): Elite Prospects 2025 NHL draft hub (https://www.eliteprospects.com/draft-center?view=stats&sort=nation)
Data Source for (for previous year prospects): Elite Prospects Draft Centers from 2000 - 2024 (https://www.eliteprospects.com/draft/nhl-entry-draft)



✅ 1. Data Collection
a. Scrape current prospects from EliteProspects
👉 Done — saved as prospects_stats.csv

b. Scrape historical draft data
Loop over years (e.g., 2000–2020) and collect:

Draft year

Round

Pick #

Player name

Stats (GP, G, A, TP)

Nationality, League, Position

c. Collect player outcomes
Scrape or download:

NHL games played

Career points

Seasons played

Time to debut

Final status (active/retired)

🧼 2. Data Cleaning & Transformation
Merge draft + NHL outcome datasets using name + year

Convert stats to numeric

Encode Position, League, Nationality

Create Success label (e.g., NHL_GP >= 100)

📊 3. Exploratory Data Analysis (EDA)
Distribution of nationalities and leagues over years

Trends in GP, PTS per draft round

Correlation heatmap: G, A, TP, League, Success

Most predictive stats for NHL success

🤖 4. Machine Learning Modeling
Target:
text
Copy
Edit
Success = 1 if NHL_GP ≥ 100, else 0
Algorithms to use:
Logistic Regression

Random Forest

XGBoost

Steps:
Train/test split

Cross-validation

Accuracy, precision, recall, ROC AUC

Feature importance

🧪 5. Draft Simulator (Optional UX)
Input: draft-year stats for new players

Output: predicted probability of success

Optional: use Streamlit or Gradio to build an app

📘 6. Final Deliverables
README.md should include:
Overview

Dataset sources

Data pipeline

Key EDA visuals

Model performance

Limitations

How to run the simulator (if built)

👉 Next Step:
Would you like me to help you write the historical scraper next?
I can give you a script to:

Loop through 2000–2020 draft pages

Extract draft-year player stats

Save as historical_drafts.csv

Ready to move on to that?




