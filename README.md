# 🌎 EcoSphere: ESG Management & Gamification Platform

EcoSphere is a modern, unified ESG (Environmental, Social, Governance) Management Platform designed to measure, analyze, and improve corporate sustainability performance, promote employee CSR engagement, and track compliance audits.

---

## 🚀 Key Features & Modules

### 🍀 1. Environmental Module
- **Automated Carbon Accounting**: Simulates real-time integration with daily business operations (Fleet, Expense, Purchase, Manufacturing) to automatically calculate emissions.
- **Emission Factor Catalog**: Configure carbon factors (kg CO2 per unit) dynamically.
- **Sustainability Target Tracking**: Define environmental goals and monitor real-time progress relative to targets.

### 🤝 2. Social Module
- **CSR Campaigns Bulletin**: Community campaigns catalog with dynamic sign-ups.
- **Volunteer Approvals Drawer**: Review panel for CSR participation proofs.
- **Diversity & Demographics**: Interactive visualizations showing employee headcounts and departmental distribution.

### ⚖️ 3. Governance Module
- **Policy Document Hub**: Central repository for corporate governance policies with active "Read & Acknowledge" logs.
- **Internal Audits Register**: Record scores, auditor scopes, and key findings.
- **Compliance Issues Tracker**: Auto-flags open issues past due dates as "Overdue" and alerts owners.

### 🏆 4. Gamification Portal
- **Employee XP Leaderboard**: Dynamic ranking of employees based on XP gained from sustainability activities.
- **Challenges Lifecycle**: Manage active, draft, completed, and archived sustainability challenges.
- **Badges Showcase**: Award badges (Carbon Crusader, Eco Enthusiast) automatically on milestone completions.
- **Redemption Store**: Allow employees to trade earned points for catalog rewards (Solar Chargers, Extra Leave, etc.) with automatic inventory management.

---

## 🛠️ Technology Stack
- **Backend & Frontend**: Streamlit (Python)
- **Database**: SQLite
- **Charts & Visualization**: Altair, Pandas

---

## 💻 Getting Started

### 1. Install Dependencies
Make sure you have Python 3.10+ installed. In your terminal, run:
```bash
pip install streamlit pandas altair
```

### 2. Launch the Application
Start the Streamlit local development server:
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.
