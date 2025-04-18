# Nitrite Dynamics: Personalized Nitric Oxide Therapy Assistant

Nitrite Dynamics is a clinical research app built by JustGoingViral in collaboration with Dr. Nathan S. Bryan to support personalized nitric oxide therapy in patients with ischemic heart disease.

### 🧠 What the App Does
- Simulates plasma nitrite (NO₂⁻) levels over time after dosing with N1O1 products (e.g., Lozenges, NO Beetz).
- Tracks individual patient responses using a PostgreSQL database.
- Supports HillTau and compartmental pharmacokinetic models.
- Includes an AI assistant (`N1O1ai`) to guide researchers and doctors through the app.

### 🔬 Use Cases
- Model the effect of NO supplementation over time.
- Plan patient-specific dosing schedules.
- Record clinical trial data including dose, plasma response, and simulation curves.
- Ask N1O1ai anything about nitric oxide research, trial goals, or product use.

### 🚀 Technologies Used
- Flask + SQLAlchemy + Flask-Migrate
- PostgreSQL
- Chart.js (coming soon)
- Electron (for desktop app)
- OpenAI (under the hood) — branded as `N1O1ai` and fully private-labeled

### 🩺 For Dr. Nathan Bryan
This app visualizes how nitric oxide supplements affect NO₂⁻ levels. It's designed to help clinicians evaluate patient responses, optimize protocols, and simplify clinical trial workflows.

Visit `/patients`, `/simulations`, or `/api/assistant` to interact with data and try the chatbot.