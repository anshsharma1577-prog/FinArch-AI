import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import re
import pytesseract
from PIL import Image
import google.generativeai as genai

# ── CONFIG ──────────────────────────────────────────────────────────────────
# 👇 Set your Tesseract path (Windows default shown below)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 👇 Paste your Google Gemini API key here
# Get a free key at: https://aistudio.google.com
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

st.set_page_config(
    page_title="💰 AI Financial Advisor — India",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLING ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border: 1px solid #3d4270;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #4ade80; }
    .metric-label { font-size: 13px; color: #9ca3af; margin-top: 4px; }
    .chat-user {
        background: #1e3a5f;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        border-left: 3px solid #3b82f6;
    }
    .chat-ai {
        background: #1a2e1a;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        border-left: 3px solid #4ade80;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        color: #f9fafb;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #3d4270;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
    }
    div[data-testid="stSidebarContent"] { background-color: #1a1d2e; }
    .advice-box {
        background: #1a2e1a;
        border: 1px solid #166534;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    .warning-box {
        background: #2d1b00;
        border: 1px solid #92400e;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    .success-box {
        background: #1a2e1a;
        border: 1px solid #4ade80;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    .ocr-box {
        background: #1e2130;
        border: 2px dashed #3d4270;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "goals" not in st.session_state:
    st.session_state.goals = []
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = {}
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "ocr_pending" not in st.session_state:
    st.session_state.ocr_pending = None

# ── CATEGORIES ────────────────────────────────────────────────────────────────
CATEGORIES = [
    "🍛 Food & Dining", "🚗 Transport", "🛒 Groceries",
    "🏠 Rent & Housing", "💡 Utilities & Bills", "🏥 Health & Medical",
    "📚 Education", "👗 Shopping & Clothing", "🎬 Entertainment",
    "✈️ Travel", "💳 EMI & Loans", "📱 Mobile & Internet",
    "🙏 Religious & Charity", "💰 Savings & Investment",
    "🔧 Maintenance", "📦 Other"
]

GURUS = {
    "Warren Buffett": "value investing, long-term thinking, buying quality assets cheap",
    "Robert Kiyosaki": "assets vs liabilities, real estate, passive income",
    "Ramit Sethi": "automation, conscious spending, negotiating bills",
    "Indian SIP Philosophy": "systematic investment plans, mutual funds, rupee cost averaging",
    "Benjamin Graham": "margin of safety, intrinsic value, defensive investing"
}

# ── TESSERACT OCR FUNCTION ────────────────────────────────────────────────────
def extract_from_screenshot(uploaded_file):
    image = Image.open(uploaded_file)
    extracted_text = pytesseract.image_to_string(image)
    st.info(f"📝 Raw OCR text:\n{extracted_text}")

    # Parse amount
    amount = 0.0
    amount_patterns = [
        r'₹\s*([\d,]+\.?\d*)',
        r'Rs\.?\s*([\d,]+\.?\d*)',
        r'INR\s*([\d,]+\.?\d*)',
        r'Amount[:\s]+([\d,]+\.?\d*)',
        r'Total[:\s]+₹?\s*([\d,]+\.?\d*)',
        r'Paid[:\s]+₹?\s*([\d,]+\.?\d*)',
        r'\b([\d,]+\.\d{2})\b',
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
                if amount > 0:
                    break
            except:
                continue

    # Parse date
    date_str = ""
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s+\w+\s+\d{2,4}',
        r'\w+\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}\s+\w{3}\s+\d{2,4}',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, extracted_text)
        if match:
            date_str = match.group(0)
            break

    # Detect merchant
    merchant = ""
    for pattern in [r'Paid to\s+([A-Za-z0-9\s&]+)', r'To\s+([A-Za-z0-9\s&]+)', r'Merchant[:\s]+([A-Za-z0-9\s&]+)']:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            merchant = match.group(1).strip()[:30]
            break

    # Auto categorize
    text_lower = extracted_text.lower()
    category = "Other"
    if any(k in text_lower for k in ["swiggy", "zomato", "restaurant", "food", "cafe", "pizza", "burger"]):
        category = "Food"
    elif any(k in text_lower for k in ["uber", "ola", "rapido", "metro", "bus", "petrol", "fuel", "cab"]):
        category = "Transport"
    elif any(k in text_lower for k in ["amazon", "flipkart", "myntra", "shop", "store", "mall"]):
        category = "Shopping"
    elif any(k in text_lower for k in ["electricity", "water", "gas", "bill", "recharge", "broadband"]):
        category = "Bills"
    elif any(k in text_lower for k in ["hospital", "medical", "pharmacy", "doctor", "clinic"]):
        category = "Medical"
    elif any(k in text_lower for k in ["netflix", "hotstar", "spotify", "prime", "entertainment", "movie", "jiohotstar"]):
        category = "Entertainment"
    elif any(k in text_lower for k in ["grocer", "vegetables", "bigbasket", "blinkit", "zepto"]):
        category = "Groceries"
    elif any(k in text_lower for k in ["school", "college", "course", "tuition", "education"]):
        category = "Education"

    # Detect payment method
    payment_method = "UPI"
    if any(k in text_lower for k in ["credit card"]):
        payment_method = "Card"
    elif any(k in text_lower for k in ["debit card"]):
        payment_method = "Card"
    elif any(k in text_lower for k in ["net banking", "netbanking"]):
        payment_method = "Net Banking"
    elif "cash" in text_lower:
        payment_method = "Cash"

    return {
        "amount": amount,
        "category": category,
        "note": f"Payment to {merchant}" if merchant else "UPI Payment",
        "payment_method": payment_method,
        "merchant": merchant,
        "date": date_str,
    }

# ── BUILD CONTEXT ─────────────────────────────────────────────────────────────
def build_context(expenses, profile, guru):
    expense_summary = ""
    if expenses:
        df = pd.DataFrame(expenses)
        by_cat = df.groupby("category")["amount"].sum().to_dict()
        total = df["amount"].sum()
        expense_summary = f"\nUser expense summary:\nTotal spent: ₹{total:,.0f}\nBy category: {json.dumps(by_cat, ensure_ascii=False)}"

    profile_text = ""
    if profile:
        profile_text = f"\nUser profile: Income ₹{profile.get('income',0):,}/month, City: {profile.get('city','India')}, Age: {profile.get('age','N/A')}, Occupation: {profile.get('occupation','')}, Risk: {profile.get('risk','Moderate')}, Goals: {profile.get('goals_text','')}"

    return f"""You are an expert Indian financial advisor AI. Give personalized practical advice for Indian users.
You know deeply about:
- Indian tax: 80C, 80D, HRA, LTA deductions, new vs old tax regime
- Investments: PPF, ELSS, SIP, NPS, FD, RD, NSC, Sukanya Samriddhi Yojana
- Stock market: NSE, BSE, Nifty50, Sensex, Nifty Next 50
- UPI: PhonePe, Google Pay, Paytm, BHIM
- Banks: SBI, HDFC, ICICI, Axis, Kotak, Yes Bank
- Insurance: LIC, term insurance, health insurance, PMJJBY
- Mutual funds: Zerodha Coin, Groww, ET Money, Paytm Money
- Indian salary: CTC, in-hand, EPF, gratuity, HRA
- Real estate: home loans, PMAY scheme
- Indian economy: inflation ~5-6%, RBI repo rate

Philosophy to follow: {guru} — {GURUS[guru]}

Rules:
- Always use ₹ and Indian format (lakhs, crores)
- Give specific actionable advice with real Indian product names
- Be concise and clear
- End with: ⚠️ Educational advice only. Consult a SEBI-registered advisor for major decisions.
{expense_summary}
{profile_text}"""

# ── AI CHAT FUNCTION ──────────────────────────────────────────────────────────
def get_ai_advice(user_message, expenses, profile, guru):
    try:
        system_context = build_context(expenses, profile, guru)
        history_text = ""
        for msg in st.session_state.chat_history[-6:]:
            role = "User" if msg["role"] == "user" else "Advisor"
            history_text += f"{role}: {msg['content']}\n"
        full_prompt = f"{system_context}\n\nConversation so far:\n{history_text}\nUser: {user_message}\nAdvisor:"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error getting advice: {str(e)}"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 AI Financial Advisor")
    st.markdown("*Your personal India finance expert*")
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Dashboard",
        "💬 AI Advisor Chat",
        "📸 Screenshot OCR",
        "➕ Add Expense",
        "📊 Analytics",
        "🎯 Financial Goals",
        "📋 Budget Planner",
        "🧑 My Profile"
    ])

    st.divider()
    st.markdown("### 🧠 Choose Your Guru")
    selected_guru = st.selectbox("Financial Philosophy", list(GURUS.keys()), index=3)
    st.caption(f"*{GURUS[selected_guru][:60]}...*")

    if st.session_state.expenses:
        total = sum(e["amount"] for e in st.session_state.expenses)
        st.divider()
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Expenses", f"₹{total:,.0f}")
        st.metric("Transactions", len(st.session_state.expenses))

# ════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown('<div class="section-title">🏠 Financial Dashboard</div>', unsafe_allow_html=True)

    profile = st.session_state.profile
    income = profile.get("income", 0)
    expenses = st.session_state.expenses
    total_spent = sum(e["amount"] for e in expenses)
    savings = income - total_spent if income > 0 else 0
    savings_rate = (savings / income * 100) if income > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">₹{income:,.0f}</div>
            <div class="metric-label">Monthly Income</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171;">₹{total_spent:,.0f}</div>
            <div class="metric-label">Total Spent</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        color = "#4ade80" if savings >= 0 else "#f87171"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color};">₹{abs(savings):,.0f}</div>
            <div class="metric-label">{"Savings" if savings >= 0 else "Overspent"}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        color = "#4ade80" if savings_rate >= 20 else "#fbbf24" if savings_rate >= 10 else "#f87171"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color};">{savings_rate:.1f}%</div>
            <div class="metric-label">Savings Rate</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if expenses:
        df = pd.DataFrame(expenses)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🥧 Spending by Category")
            cat_data = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(cat_data, values="amount", names="category",
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white", showlegend=True, height=350)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### 📅 Daily Spending Trend")
            df["date"] = pd.to_datetime(df["date"])
            daily = df.groupby("date")["amount"].sum().reset_index()
            fig2 = px.line(daily, x="date", y="amount", color_discrete_sequence=["#3b82f6"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white", height=350,
                               xaxis=dict(gridcolor="#2d3748"), yaxis=dict(gridcolor="#2d3748"))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### 📋 Recent Transactions")
        recent = df.tail(8).sort_values("date", ascending=False)
        for _, row in recent.iterrows():
            col_a, col_b, col_c = st.columns([3, 2, 2])
            with col_a: st.write(f"{row['category']}")
            with col_b: st.write(f"₹{row['amount']:,.0f}")
            with col_c: st.write(f"{str(row.get('note',''))[:30]}")
    else:
        st.info("👆 Go to **📸 Screenshot OCR** or **➕ Add Expense** to start!")
        tips = [
            "📌 Follow the **50-30-20 rule**: 50% needs, 30% wants, 20% savings",
            "📌 Start a **SIP with just ₹500/month** — small amounts grow big",
            "📌 Use **Section 80C** to save up to ₹46,800 in taxes annually",
            "📌 Emergency fund = **6 months of expenses** in a liquid fund",
            "📌 **Term insurance** at 25 is far cheaper than at 35 — buy early",
            "📌 **UPI spends** are easy to forget — track every transaction",
        ]
        for tip in tips:
            st.markdown(tip)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: AI ADVISOR CHAT
# ════════════════════════════════════════════════════════════════════════════
elif page == "💬 AI Advisor Chat":
    st.markdown('<div class="section-title">💬 AI Financial Advisor</div>', unsafe_allow_html=True)
    st.caption(f"Powered by Google Gemini | Philosophy: **{selected_guru}**")

    quick_questions = [
        "How should I start investing with ₹5,000/month?",
        "What is the best way to save tax in India?",
        "How does SIP work and which fund should I choose?",
        "What is PPF and should I invest in it?",
        "How do I create an emergency fund?",
        "Should I buy term insurance or LIC policy?",
        "How to pay off my credit card debt fast?",
        "What is ELSS and how does it save tax?",
    ]

    st.markdown("#### ⚡ Quick Questions — Click Any")
    cols = st.columns(4)
    for i, q in enumerate(quick_questions):
        if cols[i % 4].button(q[:32] + "...", key=f"quick_{i}"):
            with st.spinner("Getting advice..."):
                response = get_ai_advice(q, st.session_state.expenses, st.session_state.profile, selected_guru)
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    st.markdown("---")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 <b>AI Advisor:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    user_input = st.text_area("Ask your financial question:",
                               placeholder="e.g. How much should I save every month?", height=80)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("💬 Get Advice", use_container_width=True):
            if user_input.strip():
                with st.spinner("Thinking..."):
                    response = get_ai_advice(user_input, st.session_state.expenses, st.session_state.profile, selected_guru)
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SCREENSHOT OCR
# ════════════════════════════════════════════════════════════════════════════
elif page == "📸 Screenshot OCR":
    st.markdown('<div class="section-title">📸 Screenshot Expense Extractor (OCR)</div>', unsafe_allow_html=True)
    st.caption("Upload any payment screenshot — Tesseract OCR reads it locally, no API needed!")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📤 Upload Screenshot")
        st.markdown("""
        **Supported screenshots:**
        - 📱 PhonePe payment receipt
        - 💚 Google Pay (GPay) receipt
        - 💙 Paytm payment screen
        - 🟠 BHIM UPI confirmation
        - 🏦 Bank app transaction
        - 🧾 ATM / shop receipt photo
        """)
        uploaded_file = st.file_uploader("Drop your screenshot here", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            st.image(uploaded_file, caption="Your Screenshot", use_container_width=True)
            if st.button("🔍 Extract Expense with OCR", use_container_width=True):
                with st.spinner("🔍 Tesseract is reading your screenshot..."):
                    try:
                        uploaded_file.seek(0)
                        data = extract_from_screenshot(uploaded_file)
                        amt = float(data.get("amount", 0))
                        st.session_state.ocr_pending = {
                            "amount": amt,
                            "category": data.get("category", "Other"),
                            "note": data.get("note", ""),
                            "merchant": data.get("merchant", ""),
                            "payment": data.get("payment_method", "UPI"),
                            "date": data.get("date", "")
                        }
                        if amt > 0:
                            st.success("✅ Successfully extracted!")
                        else:
                            st.warning("⚠️ Amount not detected — please enter it manually.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not read screenshot. Error: {str(e)}")

    with col2:
        st.markdown("#### ✏️ Review & Confirm")
        if st.session_state.ocr_pending:
            pending = st.session_state.ocr_pending
            st.markdown('<div class="success-box">✅ OCR done! Review & confirm:</div>', unsafe_allow_html=True)
            confirmed_amount = st.number_input("Amount (₹)", value=float(pending["amount"]), step=1.0, min_value=0.0)
            cat_index = 0
            for i, c in enumerate(CATEGORIES):
                if pending["category"].lower() in c.lower():
                    cat_index = i
                    break
            confirmed_cat = st.selectbox("Category", CATEGORIES, index=cat_index)
            default_note = f"{pending['merchant']} — {pending['note']}".strip(" —")
            confirmed_note = st.text_input("Description", value=default_note)
            confirmed_pay = st.selectbox("Payment Method",
                ["UPI (PhonePe/GPay/Paytm)", "Cash", "Credit Card", "Debit Card", "Net Banking", "EMI"])
            try:
                default_date = datetime.strptime(pending["date"], "%d %b %y").date() if pending["date"] else date.today()
            except:
                default_date = date.today()
            confirmed_date = st.date_input("Date", value=default_date)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Add to Expenses", use_container_width=True):
                    if confirmed_amount > 0:
                        st.session_state.expenses.append({
                            "amount": confirmed_amount, "category": confirmed_cat,
                            "date": str(confirmed_date), "payment": confirmed_pay, "note": confirmed_note
                        })
                        st.session_state.ocr_pending = None
                        st.success("✅ Expense added!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Please enter a valid amount!")
            with col_b:
                if st.button("❌ Discard", use_container_width=True):
                    st.session_state.ocr_pending = None
                    st.rerun()
        else:
            st.markdown("""
            <div class="ocr-box">
                <h3>👈 Upload a screenshot</h3>
                <p style="color:#9ca3af;">Tesseract OCR will read it locally on your PC</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### 📱 Or Paste UPI/Bank SMS")
            sms_text = st.text_area("Paste your SMS here:", height=100,
                placeholder="Rs.450.00 debited from A/c XX1234 on 15-01-25 by UPI. -SBI")
            if st.button("🔍 Extract from SMS", use_container_width=True):
                if sms_text.strip():
                    amount = 0.0
                    for p in [r'Rs\.?\s*([\d,]+\.?\d*)', r'INR\s*([\d,]+\.?\d*)', r'₹\s*([\d,]+\.?\d*)']:
                        m = re.search(p, sms_text, re.IGNORECASE)
                        if m:
                            try:
                                amount = float(m.group(1).replace(',', ''))
                                break
                            except:
                                pass
                    text_lower = sms_text.lower()
                    category = "Other"
                    if any(k in text_lower for k in ["food", "swiggy", "zomato"]):
                        category = "Food"
                    elif any(k in text_lower for k in ["uber", "ola", "petrol"]):
                        category = "Transport"
                    elif any(k in text_lower for k in ["bill", "recharge", "electric"]):
                        category = "Bills"
                    st.session_state.ocr_pending = {
                        "amount": amount, "category": category,
                        "note": "SMS transaction", "merchant": "", "payment": "UPI", "date": ""
                    }
                    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PAGE: ADD EXPENSE
# ════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Expense":
    st.markdown('<div class="section-title">➕ Add Expense Manually</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Enter Details")
        amount = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0)
        category = st.selectbox("Category", CATEGORIES)
        expense_date = st.date_input("Date", value=date.today())
        payment_method = st.selectbox("Payment Method",
            ["UPI (PhonePe/GPay/Paytm)", "Cash", "Credit Card", "Debit Card", "Net Banking", "EMI"])
        note = st.text_input("Note (optional)", placeholder="e.g. Lunch at office, Uber to airport")
        if st.button("✅ Add Expense"):
            st.session_state.expenses.append({
                "amount": amount, "category": category,
                "date": str(expense_date), "payment": payment_method, "note": note
            })
            st.success(f"✅ Added ₹{amount:,.0f} for {category}")
            st.rerun()
    with col2:
        st.markdown("#### 📋 Recent Expenses")
        if st.session_state.expenses:
            df = pd.DataFrame(st.session_state.expenses)
            recent = df.tail(10).sort_values("date", ascending=False)
            for _, row in recent.iterrows():
                st.markdown(f"**{row['category']}** — ₹{row['amount']:,.0f} — {str(row.get('note',''))[:25]}")
            st.markdown("---")
            if st.button("🗑️ Clear All Expenses"):
                st.session_state.expenses = []
                st.rerun()
        else:
            st.info("No expenses yet!")
    if st.session_state.expenses:
        st.markdown("---")
        st.markdown("#### 📋 All Expenses")
        df = pd.DataFrame(st.session_state.expenses)
        df_display = df.copy()
        df_display["amount"] = df_display["amount"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(df_display, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    st.markdown('<div class="section-title">📊 Spending Analytics</div>', unsafe_allow_html=True)
    if not st.session_state.expenses:
        st.info("Add some expenses first to see analytics!")
    else:
        df = pd.DataFrame(st.session_state.expenses)
        df["date"] = pd.to_datetime(df["date"])
        total = df["amount"].sum()
        avg_txn = df["amount"].mean()
        top_cat = df.groupby("category")["amount"].sum().idxmax()
        top_amount = df.groupby("category")["amount"].sum().max()
        avg_daily = df.groupby("date")["amount"].sum().mean()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{total:,.0f}</div><div class="metric-label">Total Spent</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{avg_txn:,.0f}</div><div class="metric-label">Avg Transaction</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="font-size:16px;">{top_cat[:20]}</div><div class="metric-label">Top Category</div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            cat_data = df.groupby("category")["amount"].sum().sort_values(ascending=True).reset_index()
            fig = px.bar(cat_data, x="amount", y="category", orientation="h",
                         title="Spending by Category (₹)", color="amount", color_continuous_scale="Blues")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            pay_data = df.groupby("payment")["amount"].sum().reset_index()
            fig2 = px.pie(pay_data, values="amount", names="payment", title="Payment Method Breakdown",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
            st.plotly_chart(fig2, use_container_width=True)

        daily = df.groupby("date")["amount"].sum().reset_index()
        fig3 = px.area(daily, x="date", y="amount", title="Daily Spending Trend", color_discrete_sequence=["#3b82f6"])
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300,
                           xaxis=dict(gridcolor="#2d3748"), yaxis=dict(gridcolor="#2d3748"))
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown(f"""<div class="warning-box">⚠️ <b>Spending Alert:</b> Your highest category is <b>{top_cat}</b> at ₹{top_amount:,.0f}. Average daily: ₹{avg_daily:,.0f}.</div>""", unsafe_allow_html=True)

        with st.spinner("🤖 Getting AI analysis..."):
            analysis = get_ai_advice("Analyze my spending and give me 3 specific tips to reduce expenses and save more. Be specific to Indian context.",
                st.session_state.expenses, st.session_state.profile, selected_guru)
        st.markdown(f'<div class="advice-box">🤖 <b>AI Spending Analysis:</b><br><br>{analysis}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: FINANCIAL GOALS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Financial Goals":
    st.markdown('<div class="section-title">🎯 Financial Goals</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ➕ Add New Goal")
        goal_name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund, Europe Trip")
        goal_target = st.number_input("Target Amount (₹)", min_value=1000.0, value=50000.0, step=1000.0)
        goal_saved = st.number_input("Already Saved (₹)", min_value=0.0, value=0.0, step=500.0)
        goal_deadline = st.date_input("Target Date")
        goal_category = st.selectbox("Goal Type", ["🏦 Emergency Fund", "✈️ Travel", "🏠 Home", "📱 Gadget", "🎓 Education", "💍 Wedding", "🚗 Vehicle", "📈 Investment", "🎁 Other"])
        if st.button("➕ Add Goal"):
            if goal_name:
                st.session_state.goals.append({"name": goal_name, "target": goal_target, "saved": goal_saved, "deadline": str(goal_deadline), "type": goal_category})
                st.success(f"✅ Goal '{goal_name}' added!")
                st.rerun()
    with col2:
        st.markdown("#### 🎯 Your Goals")
        if st.session_state.goals:
            for i, goal in enumerate(st.session_state.goals):
                progress = min((goal["saved"] / goal["target"]) * 100, 100)
                remaining = goal["target"] - goal["saved"]
                st.markdown(f"**{goal['type']} — {goal['name']}**")
                st.progress(progress / 100)
                st.caption(f"₹{goal['saved']:,.0f} of ₹{goal['target']:,.0f} — ₹{remaining:,.0f} to go — Due: {goal['deadline']}")
                if st.button("🗑️ Remove", key=f"del_goal_{i}"):
                    st.session_state.goals.pop(i)
                    st.rerun()
                st.markdown("---")
        else:
            st.info("No goals yet. Add your first financial goal!")

    if st.session_state.goals:
        with st.spinner("Getting goal-based advice..."):
            goals_text = ", ".join([f"{g['name']} (₹{g['target']:,.0f} by {g['deadline']})" for g in st.session_state.goals])
            advice = get_ai_advice(f"I have these goals: {goals_text}. Give me a practical monthly savings plan using Indian options like SIP, RD, liquid funds.",
                st.session_state.expenses, st.session_state.profile, selected_guru)
        st.markdown(f'<div class="advice-box">🤖 <b>AI Goal Planning:</b><br><br>{advice}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: BUDGET PLANNER
# ════════════════════════════════════════════════════════════════════════════
elif page == "📋 Budget Planner":
    st.markdown('<div class="section-title">📋 Monthly Budget Planner</div>', unsafe_allow_html=True)
    income = st.session_state.profile.get("income", 0)
    if income == 0:
        st.warning("⚠️ Please set your monthly income in **🧑 My Profile** first!")

    st.markdown("#### Set Monthly Budget per Category")
    budgets = {}
    cols = st.columns(2)
    for i, cat in enumerate(CATEGORIES):
        with cols[i % 2]:
            budgets[cat] = st.number_input(f"{cat}", min_value=0.0, value=float(st.session_state.monthly_budget.get(cat, 0.0)), step=500.0, key=f"budget_{i}")

    if st.button("💾 Save Budget"):
        st.session_state.monthly_budget = budgets
        st.success("✅ Budget saved!")

    total_budgeted = sum(budgets.values())
    if income > 0:
        unallocated = income - total_budgeted
        color = "🟢" if unallocated >= 0 else "🔴"
        st.markdown(f"**Budgeted:** ₹{total_budgeted:,.0f} | **Income:** ₹{income:,.0f} | {color} **Unallocated:** ₹{unallocated:,.0f}")

    if st.session_state.expenses and st.session_state.monthly_budget:
        st.markdown("#### 📊 Budget vs Actual")
        df = pd.DataFrame(st.session_state.expenses)
        actual = df.groupby("category")["amount"].sum().to_dict()
        rows = []
        for cat, budget in st.session_state.monthly_budget.items():
            if budget > 0:
                spent = actual.get(cat, 0)
                rows.append({"Category": cat, "Budget (₹)": budget, "Spent (₹)": spent, "Remaining (₹)": budget - spent, "Status": "✅ OK" if spent <= budget else "❌ Over Budget"})
        if rows:
            result_df = pd.DataFrame(rows)
            fig = go.Figure(data=[
                go.Bar(name="Budget", x=result_df["Category"], y=result_df["Budget (₹)"], marker_color="#3b82f6"),
                go.Bar(name="Spent", x=result_df["Category"], y=result_df["Spent (₹)"], marker_color="#f87171")
            ])
            fig.update_layout(barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(result_df, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: MY PROFILE
# ════════════════════════════════════════════════════════════════════════════
elif page == "🧑 My Profile":
    st.markdown('<div class="section-title">🧑 My Financial Profile</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name", value=st.session_state.profile.get("name", ""))
        age = st.number_input("Age", min_value=18, max_value=80, value=int(st.session_state.profile.get("age", 25)))
        city = st.selectbox("City", ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Surat", "Jaipur", "Lucknow", "Chandigarh", "Indore", "Bhopal", "Nagpur", "Visakhapatnam", "Coimbatore", "Other"])
        income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(st.session_state.profile.get("income", 30000)), step=1000.0)
    with col2:
        occupation = st.selectbox("Occupation", ["Salaried (Private)", "Salaried (Government)", "Self-Employed", "Business Owner", "Student", "Freelancer", "Homemaker"])
        dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, value=int(st.session_state.profile.get("dependents", 0)))
        risk = st.select_slider("Risk Appetite", options=["Very Low", "Low", "Moderate", "High", "Very High"], value=st.session_state.profile.get("risk", "Moderate"))
        goals_text = st.text_area("Your Financial Goals", value=st.session_state.profile.get("goals_text", ""), placeholder="e.g. Buy a house in 5 years, retire at 50")

    existing_investments = st.multiselect("Existing Investments", ["PPF", "EPF", "ELSS", "Mutual Funds SIP", "Fixed Deposit", "Stocks", "Real Estate", "Gold", "NPS", "LIC Policy", "None"])
    existing_loans = st.multiselect("Existing Loans/EMIs", ["Home Loan", "Car Loan", "Personal Loan", "Education Loan", "Credit Card Debt", "None"])

    if st.button("💾 Save Profile & Generate Report"):
        st.session_state.profile = {"name": name, "age": age, "city": city, "income": income, "occupation": occupation, "dependents": dependents, "risk": risk, "goals_text": goals_text, "investments": existing_investments, "loans": existing_loans}
        st.success("✅ Profile saved!")
        st.rerun()

    if st.session_state.profile.get("name"):
        with st.spinner("🤖 Generating your personalized financial report..."):
            report = get_ai_advice("Based on my complete profile, give me a financial health assessment and top 5 action items for this month. Format with clear sections.",
                st.session_state.expenses, st.session_state.profile, selected_guru)
        st.markdown("#### 📋 Your Personalized Financial Report")
        st.markdown(f'<div class="advice-box">{report}</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#6b7280; font-size:12px;">
⚠️ Educational tool only. Consult a SEBI-registered advisor for major decisions.<br>
💰 AI Financial Advisor India | Tesseract OCR + Google Gemini AI + Streamlit | Your data stays on your device
</p>
""", unsafe_allow_html=True)
