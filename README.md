# N1O1 Clinical Trials: Personalized Nitric Oxide Therapy Platform

N1O1 Clinical Trials is a comprehensive research platform built in collaboration with Dr. Nathan S. Bryan to support personalized nitric oxide therapy in patients with ischemic heart disease and other cardiovascular conditions.

### 🧠 Core Capabilities
- Simulates plasma nitrite (NO₂⁻) levels over time after dosing with N1O1 products (e.g., Lozenges, NO Beetz)
- Tracks individual patient responses using a PostgreSQL database
- Supports HillTau and compartmental pharmacokinetic models
- Includes an AI assistant (`N1O1ai`) to guide researchers and doctors through the app
- Features advanced AI-powered clinical tools for patient management

### 🔬 Use Cases
- Model the effect of NO supplementation over time
- Plan patient-specific dosing schedules
- Record clinical trial data including dose, plasma response, and simulation curves
- Generate AI-powered clinical notes, consent forms, and reports
- Ask N1O1ai anything about nitric oxide research, trial goals, or product use

### 🚀 Technologies Used
- Flask + SQLAlchemy + Flask-Migrate
- PostgreSQL database
- Chart.js for data visualization
- Electron (for desktop app)
- OpenAI and Anthropic Claude AI models (branded as `N1O1ai`)
- Responsive web design for mobile and desktop access

### 🧪 AI Clinical Tools (NEW)
The platform now includes advanced AI-powered clinical trial tools:

- **Pre-screening Analysis**: `/api/ai-tools/pre-screening` - Analyze patient eligibility for clinical trials based on inclusion/exclusion criteria
- **Clinical Note Generator**: `/api/ai-tools/generate-note` - Generate structured SOAP notes from visit data
- **Patient Sentiment Analysis**: `/api/ai-tools/patient-sentiment` - Analyze patient feedback for sentiment and key themes
- **Dynamic Consent Forms**: `/api/ai-tools/dynamic-consent` - Generate personalized consent forms based on patient demographics
- **AI Report Writer**: `/api/ai-tools/ai-report-writer` - Create detailed research reports from clinical trial data

### 🩺 For Clinical Researchers
This platform visualizes how nitric oxide supplements affect NO₂⁻ levels in various patient populations. It's designed to help clinicians evaluate patient responses, optimize treatment protocols, and streamline clinical trial workflows.

Visit `/patients`, `/simulations`, or access the AI assistant through the molecule icon in the corner of any page.