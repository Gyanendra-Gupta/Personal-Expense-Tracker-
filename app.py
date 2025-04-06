from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

def get_bitcoin_price():
    """Fetch the current Bitcoin price in USD."""
    try:
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
        data = response.json()
        return round(float(data['bpi']['USD']['rate'].replace(',', '')), 2)
    except Exception as e:
        print("Bitcoin API Error:", e)
        return "Unavailable"

def get_stock_price(symbol="AAPL"):
    """Fetch the current stock price for the given symbol."""
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        response = requests.get(url)
        data = response.json()
        return round(data['quoteResponse']['result'][0]['regularMarketPrice'], 2)
    except Exception as e:
        print("Stock API Error:", e)
        return "Unavailable"


def save_to_csv(budget_data):
    """Save budget data to a CSV file."""
    df = pd.DataFrame(list(budget_data.items()), columns=['Category', 'Amount'])
    df.to_csv('personal_budget.csv', index=False)

def visualize_budget_data(budget_data):
    """Generate bar and pie charts for the budget data with enhanced font sizes."""
    if not os.path.exists("static"):
        os.makedirs("static")

    categories = list(budget_data.keys())
    amounts = list(budget_data.values())

    plt.figure(figsize=(12, 7), dpi=300)
    bars = plt.bar(categories, amounts, color='skyblue')

    plt.title("Personal Budget Tracker - Bar Chart", fontsize=20)
    plt.xlabel("Category", fontsize=16)
    plt.ylabel("Amount (₹)", fontsize=16)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)

    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'₹{height:,.0f}', 
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5),
                     textcoords="offset points",
                     ha='center',
                     fontsize=12,
                     color='black',
                     fontweight='bold')

    bar_chart_path = "static/bar_chart.png"
    plt.tight_layout()
    plt.savefig(bar_chart_path, bbox_inches='tight')
    plt.close()

    expense_categories = [k for k in budget_data if k not in ['Income', 'Savings']]
    expense_amounts = [budget_data[k] for k in expense_categories]
    pie_chart_path = None

    if sum(expense_amounts) > 0:
        plt.figure(figsize=(10, 10), dpi=300)
        plt.pie(expense_amounts, 
                labels=expense_categories,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': 14})
        plt.title("Expense Breakdown", fontsize=20)
        pie_chart_path = "static/pie_chart.png"
        plt.tight_layout()
        plt.savefig(pie_chart_path, bbox_inches='tight')
        plt.close()

    return bar_chart_path, pie_chart_path

def send_email_report(receiver_email, budget_data):
    sender_email = "sg4463217@gmail.com"
    sender_password ='btoj ghqe ajez zgcl' 

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Budget Summary Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    html = """
    <html>
    <head>
<style>
  /* Base styles */
  body {
      font-family: 'Arial', sans-serif;
      background: linear-gradient(to right, #f4f4f4, #e7f2f8);
      margin: 0;
      padding: 20px;
      animation: fadeInBackground 2s ease-in-out;
  }
  
  .container {
      max-width: 600px;
      margin: auto;
      background: #ffffff;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
      overflow: hidden;
      position: relative;
      animation: scaleUp 1s ease-in-out;
  }
  
  h2 {
      color: #333333;
      text-align: center;
      font-size: 1.8rem;
      margin-bottom: 16px;
      position: relative;
  }
  
  h2::after {
      content: '';
      display: block;
      width: 50px;
      height: 3px;
      background: #2a9d8f;
      margin: 10px auto;
      border-radius: 8px;
  }
  
  .budget-table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  .budget-table th, .budget-table td {
      border: 1px solid #dddddd;
      padding: 12px;
      text-align: left;
      transition: background-color 0.3s ease;
  }
  
  .budget-table th {
      background-color: #2a9d8f;
      color: #ffffff;
      font-weight: bold;
      text-transform: uppercase;
  }
  
  .budget-table tr:hover td {
      background-color: #e3f9f5;
  }
  
  .highlight {
      font-weight: bold;
      color: #e76f51;
      animation: highlightPulse 1.5s infinite;
  }
  
  /* Footer styles */
  .footer {
      text-align: center;
      margin-top: 20px;
      font-size: 0.9em;
      color: #666666;
      animation: fadeIn 1s ease-in-out;
  }
  
  .footer a {
      color: #2a9d8f;
      text-decoration: none;
      font-weight: bold;
  }
  
  .footer a:hover {
      text-decoration: underline;
  }
  
  /* Animations */
  @keyframes fadeInBackground {
      0% {
          opacity: 0;
      }
      100% {
          opacity: 1;
      }
  }
  
  @keyframes scaleUp {
      0% {
          transform: scale(0.9);
          opacity: 0;
      }
      100% {
          transform: scale(1);
          opacity: 1;
      }
  }
  
  @keyframes highlightPulse {
      0% {
          color: #e76f51;
      }
      50% {
          color: #f4a261;
      }
      100% {
          color: #e76f51;
      }
  }
  
  @keyframes fadeIn {
      from {
          opacity: 0;
          transform: translateY(10px);
      }
      to {
          opacity: 1;
          transform: translateY(0);
      }
  }
</style>

    </head>
    <body>
        <div class="container">
            <h2>💰 Budget Summary Report</h2>
            <table class="budget-table">
                <tr>
                    <th>Category</th>
                    <th>Amount (₹)</th>
                </tr>
    """

    for category, amount in budget_data.items():
        html += f"""
                <tr>
                    <td>{category}</td>
                    <td class="highlight">₹{amount:,.2f}</td>
                </tr>
        """

    html += """
            </table>
            <div class="footer">
                <p>For more insights, visit the <a href="https://yourbudgettrackerapp.com">Budget Tracker Web App</a>.</p>
            </div>
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
        print("Email Error:", e)
        return False



def get_savings_tip(savings, income):
    if income == 0:
        return "No income recorded."
    savings_pct = (savings / income) * 100
    if savings_pct > 30:
        return "Excellent savings! You’re financially healthy. Consider long-term investments."
    elif savings_pct > 15:
        return "Good job! Try to push it a bit more for better future stability."
    elif savings_pct > 0:
        return "You're saving something, but aim to save at least 15% of your income."
    else:
        return "You’re spending more than you earn. Try cutting unnecessary expenses."

def get_major_expense(budget_data):
    expenses = {k: v for k, v in budget_data.items() if k not in ['Income', 'Savings']}
    if expenses:
        max_category = max(expenses, key=expenses.get)
        return max_category, expenses[max_category]
    return "None", 0

@app.route('/')
def index():
    return render_template('finance.html')

@app.route('/track_budget', methods=['POST'])
def track_budget():
    try:
        form = request.form
        income = float(form['income'])
        rent = float(form['rent'])
        utilities = float(form['utilities'])
        groceries = float(form['groceries'])
        transport = float(form['transport'])
        entertainment = float(form['entertainment'])
        other_expenses = float(form['other_expenses'])
        email = form['email'].strip()

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

        savings_tip = get_savings_tip(savings, income)
        major_expense_cat, major_expense_amt = get_major_expense(budget_data)
        bitcoin_price = get_bitcoin_price()
        apple_price = get_stock_price("AAPL")

        email_sent = send_email_report(email, budget_data)

        return render_template('result.html',
                       budget_data=budget_data,
                       bar_chart=bar_chart,
                       pie_chart=pie_chart,
                       bitcoin_price=bitcoin_price,
                       stock_price=apple_price,
                       savings_tip=savings_tip,
                       major_expense=major_expense_cat,
                       major_expense_amt=major_expense_amt,
                       savings=savings,
                       email_status=email_sent)
    except Exception as e:
        return f"<h2 style='color:red;'>Error: {str(e)}</h2><p><a href='/'>Go Back</a></p>"
if __name__ == "__main__":
    app.run(debug=True)