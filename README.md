# 🏛️ FinArch-AI — Intelligent Financial Advisor & Expense Manager

> An AI-powered personal finance assistant built specifically for Indian users.  
> Track expenses via screenshots, get personalized financial advice, plan budgets, and achieve financial goals — all in one app.

---

## 🚨 Problem Statement

Indians collectively lose billions of rupees annually to poor financial decisions — not from a lack of income, but from a lack of awareness. The average Indian salaried professional juggles UPI payments across PhonePe, Google Pay, and Paytm; shares expenses on Splitwise; receives bank SMS alerts; and still has no unified picture of where their money is actually going.

Existing apps like Walnut or Money Manager require manual entry, lack conversational intelligence, and offer zero personalized advice. Meanwhile, certified financial advisors remain inaccessible to middle-income earners. The result: impulsive spending, missed SIP investments, no tax-saving strategy, and zero wealth building — despite stable income.

**The core gap:** No tool exists that can automatically read a user's financial footprint from screenshots and messages, understand it, and then coach them with actionable, India-specific guidance rooted in proven financial philosophies.

**FinArch-AI solves this.**

---

## 🎯 Project Overview

**FinArch-AI** is a **Track A — Personal Finance Assistant** built as part of the Capabl AI Agent Development Project. It combines **Tesseract OCR** for reading payment screenshots, **Google Gemini AI** for personalized financial advice, and **Streamlit** for a clean interactive dashboard — designed specifically for the Indian financial ecosystem.

The name **FinArch** stands for **Financial Architecture** — helping users build a strong foundation for their financial future.

---

## ✨ Features

### 🏠 Dashboard
- Real-time summary of monthly income, total spending, savings, and savings rate
- Pie chart of spending by category
- Daily spending trend line chart
- Recent transactions table

### 💬 AI Advisor Chat
- Powered by **Google Gemini 2.0 Flash**
- 5 financial guru philosophies to choose from:
  - Warren Buffett (Value Investing)
  - Robert Kiyosaki (Assets vs Liabilities)
  - Ramit Sethi (Conscious Spending)
  - Indian SIP Philosophy (Mutual Funds & SIP)
  - Benjamin Graham (Defensive Investing)
- 8 quick-question shortcuts for common Indian finance topics
- Full conversation history with context awareness
- Advice covers: SIP, PPF, ELSS, NPS, 80C tax saving, term insurance, emergency funds, UPI spending, and more

### 📸 Screenshot OCR
- Upload **PhonePe, GPay, Paytm, BHIM, Bank app** screenshots
- **Tesseract OCR** extracts: amount, merchant name, date, payment method
- Auto-categorizes into: Food, Transport, Shopping, Bills, Medical, Entertainment, Groceries, Education
- Review and confirm extracted data before saving
- Also supports **UPI/Bank SMS paste** for text-based extraction

### ➕ Add Expense Manually
- Add expenses with category, date, payment method, and notes
- 16 Indian expense categories with emoji labels
- View and clear all expenses in a table

### 📊 Analytics
- Horizontal bar chart: spending by category
- Pie chart: payment method breakdown (UPI vs Cash vs Card)
- Area chart: daily spending trend
- AI-generated spending analysis with 3 specific Indian saving tips

### 🎯 Financial Goals
- Set goals with target amount, saved amount, and deadline
- Visual progress bars for each goal
- Goal types: Emergency Fund, Travel, Home, Gadget, Education, Wedding, Vehicle, Investment
- AI generates a monthly savings plan using SIP, RD, and liquid funds

### 📋 Budget Planner
- Set monthly budgets for all 16 categories
- Budget vs Actual comparison bar chart
- Remaining/overspent status for each category
- Income vs total budgeted tracking

### 🧑 My Profile
- Personal details: name, age, city, income, occupation
- Risk appetite slider
- Existing investments and loans tracker
- Auto-generates a personalized financial health report with top 5 action items

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend & UI | Streamlit |
| AI / LLM | Google Gemini 2.0 Flash |
| OCR Engine | Tesseract OCR + Pytesseract |
| Image Processing | Pillow (PIL) |
| Data Processing | Pandas |
| Charts | Plotly Express + Plotly Graph Objects |
| Language | Python 3.10+ |
| Deployment | Streamlit Cloud |

---

## 📋 Requirements

### System Requirements
- Python 3.10 or higher
- Tesseract OCR installed on your system
- Windows / Mac / Linux

### Python Libraries
```
streamlit
pandas
plotly
google-generativeai
pytesseract
Pillow
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/FinArch-AI.git
cd FinArch-AI
```

### Step 2 — Install Python Dependencies
```bash
pip install streamlit pandas plotly google-generativeai pytesseract Pillow
```

### Step 3 — Install Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it — default path is `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. FinArch-AI is already configured for this path

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

### Step 4 — Get Free Google Gemini API Key
1. Go to **https://aistudio.google.com**
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy the key (starts with `AIzaSy...`)
5. Paste it in `app.py` at this line:
```python
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

### Step 5 — Run FinArch-AI
```bash
streamlit run app.py
```
The app will open automatically at `http://localhost:8501`

---

## 🚀 Deployment on Streamlit Cloud

1. Push your code to GitHub (repo name: `FinArch-AI`)
2. Go to **https://share.streamlit.io**
3. Sign in with GitHub
4. Click **"New App"**
5. Select your `FinArch-AI` repository and `app.py`
6. Click **Deploy**
7. App will be live at `https://finarch-ai.streamlit.app`

---

## 📁 Project Structure

```
FinArch-AI/
│
├── app.py                  # Main application file
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## 📄 requirements.txt

```
streamlit
pandas
plotly
google-generativeai
pytesseract
Pillow
```

---

## 🇮🇳 Indian Finance Coverage

**FinArch-AI** is built specifically for Indian users and covers:

- **Tax Saving:** Section 80C, 80D, HRA, LTA, new vs old tax regime
- **Investments:** PPF, ELSS, SIP, NPS, FD, RD, NSC, Sukanya Samriddhi Yojana
- **Stock Market:** NSE, BSE, Nifty50, Sensex, Nifty Next 50
- **UPI Payments:** PhonePe, Google Pay, Paytm, BHIM
- **Banking:** SBI, HDFC, ICICI, Axis, Kotak, Yes Bank
- **Insurance:** LIC, term insurance, health insurance, PMJJBY
- **Platforms:** Zerodha, Groww, ET Money, Paytm Money
- **Salary:** CTC, in-hand, EPF, gratuity, HRA

---

## 📸 Supported Screenshot Types for OCR

| App | Supported |
|---|---|
| PhonePe | ✅ Yes |
| Google Pay (GPay) | ✅ Yes |
| Paytm | ✅ Yes |
| BHIM UPI | ✅ Yes |
| SBI / HDFC / ICICI Bank App | ✅ Yes |
| ATM Receipt Photo | ✅ Yes |
| Any UPI Confirmation Screen | ✅ Yes |

---

## 💡 How to Use FinArch-AI — Step by Step

1. **First time?** Go to **🧑 My Profile** → fill in your name, income, city, and goals
2. **Add expenses** → Use **📸 Screenshot OCR** to upload a payment screenshot OR **➕ Add Expense** to add manually
3. **Get advice** → Go to **💬 AI Advisor Chat** → ask any financial question in plain English
4. **Analyze spending** → **📊 Analytics** shows charts and AI tips to save more
5. **Set goals** → **🎯 Financial Goals** → plan for future savings targets
6. **Plan budget** → **📋 Budget Planner** → set monthly limits per category and track them

---

## 🔒 Privacy & Security

- ✅ All financial data stays **on your device only** — nothing is uploaded to any server
- ✅ OCR processing runs **locally** on your PC using Tesseract
- ✅ Gemini API receives only text prompts, never your raw financial images
- ✅ Session data is cleared automatically when you close the browser
- ✅ No user accounts, no database, no data retention

---

## ⚠️ Disclaimer

**FinArch-AI** is an **educational tool** designed to help users understand personal finance concepts. It does **not** constitute certified financial advice. Always consult a **SEBI-registered financial advisor** before making major investment or financial decisions.

---

## 👨‍💻 Developer

**Built as part of Capabl AI Agent Development Project — Track A**

- **Project Name:** FinArch-AI (Financial Architecture AI)
- **Domain:** Personal Finance Assistant & Expense Tracking Agent
- **APIs:** Google Gemini 2.0 Flash + Tesseract OCR
- **Framework:** Streamlit
- **Deployment:** Streamlit Cloud
- **Duration:** 8 Weeks | Track A → Track B

---

*🏛️ FinArch-AI | Financial Architecture for Every Indian | Powered by Google Gemini 2.0 Flash + Tesseract OCR + Streamlit*

