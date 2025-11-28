import gradio as gr
import pandas as pd
from accounts import Account, get_share_price

# Initialize the account with a default user
account = None

def create_account(user_id, initial_deposit):
    global account
    try:
        account = Account(user_id, float(initial_deposit))
        return f"Account created for {user_id} with initial deposit of ${initial_deposit}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit(amount):
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        account.deposit_funds(float(amount))
        return f"Successfully deposited ${amount}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw(amount):
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        account.withdraw_funds(float(amount))
        return f"Successfully withdrew ${amount}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        account.buy_shares(symbol, int(quantity))
        return f"Successfully bought {quantity} shares of {symbol} at ${get_share_price(symbol):.2f} per share."
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first."
    
    try:
        account.sell_shares(symbol, int(quantity))
        return f"Successfully sold {quantity} shares of {symbol} at ${get_share_price(symbol):.2f} per share."
    except ValueError as e:
        return f"Error: {str(e)}"

def get_account_summary():
    global account
    if account is None:
        return "Please create an account first."
    
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_or_loss()
    
    summary = f"User ID: {account.user_id}\n"
    summary += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    summary += f"Current Balance: ${account.balance:.2f}\n"
    summary += f"Portfolio Value: ${portfolio_value:.2f}\n"
    summary += f"Total Account Value: ${(account.balance + portfolio_value):.2f}\n"
    summary += f"Profit/Loss: ${profit_loss:.2f} ({'Profit' if profit_loss >= 0 else 'Loss'})"
    
    return summary

def get_holdings():
    global account
    if account is None:
        return "Please create an account first."
    
    holdings = account.get_holdings()
    if not holdings:
        return "You don't have any holdings yet."
    
    result = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        result += f"{symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    
    return result

def get_transactions():
    global account
    if account is None:
        return "Please create an account first."
    
    transactions = account.get_transaction_history()
    if not transactions:
        return "No transactions yet."
    
    df = pd.DataFrame(transactions)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df

def get_available_stocks():
    return "Available stocks for demo:\nAAPL: $150.00\nTSLA: $800.00\nGOOGL: $2500.00"

with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    
    with gr.Tab("Account Management"):
        with gr.Group():
            gr.Markdown("## Create Account")
            with gr.Row():
                user_id_input = gr.Textbox(label="User ID")
                initial_deposit_input = gr.Number(label="Initial Deposit ($)")
            create_btn = gr.Button("Create Account")
            create_output = gr.Textbox(label="Result")
            create_btn.click(create_account, [user_id_input, initial_deposit_input], create_output)
        
        with gr.Group():
            gr.Markdown("## Deposit/Withdraw Funds")
            with gr.Row():
                deposit_input = gr.Number(label="Deposit Amount ($)")
                deposit_btn = gr.Button("Deposit")
            deposit_output = gr.Textbox(label="Deposit Result")
            deposit_btn.click(deposit, [deposit_input], deposit_output)
            
            with gr.Row():
                withdraw_input = gr.Number(label="Withdraw Amount ($)")
                withdraw_btn = gr.Button("Withdraw")
            withdraw_output = gr.Textbox(label="Withdraw Result")
            withdraw_btn.click(withdraw, [withdraw_input], withdraw_output)
    
    with gr.Tab("Trading"):
        with gr.Group():
            gr.Markdown("## Stock Information")
            stocks_info = gr.Textbox(label="Available Stocks", value=get_available_stocks())
        
        with gr.Group():
            gr.Markdown("## Buy Shares")
            with gr.Row():
                buy_symbol = gr.Textbox(label="Stock Symbol")
                buy_quantity = gr.Number(label="Quantity", precision=0)
            buy_btn = gr.Button("Buy Shares")
            buy_output = gr.Textbox(label="Buy Result")
            buy_btn.click(buy_shares, [buy_symbol, buy_quantity], buy_output)
        
        with gr.Group():
            gr.Markdown("## Sell Shares")
            with gr.Row():
                sell_symbol = gr.Textbox(label="Stock Symbol")
                sell_quantity = gr.Number(label="Quantity", precision=0)
            sell_btn = gr.Button("Sell Shares")
            sell_output = gr.Textbox(label="Sell Result")
            sell_btn.click(sell_shares, [sell_symbol, sell_quantity], sell_output)
    
    with gr.Tab("Portfolio"):
        with gr.Group():
            gr.Markdown("## Account Summary")
            summary_btn = gr.Button("Get Account Summary")
            summary_output = gr.Textbox(label="Account Summary")
            summary_btn.click(get_account_summary, [], summary_output)
        
        with gr.Group():
            gr.Markdown("## Current Holdings")
            holdings_btn = gr.Button("Get Holdings")
            holdings_output = gr.Textbox(label="Holdings")
            holdings_btn.click(get_holdings, [], holdings_output)
    
    with gr.Tab("Transaction History"):
        with gr.Group():
            gr.Markdown("## Transaction History")
            transactions_btn = gr.Button("Get Transactions")
            transactions_output = gr.Dataframe(label="Transactions")
            transactions_btn.click(get_transactions, [], transactions_output)

if __name__ == "__main__":
    demo.launch()