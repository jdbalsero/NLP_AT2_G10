import streamlit as st

def display_company_form():
    st.header("Company Form")
    st.text("Please fill out the form below to get tailored guidance for your company.")

    # Initialize session state
    if 'emission_sources' not in st.session_state:
        st.session_state.emission_sources = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Section 1: Company Basics
    st.subheader("1. Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name (Optional)")
        industry = st.selectbox(
            "Industry/Sector*",
            options=["", "Mining", "Manufacturing", "Agriculture", "Energy", 
                    "Transport", "Construction", "Retail", "Other"]
        )
    with col2:
        company_size = st.selectbox(
            "Company Size*",
            options=["", "Small (<20 employees)", "Medium (20-199)", "Large (200+)"]
        )
        location = st.selectbox(
            "Location (State/Territory)*",
            options=["", "NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]
        )

    # Section 2: Emissions Profile
    st.subheader("2. Emissions Profile")
    reporting_status = st.radio(
        "Current GHG Emissions Reporting Status*",
        options=["Already reporting", "New to reporting", "Unsure"],
        horizontal=True
    )
    
    emission_scopes = st.multiselect(
        "Which emission scopes are you assessing?*",
        options=["Scope 1 (Direct)", "Scope 2 (Indirect - Energy)", 
                "Scope 3 (Other Indirect)", "Unsure – need guidance"]
    )
    
    current_sources = st.multiselect(
        "Primary Emission Sources*",
        options=["Electricity", "Fuel Combustion", "Fleet Vehicles", 
                "Waste", "Refrigerants", "Supply Chain", "Other"],
        default=st.session_state.emission_sources
    )

    # Section 3: Operational Details (Now properly conditional)
    st.subheader("3. Operational Details")
    
    # Energy Usage (appears only when Electricity is selected)
    if "Electricity" in current_sources:
        st.markdown("**Energy Usage**")
        electricity = st.number_input("Annual Electricity Consumption (kWh)", min_value=0)
        renewables = st.slider("Renewable Energy Usage (%)", 0, 100, 0)
    
    # Fleet/Transport (appears only when Fleet Vehicles is selected)
    if "Fleet Vehicles" in current_sources:
        st.markdown("**Fleet/Transport**")
        fleet_size = st.number_input("Number of Vehicles", min_value=0)
        fuel_type = st.selectbox("Primary Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"])

    # Section 4: Goals & Output
    st.subheader("4. Goals & Preferences")
    objective = st.selectbox(
        "Primary Objective*",
        options=["Compliance only", "Reduction strategy", "Net-zero planning", "Educational"]
    )
    
    output_format = st.radio(
        "Preferred Output Format",
        options=["Step-by-step guide", "Summary report", "Regulatory citations"],
        horizontal=True
    )

    # Optional Challenges
    st.subheader("(Optional) Additional Details")
    challenges = st.text_area("Describe any challenges you're facing (e.g., data collection, Scope 3 calculations)")

    # Submit button
    if st.button("Submit Form"):
        if not industry or not company_size or not location:
            st.error("Please fill required fields (*)")
        else:
            st.session_state.submitted = True
            st.session_state.emission_sources = current_sources
            
            form_data = {
                "company_name": company_name,
                "industry": industry,
                "company_size": company_size,
                "location": location,
                "reporting_status": reporting_status,
                "emission_scopes": emission_scopes,
                "emission_sources": current_sources,
                "objective": objective,
                "challenges": challenges
            }

    if st.session_state.submitted:
        st.session_state["company_info"] = form_data
        st.session_state.ghg_assistant.set_context_form(form_data)
        st.success(f"Thanks for submitting the form!")
        st.balloons()        