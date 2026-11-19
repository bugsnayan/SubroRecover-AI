# SubroRecover AI — Machine Learning Model Documentation

## 1. Executive Summary

The SubroRecover AI Machine Learning subsystem prioritizes incoming property & casualty (P&C) auto insurance claims for subrogation investigation. By identifying high-yield recovery opportunities early in the claim lifecycle, the model minimizes subrogation leakage, shortens cycle times, and optimizes adjuster labor allocation.

---

## 2. Model Architecture & Problem Formulation

| Attribute | Specification |
|---|---|
| **Task Formulation** | Multi-Class Supervised Classification |
| **Target Variable** | `priority_level` (`High`, `Medium`, `Low`) |
| **Model Algorithm** | Scikit-learn `RandomForestClassifier` |
| **Ensemble Size** | 100 Decision Trees |
| **Max Tree Depth** | 6 (prevents overfitting on synthetic signal) |
| **Min Samples Split** | 4 |
| **Min Samples Leaf** | 2 |
| **Class Weighting** | `balanced` (handles class distribution shifts) |
| **Data Partitioning** | 80% Train, 20% Test (Stratified by Target Class) |
| **Random State** | 42 (ensures deterministic reproducibility) |

---

## 3. Feature Engineering & Feature Dictionary

The model consumes 10 domain-specific features derived from first-party claim records, police accident narratives, and historical recovery profiles:

| Feature Name | Type | Processing | Description |
|---|---|---|---|
| `adverse_fault_pct` | Float | Clipped [0, 100] | Assessed preliminary liability of adverse driver |
| `num_parties` | Integer | Min value 1 | Total number of involved operators/vehicles |
| `citations_issued` | Binary (0/1) | Extracted flag | Whether traffic court citations were issued to adverse party |
| `has_police_report` | Binary (0/1) | Extracted flag | Verified official law enforcement report present |
| `paid_amount` | Float | Continuous ($) | Net carrier loss disbursement paid out |
| `claim_amount` | Float | Continuous ($) | Gross claimed property/repair damage |
| `deductible_amount` | Float | Continuous ($) | Insured deductible liability |
| `days_to_report` | Integer | Non-negative integer | Latency between loss date and carrier FNOL filing |
| `claim_type_enc` | Categorical | Label Encoded | Collision kinematics (`Rear-end`, `T-bone`, `Side-swipe`, etc.) |
| `incident_state_enc`| Categorical | Label Encoded | State jurisdiction code governing negligence doctrine |

---

## 4. Evaluation Metrics & Experimental Benchmarks

Evaluated on an independent, hold-out stratified test set (36 samples):

| Evaluation Metric | Benchmark Value | Description |
|---|---|---|
| **Accuracy** | **100.00%** | Overall correct class predictions |
| **Weighted Precision** | **100.00%** | Proportion of positive identifications that were correct |
| **Weighted Recall** | **100.00%** | Proportion of actual positives correctly identified |
| **Weighted F1-Score** | **100.00%** | Harmonic mean of precision and recall |
| **ROC-AUC (OVR Weighted)** | **1.0000** | Multi-class One-vs-Rest area under ROC curve |

### 4.1 Confusion Matrix

$$\begin{pmatrix} 24 & 0 & 0 \\ 0 & 6 & 0 \\ 0 & 0 & 6 \end{pmatrix}$$
*(Rows = True Class [Low, Medium, High]; Columns = Predicted Class [Low, Medium, High])*

---

## 5. Feature Importance Rankings (Model Explainability)

Feature importances extracted from the Gini impurity reduction across all 100 decision trees:

| Rank | Feature Name | Relative Importance | Interpretability Insight |
|:---:|---|:---:|---|
| **1** | `adverse_fault_pct` | **29.80%** | Primary determinant of statutory recovery viability |
| **2** | `num_parties` | **17.31%** | Distinguishes multi-vehicle collisions from single-vehicle crashes |
| **3** | `citations_issued` | **16.59%** | Statutory violations strongly correlate with adverse carrier liability acceptance |
| **4** | `claim_type_enc` | **14.15%** | Kinematics (e.g. rear-end collisions carry strong fault presumption) |
| **5** | `has_police_report` | **11.71%** | Official police records significantly enhance recovery probability |
| **6** | `claim_amount` | **3.06%** | Financial scale of property damage |
| **7** | `paid_amount` | **2.63%** | Carrier recovery quantum potential |
| **8** | `incident_state_enc` | **2.22%** | Comparative fault threshold (e.g., 51% bar vs. Pure Comparative) |
| **9** | `deductible_amount` | **1.78%** | Insured policyholder deductible stake |
| **10** | `days_to_report` | **0.75%** | Minor impact on final recovery yield |

---

## 6. Serialization & Inference Pipeline

- Artifact location: `ml/models/rf_priority_model.joblib`
- Metadata: `ml/models/model_metrics.json`
- Real-time prediction interface: `ml/predict.py` (`predict_case_priority(claim_dict)`)
- Provides class probabilities (`High`, `Medium`, `Low`), confidence score, top contributing factors, and a human-readable explanation string for adjusters.

---

## 7. Synthetic Data Limitations & Real-World Generalization Notice

> [!NOTE]
> The current model is trained on synthetic insurance claim records generated to mirror US P&C comparative negligence distributions. 
> 
> **Limitations:**
> 1. In real-world carrier environments, police crash reports may contain ambiguous handwriting, conflicting eyewitness statements, or delayed adverse policy identification.
> 2. The 100% test accuracy benchmark reflects clean synthetic signal separation; real-world production models typically achieve 82–89% F1-score due to disputed comparative liability splits.
