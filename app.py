import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
import os
from datetime import datetime
from database import DB_PATH, get_connection, init_db
from data_generator import seed_data
import utils
import textwrap

def clean_html(html_str):
    """Strip leading/trailing whitespaces from each line and join them without newlines
    to prevent the Streamlit markdown parser from splitting HTML into code blocks."""
    lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    return "".join(lines)

# Patches to auto-dedent multiline strings for markdown rendering in Streamlit
_orig_markdown = st.markdown
_orig_sidebar_markdown = st.sidebar.markdown

def patched_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        if body.strip().startswith("<") or "</" in body:
            body = clean_html(body)
        else:
            body = textwrap.dedent(body)
    return _orig_markdown(body, *args, **kwargs)

def patched_sidebar_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        if body.strip().startswith("<") or "</" in body:
            body = clean_html(body)
        else:
            body = textwrap.dedent(body)
    return _orig_sidebar_markdown(body, *args, **kwargs)

st.markdown = patched_markdown
st.sidebar.markdown = patched_sidebar_markdown

# Set up page configurations
st.set_page_config(
    page_title="EcoSphere | ESG Management Platform",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Initialize DB and Seed Data if needed
init_db()
seed_data()

# Trigger automatic scans (compliance overdue dates) and update scores on app load
utils.check_overdue_compliance_issues()
utils.calculate_scores()

# 2. Inject Premium CSS Styling
styles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.css")
if os.path.exists(styles_path):
    with open(styles_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("Custom stylesheet 'styles.css' not found. Using default styles.")

# 3. Handle Active User Profile Session State
if "active_user_id" not in st.session_state:
    # Default active user: Sarah Jenkins (Admin)
    st.session_state["active_user_id"] = 1
    st.session_state["active_user_name"] = "Sarah Jenkins"
    st.session_state["active_user_role"] = "Admin"

# Fetch list of employees to populate profile switcher
with get_connection() as conn:
    df_emps_switch = pd.read_sql_query("SELECT id, name, role FROM employees", conn)

# Sidebar - Active Profile Switcher
st.sidebar.markdown("<h2 style='text-align: center;'>🌎 EcoSphere</h2>", unsafe_allow_html=True)
st.sidebar.subheader("👤 Active Profile Switcher")

# Format name for dropdown selectbox
user_options = {row["name"]: (row["id"], row["name"], row["role"]) for _, row in df_emps_switch.iterrows()}
current_user_name = [name for name, val in user_options.items() if val[0] == st.session_state["active_user_id"]]
default_index = list(user_options.keys()).index(current_user_name[0]) if current_user_name else 0

selected_user = st.sidebar.selectbox(
    "Switch Profile context to:",
    options=list(user_options.keys()),
    index=default_index
)

# Update session state on change
user_id, user_name, user_role = user_options[selected_user]
if st.session_state["active_user_id"] != user_id:
    st.session_state["active_user_id"] = user_id
    st.session_state["active_user_name"] = user_name
    st.session_state["active_user_role"] = user_role
    st.rerun()

# Display active user card in sidebar
# Query details for current employee
with get_connection() as conn:
    emp_details = pd.read_sql_query(
        "SELECT e.*, d.name as department_name FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE e.id = ?",
        conn, params=(user_id,)
    )

if not emp_details.empty:
    emp = emp_details.iloc[0]
    avatar = "💼" if user_role == "Admin" else ("🔎" if user_role == "Auditor" else "🌱")
    st.sidebar.markdown(f"""
    <div class="sidebar-profile">
        <div class="profile-avatar">{avatar}</div>
        <div class="profile-name">{emp['name']}</div>
        <div class="profile-role">{emp['role']} ({emp['department_name'] or 'N/A'})</div>
        <div style="margin-top: 8px; font-size: 0.85rem; color: #94a3b8;">
            <b>XP:</b> {emp['xp']} | <b>Points:</b> {emp['points']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation Menu
st.sidebar.subheader("🧭 Navigation Menu")
menu_selection = st.sidebar.radio(
    "Go to page:",
    [
        "📊 Overview Dashboard",
        "🍀 Environmental Module",
        "🤝 Social Module",
        "⚖️ Governance Module",
        "🏆 Gamification Portal",
        "📋 Custom Report Builder",
        "⚙️ Settings & Configuration"
    ]
)

# ----------------- 📊 Overview Dashboard -----------------
if menu_selection == "📊 Overview Dashboard":
    st.markdown("<h1 class='gradient-text-blue'>📊 Organization ESG Overview</h1>", unsafe_allow_html=True)
    st.write("Real-time monitoring of Environmental, Social, and Governance performance indexes.")

    # Fetch cached scores
    with get_connection() as conn:
        df_ds = pd.read_sql_query("""
            SELECT AVG(environmental_score) as env, AVG(social_score) as soc, AVG(governance_score) as gov, AVG(total_score) as total
            FROM department_scores
        """, conn)

    if not df_ds.empty and df_ds.iloc[0]["total"] is not None:
        row = df_ds.iloc[0]
        env_val = row["env"]
        soc_val = row["soc"]
        gov_val = row["gov"]
        total_val = row["total"]
    else:
        env_val = soc_val = gov_val = total_val = 100.0

    # Score Cards Row
    st.markdown(f"""
    <div class="esg-card-container">
        <div class="esg-card card-total">
            <div class="card-title">Overall ESG Index</div>
            <div class="card-value">{total_val:.1f}</div>
            <div class="card-subtext">Weighted Organizational Score</div>
        </div>
        <div class="esg-card card-env">
            <div class="card-title">Environmental Score</div>
            <div class="card-value">{env_val:.1f}</div>
            <div class="card-subtext">Carbon Footprint & Eco Goals</div>
        </div>
        <div class="esg-card card-soc">
            <div class="card-title">Social Score</div>
            <div class="card-value">{soc_val:.1f}</div>
            <div class="card-subtext">CSR, Diversity & Engagement</div>
        </div>
        <div class="esg-card card-gov">
            <div class="card-title">Governance Score</div>
            <div class="card-value">{gov_val:.1f}</div>
            <div class="card-subtext">Audits, Compliance & Policies</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍀 Environmental Carbon Emissions Trend")
        # Fetch carbon emissions per month grouped by department
        with get_connection() as conn:
            df_emissions = pd.read_sql_query("""
                SELECT strftime('%Y-%m', transaction_date) as month, d.name as department, SUM(calculated_emissions) as emissions
                FROM carbon_transactions ct
                JOIN departments d ON ct.department_id = d.id
                GROUP BY month, department
                ORDER BY month ASC
            """, conn)
        
        if not df_emissions.empty:
            chart = alt.Chart(df_emissions).mark_line(point=True).encode(
                x=alt.X('month:T', title='Month'),
                y=alt.Y('emissions:Q', title='Emissions (kg CO2)'),
                color='department:N',
                tooltip=['month', 'department', 'emissions']
            ).properties(height=300).configure_view(strokeOpacity=0)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No carbon emissions recorded yet.")

    with col2:
        st.subheader("⚖️ Governance Compliance Issues")
        # Query counts of Open, Overdue, and Resolved compliance issues
        with get_connection() as conn:
            df_comp_status = pd.read_sql_query("""
                SELECT status, COUNT(*) as count 
                FROM compliance_issues 
                GROUP BY status
            """, conn)

        if not df_comp_status.empty:
            donut_chart = alt.Chart(df_comp_status).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="count", type="quantitative"),
                color=alt.Color(field="status", type="nominal", scale=alt.Scale(
                    domain=['Open', 'Overdue', 'Resolved'],
                    range=['#fbbf24', '#f87171', '#34d399']
                )),
                tooltip=['status', 'count']
            ).properties(height=300)
            st.altair_chart(donut_chart, use_container_width=True)
        else:
            st.info("No compliance issues logged.")

    col3, col4 = st.columns([3, 2])

    with col3:
        st.subheader("🏆 Department Score Leaderboard")
        with get_connection() as conn:
            df_leaderboard = pd.read_sql_query("""
                SELECT d.name as Department, d.code as Code, d.head as Head, d.employee_count as Employees,
                       ds.environmental_score as Env, ds.social_score as Soc, ds.governance_score as Gov, ds.total_score as Total
                FROM department_scores ds
                JOIN departments d ON ds.department_id = d.id
                ORDER BY ds.total_score DESC
            """, conn)
        
        # Format the table using custom HTML rankings
        html_table = """
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Department</th>
                    <th>Head</th>
                    <th>Env</th>
                    <th>Soc</th>
                    <th>Gov</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, row in df_leaderboard.iterrows():
            rank_class = f"rank-{i+1}" if i < 3 else "rank-other"
            html_table += f"""
            <tr class="leaderboard-row">
                <td><span class="rank-pill {rank_class}">{i+1}</span></td>
                <td><b>{row['Department']}</b> <code style='font-size:0.8rem;'>{row['Code']}</code></td>
                <td>{row['Head']}</td>
                <td style='color:#34d399;'>{row['Env']:.1f}</td>
                <td style='color:#60a5fa;'>{row['Soc']:.1f}</td>
                <td style='color:#a78bfa;'>{row['Gov']:.1f}</td>
                <td><b>{row['Total']:.1f}</b></td>
            </tr>
            """
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)

    with col4:
        st.subheader("🔔 In-App Notifications")
        user_notifications = utils.get_notifications(user_id, unread_only=False)
        
        if user_notifications:
            # Mark all as read button
            if st.button("Mark All as Read"):
                utils.mark_notifications_read(user_id)
                st.success("Notifications marked as read!")
                st.rerun()

            noti_html = "<div class='notification-container'>"
            # Show top 5
            for item in user_notifications[:5]:
                read_dot = "●" if item['is_read'] == 0 else ""
                noti_html += f"""
                <div class="notification-item type-{item['type']}">
                    <div>
                        <span style="color:#fbbf24; font-size:1.1rem; margin-right:4px;">{read_dot}</span>
                        <span class="notification-message">{item['message']}</span>
                    </div>
                    <div class="notification-time">{item['created_at'].split()[0]}</div>
                </div>
                """
            noti_html += "</div>"
            st.markdown(noti_html, unsafe_allow_html=True)
        else:
            st.info("You have no notifications.")

# ----------------- 🍀 Environmental Module -----------------
elif menu_selection == "🍀 Environmental Module":
    st.markdown("<h1 class='gradient-text-green'>🍀 Environmental & Carbon Accounting</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏭 ERP Simulator & Operations", "📊 Carbon Ledger", "🎯 Emission Factors & Goals"])

    with tab1:
        st.header("🏭 Operational ERP Simulator")
        st.write("Post daily business transaction activities to simulate automatic carbon footprint accounting.")

        col_form, col_pending = st.columns([1, 1])

        with col_form:
            st.subheader("Log Operational Event")
            with st.form("erp_log_form"):
                rec_type = st.selectbox("Record Type", ["Purchase", "Manufacturing", "Expense", "Fleet"])
                description = st.text_input("Description", placeholder="e.g., Factory A Electricity Grid Supply")
                amount = st.number_input("Amount (Activity Unit)", min_value=0.1, step=1.0)
                
                # Fetch departments & factors matching type
                with get_connection() as conn:
                    depts = pd.read_sql_query("SELECT id, name FROM departments WHERE status = 'Active'", conn)
                    factors = pd.read_sql_query("SELECT id, name, unit, factor FROM emission_factors WHERE category = ?", conn, params=(rec_type,))

                dept_choice = st.selectbox("Department Name", options=depts["name"].tolist())
                factor_choice = st.selectbox(
                    "Linked Emission Factor", 
                    options=[f"{r['name']} ({r['factor']} kg CO2 / {r['unit']})" for _, r in factors.iterrows()]
                )

                submit_btn = st.form_submit_button("Post Transaction")

                if submit_btn:
                    # Resolve IDs
                    selected_dept_id = depts[depts["name"] == dept_choice]["id"].values[0]
                    factor_name = factor_choice.split(" (")[0]
                    selected_factor_row = factors[factors["name"] == factor_name].iloc[0]
                    selected_factor_id = selected_factor_row["id"]
                    unit = selected_factor_row["unit"]

                    # Write record
                    now_date = datetime.now().strftime("%Y-%m-%d")
                    auto_calc = utils.get_setting("auto_emission_calculation", "True")
                    status = "Pending" if auto_calc != "True" else "Processed"

                    with get_connection() as conn:
                        cursor = conn.cursor()
                        erp_id = utils.execute_write("""
                            INSERT INTO erp_records (type, description, amount, unit, department_id, date, emission_factor_id, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (rec_type, description, amount, unit, int(selected_dept_id), now_date, int(selected_factor_id), status))
                        
                    st.success(f"ERP Record successfully posted! Status: {status}")
                    
                    if auto_calc == "True":
                        utils.process_erp_record(erp_id)
                        st.info("Auto calculation active. Carbon Transaction generated instantly.")
                    st.rerun()

        with col_pending:
            st.subheader("Pending ERP Records Queue")
            with get_connection() as conn:
                df_pending = pd.read_sql_query("""
                    SELECT er.id, er.type, er.description, er.amount, er.unit, d.name as department, er.date
                    FROM erp_records er
                    JOIN departments d ON er.department_id = d.id
                    WHERE er.status = 'Pending'
                """, conn)

            if not df_pending.empty:
                st.dataframe(df_pending, use_container_width=True)
                
                # Option to process
                if st.session_state["active_user_role"] in ["Admin", "Auditor"]:
                    record_to_process = st.selectbox("Select Record ID to process manually:", df_pending["id"].tolist())
                    if st.button("Process & Generate Emissions"):
                        success = utils.process_erp_record(record_to_process)
                        if success:
                            st.success(f"Calculated and logged emissions for ERP Record #{record_to_process}.")
                            st.rerun()
                else:
                    st.warning("Only Admins or Auditors can process pending ERP records manually.")
            else:
                st.info("No pending ERP records in the integration queue.")

    with tab2:
        st.header("📊 Carbon Transactions Ledger")
        with get_connection() as conn:
            df_ledger = pd.read_sql_query("""
                SELECT ct.id, ct.transaction_date as Date, d.name as Department, ct.source_type as Source, 
                       ct.activity_amount as Amount, ef.unit as Unit, ef.name as Emission_Factor, ct.calculated_emissions as [Emissions (kg CO2)]
                FROM carbon_transactions ct
                JOIN departments d ON ct.department_id = d.id
                JOIN emission_factors ef ON ct.emission_factor_id = ef.id
                ORDER BY ct.id DESC
            """, conn)
        
        if not df_ledger.empty:
            st.dataframe(df_ledger, use_container_width=True)
        else:
            st.info("No carbon transactions logged yet.")

    with tab3:
        st.header("🎯 System Emission Factors")
        with get_connection() as conn:
            df_ef = pd.read_sql_query("SELECT name as Name, code as Code, factor as [Factor (kg CO2 / Unit)], unit as Unit, category as Category FROM emission_factors", conn)
        st.dataframe(df_ef, use_container_width=True)

        st.subheader("🎯 Active Sustainability & Environmental Goals")
        with get_connection() as conn:
            df_goals = pd.read_sql_query("SELECT * FROM environmental_goals", conn)

        for _, goal in df_goals.iterrows():
            progress_pct = min(1.0, goal['current_value'] / goal['target_value']) if goal['target_value'] > 0 else 1.0
            
            # Formulate color status pills
            status_style = "status-on-track"
            if goal['status'] == "At Risk":
                status_style = "status-at-risk"
            elif goal['status'] == "Achieved":
                status_style = "status-achieved"

            st.markdown(f"""
            <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                    <span style="font-weight:700; font-size:1.1rem; color:#ffffff;">{goal['title']}</span>
                    <span class="status-pill {status_style}">{goal['status']}</span>
                </div>
                <div style="font-size:0.875rem; color:#94a3b8; margin-bottom: 8px;">{goal['description']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.85rem; color:#f8fafc; margin-bottom: 4px;">
                    <span><b>Progress:</b> {goal['current_value']} / {goal['target_value']} {goal['unit']}</span>
                    <span>{progress_pct*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress_pct)

# ----------------- 🤝 Social Module -----------------
elif menu_selection == "🤝 Social Module":
    st.markdown("<h1 class='gradient-text-blue'>🤝 Social Operations & CSR Engagement</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🌳 CSR Activities bulletin", "📊 Diversity Metrics"])

    with tab1:
        st.header("🌳 Corporate Social Responsibility (CSR) Volunteering")
        st.write("Browse company-wide social campaigns, enroll to volunteer, and submit evidence.")

        col_acts, col_manage = st.columns([2, 1.2])

        with col_acts:
            st.subheader("CSR Campaigns Catalog")
            with get_connection() as conn:
                df_csr = pd.read_sql_query("SELECT c.*, cat.name as category_name FROM csr_activities c JOIN categories cat ON c.category_id = cat.id", conn)

            for _, act in df_csr.iterrows():
                # Fetch total approved participants
                with get_connection() as conn:
                    part_count = pd.read_sql_query("""
                        SELECT COUNT(*) as count FROM employee_participations 
                        WHERE activity_id = ? AND approval_status = 'Approved'
                    """, conn, params=(act["id"],)).iloc[0]["count"]

                status_style = "status-completed" if act["status"] == "Completed" else "status-active"

                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                        <span style="font-weight:700; font-size:1.15rem; color:#ffffff;">{act['title']}</span>
                        <div>
                            <span class="status-pill status-approved" style="margin-right:6px;">🏆 {act['points_value']} Points</span>
                            <span class="status-pill {status_style}">{act['status']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.875rem; color:#94a3b8; margin-bottom: 8px;">{act['description']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.825rem; color:#cbd5e1;">
                        <span>📅 <b>Date:</b> {act['date']} | 🏷️ <b>Category:</b> {act['category_name']}</span>
                        <span><b>Volunteers:</b> {part_count} Active</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action button based on active role
                # Standard employees can join
                if act["status"] == "Active":
                    # Check if already joined
                    with get_connection() as conn:
                        participation = pd.read_sql_query(
                            "SELECT * FROM employee_participations WHERE employee_id = ? AND activity_id = ?",
                            conn, params=(user_id, act["id"])
                        )

                    if participation.empty:
                        with st.expander(f"Register for {act['title']}"):
                            proof_file = st.text_input("Add description/mock file (e.g. proof.jpg)", key=f"proof_csr_{act['id']}")
                            if st.button("Submit Registration", key=f"reg_csr_{act['id']}"):
                                required = utils.get_setting("evidence_requirement", "True")
                                if required == "True" and not proof_file:
                                    st.error("Submission failed. Proof file is required per system settings.")
                                else:
                                    execute_write("""
                                        INSERT INTO employee_participations (employee_id, activity_id, proof_file, approval_status, points_earned)
                                        VALUES (?, ?, ?, 'Pending', 0)
                                    """, (user_id, act["id"], proof_file))
                                    st.success("Successfully registered! Awaiting admin approval.")
                                    st.rerun()
                    else:
                        status = participation.iloc[0]["approval_status"]
                        st.markdown(f"Status of your application: <span class='status-pill status-{status.lower()}'>{status}</span>", unsafe_allow_html=True)
                        st.write("---")

        with col_manage:
            if st.session_state["active_user_role"] == "Admin":
                st.subheader("⚙️ Admin CSR Approvals Panel")
                with get_connection() as conn:
                    df_pending_csr = pd.read_sql_query("""
                        SELECT ep.id, e.name as employee, e.id as emp_id, a.title as activity, ep.proof_file, a.points_value
                        FROM employee_participations ep
                        JOIN employees e ON ep.employee_id = e.id
                        JOIN csr_activities a ON ep.activity_id = a.id
                        WHERE ep.approval_status = 'Pending'
                    """, conn)

                if not df_pending_csr.empty:
                    for _, req in df_pending_csr.iterrows():
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1rem; margin-bottom:0.75rem;">
                            <b>User:</b> {req['employee']}<br>
                            <b>Activity:</b> {req['activity']}<br>
                            <b>Proof attached:</b> <code>{req['proof_file'] or 'None'}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        col_app, col_rej = st.columns(2)
                        
                        # Use unique buttons
                        if col_app.button("Approve", key=f"app_csr_sub_{req['id']}"):
                            # Update participation
                            now_date = datetime.now().strftime("%Y-%m-%d")
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE employee_participations 
                                    SET approval_status = 'Approved', points_earned = ?, completion_date = ?
                                    WHERE id = ?
                                """, (req["points_value"], now_date, req["id"]))
                                # Award points to employee
                                cursor.execute("UPDATE employees SET points = points + ? WHERE id = ?", (req["points_value"], req["emp_id"]))
                                conn.commit()
                            # Notify employee
                            utils.add_notification(req["emp_id"], f"Your participation in '{req['activity']}' was approved! +{req['points_value']} points awarded.", "CSR")
                            # Trigger badges check
                            utils.check_badge_awards(req["emp_id"])
                            st.success(f"Approved {req['employee']}'s submission.")
                            st.rerun()

                        if col_rej.button("Reject", key=f"rej_csr_sub_{req['id']}"):
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("UPDATE employee_participations SET approval_status = 'Rejected' WHERE id = ?", (req["id"],))
                                conn.commit()
                            utils.add_notification(req["emp_id"], f"Your participation in '{req['activity']}' was rejected.", "CSR")
                            st.warning(f"Rejected {req['employee']}'s submission.")
                            st.rerun()
                else:
                    st.info("No pending CSR approvals.")
            else:
                st.subheader("💡 CSR Info")
                st.info("Log in as Admin to access the volunteer approval queue panel.")

    with tab2:
        st.header("📊 Diversity & Demographic Metrics")
        
        # Gender ratio (Simulated or based on employees list)
        # In a real system, employees would have metadata. Let's build a nice chart based on departments employee count
        with get_connection() as conn:
            df_dept_counts = pd.read_sql_query("SELECT name, employee_count FROM departments", conn)

        st.subheader("Departmental Headcount Distribution")
        dept_chart = alt.Chart(df_dept_counts).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('name:N', title='Department', sort='-y'),
            y=alt.Y('employee_count:Q', title='Employee Count'),
            color=alt.Color('name:N', legend=None)
        ).properties(height=350)
        st.altair_chart(dept_chart, use_container_width=True)

# ----------------- ⚖️ Governance Module -----------------
elif menu_selection == "⚖️ Governance Module":
    st.markdown("<h1 class='gradient-text-gold'>⚖️ Governance & Compliance Hub</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Compliance Policies", "🔍 Internal Audits", "⚠️ Compliance Issues"])

    with tab1:
        st.header("📝 Corporate Compliance Policies")
        st.write("Review core compliance policies and record acknowledgements.")

        col_pols, col_stats = st.columns([1.5, 1])

        with col_pols:
            st.subheader("Active Corporate Policies")
            with get_connection() as conn:
                df_pols = pd.read_sql_query("SELECT * FROM esg_policies WHERE status = 'Active'", conn)

            for _, policy in df_pols.iterrows():
                # Check if current user acknowledged
                with get_connection() as conn:
                    ack = pd.read_sql_query(
                        "SELECT * FROM policy_acknowledgements WHERE employee_id = ? AND policy_id = ?",
                        conn, params=(user_id, policy["id"])
                    )
                
                is_acknowledged = not ack.empty

                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                        <span style="font-weight:700; font-size:1.1rem; color:#ffffff;">{policy['title']}</span>
                        <span class="status-pill status-approved">v{policy['version']}</span>
                    </div>
                    <div style="font-size:0.875rem; color:#94a3b8; margin-bottom: 12px;">{policy['description']}</div>
                    <div style="font-size:0.825rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center;">
                        <span>📅 <b>Effective:</b> {policy['effective_date']} | 🏛️ <b>Category:</b> {policy['category']}</span>
                        <span><b>Status:</b> {"✅ Acknowledged" if is_acknowledged else "⚠️ Pending"}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not is_acknowledged:
                    if st.button("Acknowledge Policy", key=f"ack_pol_{policy['id']}"):
                        now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        execute_write("""
                            INSERT INTO policy_acknowledgements (policy_id, employee_id, acknowledgement_date)
                            VALUES (?, ?, ?)
                        """, (policy["id"], user_id, now_dt))
                        st.success(f"Acknowledged policy: '{policy['title']}'")
                        utils.calculate_scores()
                        st.rerun()

        with col_stats:
            st.subheader("Policy Compliance Stats")
            with get_connection() as conn:
                df_ack_stats = pd.read_sql_query("""
                    SELECT p.title as Policy, COUNT(pa.id) as Acks
                    FROM esg_policies p
                    LEFT JOIN policy_acknowledgements pa ON p.id = pa.policy_id
                    WHERE p.status = 'Active'
                    GROUP BY p.id
                """, conn)
            
            st.dataframe(df_ack_stats, use_container_width=True)

    with tab2:
        st.header("🔍 Corporate Internal Audits")
        with get_connection() as conn:
            df_audits = pd.read_sql_query("SELECT id, title as Title, scope as Scope, auditor as Auditor, audit_date as Date, score as Score, findings as Findings, status as Status FROM audits ORDER BY id DESC", conn)
        
        st.dataframe(df_audits, use_container_width=True)

        if st.session_state["active_user_role"] in ["Admin", "Auditor"]:
            with st.expander("Log New Internal Audit Record"):
                with st.form("audit_form"):
                    a_title = st.text_input("Audit Title")
                    a_scope = st.text_input("Scope")
                    a_auditor = st.text_input("Auditor Organization")
                    a_score = st.slider("Audit Score (Percentage)", 0.0, 100.0, 90.0)
                    a_findings = st.text_area("Audit Findings / Recommendations")
                    a_status = st.selectbox("Audit Status", ["Planned", "In Progress", "Completed"])
                    
                    submit_a = st.form_submit_button("Record Audit")

                    if submit_a:
                        now_d = datetime.now().strftime("%Y-%m-%d")
                        execute_write("""
                            INSERT INTO audits (title, scope, auditor, audit_date, score, findings, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (a_title, a_scope, a_auditor, now_d, a_score, a_findings, a_status))
                        st.success("New audit registered successfully.")
                        utils.calculate_scores()
                        st.rerun()

    with tab3:
        st.header("⚠️ Compliance & Governance Issues")
        
        col_list, col_add = st.columns([2, 1])

        with col_list:
            st.subheader("Active Issues Tracking")
            with get_connection() as conn:
                df_issues = pd.read_sql_query("""
                    SELECT ci.id, ci.description as Description, ci.severity as Severity, e.name as Owner, ci.due_date as [Due Date], ci.status as Status, ci.owner_id
                    FROM compliance_issues ci
                    JOIN employees e ON ci.owner_id = e.id
                    ORDER BY 
                      CASE ci.status 
                        WHEN 'Overdue' THEN 1 
                        WHEN 'Open' THEN 2 
                        ELSE 3 
                      END ASC
                """, conn)

            for _, issue in df_issues.iterrows():
                status_style = "status-" + issue["Status"].lower()
                
                # Check owner to render resolution action
                owned_by_current = issue["owner_id"] == user_id

                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                        <span style="font-weight:700; font-size:1.05rem; color:#ffffff;">{issue['Description']}</span>
                        <div>
                            <span class="status-pill status-at-risk" style="margin-right:6px;">{issue['Severity']}</span>
                            <span class="status-pill {status_style}">{issue['Status']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center;">
                        <span>👤 <b>Owner:</b> {issue['Owner']} | 📅 <b>Due Date:</b> {issue['Due Date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if issue["Status"] in ["Open", "Overdue"] and (owned_by_current or st.session_state["active_user_role"] == "Admin"):
                    if st.button("Mark as Resolved", key=f"resolve_issue_{issue['id']}"):
                        with get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE compliance_issues SET status = 'Resolved' WHERE id = ?", (issue["id"],))
                            conn.commit()
                        st.success("Issue resolved!")
                        utils.calculate_scores()
                        st.rerun()

        with col_add:
            if st.session_state["active_user_role"] in ["Admin", "Auditor"]:
                st.subheader("Raise Compliance Issue")
                with st.form("issue_form"):
                    desc = st.text_input("Description of issue")
                    sev = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
                    
                    # Fetch employee names
                    with get_connection() as conn:
                        emp_list = pd.read_sql_query("SELECT id, name FROM employees", conn)
                    
                    owner_choice = st.selectbox("Assign Owner", options=emp_list["name"].tolist())
                    due_date = st.date_input("Due Date")

                    submit_issue = st.form_submit_button("Raise Issue")

                    if submit_issue:
                        owner_id_val = emp_list[emp_list["name"] == owner_choice]["id"].values[0]
                        due_date_str = due_date.strftime("%Y-%m-%d")

                        execute_write("""
                            INSERT INTO compliance_issues (severity, description, owner_id, due_date, status)
                            VALUES (?, ?, ?, ?, 'Open')
                        """, (sev, desc, int(owner_id_val), due_date_str))
                        
                        # Notify Owner
                        utils.add_notification(owner_id_val, f"A new compliance issue: '{desc}' has been raised and assigned to you.", "Compliance")
                        
                        st.success("Governance issue registered successfully!")
                        utils.calculate_scores()
                        st.rerun()
            else:
                st.subheader("Raise Issue Panel")
                st.info("Log in as Admin or Auditor to raise compliance violations.")

# ----------------- 🏆 Gamification Portal -----------------
elif menu_selection == "🏆 Gamification Portal":
    st.markdown("<h1 class='gradient-text-gold'>🏆 Gamification & Rewards Center</h1>", unsafe_allow_html=True)
    
    # Active employee details
    st.markdown(f"### Welcome to the Gamification Center, **{user_name}**!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Leaderboard", "⚔️ Active Challenges", "🏅 Badges", "🎁 Rewards Shop"])

    with tab1:
        st.header("🔥 Employee XP Leaderboard")
        with get_connection() as conn:
            df_leader = pd.read_sql_query("""
                SELECT name as Name, xp as [XP Accumulated], points as [Points Balance], role as Role
                FROM employees 
                ORDER BY xp DESC
            """, conn)
        
        # Display as a styled leaderboard table
        html_lead = """
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>XP (Level Points)</th>
                    <th>Redeemable Points</th>
                    <th>Role</th>
                </tr>
            </thead>
            <tbody>
        """
        for i, row in df_leader.iterrows():
            rank_class = f"rank-{i+1}" if i < 3 else "rank-other"
            html_lead += f"""
            <tr class="leaderboard-row">
                <td><span class="rank-pill {rank_class}">{i+1}</span></td>
                <td><b>{row['Name']}</b></td>
                <td>🔥 {row['XP Accumulated']} XP</td>
                <td>💎 {row['Points Balance']} pts</td>
                <td>{row['Role']}</td>
            </tr>
            """
        html_lead += "</tbody></table>"
        st.markdown(html_lead, unsafe_allow_html=True)

    with tab2:
        st.header("⚔️ Sustainability & Compliance Challenges")
        st.write("Join active challenges, record your progress, and get rewarded.")

        col_challs, col_rev = st.columns([1.5, 1])

        with col_challs:
            st.subheader("Challenges bulletin")
            with get_connection() as conn:
                df_challenges = pd.read_sql_query("SELECT c.*, cat.name as category_name FROM challenges c JOIN categories cat ON c.category_id = cat.id", conn)

            for _, chal in df_challenges.iterrows():
                # Get current employee status
                with get_connection() as conn:
                    participation = pd.read_sql_query(
                        "SELECT * FROM challenge_participations WHERE employee_id = ? AND challenge_id = ?",
                        conn, params=(user_id, chal["id"])
                    )

                is_participating = not participation.empty
                progress = participation.iloc[0]["progress"] if is_participating else 0
                approval = participation.iloc[0]["approval_status"] if is_participating else "None"
                
                status_style = "status-" + chal["status"].lower()

                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                        <span style="font-weight:700; font-size:1.15rem; color:#ffffff;">{chal['title']}</span>
                        <div>
                            <span class="status-pill status-completed" style="margin-right:6px;">🔥 {chal['xp']} XP</span>
                            <span class="status-pill {status_style}">{chal['status']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.875rem; color:#94a3b8; margin-bottom: 12px;">{chal['description']}</div>
                    <div style="font-size:0.825rem; color:#cbd5e1; display:flex; justify-content:space-between; align-items:center;">
                        <span>📅 <b>Deadline:</b> {chal['deadline']} | 🏔️ <b>Difficulty:</b> {chal['difficulty']}</span>
                        <span><b>Joined:</b> {"Yes ✅" if is_participating else "No"}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if chal["status"] == "Active":
                    if not is_participating:
                        if st.button("Join Challenge", key=f"join_chal_{chal['id']}"):
                            execute_write("""
                                INSERT INTO challenge_participations (challenge_id, employee_id, progress, approval_status, xp_awarded)
                                VALUES (?, ?, 0, 'Pending', 0)
                            """, (chal["id"], user_id))
                            st.success("Successfully registered for challenge! Log progress below.")
                            st.rerun()
                    else:
                        with st.expander(f"Update Progress: {chal['title']}"):
                            st.write(f"Approval status of submission: **{approval}**")
                            prog_val = st.slider("Select progress %", 0, 100, progress, key=f"progress_slider_{chal['id']}")
                            proof_text = st.text_input("Evidence description / mock file:", value=participation.iloc[0]["proof_file"] or "", key=f"proof_chal_{chal['id']}")
                            
                            if st.button("Submit Progress Update", key=f"up_chal_{chal['id']}"):
                                with get_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE challenge_participations 
                                        SET progress = ?, proof_file = ?, approval_status = 'Pending'
                                        WHERE challenge_id = ? AND employee_id = ?
                                    """, (prog_val, proof_text, chal["id"], user_id))
                                    conn.commit()
                                st.success("Challenge progress updated! Awaiting approval.")
                                st.rerun()
                st.write("---")

        with col_rev:
            if st.session_state["active_user_role"] == "Admin":
                st.subheader("⚙️ Admin Challenge Approvals")
                with get_connection() as conn:
                    df_pending_chal = pd.read_sql_query("""
                        SELECT cp.id, e.name as employee, e.id as emp_id, c.title as challenge, cp.progress, cp.proof_file, c.xp, cp.challenge_id
                        FROM challenge_participations cp
                        JOIN employees e ON cp.employee_id = e.id
                        JOIN challenges c ON cp.challenge_id = c.id
                        WHERE cp.approval_status = 'Pending' AND cp.progress = 100
                    """, conn)

                if not df_pending_chal.empty:
                    for _, req in df_pending_chal.iterrows():
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1rem; margin-bottom:0.75rem;">
                            <b>User:</b> {req['employee']}<br>
                            <b>Challenge:</b> {req['challenge']}<br>
                            <b>Progress:</b> {req['progress']}%<br>
                            <b>Proof attached:</b> <code>{req['proof_file'] or 'None'}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        col_app, col_rej = st.columns(2)
                        
                        if col_app.button("Approve", key=f"app_chal_sub_{req['id']}"):
                            now_date = datetime.now().strftime("%Y-%m-%d")
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                # Mark participation as approved
                                cursor.execute("""
                                    UPDATE challenge_participations 
                                    SET approval_status = 'Approved', xp_awarded = ?, completion_date = ?
                                    WHERE id = ?
                                """, (req["xp"], now_date, req["id"]))
                                # Add XP to employee
                                cursor.execute("UPDATE employees SET xp = xp + ?, points = points + ? WHERE id = ?", (req["xp"], req["xp"], req["emp_id"]))
                                conn.commit()
                            
                            utils.add_notification(req["emp_id"], f"Your submission for challenge '{req['challenge']}' has been approved! +{req['xp']} XP / points awarded.", "Challenge")
                            # Trigger badges check
                            utils.check_badge_awards(req["emp_id"])
                            utils.calculate_scores()
                            st.success(f"Approved {req['employee']}'s completion.")
                            st.rerun()

                        if col_rej.button("Reject", key=f"rej_chal_sub_{req['id']}"):
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("UPDATE challenge_participations SET approval_status = 'Rejected' WHERE id = ?", (req["id"],))
                                conn.commit()
                            utils.add_notification(req["emp_id"], f"Your submission for challenge '{req['challenge']}' was rejected.", "Challenge")
                            st.warning(f"Rejected {req['employee']}'s submission.")
                            st.rerun()
                else:
                    st.info("No pending challenge submissions.")
            else:
                st.subheader("💡 Challenge Info")
                st.info("Log in as Admin to access the challenge completion approval queue.")

    with tab3:
        st.header("🏅 Unlocked Badges")
        
        # Load user badges
        with get_connection() as conn:
            user_badge_ids = [r["badge_id"] for r in execute_query("SELECT badge_id FROM employee_badges WHERE employee_id = ?", (user_id,))]
            all_badges = execute_query("SELECT * FROM badges")

        # HTML badges display
        badge_html = "<div class='badges-container'>"
        for badge in all_badges:
            unlocked = badge["id"] in user_badge_ids
            locked_class = "" if unlocked else "badge-locked"
            locked_label = "" if unlocked else "<div style='font-size:0.7rem; color:#f87171; font-weight:700; margin-top:2px;'>LOCKED</div>"
            
            badge_html += f"""
            <div class="badge-item {locked_class}">
                <div class="badge-icon">{badge['icon']}</div>
                <div class="badge-name">{badge['name']}</div>
                <div class="badge-desc">{badge['description']}</div>
                {locked_label}
            </div>
            """
        badge_html += "</div>"
        st.markdown(badge_html, unsafe_allow_html=True)

    with tab4:
        st.header("🎁 Redeem Rewards Shop")
        st.write(f"Your point balance: **💎 {emp['points']} Points**")

        # Query reward catalogs
        with get_connection() as conn:
            rewards = execute_query("SELECT * FROM rewards WHERE status = 'Active'")

        rewards_html = "<div class='rewards-grid'>"
        
        col_item_shop, col_buy_logic = st.columns([2, 1])

        with col_item_shop:
            for item in rewards:
                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.3); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                        <span style="font-weight:700; font-size:1.1rem; color:#ffffff;">{item['name']}</span>
                        <span class="status-pill status-completed">💎 {item['points_required']} Points</span>
                    </div>
                    <div style="font-size:0.875rem; color:#cbd5e1; margin-bottom: 8px;">{item['description']}</div>
                    <div style="font-size:0.8rem; color:#94a3b8;">📦 <b>Stock available:</b> {item['stock']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Check requirements
                can_redeem = emp['points'] >= item['points_required'] and item['stock'] > 0
                
                # Unique button key
                btn_label = "Redeem" if item['stock'] > 0 else "Out of Stock"
                if st.button(f"{btn_label} '{item['name']}'", disabled=not can_redeem, key=f"buy_item_{item['id']}"):
                    # Execute redemption
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        # Deduct employee points
                        cursor.execute("UPDATE employees SET points = points - ? WHERE id = ?", (item['points_required'], user_id))
                        # Decrement stock
                        cursor.execute("UPDATE rewards SET stock = stock - 1 WHERE id = ?", (item['id'],))
                        conn.commit()
                    
                    # Notify
                    utils.add_notification(user_id, f"Redeemed '{item['name']}' successfully! -{item['points_required']} points.", "CSR")
                    st.success(f"You have successfully redeemed: '{item['name']}'!")
                    st.rerun()
                st.write("---")

# ----------------- 📋 Custom Report Builder -----------------
elif menu_selection == "📋 Custom Report Builder":
    st.markdown("<h1 class='gradient-text-blue'>📋 Custom ESG Report Builder</h1>", unsafe_allow_html=True)
    st.write("Build tailored ESG compliance reports and export them immediately.")

    # Search Filters Form
    with st.expander("Filter Criteria Options", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            with get_connection() as conn:
                depts_list = pd.read_sql_query("SELECT id, name FROM departments", conn)
            dept_filt = st.selectbox("Department", ["All"] + depts_list["name"].tolist())

        with col_f2:
            module_filt = st.selectbox("ESG Module Scope", ["All", "Environmental", "Social", "Governance"])

        with col_f3:
            with get_connection() as conn:
                emp_list = pd.read_sql_query("SELECT id, name FROM employees", conn)
            emp_filt = st.selectbox("Responsible Employee", ["All"] + emp_list["name"].tolist())

        col_f4, col_f5 = st.columns(2)
        with col_f4:
            start_date = st.date_input("Start Date", value=datetime(2026, 1, 1))
        with col_f5:
            end_date = st.date_input("End Date", value=datetime(2026, 12, 31))

    # Process Filtering
    start_d_str = start_date.strftime("%Y-%m-%d")
    end_d_str = end_date.strftime("%Y-%m-%d")

    # Generate Report Table based on Module Selection
    # Let's write queries to aggregate matching tables
    report_df = pd.DataFrame()
    report_title = f"Custom ESG {module_filt} Report"

    with get_connection() as conn:
        if module_filt == "Environmental" or module_filt == "All":
            query = """
                SELECT ct.transaction_date as Date, 'Environmental' as Module, d.name as Department, 
                       'Carbon Footprint' as Type, ct.source_type || ' (' || ef.name || ')' as Description, 
                       ct.calculated_emissions || ' kg CO2' as Impact, 'System' as Owner
                FROM carbon_transactions ct
                JOIN departments d ON ct.department_id = d.id
                JOIN emission_factors ef ON ct.emission_factor_id = ef.id
                WHERE ct.transaction_date BETWEEN ? AND ?
            """
            params = [start_d_str, end_d_str]
            if dept_filt != "All":
                query += " AND d.name = ?"
                params.append(dept_filt)
            
            df_env = pd.read_sql_query(query, conn, params=params)
            report_df = pd.concat([report_df, df_env], ignore_index=True)

        if module_filt == "Social" or module_filt == "All":
            query = """
                SELECT ep.completion_date as Date, 'Social' as Module, d.name as Department, 
                       'CSR Participation' as Type, ca.title || ' (Proof: ' || IFNULL(ep.proof_file, 'None') || ')' as Description, 
                       '+' || ep.points_earned || ' Points' as Impact, e.name as Owner
                FROM employee_participations ep
                JOIN employees e ON ep.employee_id = e.id
                JOIN departments d ON e.department_id = d.id
                JOIN csr_activities ca ON ep.activity_id = ca.id
                WHERE ep.approval_status = 'Approved' AND ep.completion_date BETWEEN ? AND ?
            """
            params = [start_d_str, end_d_str]
            if dept_filt != "All":
                query += " AND d.name = ?"
                params.append(dept_filt)
            if emp_filt != "All":
                query += " AND e.name = ?"
                params.append(emp_filt)

            df_soc = pd.read_sql_query(query, conn, params=params)
            report_df = pd.concat([report_df, df_soc], ignore_index=True)

        if module_filt == "Governance" or module_filt == "All":
            query = """
                SELECT ci.due_date as Date, 'Governance' as Module, d.name as Department, 
                       'Compliance issue' as Type, ci.description || ' (Severity: ' || ci.severity || ')' as Description, 
                       ci.status as Impact, e.name as Owner
                FROM compliance_issues ci
                JOIN employees e ON ci.owner_id = e.id
                JOIN departments d ON e.department_id = d.id
                WHERE ci.due_date BETWEEN ? AND ?
            """
            params = [start_d_str, end_d_str]
            if dept_filt != "All":
                query += " AND d.name = ?"
                params.append(dept_filt)
            if emp_filt != "All":
                query += " AND e.name = ?"
                params.append(emp_filt)

            df_gov = pd.read_sql_query(query, conn, params=params)
            report_df = pd.concat([report_df, df_gov], ignore_index=True)

    # Sort report by date
    if not report_df.empty:
        report_df = report_df.sort_values(by="Date", ascending=False)
        st.subheader("Generated Report Preview")
        st.dataframe(report_df, use_container_width=True)

        # Download buttons
        csv = report_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Report as CSV",
            data=csv,
            file_name=f"esg_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )

        # Render printable HTML
        html_report = f"""
        <html>
        <head>
            <title>{report_title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
                h1 {{ color: #2b3e50; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #f3f4f6; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
                .meta {{ font-size: 0.9rem; color: #666; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>EcoSphere ESG Audit Report</h1>
            <div class="meta">
                <b>Scope:</b> {module_filt} | <b>Department:</b> {dept_filt} | <b>Employee:</b> {emp_filt}<br>
                <b>Date Range:</b> {start_d_str} to {end_d_str}<br>
                <b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Module</th>
                        <th>Department</th>
                        <th>Record Type</th>
                        <th>Description</th>
                        <th>Impact / Status</th>
                        <th>Owner</th>
                    </tr>
                </thead>
                <tbody>
        """
        for _, r in report_df.iterrows():
            html_report += f"""
                    <tr>
                        <td>{r['Date']}</td>
                        <td>{r['Module']}</td>
                        <td>{r['Department']}</td>
                        <td>{r['Type']}</td>
                        <td>{r['Description']}</td>
                        <td>{r['Impact']}</td>
                        <td>{r['Owner']}</td>
                    </tr>
            """
        html_report += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="🖥️ Export Report as HTML",
            data=html_report,
            file_name=f"esg_report_{datetime.now().strftime('%Y%m%d')}.html",
            mime='text/html'
        )
    else:
        st.info("No records match the filtering criteria.")

# ----------------- ⚙️ Settings & Configuration -----------------
elif menu_selection == "⚙️ Settings & Configuration":
    st.markdown("<h1 class='gradient-text-blue'>⚙️ System Configuration</h1>", unsafe_allow_html=True)
    st.write("Tune business logic rule parameters and score calculation weights.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚖️ ESG Score Target Weights")
        st.write("Configure the organizational score index weightings. The slider values must sum to 100%.")

        w_env = float(utils.get_setting("env_weight", "40"))
        w_soc = float(utils.get_setting("soc_weight", "30"))
        w_gov = float(utils.get_setting("gov_weight", "30"))

        input_env = st.slider("Environmental Weight (%)", 0, 100, int(w_env))
        input_soc = st.slider("Social Weight (%)", 0, 100, int(w_soc))
        input_gov = st.slider("Governance Weight (%)", 0, 100, int(w_gov))

        total_input = input_env + input_soc + input_gov
        st.write(f"Current Cumulative Weights Sum: **{total_input}%**")

        if total_input != 100:
            st.error("Invalid Configuration: Weights must sum up to exactly 100% to save changes.")
        else:
            if st.button("Apply Weights"):
                utils.set_setting("env_weight", str(input_env))
                utils.set_setting("soc_weight", str(input_soc))
                utils.set_setting("gov_weight", str(input_gov))
                utils.calculate_scores()
                st.success("Target weights updated and ESG index recalculated successfully!")
                st.rerun()

    with col2:
        st.subheader("🛠️ Core Business Rule Toggles")
        st.write("Enable/disable automated workflows.")

        # Toggles load state
        calc_toggle = utils.get_setting("auto_emission_calculation", "True") == "True"
        evidence_toggle = utils.get_setting("evidence_requirement", "True") == "True"
        badge_toggle = utils.get_setting("badge_auto_award", "True") == "True"

        new_calc = st.checkbox("Enable Automated Carbon Emissions (linked records auto-post)", value=calc_toggle)
        new_evidence = st.checkbox("Require evidence file/link for CSR approvals", value=evidence_toggle)
        new_badge = st.checkbox("Enable Employee Badge Auto-Awards", value=badge_toggle)

        if st.button("Save Business Rules Configuration"):
            utils.set_setting("auto_emission_calculation", str(new_calc))
            utils.set_setting("evidence_requirement", str(new_evidence))
            utils.set_setting("badge_auto_award", str(new_badge))
            st.success("Business rules saved.")
            st.rerun()

        st.subheader("⚠️ Reset System Database")
        st.write("Wipe SQLite cache and restore initial seed demo data.")
        if st.button("Reset & Reseed Database", type="secondary"):
            seed_data(force=True)
            utils.calculate_scores()
            st.success("Database has been reset to seed defaults.")
            st.rerun()
