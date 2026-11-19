# SubroRecover AI — System Limitations & Responsible AI Disclosures

## 1. Regulatory & Legal Boundaries

1. **Decision-Support Classification:** SubroRecover AI is engineered exclusively as an administrative and analytical decision-support system for insurance claims adjusters. It does **not** practice law, establish binding legal liability, guarantee arbitration rulings, or render final judicial decrees.
2. **Statute of Limitations (SOL):** While the system tracks standard statutory deadlines across US jurisdictions, filing periods can be tolled by court orders, minority of claimants, or government vehicle immunities. Adjusters must verify jurisdictional docket rules.
3. **Adverse Carrier Solvency & Limits:** Recovery quantum estimates represent theoretical comparative negligence exposure based on loss magnitude. Actual recovery is subject to adverse policy limits (e.g., minimum state financial responsibility limits such as $25,000 property damage in Texas) and carrier solvency.

---

## 2. Machine Learning Model Disclosures

1. **Synthetic Training Signal:** The Random Forest prioritization classifier was trained and evaluated on synthetic insurance claims datasets structured to simulate realistic P&C auto comparative fault distributions.
2. **High Test Benchmark Interpretation:** The model's 100% test accuracy benchmark reflects clear synthetic separability between unambiguous rear-end collisions with statutory citations and single-vehicle accidents. Real-world commercial deployment on unstructured, noisy handwriting and disputed multi-vehicle statements typically exhibits 82–89% F1-scores.
3. **Retraining Frequency:** Models should be retrained semi-annually with verified closed file recovery settlements to adjust for regional arbitration trends.

---

## 3. Document Intelligence & RAG Retrieval Safeguards

1. **OCR Quality Dependencies:** Document parsing assumes legible PDF text layers or high-resolution police crash report scans. Heavily degraded thermal faxes or illegible handwritten officer diagrams require manual adjuster transcription.
2. **Attribution Guarantee:** SubroRecover AI strictly separates verified law enforcement findings from self-reported claims and prohibits AI model hallucination of statutory citations or claim amounts.

---

## 4. Technical & Environmental Boundaries

1. **Database Fallback Mode:** In local development environments without an active PostgreSQL daemon, the application gracefully operates on an embedded SQLite database (`subro_recover.db`). Production carrier deployments should migrate to PostgreSQL with `pgvector` and connection pooling enabled.
2. **LLM Connectivity:** When external Gemini API access is unavailable or offline, the platform seamlessly defaults to rule-grounded deterministic analytical simulations, explicitly labeling all outputs as `LOCAL_DETERMINISTIC_RULES` in audit logs.
