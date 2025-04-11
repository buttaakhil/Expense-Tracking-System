import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL="http://127.0.0.1:8000"

st.title("Expense Management System 2025")
tab1,tab2,tab3=st.tabs(["Add/Update","Analytics","Analytics By Months"])

with tab1:
    selected_date=st.date_input("Enter Date",
                                value=datetime(2025,1,1),
                                min_value=datetime(2025, 1, 1),
                                max_value=datetime(2025, 12, 31),
                                label_visibility="collapsed"
    )


    response=requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses=[]

    categories=["Rent","Food","Shopping","Entertainment","Other"]
    
    with st.form(key="expense_key"):
        col1,col2,col3 = st.columns(3)
        with col1:
            st.text("Amount")
        with col2:
            st.text("Category")
        with col3:
            st.text("Notes")

        expenses=[]
        for i in range(5):

            if i< len(existing_expenses):
                amount=existing_expenses[i]["amount"]
                category=existing_expenses[i]["category"]
                notes=existing_expenses[i]["notes"]
            else:
                amount=0.0
                category="Shopping"
                notes=""

            col1,col2,col3=st.columns(3)
            with col1:
                amount_input=st.number_input(label="Amount",min_value=0.0,step=1.0,value=amount,key=f"amount{i}",label_visibility="collapsed")
            with col2:
                category_input=st.selectbox(label="Category",options=categories,index=categories.index(category),key=f"category{i}",label_visibility="collapsed")
            with col3:
                notes_input=st.text_input(label="Notes",value=notes,key=f"notes{i}",label_visibility="collapsed")

            expenses.append({
                'amount':amount_input,
                'category':category_input,
                'notes':notes_input
            })
        submit_button = st.form_submit_button()
        if submit_button:
            filtered_expenses =[expense for expense in expenses if expense['amount']>0]
            response=requests.post(f"{API_URL}/expenses/{selected_date}",json=filtered_expenses)
            if response.status_code == 200:
                st.success("Expenses updated successfully")
            else:
                st.error("Failed to update expenses")



with tab2:
    col1,col2 = st.columns(2)
    with col1:
        stat_date=st.date_input("Start Date",value=datetime(2025,1,1),min_value=datetime(2025, 1, 1),max_value=datetime(2025, 12, 31))
    with col2:
        end_date=st.date_input("End Date",value=datetime(2025,12,31),min_value=datetime(2025, 1, 1),max_value=datetime(2025, 12, 31))

    if st.button("Get Analytics"):
        payload={
            "start_date":stat_date.strftime("%Y-%m-%d"),
            "end_date":end_date.strftime("%Y-%m-%d")
        }
        response=requests.post(f"{API_URL}/analytics",json=payload)
        response=response.json()

        if response:
            data={
            "Category":list(response.keys()),
            "Total":[response[category]["total"] for category in response.keys()],
            "Percentage":[response[category]["percentage"] for category in response.keys()]
            }

            df=pd.DataFrame(data)
            df_sorted=df.sort_values(by="Percentage",ascending=False)

            st.title("Expense Breakdown by Category")
            st.bar_chart(data=df_sorted.set_index("Category")['Percentage'])
            st.table(df_sorted)
        else:
            st.warning("No expenses found.")


with tab3:
    st.subheader("Expense Breakdown by Months")
    response=requests.get(f"{API_URL}/monthly_analytics")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses=[]


    if existing_expenses:
        df = pd.DataFrame(existing_expenses)
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df = df.sort_values("month")
        df["month"] = df["month"].dt.strftime("%B")  
        month_order = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)
        

        df.rename(columns={"total_amount": "Amount", "month": "Month"}, inplace=True)
        st.bar_chart(df.set_index("Month")["Amount"])
        st.table(df)  
    else:
        st.warning("No expenses found.")
