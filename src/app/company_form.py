import streamlit as st


def display_company_form():
    st.header("GHG Emissions Guidance Form")
    st.text(
        "Fill out this form to receive tailored guidance based on your region and reporting needs."
    )

    if "emission_sources" not in st.session_state:
        st.session_state.emission_sources = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Section 1: Company Info
    st.subheader("1. Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name (Optional)")
        industry = st.selectbox(
            "Industry/Sector*",
            [
                "",
                "Mining",
                "Manufacturing",
                "Agriculture",
                "Energy",
                "Transport",
                "Construction",
                "Retail",
                "Other",
            ],
        )
        revenue_range = st.selectbox(
            "Annual Revenue (AUD)",
            ["", "<50M", "50M–200M", "200M–500M", ">500M", "Prefer not to say"],
        )
    with col2:
        company_size = st.selectbox(
            "Company Size*",
            ["", "Small (<20 employees)", "Medium (20–199)", "Large (200+)"],
        )
        location = st.selectbox(
            "Location (State/Territory)*",
            ["", "NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"],
        )

    # Section 2: Emissions Profile
    st.subheader("2. Emissions Profile")
    reporting_status = st.radio(
        "Current GHG Reporting Status*",
        ["Already reporting", "New to reporting", "Unsure"],
        horizontal=True,
    )

    emission_scopes = st.multiselect(
        "Which emission scopes are you assessing?*",
        [
            "Scope 1 (Direct)",
            "Scope 2 (Indirect – Energy)",
            "Scope 3 (Value chain)",
            "Unsure – need guidance",
        ],
    )

    current_sources = st.multiselect(
        "Key Emission Sources*",
        [
            "Stationary combustion (boilers, generators)",
            "Mobile combustion (fleets, transport)",
            "Electricity use",
            "Fugitive emissions (e.g. refrigerants, methane)",
            "Waste and wastewater",
            "Purchased goods and services",
            "Employee commuting / travel",
            "Use of sold products",
            "Other Scope 3 sources",
        ],
        default=st.session_state.emission_sources,
    )

    # Section 3: Operational Details (Conditional)
    st.subheader("3. Operational Details")

    if "Electricity use" in current_sources:
        st.markdown("**Energy Usage**")
        electricity = st.number_input(
            "Annual Electricity Consumption (kWh)", min_value=0
        )
        renewables = st.slider("Renewable Energy Usage (%)", 0, 100, 0)

    if "Mobile combustion (fleets, transport)" in current_sources:
        st.markdown("**Fleet / Transport**")
        fleet_size = st.number_input("Number of Vehicles", min_value=0)
        fuel_type = st.selectbox(
            "Primary Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"]
        )

    # Section 4: Goals & Output
    st.subheader("4. Goals & Preferences")
    objective = st.selectbox(
        "Primary Objective*",
        ["Compliance only", "Reduction strategy", "Net-zero planning", "Educational"],
    )
    output_format = st.radio(
        "Preferred Output Format",
        ["Step-by-step guide", "Summary report", "Regulatory citations"],
        horizontal=True,
    )

    # Section 5: Regulatory & Framework Preferences
    st.subheader("5. Standards & Framework Preferences")
    regulatory_basis = st.selectbox(
        "Which regulatory framework should the guidance follow?",
        options=[
            "Australia 2025 Climate Reporting (Default)",
            "United States – EPA Framework",
            "European Union – ESRS / CSRD",
            "General / International Guidance (GHG Protocol, ISO, API)",
        ],
    )

    reference_support = st.checkbox(
        "Include references to international best practices (GHG Protocol, ISO 14064/67, API Compendium, etc.)"
    )

    # Section 6: Optional Details
    st.subheader("(Optional) Additional Info")
    challenges = st.text_area(
        "Any specific challenges you’re facing? (e.g. Scope 3, data collection, internal systems)"
    )

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
                "revenue_range": revenue_range,
                "reporting_status": reporting_status,
                "emission_scopes": emission_scopes,
                "emission_sources": current_sources,
                "objective": objective,
                "output_format": output_format,
                "regulatory_basis": regulatory_basis,
                "reference_support": reference_support,
                "challenges": challenges,
            }

            # Build dynamic context string
            context = f"""
The user is requesting guidance from a GHG consultant based on the following regulatory focus: **{regulatory_basis}**.
{"They also wish to include global best practices and references (GHG Protocol, ISO 14064/67, API Compendium, ESRS)." if reference_support else "They prefer guidance based strictly on the selected framework."}

Company Info:
- Industry: {industry}
- Company Size: {company_size}
- Location: {location}
- Revenue: {revenue_range}
- Reporting Status: {reporting_status}

Scopes being assessed: {", ".join(emission_scopes)}
Key emission sources: {", ".join(current_sources)}
Objective: {objective}
Preferred Output Format: {output_format}

Additional challenges: {challenges if challenges else "None provided"}
"""

            st.session_state["company_info"] = form_data
            st.session_state.ghg_assistant.set_context_form(context)

            st.success(
                "Thanks for submitting the form! Your guidance will be generated based on your selection."
            )
            st.balloons()
