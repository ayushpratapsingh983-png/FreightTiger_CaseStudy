# FreightTiger Cost Anomaly Detection System

## 🚀 Executive Summary
I have implemented a hybrid deterministic-AI pipeline to identify and justify transportation cost anomalies. Unlike a pure LLM approach, this system ensures 100% mathematical accuracy and reproducibility.

//"For the first 8 weeks of the dataset, the historical baseline is calculated using all available prior weeks, as a full 8-week window is not yet available. This ensures no data is ignored while maintaining the integrity of the sliding window."


## 🛠️ Technical Architecture
### 1. Deterministic Math Engine (`src/processor.py`)
- **Weekly Aggregation:** Calculated `cost_per_tonne_km` as $\frac{\sum \text{Freight Cost}}{\sum (\text{Quantity} \times \text{Distance})}$.
- **Sliding Window Baseline:** Implemented a strict 8-week look-back window for historical comparison to avoid "look-ahead bias."
- **Cross-Sectional Baseline:** Compared routes against their specific `route_type` peers for the same week to separate route-specific issues from market-wide trends.

### 2. Rule-Based Triage (`src/retriever.py`)
To eliminate hallucinations, I implemented a strict filtering layer before any text generation:
- **Spatio-Temporal Filter:** Notes must match the route (or 'All Routes') and fall within a $\pm 7$-day window of the anomaly.
- **Sentiment Trap Filter:** I implemented a keyword-blacklist to ignore notes that explicitly state "no significant effect" or "no rate change" (e.g., Notes N005, N010).

### 3. Reproducibility & QA
- **Deterministic Results:** Because the logic is rule-based, running the script $N$ times yields identical results.
- **Edge Case Handling:** Addressed routes with $<8$ weeks of history by using the available subset.

## 📊 Analysis Results
- **Threshold used:** 10% deviation from either baseline.
- **Key Finding:** Correctly flagged the Chennai-Bangalore March 10th anomaly as "Unexplained" because the flood note (N001) ended on March 8th.

## 🚀 How to Run
1. Install requirements: `pip install pandas numpy`
2. Navigate to the project root: `cd D:\FreightTiger_CaseStudy`
3. Run the main script: `python src/main.py`
