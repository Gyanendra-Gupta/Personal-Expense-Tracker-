from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yfinance as yf
import random
app = Flask(__name__)
# Predefined stock tickers
stock_tickers = {
    "AAPL": "Apple",
    "GOOGL": "Google",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "META": "Meta",
    "NVDA": "NVIDIA",
    "NFLX": "Netflix"
}

# Fetch live Bitcoin price
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return round(data['bitcoin']['usd'], 2)
    except Exception as e:
        print(f"Bitcoin API Error: {e}")
        return 0.0

# Fetch price for a single stock
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
    except:
        return None

# Save budget data to CSV
def save_to_csv(budget_data):
    df = pd.DataFrame(list(budget_data.items()), columns=['Category', 'Amount'])
    df.to_csv('personal_budget.csv', index=False)

# Generate bar and pie chart visualizations
def visualize_budget_data(budget_data):
    if not os.path.exists("static"):
        os.makedirs("static")

    categories = list(budget_data.keys())
    amounts = list(budget_data.values())

    # Bar Chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(categories, amounts, color='indigo')
    plt.title("Budget Overview", fontsize=20)
    plt.xlabel("Categories", fontsize=16)
    plt.ylabel("Amount (₹)", fontsize=16)
    plt.xticks(rotation=45)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 50, f'₹{int(yval)}', ha='center', fontsize=12)
    bar_path = "static/bar_chart.png"
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    # Pie Chart (Expenses only)
    expense_categories = [k for k in budget_data if k not in ['Income', 'Savings']]
    expense_values = [budget_data[k] for k in expense_categories]
    if sum(expense_values) > 0:
        plt.figure(figsize=(8, 8))
        plt.pie(expense_values, labels=expense_categories, autopct='%1.1f%%', startangle=140)
        plt.title("Expense Distribution", fontsize=18)
        pie_path = "static/pie_chart.png"
        plt.tight_layout()
        plt.savefig(pie_path)
        plt.close()
    else:
        pie_path = None

    return bar_path, pie_path

# Email Report Sender
def send_email_report(receiver_email, budget_data):
    sender_email = "saquibanjum010@gmail.com"
    sender_password = "nqzi djbz ctle touv"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Budget Summary Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Email HTML content
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="background-color: white; padding: 20px; border-radius: 10px;">
            <h2 style="color: #333;">💰 Budget Summary Report</h2>
            <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #2a9d8f; color: white;">
                    <th>Category</th><th>Amount (₹)</th>
                </tr>
    """
    for category, amount in budget_data.items():
        html += f"<tr><td>{category}</td><td>₹{amount:,.2f}</td></tr>"

    html += """
            </table>
            <p style="text-align:center;">Thanks for using <strong>Smart Budget Tracker</strong> 💡</p>
        </div>
    </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

# Tip based on savings
def get_savings_tip(savings, income):
    if income == 0:
        return "No income recorded."
    percent = (savings / income) * 100
    if percent >= 30:
        return "Great job! Consider investing your surplus."
    elif percent >= 15:
        return "Good! Try pushing it to 30% for better security."
    elif percent > 0:
        return "You're saving, but aim for at least 15% of income."
    else:
        return "You're overspending. Review your expenses."

# Detect major expense category
def get_major_expense(budget_data):
    expenses = {k: v for k, v in budget_data.items() if k not in ['Income', 'Savings']}
    if expenses:
        max_cat = max(expenses, key=expenses.get)
        return max_cat, expenses[max_cat]
    return "None", 0

# Landing Page
@app.route('/')
def home():
    return render_template('finance.html')

# Process Budget Form
@app.route('/track_budget', methods=['POST'])
def track_budget():
    try:
        form = request.form
        income = float(form.get('income', 0))
        rent = float(form.get('rent', 0))
        utilities = float(form.get('utilities', 0))
        groceries = float(form.get('groceries', 0))
        transport = float(form.get('transport', 0))
        entertainment = float(form.get('entertainment', 0))
        other_expenses = float(form.get('other_expenses', 0))
        email = form.get('email').strip()

        total_expenses = rent + utilities + groceries + transport + entertainment + other_expenses
        savings = income - total_expenses

        budget_data = {
            "Income": income,
            "Rent": rent,
            "Utilities": utilities,
            "Groceries": groceries,
            "Transport": transport,
            "Entertainment": entertainment,
            "Other Expenses": other_expenses,
            "Savings": savings
        }

        save_to_csv(budget_data)
        bar_chart, pie_chart = visualize_budget_data(budget_data)
        bitcoin_price = get_bitcoin_price()
        stock_price = get_stock_price("AAPL")
        savings_tip = get_savings_tip(savings, income)
        major_expense, major_amt = get_major_expense(budget_data)
        email_status = send_email_report(email, budget_data)

        return render_template('result.html',
                               budget_data=budget_data,
                               bar_chart=bar_chart,
                               pie_chart=pie_chart,
                               bitcoin_price=bitcoin_price,
                               stock_price=stock_price,
                               savings_tip=savings_tip,
                               major_expense=major_expense,
                               major_expense_amt=major_amt,
                               savings=savings,
                               email_status=email_status)
    except Exception as e:
        return f"<h2>Error: {e}</h2><a href='/'>Go Back</a>"

if __name__ == "__main__":
    app.run(debug=True)
