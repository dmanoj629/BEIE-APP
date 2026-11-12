"""Citizen and Business onboarding flows — tappable chips, progress bar, skip, custom text for 'Other' and loan/EMI details."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.state import save_profile
from app.theme import CUSTOM_CSS
from beie.ingest.pincode import resolve_pincode

CITIZEN_STEPS = [
    {
        "key": "name",
        "title": "Your Display Name",
        "question": "What is your name?",
        "chips": [],
        "is_name_step": True,
        "skippable": False,
    },
    {
        "key": "language",
        "title": ":material/public: Preferred Language",
        "question": "Which language would you like explanations in?",
        "chips": ["English", "ಕನ್ನಡ (Kannada)", "हिंदी (Hindi)"],
        "skippable": False,
    },
    {
        "key": "state_district",
        "title": ":material/location_on: Your Location",
        "question": "Enter your 6-digit Indian PIN Code to automatically detect your location:",
        "chips": [],
        "is_pin_step": True,
        "skippable": False,
    },
    {
        "key": "occupation",
        "title": ":material/engineering: Your Occupation & Work",
        "question": "What is your main work or occupation?",
        "chips": [
            "Farmer",
            "Salaried Employee",
            "Shopkeeper / Self-Employed",
            "Gig Worker / Delivery / Driver",
            "Student",
            "Homemaker",
            "Retiree",
            "Other (type below)",
        ],
        "skippable": False,
        "has_other": True,
        "other_prompt": "Tell us what specific work or trade you do:",
        "other_placeholder": "e.g., Auto / Taxi Driver, Electrician, Tailor, Private Tutor, Tea Stall Owner, Plumber...",
    },
    {
        "key": "income_band",
        "title": ":material/payments: Monthly Income",
        "question": "What is your approximate monthly household income?",
        "chips": [
            "Under ₹10,000",
            "₹10,000–₹25,000",
            "₹25,000–₹50,000",
            "₹50,000–₹1,00,000",
            "Above ₹1,00,000",
            "Prefer not to say",
        ],
        "skippable": False,
    },
    {
        "key": "goals",
        "title": ":material/target: What do you want to understand?",
        "question": "What is your main objective or question?",
        "chips": [
            "When to buy something (phone, appliance, vehicle, gold)",
            "Why prices are rising & how inflation hits my budget",
            "Farming decisions, mandi prices & fertilizer costs",
            "Loan EMI changes & repo rate sensitivity",
            "Saving & investing guidance (safe returns vs inflation)",
            "Govt welfare schemes & PDS subsidies",
            "Other question (type below)",
        ],
        "skippable": False,
        "has_other": True,
        "other_prompt": "Describe your other question or specific objective:",
        "other_placeholder": "e.g., When will mobile prices drop, tractor loan subsidy, gold price trends...",
    },
    {
        "key": "has_emi",
        "title": ":material/account_balance: Loans / EMIs (Optional)",
        "question": "Do you have any active loans or EMIs?",
        "chips": [
            "Yes — Bike / Two-Wheeler EMI",
            "Yes — Smartphone / Electronics EMI",
            "Yes — Car / Vehicle Loan",
            "Yes — Home Loan",
            "Yes — Personal / Education Loan",
            "Yes — Other Loan or EMI (describe below)",
            "No loans / EMIs",
        ],
        "skippable": True,
        "has_emi_input": True,
    },
    {
        "key": "main_expenses",
        "title": ":material/shopping_cart: Main Monthly Expenses (Optional)",
        "question": "What are your biggest monthly expense categories? (pick all that apply)",
        "chips": [
            "Food & Groceries",
            "Fuel / Petrol / Diesel / LPG",
            "House Rent",
            "Education & Fees",
            "Medical & Health",
            "Daily Transport",
            "Other essentials (describe below)",
        ],
        "skippable": True,
        "multi": True,
        "has_other": True,
        "other_prompt": "Please describe your other major monthly expense:",
        "other_placeholder": "e.g., Medical treatment, farm diesel, vehicle maintenance...",
    },
    {
        "key": "household_size",
        "title": ":material/person: Household Size (Optional)",
        "question": "How many people live in your household?",
        "chips": ["Just me (1)", "2 people", "3–4 people", "5–6 people", "7 or more"],
        "skippable": True,
    },
]

BUSINESS_STEPS = [
    {
        "key": "biz_owner_name",
        "title": "Your & Enterprise Name",
        "question": "What is your name and business name?",
        "chips": [],
        "is_name_step": True,
        "skippable": True,
    },
    {
        "key": "business_type",
        "title": ":material/factory: Business Type",
        "question": "What kind of business do you operate?",
        "chips": [
            "Retail Shop",
            "Manufacturing / MSME",
            "Logistics / Transport",
            "Agribusiness / Farm",
            "Trader / Wholesale",
            "Other",
        ],
        "skippable": False,
        "has_other": True,
        "other_prompt": "Please describe your business type:",
        "other_placeholder": "e.g., Cloud kitchen, Cold storage, Textile dyeing, Packaging unit, Fabrication...",
    },
    {
        "key": "sector",
        "title": ":material/sell: Your Sector",
        "question": "Which sector best describes your business?",
        "chips": [
            "Food & Beverages",
            "Textiles & Apparel",
            "Chemicals & Fertilizers",
            "Metals & Engineering",
            "Transport & Logistics",
            "FMCG / Consumer Goods",
            "Agriculture & Allied",
            "IT / Services",
            "Construction",
            "Other",
        ],
        "skippable": True,
        "has_other": True,
        "other_prompt": "Please specify your sector / industry:",
        "other_placeholder": "e.g., Renewable energy, Handicraft exports, Automobile components...",
    },
    {
        "key": "district",
        "title": ":material/location_on: Your District",
        "question": "Which district is your main operations in?",
        "chips": [
            "Bengaluru Urban",
            "Bengaluru Rural",
            "Mysuru",
            "Hubli-Dharwad",
            "Mangaluru",
            "Belagavi",
            "Tumkur",
            "Davangere",
            "Shivamogga",
            "Other Karnataka",
            "Outside Karnataka",
        ],
        "skippable": True,
        "has_other": True,
        "other_prompt": "Specify your operating district or city:",
        "other_placeholder": "e.g., Ballari, Hassan, Bagalkot, Pune, Hosur...",
    },
    {
        "key": "turnover_band",
        "title": ":material/bar_chart: Annual Turnover",
        "question": "What is your approximate annual business turnover?",
        "chips": [
            "Under ₹25 Lakh",
            "₹25L–₹2 Crore",
            "₹2Cr–₹10 Crore",
            "₹10Cr–₹100 Crore",
            "Above ₹100 Crore",
            "Prefer not to say",
        ],
        "skippable": True,
    },
    {
        "key": "main_inputs",
        "title": ":material/settings: Main Cost Inputs",
        "question": "Which input categories are your major costs? (pick all that apply)",
        "chips": [
            "Fuel / Diesel",
            "Raw Materials",
            "Transport / Freight",
            "Power / Electricity",
            "Labour",
            "Packaging",
            "Finance / EMI",
            "Other",
        ],
        "skippable": True,
        "multi": True,
        "has_other": True,
        "other_prompt": "Describe your other major cost inputs:",
        "other_placeholder": "e.g., Cold storage cooling fees, imported chemicals, machinery spare parts...",
    },
    {
        "key": "has_emi",
        "title": ":material/account_balance: Business Loans / EMIs",
        "question": "Does your business have active loans or credit lines?",
        "chips": [
            "Yes — Term Loan",
            "Yes — Working Capital / CC / OD",
            "Yes — Machinery / Equipment Finance",
            "Yes — Commercial Vehicle / Fleet Loan (e.g. delivery vans, trucks)",
            "Yes — Other Loan or Credit Facility (describe below)",
            "No business loans",
        ],
        "skippable": True,
        "has_emi_input": True,
    },
]


def _income_to_rs(income_band: str) -> float:
    mapping = {
        "Under ₹10,000": 7500,
        "₹10,000–₹25,000": 17500,
        "₹25,000–₹50,000": 37500,
        "₹50,000–₹1,00,000": 75000,
        "Above ₹1,00,000": 125000,
        "Prefer not to say": 25000,
    }
    return mapping.get(income_band, 25000)


def _occ_to_key(occ: str) -> str:
    s = str(occ).lower()
    if "farmer" in s or "farm" in s or "agri" in s or "crop" in s or "dairy" in s:
        return "farmer"
    if "salaried" in s or "employee" in s or "engineer" in s or "teacher" in s or "govt" in s or "corporate" in s or "officer" in s:
        return "salaried"
    if "shopkeeper" in s or "shop" in s or "retail" in s or "trader" in s or "merchant" in s or "store" in s or "business" in s:
        return "shopkeeper"
    if "gig" in s or "delivery" in s or "driver" in s or "swiggy" in s or "zomato" in s or "uber" in s or "ola" in s or "taxi" in s or "auto" in s:
        return "gig_worker"
    return "default"


def _lang_to_code(lang: str) -> str:
    if "Kannada" in lang or "ಕನ್ನಡ" in lang:
        return "kn"
    if "Hindi" in lang or "हिंदी" in lang:
        return "hi"
    return "en"


def _is_other_triggered(selected: any) -> bool:
    """Check if 'Other' or custom option was selected in single or multi choice."""
    if not selected:
        return False
    if isinstance(selected, list):
        return any("other" in str(item).lower() for item in selected)
    return "other" in str(selected).lower()


def _is_loan_active(selected: any) -> bool:
    """Check if user selected any active loan/EMI option."""
    if not selected:
        return False
    if isinstance(selected, list):
        return any(str(item).startswith("Yes") for item in selected)
    return str(selected).startswith("Yes")


def extract_context_from_text(text: str) -> dict[str, Any]:
    """Intelligently converts free-text descriptions into explicit facts and inferred context (Blueprint §5D)."""
    txt = text.lower().strip()
    if not txt:
        return {"stated": {}, "inferred": {}}

    stated: dict[str, Any] = {}
    inferred: dict[str, Any] = {}

    # Products & Activities
    if "coconut" in txt or "copra" in txt:
        stated["product"] = "Coconut oil / processing"
        stated["inputs"] = ["Coconuts from local farmers"]
    elif "dairy" in txt or "milk" in txt:
        stated["product"] = "Dairy & cattle farming"
    elif "rice" in txt or "paddy" in txt:
        stated["product"] = "Paddy / Rice cultivation or milling"
    elif "garment" in txt or "textile" in txt or "apparel" in txt:
        stated["product"] = "Textiles & garments"
    elif "cold storage" in txt or "warehouse" in txt:
        stated["product"] = "Warehousing & cold chain"

    # Energy source
    if "electricity" in txt or "power" in txt:
        stated["energy_dependency"] = "Electricity"
        inferred["tariff_sensitivity"] = "High"
    if "diesel" in txt or "generator" in txt or "fuel" in txt:
        stated["fuel_dependency"] = "Diesel"
        inferred["diesel_sensitivity"] = "High"

    # Transport / logistics
    if any(t in txt for t in ["transport", "delivery", "vehicle", "truck", "tempo", "van", "fleet", "shops"]):
        stated["transportation_dependency"] = "Yes (local distribution)"
        inferred["freight_exposure"] = "Moderate to High"

    # Regional extraction (Karnataka focus)
    karnataka_districts = [
        "Bengaluru", "Mysuru", "Hubli", "Dharwad", "Belagavi", "Mangaluru",
        "Shivamogga", "Tumakuru", "Davangere", "Ballari", "Vijayapura",
        "Kalaburagi", "Udupi", "Hassan", "Mandya", "Kolar", "Chikkamagaluru",
    ]
    for dist in karnataka_districts:
        if dist.lower() in txt:
            stated["region"] = dist
            break

    return {"stated": stated, "inferred": inferred}


def show_citizen_onboarding() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:1.8rem;text-align:center;padding:16px 0"><i class=ic-user></i> Citizen & Worker Profile Setup</div>',
        unsafe_allow_html=True,
    )

    if "ob_step" not in st.session_state:
        st.session_state["ob_step"] = 0
    if "ob_answers" not in st.session_state:
        st.session_state["ob_answers"] = {}

    step_idx = st.session_state["ob_step"]
    total_steps = len(CITIZEN_STEPS)

    if step_idx >= total_steps:
        _finalize_citizen()
        return

    step = CITIZEN_STEPS[step_idx]
    progress = step_idx / total_steps

    # Progress bar
    st.markdown(
        f'<div class="progress-track"><div class="progress-fill" style="width:{int(progress * 100)}%"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Step {step_idx + 1} of {total_steps} — {step['title']}")
    st.markdown(f"### {step['question']}")

    is_multi = step.get("multi", False)
    chips = step["chips"]

    # PIN Code auto-detection block for location step (NO radio options as per instruction)
    detected_district = st.session_state["ob_answers"].get("detected_district")
    if step["key"] == "state_district":
        st.markdown(
            """<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.25);border-radius:14px;padding:18px;margin:10px 0 16px 0;">
              <div style="font-weight:700;color:#2DD4BF;font-size:0.98rem;margin-bottom:6px;"><i class=ic-mail></i> Instant Location Auto-Detection via PIN Code</div>
              <div style="font-size:0.84rem;color:#94A3B8;">Enter your 6-digit PIN code. BEIE will automatically locate your post office, district, and state:</div>
            </div>""",
            unsafe_allow_html=True,
        )
        c_pin1, c_pin2 = st.columns([2, 1])
        with c_pin1:
            pin_val = st.text_input(
                "Indian PIN Code (6 digits):",
                value=st.session_state["ob_answers"].get("pincode", ""),
                placeholder="e.g. 560001, 577427, 570001, 580020, 590001, 110001...",
                max_chars=6,
                key="ob_pin_citizen_input",
            )
        with c_pin2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            click_detect = st.button(":material/location_on: Detect Location", key="btn_detect_citizen_pin")

        if pin_val.strip() and (len(pin_val.strip()) == 6 or click_detect):
            res = resolve_pincode(pin_val.strip())
            if res["status"] == "success":
                detected_district = res["district"]
                st.session_state["ob_answers"]["pincode"] = res["pincode"]
                st.session_state["ob_answers"]["formatted_address"] = res["formatted_address"]
                st.session_state["ob_answers"]["detected_state"] = res["state"]
                st.session_state["ob_answers"]["detected_district"] = res["district"]
                st.session_state["ob_answers"]["state_district"] = res["district"]
                st.markdown(
                    f"""<div style="background:rgba(16,185,129,0.12);border:1px solid #34D399;border-radius:12px;padding:14px;margin:10px 0;font-size:0.92rem;color:#A7F3D0;">
                      <i class=ic-circle-check></i> <b>Location Identified:</b> {res['formatted_address']}  <br>
                      <span style="font-size:0.8rem;color:#6EE7B7;">District automatically assigned: <b>{res['district']}</b> ({res['source']})</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="beie-warning">{res["message"]}</div>', unsafe_allow_html=True)

        selected = detected_district or ""

    # Name step widget
    elif step.get("is_name_step"):
        st.markdown(
            """<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.25);border-radius:14px;padding:18px;margin:10px 0 16px 0;">
              <div style="font-weight:700;color:#2DD4BF;font-size:0.98rem;margin-bottom:6px;"><i class=ic-user></i> Personalise Your Economic Command Center</div>
              <div style="font-size:0.84rem;color:#94A3B8;">Enter your name so BEIE addresses you personally across insights, reports, and AI chats (changeable anytime):</div>
            </div>""",
            unsafe_allow_html=True,
        )
        curr_name = st.session_state["ob_answers"].get("name") or st.session_state.get("user_name", "")
        if curr_name in ["Citizen", "Demo Officer", "User"]:
            curr_name = ""
        user_name_val = st.text_input(
            "Your Full Name / Display Name:",
            value=curr_name,
            placeholder="e.g. Ramesh Kumar, Priya Sharma, Venkatesh Rao...",
            key="ob_citizen_full_name_input",
        )
        selected = user_name_val.strip()

    # Selection widget (for non-name, non-pin steps)
    elif is_multi:
        selected = st.multiselect(
            "Select all that apply:", chips, key=f"ob_{step['key']}"
        )
    else:
        selected = st.radio(
            "Choose one:", chips, key=f"ob_{step['key']}", horizontal=False
        )

    # Contextual 'Other' text description field
    other_text = ""
    if step.get("has_other") and _is_other_triggered(selected):
        st.markdown(
            f"""<div style="background:rgba(45,212,191,0.08);border:1px solid rgba(45,212,191,0.25);border-radius:12px;padding:16px;margin:12px 0;">
              <div style="font-weight:600;color:#2DD4BF;font-size:0.9rem;margin-bottom:6px;">{step.get('other_prompt', '<i class=ic-file-pen></i> Please describe:')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        prev_other = st.session_state["ob_answers"].get(f"{step['key']}_custom", "")
        other_text = st.text_input(
            "Describe details:",
            value=prev_other,
            placeholder=step.get("other_placeholder", "Type your specific details here..."),
            key=f"ob_input_other_{step['key']}",
            label_visibility="collapsed",
        )

    # Contextual Loan / EMI detailed description & amount fields
    emi_desc = ""
    emi_amount = 0.0
    if step.get("has_emi_input") and _is_loan_active(selected):
        st.markdown(
            """<div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.3);border-radius:12px;padding:16px;margin:14px 0;">
              <div style="font-weight:700;color:#F97316;font-size:0.95rem;margin-bottom:4px;"><i class=ic-credit-card></i> Specific Loan & EMI Breakdown</div>
              <div style="font-size:0.82rem;color:#94A3B8;">Describe what item or vehicle you have an EMI for (e.g., bike EMI, phone EMI, car loan, etc.)</div>
            </div>""",
            unsafe_allow_html=True,
        )
        c_emi1, c_emi2 = st.columns([2, 1])
        with c_emi1:
            prev_desc = st.session_state["ob_answers"].get("emi_detail", "")
            emi_desc = st.text_input(
                "Loan / EMI Description (e.g., Bike EMI, Smartphone EMI, Car Loan):",
                value=prev_desc,
                placeholder="e.g. Hero Splendor bike EMI, iPhone 15 EMI, Maruti Suzuki car loan, Bajaj consumer loan...",
                key="ob_input_emi_desc",
            )
        with c_emi2:
            prev_amt = float(st.session_state["ob_answers"].get("emi_monthly_amount", 0.0))
            emi_amount = st.number_input(
                "Total Monthly Outflow (₹/mo):",
                min_value=0.0,
                max_value=10_000_000.0,
                value=prev_amt,
                step=500.0,
                key="ob_input_emi_amount",
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("Next →", key=f"ob_next_{step_idx}"):
            if step["key"] == "state_district":
                if not st.session_state["ob_answers"].get("detected_district"):
                    st.error("Please enter a valid 6-digit Indian PIN code to locate your district.")
                else:
                    st.session_state["ob_step"] += 1
                    st.rerun()
            elif step.get("is_name_step"):
                if not user_name_val.strip():
                    st.error("Please enter your name to proceed.")
                else:
                    st.session_state["ob_answers"]["name"] = user_name_val.strip()
                    st.session_state["user_name"] = user_name_val.strip()
                    st.session_state["ob_step"] += 1
                    st.rerun()
            elif selected or step.get("skippable", False):
                st.session_state["ob_answers"][step["key"]] = selected
                if other_text.strip():
                    st.session_state["ob_answers"][f"{step['key']}_custom"] = other_text.strip()
                    if step["key"] == "occupation":
                        st.session_state["ob_answers"]["occupation_custom"] = other_text.strip()
                if emi_desc.strip():
                    st.session_state["ob_answers"]["emi_detail"] = emi_desc.strip()
                if emi_amount > 0:
                    st.session_state["ob_answers"]["emi_monthly_amount"] = emi_amount
                st.session_state["ob_step"] += 1
                st.rerun()
            else:
                st.error("This field is required. Please choose an option to continue.")
    with col2:
        if step.get("skippable", False):
            if st.button("Skip", key=f"ob_skip_{step_idx}"):
                st.session_state["ob_answers"][step["key"]] = None
                st.session_state["ob_step"] += 1
                st.rerun()
    with col3:
        if step_idx > 0 and st.button("← Back", key=f"ob_back_{step_idx}"):
            st.session_state["ob_step"] -= 1
            st.rerun()

    st.markdown(
        '<div class="beie-info" style="margin-top:20px"><i class=ic-lock></i> Your answers are stored locally in this browser session. No Aadhaar, PAN, or bank credentials are ever requested.</div>',
        unsafe_allow_html=True,
    )


def _finalize_citizen() -> None:
    answers = st.session_state.get("ob_answers", {})
    name_val = answers.get("name", "").strip() or st.session_state.get("user_name", "")
    if name_val and name_val not in ["Citizen", "Demo Officer"]:
        st.session_state["user_name"] = name_val

    occ_raw = answers.get("occupation", "Other") or "Other"
    custom_occ = answers.get("occupation_custom", "").strip()

    # If user provided a specific occupation/trade, use it as their display title!
    if custom_occ:
        occ_label = f"{custom_occ}"
    elif "Other" in str(occ_raw):
        occ_label = "Citizen"
    else:
        occ_label = str(occ_raw)

    district_raw = answers.get("state_district", "Bengaluru Urban")
    custom_district = answers.get("state_district_custom", "").strip()
    detected_district = answers.get("detected_district", "").strip()
    pincode = answers.get("pincode", "").strip()
    formatted_address = answers.get("formatted_address", "").strip()

    if custom_district and "Other" in str(district_raw):
        district_final = custom_district
    elif detected_district and ("Other" in str(district_raw) or detected_district.lower() in str(district_raw).lower()):
        district_final = detected_district
    else:
        district_final = district_raw

    income_raw = answers.get("income_band", "₹25,000–₹50,000") or "₹25,000–₹50,000"
    lang_raw = answers.get("language", "English") or "English"

    # Loan / EMI details
    emi_raw = answers.get("has_emi", "No loans / EMIs")
    emi_detail = answers.get("emi_detail", "").strip()
    emi_monthly_amt = float(answers.get("emi_monthly_amount", 0.0))

    if emi_detail:
        emi_display = f"{emi_raw} ({emi_detail})"
    else:
        emi_display = str(emi_raw)

    profile = {
        "panel": "citizen",
        "name": name_val,
        "language": _lang_to_code(lang_raw),
        "district": district_final,
        "district_custom": custom_district,
        "pincode": pincode,
        "formatted_address": formatted_address,
        "occupation": _occ_to_key(custom_occ if custom_occ else occ_raw),
        "occupation_label": occ_label,
        "occupation_custom": custom_occ,
        "age_band": answers.get("age_band", "25–34"),
        "household_size": answers.get("household_size", "3–4 people"),
        "income_band": income_raw,
        "monthly_income": _income_to_rs(income_raw),
        "main_expenses": answers.get("main_expenses", []),
        "main_expenses_custom": answers.get("main_expenses_custom", ""),
        "has_emi": emi_display,
        "emi_detail": emi_detail,
        "emi_load_rs": emi_monthly_amt if emi_monthly_amt > 0 else (12000.0 if "Yes" in str(emi_raw) else 0.0),
        "goals": answers.get("goals", []),
        "goals_custom": answers.get("goals_custom", ""),
        "has_emergency_fund": False,
        "extracted_context": extract_context_from_text(f"{custom_occ} {answers.get('goals_custom', '')} {answers.get('main_expenses_custom', '')}"),
    }
    save_profile(profile)
    st.session_state["language"] = profile["language"]
    st.session_state["ob_step"] = 0
    st.session_state["ob_answers"] = {}
    st.rerun()


def show_business_onboarding() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:1.8rem;text-align:center;padding:16px 0"><i class=ic-factory></i> Business & MSME Profile Setup</div>',
        unsafe_allow_html=True,
    )

    if "ob_step" not in st.session_state:
        st.session_state["ob_step"] = 0
    if "ob_answers" not in st.session_state:
        st.session_state["ob_answers"] = {}

    step_idx = st.session_state["ob_step"]
    total_steps = len(BUSINESS_STEPS)

    if step_idx >= total_steps:
        _finalize_business()
        return

    step = BUSINESS_STEPS[step_idx]
    progress = step_idx / total_steps

    st.markdown(
        f'<div class="progress-track"><div class="progress-fill" style="width:{int(progress * 100)}%"></div></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Step {step_idx + 1} of {total_steps} — {step['title']}")
    st.markdown(f"### {step['question']}")

    is_multi = step.get("multi", False)
    chips = step["chips"]

    # PIN Code auto-detection block for business location step
    detected_district = st.session_state["ob_answers"].get("biz_detected_district")
    if step["key"] == "district":
        st.markdown(
            """<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.25);border-radius:14px;padding:16px;margin:10px 0 16px 0;">
              <div style="font-weight:700;color:#2DD4BF;font-size:0.92rem;margin-bottom:4px;"><i class=ic-mail></i> Auto-Detect Business Location by PIN Code</div>
              <div style="font-size:0.8rem;color:#94A3B8;">Enter your 6-digit facility or registered office PIN code to automatically locate your district:</div>
            </div>""",
            unsafe_allow_html=True,
        )
        c_pin1, c_pin2 = st.columns([2, 1])
        with c_pin1:
            pin_val = st.text_input(
                "Facility / Office PIN Code (6 digits):",
                value=st.session_state["ob_answers"].get("biz_pincode", ""),
                placeholder="e.g. 560001, 577427, 570001, 580020, 590001...",
                max_chars=6,
                key="ob_biz_pin_input",
            )
        with c_pin2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            click_detect = st.button(":material/location_on: Detect Address", key="btn_detect_biz_pin")

        if pin_val.strip() and (len(pin_val.strip()) == 6 or click_detect):
            res = resolve_pincode(pin_val.strip())
            if res["status"] == "success":
                detected_district = res["district"]
                st.session_state["ob_answers"]["biz_pincode"] = res["pincode"]
                st.session_state["ob_answers"]["biz_formatted_address"] = res["formatted_address"]
                st.session_state["ob_answers"]["biz_detected_state"] = res["state"]
                st.session_state["ob_answers"]["biz_detected_district"] = res["district"]
                st.markdown(
                    f"""<div style="background:rgba(16,185,129,0.12);border:1px solid #34D399;border-radius:10px;padding:12px;margin:8px 0;font-size:0.88rem;color:#A7F3D0;">
                      <i class=ic-circle-check></i> <b>Business Address Detected:</b> {res['formatted_address']}  <br>
                      <span style="font-size:0.78rem;color:#6EE7B7;">District auto-matched to: <b>{res['district']}</b> ({res['source']})</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div class="beie-warning">{res["message"]}</div>', unsafe_allow_html=True)

        st.markdown("<div style='font-size:0.82rem;color:#94A3B8;margin:12px 0 6px 0;'>Or select your district manually:</div>", unsafe_allow_html=True)

    # Name step widget for business
    biz_owner_name = ""
    biz_enterprise_name = ""
    if step.get("is_name_step"):
        st.markdown(
            """<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.25);border-radius:14px;padding:16px;margin:10px 0 16px 0;">
              <div style="font-weight:700;color:#2DD4BF;font-size:0.95rem;margin-bottom:4px;"><i class=ic-factory></i> Personalise Your Enterprise Console</div>
              <div style="font-size:0.82rem;color:#94A3B8;">Enter your name and firm/enterprise name to personalise your executive reports and stress digests:</div>
            </div>""",
            unsafe_allow_html=True,
        )
        c_bname1, c_bname2 = st.columns(2)
        with c_bname1:
            curr_owner = st.session_state["ob_answers"].get("owner_name") or st.session_state.get("user_name", "")
            if curr_owner in ["Bengaluru MSME", "Demo Officer"]:
                curr_owner = ""
            biz_owner_name = st.text_input(
                "Your Name (Owner / CFO / Manager):",
                value=curr_owner,
                placeholder="e.g. Suresh Patil, Arvind Rao...",
                key="ob_biz_owner_name_input",
            )
        with c_bname2:
            curr_biz = st.session_state["ob_answers"].get("business_name", "")
            biz_enterprise_name = st.text_input(
                "Enterprise / Company Name:",
                value=curr_biz,
                placeholder="e.g. Patil Agro Logistics, Karnataka Precision Tech...",
                key="ob_biz_enterprise_name_input",
            )
        selected = biz_owner_name.strip() or biz_enterprise_name.strip()

    elif is_multi:
        selected = st.multiselect(
            "Select all that apply:", chips, key=f"ob_biz_{step['key']}"
        )
    else:
        def_radio_idx = 0
        if detected_district and step["key"] == "district":
            for idx, chip in enumerate(chips):
                if detected_district.lower() in chip.lower() or chip.lower() in detected_district.lower():
                    def_radio_idx = idx
                    break
        selected = st.radio(
            "Choose one:", chips, index=def_radio_idx, key=f"ob_biz_{step['key']}", horizontal=False
        )

    # Contextual 'Other' text description field for business questions
    other_text = ""
    if step.get("has_other") and _is_other_triggered(selected):
        st.markdown(
            f"""<div style="background:rgba(45,212,191,0.08);border:1px solid rgba(45,212,191,0.25);border-radius:12px;padding:16px;margin:12px 0;">
              <div style="font-weight:600;color:#2DD4BF;font-size:0.9rem;margin-bottom:6px;">{step.get('other_prompt', '<i class=ic-file-pen></i> Please describe:')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        prev_other = st.session_state["ob_answers"].get(f"{step['key']}_custom", "")
        other_text = st.text_input(
            "Describe details:",
            value=prev_other,
            placeholder=step.get("other_placeholder", "Type specific business details here..."),
            key=f"ob_biz_input_other_{step['key']}",
            label_visibility="collapsed",
        )

    # Contextual Loan / EMI description field for business
    emi_desc = ""
    emi_amount = 0.0
    if step.get("has_emi_input") and _is_loan_active(selected):
        st.markdown(
            """<div style="background:rgba(249,115,22,0.08);border:1px solid rgba(249,115,22,0.3);border-radius:12px;padding:16px;margin:14px 0;">
              <div style="font-weight:700;color:#F97316;font-size:0.95rem;margin-bottom:4px;"><i class=ic-credit-card></i> Business Debt & Credit Facility Details</div>
              <div style="font-size:0.82rem;color:#94A3B8;">Describe your active business loans, CC lines, or commercial vehicle/equipment EMIs:</div>
            </div>""",
            unsafe_allow_html=True,
        )
        c_emi1, c_emi2 = st.columns([2, 1])
        with c_emi1:
            prev_desc = st.session_state["ob_answers"].get("biz_emi_detail", "")
            emi_desc = st.text_input(
                "Loan / Facility Description (e.g. Delivery fleet EMI, Mudra loan, Machinery loan):",
                value=prev_desc,
                placeholder="e.g. 3 Tata Ace delivery trucks EMI ₹36,000/mo, CNC milling machine term loan ₹45,000/mo...",
                key="ob_biz_input_emi_desc",
            )
        with c_emi2:
            prev_amt = float(st.session_state["ob_answers"].get("biz_emi_monthly_amount", 0.0))
            emi_amount = st.number_input(
                "Total Monthly Debt Outflow (₹/mo):",
                min_value=0.0,
                max_value=100_000_000.0,
                value=prev_amt,
                step=5000.0,
                key="ob_biz_input_emi_amount",
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("Next →", key=f"ob_biz_next_{step_idx}"):
            if step.get("is_name_step"):
                st.session_state["ob_answers"]["owner_name"] = biz_owner_name.strip()
                st.session_state["ob_answers"]["business_name"] = biz_enterprise_name.strip()
                if biz_owner_name.strip():
                    st.session_state["user_name"] = biz_owner_name.strip()
                st.session_state["ob_step"] += 1
                st.rerun()
            elif selected or step.get("skippable", False):
                st.session_state["ob_answers"][step["key"]] = selected
                if other_text.strip():
                    st.session_state["ob_answers"][f"{step['key']}_custom"] = other_text.strip()
                if emi_desc.strip():
                    st.session_state["ob_answers"]["biz_emi_detail"] = emi_desc.strip()
                if emi_amount > 0:
                    st.session_state["ob_answers"]["biz_emi_monthly_amount"] = emi_amount
                st.session_state["ob_step"] += 1
                st.rerun()
    with col2:
        if step.get("skippable") and st.button("Skip", key=f"ob_biz_skip_{step_idx}"):
            st.session_state["ob_answers"][step["key"]] = None
            st.session_state["ob_step"] += 1
            st.rerun()
    with col3:
        if step_idx > 0 and st.button("← Back", key=f"ob_biz_back_{step_idx}"):
            st.session_state["ob_step"] -= 1
            st.rerun()

    st.markdown(
        '<div class="beie-info" style="margin-top:20px"><i class=ic-lock></i> Business profile data is stored locally in your browser session only. No proprietary financials or credentials are transmitted.</div>',
        unsafe_allow_html=True,
    )


def _finalize_business() -> None:
    answers = st.session_state.get("ob_answers", {})
    owner_name = answers.get("owner_name", "").strip() or st.session_state.get("user_name", "")
    biz_name = answers.get("business_name", "").strip()
    if owner_name and owner_name not in ["Bengaluru MSME", "Demo Officer"]:
        st.session_state["user_name"] = owner_name

    btype_raw = answers.get("business_type", "Retail Shop")
    custom_btype = answers.get("business_type_custom", "").strip()
    btype_final = custom_btype if (custom_btype and "Other" in str(btype_raw)) else btype_raw

    sector_raw = answers.get("sector", "Food & Beverages")
    custom_sector = answers.get("sector_custom", "").strip()
    sector_final = custom_sector if (custom_sector and "Other" in str(sector_raw)) else sector_raw

    district_raw = answers.get("district", "Bengaluru Urban")
    custom_district = answers.get("district_custom", "").strip()
    detected_district = answers.get("biz_detected_district", "").strip()
    pincode = answers.get("biz_pincode", "").strip()
    formatted_address = answers.get("biz_formatted_address", "").strip()

    if custom_district and "Other" in str(district_raw):
        district_final = custom_district
    elif detected_district and ("Other" in str(district_raw) or detected_district.lower() in str(district_raw).lower()):
        district_final = detected_district
    else:
        district_final = district_raw

    emi_raw = answers.get("has_emi", "No business loans")
    emi_detail = answers.get("biz_emi_detail", "").strip()
    emi_monthly_amt = float(answers.get("biz_emi_monthly_amount", 0.0))

    if emi_detail:
        emi_display = f"{emi_raw} ({emi_detail})"
    else:
        emi_display = str(emi_raw)

    profile = {
        "panel": "business",
        "name": owner_name,
        "owner_name": owner_name,
        "biz_name": biz_name,
        "business_name": biz_name,
        "language": "en",
        "business_type": btype_final,
        "business_type_custom": custom_btype,
        "sector": sector_final,
        "sector_custom": custom_sector,
        "district": district_final,
        "district_custom": custom_district,
        "pincode": pincode,
        "formatted_address": formatted_address,
        "turnover_band": answers.get("turnover_band", "₹25L–₹2 Crore"),
        "main_inputs": answers.get("main_inputs", []),
        "main_inputs_custom": answers.get("main_inputs_custom", ""),
        "has_emi": emi_display,
        "emi_detail": emi_detail,
        "emi_monthly_amount": emi_monthly_amt,
        "monthly_income": 200000,
        "extracted_context": extract_context_from_text(f"{custom_btype} {custom_sector} {answers.get('main_inputs_custom', '')}"),
    }
    save_profile(profile)
    st.session_state["ob_step"] = 0
    st.session_state["ob_answers"] = {}
    st.rerun()
