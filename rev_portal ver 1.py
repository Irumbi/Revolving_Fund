import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import datetime
import os
from PIL import Image
import io

# Set the path to the Revolving_Fund database
db_path = "Revolving_Fund.db"

# Function to initialize the database and create the table if it doesn't exist
def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create requests table if it doesn't exist
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_code TEXT,
        agent_name TEXT,
        month TEXT,
        requested_amount REAL,
        status TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Function to check if the agent has already submitted a request for the current month
def check_previous_request(agent_code, month):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    SELECT * FROM requests
    WHERE agent_code = ? AND month = ? 
    ''', (agent_code, month))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Function to fetch agent data from the commission table in Revolving_Fund DB
def get_agent_data(agent_code):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    SELECT Agent_Code, Agent_Name, Amount, Agent_Image FROM commission WHERE Agent_Code = ? 
    ''', (agent_code,))
    agent_data = cursor.fetchone()
    conn.close()
    return agent_data

# Function to submit a fund request
def submit_request(agent_code, agent_name, requested_amount, month, status="Pending"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    INSERT INTO requests (agent_code, agent_name, month, requested_amount, status)
    VALUES (?, ?, ?, ?, ?) 
    ''', (agent_code, agent_name, month, requested_amount, status))
    conn.commit()
    conn.close()

# Function to fetch all requests (for payroll team view)
def get_all_requests():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    all_requests = cursor.fetchall()
    conn.close()
    return all_requests



# Initialize the database
create_db()

# Streamlit UI: Set custom CSS for background and styling (customize colors, fonts, layout)
st.markdown("""
    <style>
    /* General Page Styling */
    body {
        background-color: #f0f8ff;
        font-family: 'Arial', sans-serif;
        color: #333;
    }

    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #2980b9;
    }

    /* Sticky Navigation Menu */
    .sidebar .sidebar-content {
        background-color: #fff;
        border-right: 2px solid #ddd;
        width: 250px;
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        padding-top: 20px;
        z-index: 10;
    }

    .sidebar .sidebar-content a {
        text-decoration: none;
        color: #333;
        font-size: 18px;
        padding: 15px;
        display: block;
        margin: 10px 0;
    }

    .sidebar .sidebar-content a:hover {
        background-color: #f0f0f0;
    }

    /* Fullscreen Image Section */
    .full-screen-image {
        height: 100vh;
        background: url('https://www.example.com/money_image1.jpg') no-repeat center center fixed;
        background-size: cover;
        color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    /* Add styles for page header */
    .page-header {
        font-size: 2rem;
        font-weight: bold;
    }

    .page-subheader {
        font-size: 1.2rem;
    }

    </style>
""", unsafe_allow_html=True)

# Function for the "Get Started" page with image gallery
# Function for the "Get Started" page with image gallery and article
def get_started():
    st.title("Welcome to the Revolving Fund Program")
    st.write("""
    This portal allows you to manage your fund requests, check loan limits, and track your requests. 
    Please use the navigation pane to get started.
    """)

    # Add an article on managing borrowed money
    st.subheader("Managing Borrowed Money: Tips and Best Practices")
    st.write("""
    Borrowing money is a tool that can be used to achieve goals, but it requires careful planning to ensure that it doesn’t lead to financial stress. 
    One of the first steps in managing borrowed money effectively is to ensure that you borrow only what you truly need and can repay. 
    Create a clear plan to repay the loan in installments, setting realistic goals for each payment. Prioritize high-interest loans, as they can accumulate quickly. 
    It’s also important to track your spending and ensure that the borrowed funds are being used for the intended purpose rather than unnecessary expenses.

    Another important aspect of managing borrowed money is to keep communication open with your lender. 
    If you're unable to make a payment, it's crucial to notify the lender and discuss possible arrangements. Lenders are often more understanding if you're proactive in your communication. 
    Additionally, keeping track of your loans in a budget or financial planning app can help you stay organized and ensure that you don't miss payments. 
    Always remember that borrowing money should be a temporary solution, and as you manage your borrowed funds wisely, you will be better equipped to avoid debt traps in the future.
    """)

    # Add a picture gallery section
    st.subheader("learn more about Money Management")
    
    # Create a container to hold the image gallery
    gallery = st.container()
    with gallery:
        # You can add a list of image paths (you can upload images or use URLs)
        image_paths = [
            "https://www.resolvefs.co.uk/wp-content/uploads/2021/04/Funds-1.png"  # Replace with actual image URLs or local file paths
        ]

        # Display the images in a nice layout
        st.write("#### gallery Coming soon..")
        cols = st.columns(3)  # Divide the space into 3 columns for the gallery
        for i, col in enumerate(cols):
            if i < len(image_paths):
                # Display the images in each column using use_container_width
                with col:
                    st.image(image_paths[i], use_container_width=True)  # Updated to use_container_width

        # Optionally, you can add a border or background styling for the container
        st.markdown("""
        <style>
        .stContainer {
            background-color: #e8f4f8;
            border-radius: 10px;
            padding: 20px;
        }
        </style>
        """, unsafe_allow_html=True)


# Function for the "Apply for a Loan" page
def apply_for_loan():
    st.title("Apply for a Loan")
    agent_code_input = st.text_input("Enter Agent Code", type="password")

    # Fetch agent data
    agent_data = get_agent_data(agent_code_input)

    if agent_data:
        agent_code, agent_name, agent_amount, agent_image = agent_data
        st.subheader(f"Hello {agent_name}, apply for a loan below!")
        
        eligible_amount = agent_amount / 3
        st.write(f"You are eligible for a loan of Ksh. **{eligible_amount}**")

        # Get the current month (for the check)
        current_month = datetime.now().strftime('%b')  # Example: 'Mar' for March

        # Check if the agent has already submitted a request for this month
        if check_previous_request(agent_code_input, current_month):
            st.error(f"You have already submitted a fund request for the month of {current_month}. You cannot submit another request this month.")
            
            # Display the table with the previous request details
            previous_request = get_previous_request(agent_code_input, current_month)
            if previous_request:
                st.write(f"Previous Request for {current_month}:")
                st.dataframe(previous_request)  # Display the previous request details in a table
                
        else:
            # Allow the user to input the amount they want to request
            requested_amount = st.number_input(
                "Enter the amount you want to request", 
                min_value=0.0,  
                max_value=float(eligible_amount),
                step=500.0  
            )
            
            if st.button("Submit Fund Request"):
                # Submit the request
                submit_request(agent_code_input, agent_name, requested_amount, current_month)
                st.success(f"Your request for Ksh. {requested_amount} has been submitted for approval.")
    
    else:
        st.error("Invalid Agent Code! Please try again.")

# Function to get previous request data for the current month (if it exists)
def get_previous_request(agent_code, month=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if month:
        # If a specific month is provided, filter by that month
        cursor.execute('''
        SELECT month, SUM(requested_amount) 
        FROM requests
        WHERE agent_code = ? AND month = ?
        GROUP BY month
        ORDER BY month DESC
        ''', (agent_code, month))
    else:
        # If no month is provided, fetch data for all months
        cursor.execute('''
        SELECT month, SUM(requested_amount) 
        FROM requests
        WHERE agent_code = ?
        GROUP BY month
        ORDER BY month DESC
        ''', (agent_code,))

    result = cursor.fetchall()
    conn.close()
    
    return result

    
    # Get the results and close the connection
    result = cursor.fetchall()
    conn.close()
    
    # Return the result
    return result
def Total_Loan_Request():
    st.title("View Total Loan Requests")

    # Add a password input for accessing the page (only for payroll team)
    password = st.text_input("Enter the payroll team password", type="password")

    # Check if the entered password is correct (using a hardcoded password "1234" for now)
    if password == "1234":
        # Fetch all loan requests made by all agents
        previous_loans = get_all_requests()  # You may modify this function to show only total loan requests for the month, etc.

        if previous_loans:
            # Display loan requests
            st.write("Total loan requests made:")
            request_data = pd.DataFrame(previous_loans, columns=["ID", "Agent Code", "Agent Name", "Month", "Requested Amount", "Status"])
            st.dataframe(request_data)
        else:
            st.write("No loan requests found.")
    
    else:
        # If the password is incorrect, show an error message
        st.error("Invalid password! Access denied.")


# Function for the "Check Loan Limit" page
def check_loan_limit():
    st.title("Check Loan Limit")
    
    # Only ask for agent code without a password
    agent_code_input = st.text_input("Enter Agent Code")

    # Fetch agent data based on the entered agent code
    agent_data = get_agent_data(agent_code_input)
    
    if agent_data:
        _, agent_name, agent_amount, _ = agent_data
        eligible_amount = agent_amount / 3
        st.write(f"Your loan limit is Ksh. **{eligible_amount}**")
    else:
        st.error("")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define the function to send email
def send_email(subject, body, to_email):
    from_email = "irumbij@gmail.com"  # Replace with your email
    password = "Sygyz@1234"  # Replace with your email password or app-specific password

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Set up the server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Admin Approval function
# Function to get the public IP address of the user
def get_client_ip():
    try:
        # Get the public IP address of the user (from an external API)
        ip = requests.get('https://api.ipify.org').text
        return ip
    except requests.exceptions.RequestException:
        return "Unknown"  # In case of an error in fetching the IP

# Function to store approval data (can be a database, file, etc.)
def store_approval_data(loan_id, agent_name, approved_by, approval_level, ip_address):
    # Here you can write this to a database or a file, for simplicity let's just print
    # You can replace this with actual database storage (e.g., SQLite, MySQL, etc.)
    st.write(f"Approval Record - Loan ID: {loan_id}, Agent: {agent_name}, Approved By: {approved_by}, Level: {approval_level}, IP Address: {ip_address}")

def admin_approval():
    st.title("Admin Approval Section")

    # Password protection for the admin approval section
    admin_password = st.text_input("Enter admin password", type="password")

    if admin_password == "admin123":  # Replace with a secure password
        st.subheader("Loan Requests Pending Approval")

        # Fetch all loan requests with "Pending" status
        pending_requests = get_all_requests()
        
        # Separate the loan requests into three categories
        auto_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] < 10000]
        ho_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and 10000 <= req[4] <= 50000]
        md_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] > 50000]

        # Automatic Approval Section (for loans less than 10K)
        st.subheader("Automatic Approval (Loans less than 10K)")
        if auto_approved_loans:
            loan_df = pd.DataFrame(auto_approved_loans, columns=["ID", "Agent Code", "Agent Name", "Month", "Requested Amount", "Status"])
            st.dataframe(loan_df)

            # Approve the loans automatically
            for req in auto_approved_loans:
                loan_id, agent_code, agent_name, month, requested_amount, status = req
                if st.button(f"Approve loan of Ksh {requested_amount} for {agent_name}", key=f"auto_approve_{loan_id}"):
                    approve_loan(loan_id, "Approved")
                    ip_address = get_client_ip()  # Get the IP address of the approver
                    store_approval_data(loan_id, agent_name, "Admin", "Auto Approval", ip_address)
                    st.success(f"Loan of Ksh {requested_amount} for {agent_name} has been automatically approved.")
                    # Refresh the pending requests after approval
                    pending_requests = get_all_requests()
                    auto_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] < 10000]
                    ho_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and 10000 <= req[4] <= 50000]
                    md_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] > 50000]
        else:
            st.write("No loans for automatic approval.")

        # Head of Ordinary Life (HO) Section (for loans between 10K and 50K)
        st.subheader("Head of Ordinary Life (Loans between 10K and 50K)")

        ho_password = st.text_input("Enter HO approval password", type="password")
        if ho_password == "1236":
            if ho_approved_loans:
                loan_df = pd.DataFrame(ho_approved_loans, columns=["ID", "Agent Code", "Agent Name", "Month", "Requested Amount", "Status"])
                st.dataframe(loan_df)

                # Approve the loans for HO
                for req in ho_approved_loans:
                    loan_id, agent_code, agent_name, month, requested_amount, status = req
                    if st.button(f"Approve loan of Ksh {requested_amount} for {agent_name}", key=f"ho_approve_{loan_id}"):
                        approve_loan(loan_id, "Approved")
                        ip_address = get_client_ip()  # Get the IP address of the approver
                        store_approval_data(loan_id, agent_name, "HO", "HO Approval", ip_address)
                        st.success(f"Loan of Ksh {requested_amount} for {agent_name} has been approved by Head of Ordinary Life.")
                        # Refresh the pending requests after approval
                        pending_requests = get_all_requests()
                        auto_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] < 10000]
                        ho_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and 10000 <= req[4] <= 50000]
                        md_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] > 50000]
            else:
                st.write("No loans for approval by Head of Ordinary Life.")
        else:
            st.error("Invalid HO password. Access denied.")

        # Managing Director (MD) Section (for loans greater than 50K)
        st.subheader("Managing Director (Loans greater than 50K)")

        md_password = st.text_input("Enter MD approval password", type="password")
        if md_password == "1235":
            if md_approved_loans:
                loan_df = pd.DataFrame(md_approved_loans, columns=["ID", "Agent Code", "Agent Name", "Month", "Requested Amount", "Status"])
                st.dataframe(loan_df)

                # Approve the loans for MD
                for req in md_approved_loans:
                    loan_id, agent_code, agent_name, month, requested_amount, status = req
                    if st.button(f"Approve loan of Ksh {requested_amount} for {agent_name}", key=f"md_approve_{loan_id}"):
                        approve_loan(loan_id, "Approved")
                        ip_address = get_client_ip()  # Get the IP address of the approver
                        store_approval_data(loan_id, agent_name, "MD", "MD Approval", ip_address)
                        st.success(f"Loan of Ksh {requested_amount} for {agent_name} has been approved by Managing Director.")
                        # Refresh the pending requests after approval
                        pending_requests = get_all_requests()
                        auto_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] < 10000]
                        ho_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and 10000 <= req[4] <= 50000]
                        md_approved_loans = [req for req in pending_requests if req[5] == 'Pending' and req[4] > 50000]
            else:
                st.write("No loans for approval by Managing Director.")
        else:
            st.error("Invalid MD password. Access denied.")

    else:
        st.error("Invalid admin password. Access denied.")

# Function for the "Contact Us" page

# Function to approve the loan and update its status in the database
def approve_loan(loan_id, status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    UPDATE requests
    SET status = ?
    WHERE id = ?
    ''', (status, loan_id))
    conn.commit()
    conn.close()


def contact_us():
    st.title("📞 Contact Us")
    
    # Set background color of the page to a dimmer shade using CSS
    st.markdown("""
    <style>
        body {
            background-color: #384646;  /* Light grey background */
            color: #333333;  /* Dark text for contrast */
        }
        .title {
            text-align: center;
        }
        .contact-info {
            padding-left: 10px;
            padding-right: 10px;
        }
        .contact-header {
            color: #007BFF;  /* Blue color for headers */
            font-size: 1.5em;
        }
        .contact-item {
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .contact-link {
            color: #007BFF; /* Links color */
            text-decoration: none;
        }
        .contact-link:hover {
            text-decoration: underline;
        }
        .button-style {
            background-color: #4CAF50; /* Green background */
            color: white;
            border-radius: 8px;
            padding: 10px;
            width: 100%;
            cursor: pointer;
        }
        .button-style:hover {
            background-color: #45a049;
        }
    </style>
    """, unsafe_allow_html=True)

    # Contact Information Section
    st.markdown("<div class='contact-info'>", unsafe_allow_html=True)

    st.markdown("<div class='contact-header'>For any inquiries or support, please contact our team:</div>", unsafe_allow_html=True)

    # Contact details with links
    st.markdown("""
    <div class='contact-item'>
        <strong>📧 Email:</strong> 
        <a href='mailto:AgencyServices@madison.co.ke' class='contact-link'>AgencyServices@madison.co.ke</a>
    </div>
    <div class='contact-item'>
        <strong>☎️ Contact Centre:</strong> 
        <a href='tel:+254709922000' class='contact-link'>0709 922 000</a>
    </div>
    <div class='contact-item'>
        <strong>💬 WhatsApp:</strong> 
        <a href='https://wa.me/254110941061' target='_blank' class='contact-link'>0110 941 061</a>
    </div>
    <div class='contact-item'>
        <strong>📱 SMS Number:</strong> 
        <a href='tel:*828#' class='contact-link'>20286 USSD: *828#</a>
    </div>
    <div class='contact-item'>
        <strong>🏢 Location:</strong> Madison House Upper Hill Close, P.O Box 41163-00100, Nairobi
    </div>
    <div class='contact-item'>
        <strong>📧 General Email:</strong> 
        <a href='mailto:madison@madison.co.ke' class='contact-link'>madison@madison.co.ke</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Send us an email button (removed query parameters handling, just uses mailto link)
    st.markdown("""
    <div style='margin-top: 20px;'>
        <a href='mailto:AgencyServices@madison.co.ke'>
            <button class='button-style'>Send us an Email</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


# Add the admin approval page to the sidebar menu
menu = ["Get Started", "Check Loan Limit","Apply for a Loan", 
        "View Total_Loan_Request", "Admin Approval"]

# Sidebar for the Contact Us option
st.sidebar.title("Menu")

# Custom CSS to style the navigation bar
menu_css = """
    <style>
    .css-1d391kg {
        display: flex;
        justify-content: center;
        background-color: #3498db;  /* Bright Blue */
        padding: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stRadio > div {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    .stRadio > div > label {
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        border-radius: 20px;
        color: white;
        background-color: #3498db;  /* Bright Blue */
        transition: background-color 0.3s ease;
    }
    .stRadio > div > label:hover {
        background-color: #1abc9c;  /* Lively Teal */
    }
    .stRadio > div > div > div {
        display: inline-block;
        margin-right: 10px;
    }
    </style>
"""

# Apply the CSS styles to the app
st.markdown(menu_css, unsafe_allow_html=True)

selection = st.radio("", menu, horizontal=True)


sidebar_selection = st.sidebar.radio("", ["Contact Us"])


# Render the selected page
if selection == "Admin Approval":
    admin_approval()
elif selection == "Get Started":
    get_started()
elif selection == "Apply for a Loan":
    apply_for_loan()
elif selection == "View Total_Loan_Request":
    Total_Loan_Request()
elif selection == "Check Loan Limit":
    check_loan_limit()

if sidebar_selection == "Contact Us":
    contact_us()