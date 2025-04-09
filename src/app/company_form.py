import streamlit as st

def display_company_form():
    st.header("Company Form")
    st.text("Please fill out the form below to provide your company details in order to add valuable context to the consultant.")

    with st.form("company_form"):
        name = st.text_input("Company Name")
        employees = st.number_input("Company Employees", min_value=0, max_value=120, step=1)
        description = st.text_area("Company Description")
        
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state["company_info"] = {
            "name": name,
            "employees": employees,
            "description": description
        }
        st.success(f"Thanks for submitting the form, {name}!")