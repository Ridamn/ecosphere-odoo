import sqlite3
from datetime import datetime
from database import get_connection, execute_query, execute_write

def get_setting(key, default_value):
    """Retrieve a system setting value."""
    result = execute_query("SELECT value FROM settings WHERE key = ?", (key,))
    if result:
        return result[0]["value"]
    return default_value

def set_setting(key, value):
    """Update or insert a system setting value."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, str(value)))
        conn.commit()

def add_notification(recipient_id, message, type_):
    """Create a user notification."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_write("""
        INSERT INTO notifications (recipient_id, message, type, created_at, is_read)
        VALUES (?, ?, ?, ?, 0)
    """, (recipient_id, message, type_, now))

def get_notifications(recipient_id, unread_only=True):
    """Fetch notifications for a user."""
    if unread_only:
        return execute_query("""
            SELECT * FROM notifications 
            WHERE recipient_id = ? AND is_read = 0 
            ORDER BY created_at DESC
        """, (recipient_id,))
    else:
        return execute_query("""
            SELECT * FROM notifications 
            WHERE recipient_id = ? 
            ORDER BY created_at DESC
        """, (recipient_id,))

def mark_notifications_read(recipient_id):
    """Mark all notifications as read for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE recipient_id = ?", (recipient_id,))
        conn.commit()

def check_badge_awards(employee_id):
    """Check if employee qualifies for new badges and auto-award them if enabled."""
    if get_setting("badge_auto_award", "True") != "True":
        return

    # Fetch employee stats
    emp = execute_query("SELECT xp, name FROM employees WHERE id = ?", (employee_id,))
    if not emp:
        return
    emp_xp = emp[0]["xp"]
    emp_name = emp[0]["name"]

    # Number of completed challenges (approved progress = 100)
    challenges_completed = execute_query("""
        SELECT COUNT(*) as count FROM challenge_participations
        WHERE employee_id = ? AND progress = 100 AND approval_status = 'Approved'
    """, (employee_id,))[0]["count"]

    # Number of approved CSR activity participations
    csr_participations = execute_query("""
        SELECT COUNT(*) as count FROM employee_participations
        WHERE employee_id = ? AND approval_status = 'Approved'
    """, (employee_id,))[0]["count"]

    # Get all badges
    badges = execute_query("SELECT * FROM badges")

    # Get already unlocked badges
    unlocked_badge_ids = [r["badge_id"] for r in execute_query(
        "SELECT badge_id FROM employee_badges WHERE employee_id = ?", (employee_id,)
    )]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for badge in badges:
        badge_id = badge["id"]
        if badge_id in unlocked_badge_ids:
            continue

        metric = badge["metric"]
        threshold = badge["threshold"]
        badge_name = badge["name"]
        badge_icon = badge["icon"]

        qualifies = False
        if metric == "XP" and emp_xp >= threshold:
            qualifies = True
        elif metric == "Completed Challenges" and challenges_completed >= threshold:
            qualifies = True
        elif metric == "CSR Participations" and csr_participations >= threshold:
            qualifies = True

        if qualifies:
            # Award badge
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO employee_badges (employee_id, badge_id, awarded_at)
                    VALUES (?, ?, ?)
                """, (employee_id, badge_id, now))
                conn.commit()
            
            # Send notification
            msg = f"Congratulations {emp_name}! You have unlocked the '{badge_name}' badge {badge_icon}!"
            add_notification(employee_id, msg, "Badge")
            print(f"Awarded badge '{badge_name}' to {emp_name}")

def process_erp_record(erp_id):
    """Process a single ERP record, calculate carbon emissions, and log carbon transaction."""
    erp = execute_query("""
        SELECT er.id, er.type, er.amount, er.unit, er.department_id, er.date, er.emission_factor_id, er.status, ef.factor
        FROM erp_records er
        JOIN emission_factors ef ON er.emission_factor_id = ef.id
        WHERE er.id = ?
    """, (erp_id,))
    
    if not erp:
        return False
    
    erp_record = erp[0]
    if erp_record["status"] == "Processed":
        return True

    # Check if auto calculation setting is active
    if get_setting("auto_emission_calculation", "True") == "True":
        amount = erp_record["amount"]
        factor = erp_record["factor"]
        emissions = amount * factor

        # Insert Carbon Transaction
        execute_write("""
            INSERT INTO carbon_transactions 
            (transaction_date, department_id, source_type, source_reference, activity_amount, emission_factor_id, calculated_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            erp_record["date"],
            erp_record["department_id"],
            erp_record["type"],
            str(erp_record["id"]),
            amount,
            erp_record["emission_factor_id"],
            emissions
        ))

    # Mark ERP record as processed regardless (since calculation was either done or skipped as manual)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE erp_records SET status = 'Processed' WHERE id = ?", (erp_id,))
        conn.commit()

    # Refresh scores
    calculate_scores()
    return True

def check_overdue_compliance_issues():
    """Scan open compliance issues, flag overdue ones, and trigger owner alert notifications."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Fetch issues that are past due date and still open
    overdue_issues = execute_query("""
        SELECT ci.id, ci.description, ci.owner_id, ci.due_date, e.name 
        FROM compliance_issues ci
        JOIN employees e ON ci.owner_id = e.id
        WHERE ci.status = 'Open' AND ci.due_date < ?
    """, (today,))

    if overdue_issues:
        with get_connection() as conn:
            cursor = conn.cursor()
            for issue in overdue_issues:
                # Update status
                cursor.execute("UPDATE compliance_issues SET status = 'Overdue' WHERE id = ?", (issue["id"],))
                # Dispatch notification
                msg = f"Urgent: Your assigned compliance issue '{issue['description']}' is OVERDUE (Due: {issue['due_date']}). Action required."
                add_notification(issue["owner_id"], msg, "Compliance")
            conn.commit()
        # Recalculate scores as overdue compliance issues penalize governance
        calculate_scores()

def calculate_scores():
    """Calculate ESG scores for all departments and cache them in the database."""
    # Fetch weights
    w_env = float(get_setting("env_weight", "40"))
    w_soc = float(get_setting("soc_weight", "30"))
    w_gov = float(get_setting("gov_weight", "30"))

    # Total weight validation
    total_w = w_env + w_soc + w_gov
    if total_w > 0:
        w_env /= total_w
        w_soc /= total_w
        w_gov /= total_w

    departments = execute_query("SELECT id, employee_count FROM departments WHERE status = 'Active'")
    
    # Active policies count for Social score
    total_active_policies = execute_query("SELECT COUNT(*) as count FROM esg_policies WHERE status = 'Active'")[0]["count"]
    
    # Average completed audits score for Governance base
    audit_avg_res = execute_query("SELECT AVG(score) as avg_score FROM audits WHERE status = 'Completed'")
    audit_base = audit_avg_res[0]["avg_score"] if audit_avg_res and audit_avg_res[0]["avg_score"] is not None else 100.0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dept in departments:
        dept_id = dept["id"]
        emp_count = max(1, dept["employee_count"])

        # 1. Environmental Score (Lower emissions relative to employee count = higher score)
        # We find total carbon footprint for the department
        emissions_res = execute_query("""
            SELECT SUM(calculated_emissions) as total 
            FROM carbon_transactions 
            WHERE department_id = ?
        """, (dept_id,))
        total_emissions = emissions_res[0]["total"] if emissions_res and emissions_res[0]["total"] is not None else 0.0

        # Environmental score formula: 100 - (Emissions / (EmployeeCount * 20))
        # This gives a baseline where ~20kg per employee corresponds to 1 point deduction. Clamped 0-100.
        env_score = max(0.0, 100.0 - (total_emissions / (emp_count * 20.0)))

        # 2. Social Score
        # Part A: Policy Acknowledgement Rate in department
        policy_ack_rate = 1.0
        if total_active_policies > 0:
            ack_count_res = execute_query("""
                SELECT COUNT(*) as count 
                FROM policy_acknowledgements pa
                JOIN employees e ON pa.employee_id = e.id
                JOIN esg_policies p ON pa.policy_id = p.id
                WHERE e.department_id = ? AND p.status = 'Active'
            """, (dept_id,))
            ack_count = ack_count_res[0]["count"] if ack_count_res else 0
            possible_acks = total_active_policies * emp_count
            policy_ack_rate = ack_count / possible_acks if possible_acks > 0 else 1.0

        # Part B: Average XP of employees in department relative to a target benchmark of 300 XP
        xp_res = execute_query("SELECT SUM(xp) as total_xp FROM employees WHERE department_id = ?", (dept_id,))
        total_xp = xp_res[0]["total_xp"] if xp_res and xp_res[0]["total_xp"] is not None else 0.0
        avg_xp = total_xp / emp_count
        xp_performance = min(1.0, avg_xp / 300.0) # Cap performance factor at 1.0

        # Social score = (Policy Ack Rate * 40) + (XP Performance * 60)
        soc_score = (policy_ack_rate * 40.0) + (xp_performance * 60.0)

        # 3. Governance Score
        # Starts with Audit average base, minus penalties for open/overdue issues owned by department employees
        issues_res = execute_query("""
            SELECT 
                SUM(CASE WHEN ci.status = 'Open' THEN 1 ELSE 0 END) as open_count,
                SUM(CASE WHEN ci.status = 'Overdue' THEN 1 ELSE 0 END) as overdue_count
            FROM compliance_issues ci
            JOIN employees e ON ci.owner_id = e.id
            WHERE e.department_id = ?
        """, (dept_id,))
        
        open_issues = 0
        overdue_issues = 0
        if issues_res:
            open_issues = issues_res[0]["open_count"] if issues_res[0]["open_count"] is not None else 0
            overdue_issues = issues_res[0]["overdue_count"] if issues_res[0]["overdue_count"] is not None else 0

        gov_score = audit_base - (open_issues * 5.0) - (overdue_issues * 15.0)
        gov_score = max(0.0, min(100.0, gov_score)) # Clamp between 0 and 100

        # 4. Overall Combined Score
        total_score = (env_score * w_env) + (soc_score * w_soc) + (gov_score * w_gov)
        total_score = max(0.0, min(100.0, total_score))

        # Cache score in table
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO department_scores 
                (department_id, environmental_score, social_score, governance_score, total_score, last_calculated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(department_id) DO UPDATE SET
                    environmental_score = excluded.environmental_score,
                    social_score = excluded.social_score,
                    governance_score = excluded.governance_score,
                    total_score = excluded.total_score,
                    last_calculated = excluded.last_calculated
            """, (dept_id, env_score, soc_score, gov_score, total_score, now))
            conn.commit()

if __name__ == "__main__":
    calculate_scores()
    print("ESG Scores calculated and cached successfully.")
