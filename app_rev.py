import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from PIL import Image
import io

# Set the path to the Revolving_Fund database
db_path = r"C:\Users\lenovo\OneDrive\Desktop\basics c_part 1\Basic Python\Revolving_Fund.db"

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
    cursor.execute('SELECT * FROM requests')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize the database
create_db()

# Streamlit UI: Set custom CSS for background and styling (customize colors, fonts, layout)
st.markdown("""
    <style>
    /* Custom styles */
    body {
        background-image: 003973e;
        background-size: cover; /* Ensures the background image covers the entire screen */
        background-repeat: no-repeat;
        background-attachment: fixed; /* Makes the background fixed */
        font-family: 'Arial', sans-serif;
        color: 003973;
    }

    .stTitle {
        color: #2c3e50;
    }

    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #3498db;
    }

    .stTextInput>div>label {
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

    .stDataFrame {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    .stDataFrame th {
        background-color: #3498db;
        color: white;
        padding: 12px 15px;
        font-size: 14px;
    }

    .stDataFrame td {
        padding: 10px 15px;
        font-size: 14px;
    }

    .stCheckbox>div>label {
        color: #333;
        font-weight: bold;
    }

    .sidebar .sidebar-content {
        background-color: #003973;
        color: white;
        font-family: 'Arial', sans-serif;
        padding: 15px;
    }

    .sidebar .sidebar-content .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #fff;
    }

    /* Header Customization */
    .stHeader {
        background-color: #2c3e50;
        color: white;
        padding: 20px;
        text-align: center;
    }

    .stHeader h1 {
        font-family: 'Georgia', serif;
    }

    .stTextInput>div>div>label {
        font-family: 'Georgia', serif;
        color: #333;
    }

    </style>
    """, unsafe_allow_html=True)

# Streamlit UI
st.title("Revolving Fund Program")

# User Authentication - Agent Code Input
agent_code_input = st.text_input("Enter Agent Code", type="password")

# Fetch agent data from the database, including Agent Image
agent_data = get_agent_data(agent_code_input)

if agent_data:
    agent_code, agent_name, agent_amount, agent_image = agent_data

    # Valid agent code, show the agent's dashboard
    st.subheader(f"Welcome {agent_name}!")

    # Display agent image (if available)
    if agent_image:
        try:
            # Check if the agent_image is a file path (string)
            if isinstance(agent_image, str) and os.path.exists(agent_image):
                # If agent_image is a path, display the image
                st.sidebar.image(agent_image, caption="Agent Image", width=150)
            else:
                # If agent_image is binary data, convert it to an image using io.BytesIO
                image = Image.open(io.BytesIO(agent_image))
                st.sidebar.image(image, caption="Agent Image", width=150)
        except Exception as e:
            st.error(f"Error displaying image: {e}")
    else:
        # Placeholder if no image is available
        st.sidebar.image(r"https://th.bing.com/th/id/OIP.aKwp7zaEtoAu61UZ_V2OEQHaEo?w=248&h=180&c=7&r=0&o=5&dpr=1.2&pid=1.7", width=150)

    # Display agent's information in a more structured format
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Monthly Commission:")
    with col2:
        st.write(f"**{agent_amount}**")

    # Check Eligibility only if agent_amount is not None
    if agent_amount is None:
        st.error("Agent amount is missing. Please contact the admin for assistance.")
    else:
        eligible_amount = agent_amount / 3
        st.write(f"You qualify for a loan of Kshs.**{eligible_amount}**")

    # Get the current month dynamically
    current_month = datetime.now().strftime('%b')  # e.g., 'Mar'

    # Check if the agent has already submitted a request for the current month
    if check_previous_request(agent_code_input, current_month):
        st.error(f"You have already submitted a fund request for the month of {current_month}. You cannot submit another request this month.")
    else:
        # Allow the user to input the amount they want to request
        requested_amount = st.number_input(
            "Enter the amount you want to request", 
            min_value=0.0,  
            max_value=float(eligible_amount),
            step=500.0  
        )

        # Display an error if the requested amount exceeds the eligible amount
        if requested_amount > eligible_amount:
            st.error(f"Your requested amount exceeds the eligible limit of {eligible_amount}. Please enter a valid amount.")
        
        # If the user attempts to submit a request that is within the limit
        if st.button("Submit Fund Request"):
            if requested_amount <= eligible_amount and requested_amount > 0:
                submit_request(agent_code_input, agent_name, requested_amount, current_month)
                st.success(f"Your request for a fund of {requested_amount} has been submitted for review.")
            elif requested_amount > eligible_amount:
                st.error(f"Your requested amount of {requested_amount} exceeds the eligible limit of {eligible_amount}. Please enter a valid amount.")
            else:
                st.error(f"Please enter a valid amount greater than 0.")

else:
    # If the agent code is incorrect, show an error
    st.error("Invalid Agent Code! Please enter the correct agent code.")

# Admin interface for payroll team (view all requests)
if st.checkbox("Admin View (Payroll Team)"):

    st.subheader("All Fund Requests")
    
    # Fetch all requests from the database
    all_requests = get_all_requests()
    
    # Convert the list of requests to a DataFrame
    request_df = pd.DataFrame(all_requests, columns=['ID', 'Agent Code', 'Agent Name', 'Month', 'Requested Amount', 'Status'])
    
    # Add a little styling for the table
    st.dataframe(request_df.style.set_table_styles(
        [{'selector': 'thead th', 'props': [('background-color', '#003973'), ('color', 'red'), ('text-align', 'center')]},
         {'selector': 'tbody td', 'props': [('padding', '10px 15px'), ('text-align', 'center')]}]
    ))
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set the path to the Revolving_Fund database
db_path = r"C:\Users\lenovo\OneDrive\Desktop\basics c_part 1\Basic Python\Revolving_Fund.db"

# Function to initialize the database and create tables if they don't exist
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
        status TEXT,
        dept_head_approval TEXT,
        md_approval TEXT,
        dept_head_comment TEXT,
        md_comment TEXT,
        dept_head_timestamp DATETIME,
        md_timestamp DATETIME
    )
    ''')
    
    # Create monthly approval table if it doesn't exist
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS monthly_approval (
        month TEXT PRIMARY KEY,
        total_requested_amount REAL,
        dept_head_approval TEXT,
        md_approval TEXT,
        dept_head_comment TEXT,
        md_comment TEXT,
        dept_head_timestamp DATETIME,
        md_timestamp DATETIME
    )
    ''')

    conn.commit()
    conn.close()

# Function to calculate the total requested amount for the month
def calculate_total_requested(month):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    SELECT SUM(requested_amount) FROM requests WHERE month = ? AND status != "Approved"
    ''', (month,))
    total_requested = cursor.fetchone()[0]
    conn.close()
    return total_requested if total_requested else 0.0

# Function to approve the total request by MD and HO
def approve_total_request(month, approval_by, approver, comment):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if approver == "Dept Head":
        cursor.execute('''
        UPDATE monthly_approval 
        SET dept_head_approval = ?, dept_head_comment = ?, dept_head_timestamp = ? 
        WHERE month = ? 
        ''', ("Approved", comment, datetime.now(), month))

    elif approver == "MD":
        cursor.execute(''' 
        UPDATE monthly_approval 
        SET md_approval = ?, md_comment = ?, md_timestamp = ? 
        WHERE month = ? 
        ''', ("Approved", comment, datetime.now(), month))

    conn.commit()
    conn.close()

    # After both approvals, update the requests for the month
    update_requests_status_for_month(month)
    send_email_notifications(month)

# Function to update the status of all requests for a month
def update_requests_status_for_month(month):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check the current approval statuses
    cursor.execute(''' 
    SELECT dept_head_approval, md_approval FROM monthly_approval WHERE month = ? 
    ''', (month,))
    result = cursor.fetchone()

    if result:
        dept_head_approval, md_approval = result
        
        # Debugging: Print out the current approval statuses
        print(f"Dept Head Approval: {dept_head_approval}, MD Approval: {md_approval}")

        # Update request status only if both are approved
        if dept_head_approval == "Approved" and md_approval == "Approved":
            print(f"Both approvals received for month: {month}. Updating request statuses.")
            
            # Change status of requests to "Approved"
            cursor.execute(''' 
            UPDATE requests SET status = "Approved"
            WHERE month = ? AND status != "Approved" 
            ''', (month,))
            conn.commit()
            print(f"Request status updated for month: {month}")
        else:
            print(f"Both approvals not received for month: {month}")
    else:
        print(f"No approvals found for the month: {month}")

    conn.close()

# Function to send email notifications
def send_email_notifications(month):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(''' 
    SELECT agent_name, agent_code, month FROM requests WHERE month = ? AND status = "Approved"
    ''', (month,))

    approved_requests = cursor.fetchall()
    
    for agent_name, agent_code, month in approved_requests:
        # Send email notification for approved requests
        send_email(agent_name, agent_code, month)
    
    conn.close()

def send_email(agent_name, agent_code, month):
    # Setup email sender and receiver
    sender_email = "Irumbij@gmail.com"  # Use your email here
    receiver_email = "john.Irumbi@madison.co.ke"  # Replace with the agent's email

    # Create email content
    subject = f"Fund Request Approved for {month}"
    body = f"Dear {agent_name},\n\nYour request for the fund in {month} has been approved.\n\nBest regards,\nThe Revolving Fund Team"
    
    # Create MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email via SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, "Sygyz@123")  # Use your email credentials
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Streamlit UI: Set custom CSS for background and styling


# Initialize the database
create_db()

# Streamlit UI for MD and Department Head to approve total requested amount
if st.checkbox("Approve Total Requested Amount (Department Head / MD)"):

    # Select the month for approval
    month = st.selectbox("Select Month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    total_requested = calculate_total_requested(month)
    st.write(f"Total Requested Amount for {month}: Ksh {total_requested}")

    # Input field for comments from MD and Dept Head
    dept_head_comment = st.text_area("Dept Head Comment")
    md_comment = st.text_area("MD Comment")

    # Approve or reject the total amount
    if st.button("Approve by Dept Head"):
        approve_total_request(month, "Dept Head", "Dept Head", dept_head_comment)
        st.success(f"Department Head has approved the total requested amount for {month}.")

    if st.button("Approve by MD"):
        approve_total_request(month, "MD", "MD", md_comment)
        st.success(f"Managing Director has approved the total requested amount for {month}.")
