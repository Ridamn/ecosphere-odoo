import sqlite3
from datetime import datetime, timedelta
import random
import os
from database import DB_PATH, get_connection, init_db

def seed_data(force=False):
    """Seed the database with rich, realistic sample data."""
    if not force:
        # Check if database is already seeded
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM employees")
                if cursor.fetchone()[0] > 0:
                    print("Database already contains data. Seeding skipped.")
                    return
        except sqlite3.OperationalError:
            # Table doesn't exist, need to run init_db
            pass

    # Ensure tables exist
    init_db()

    # Clear all data if force seeding
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        tables = [
            "departments", "categories", "emission_factors", "product_esg_profiles",
            "environmental_goals", "esg_policies", "badges", "rewards", "employees",
            "erp_records", "carbon_transactions", "csr_activities", "employee_participations",
            "challenges", "challenge_participations", "policy_acknowledgements", "audits",
            "compliance_issues", "employee_badges", "notifications", "settings", "department_scores"
        ]
        for t in tables:
            cursor.execute(f"DELETE FROM {t}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    print("Seeding database with fresh mock data...")

    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. System Settings
        settings = [
            ("env_weight", "40"),
            ("soc_weight", "30"),
            ("gov_weight", "30"),
            ("auto_emission_calculation", "True"),
            ("evidence_requirement", "True"),
            ("badge_auto_award", "True")
        ]
        cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)

        # 2. Departments
        # ID 1: Executive, ID 2: R&D, ID 3: Operations, ID 4: HR, ID 5: Marketing
        departments = [
            ("Executive", "EXEC", "Sarah Jenkins", None, 5, "Active"),
            ("Research & Development", "RD", "Dr. Alan Turing", 1, 25, "Active"),
            ("Operations & Logistics", "OPS", "Marcus Vance", 1, 45, "Active"),
            ("Human Resources", "HR", "Linda Lovelace", 1, 8, "Active"),
            ("Marketing & Sales", "MKT", "Don Draper", 1, 18, "Active")
        ]
        cursor.executemany("""
            INSERT INTO departments (name, code, head, parent_department_id, employee_count, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, departments)

        # 3. Categories
        categories = [
            ("Community Volunteering", "CSR Activity", "Active"),
            ("Eco Campaigns", "CSR Activity", "Active"),
            ("Health & Wellness", "CSR Activity", "Active"),
            ("Carbon Footprint", "Challenge", "Active"),
            ("Zero Waste", "Challenge", "Active"),
            ("Professional Training", "Challenge", "Active")
        ]
        cursor.executemany("""
            INSERT INTO categories (name, type, status)
            VALUES (?, ?, ?)
        """, categories)

        # 4. Emission Factors
        emission_factors = [
            ("Electricity (Grid)", "ELEC_GRID", 0.85, "kWh", "Expense"),
            ("Natural Gas", "NAT_GAS", 2.03, "m3", "Expense"),
            ("Petrol Fleet", "FLEET_PETROL", 2.31, "liter", "Fleet"),
            ("Diesel Fleet", "FLEET_DIESEL", 2.68, "liter", "Fleet"),
            ("Office Paper", "PAPER_OFFICE", 0.50, "kg", "Purchase"),
            ("Raw Steel", "MAT_STEEL", 1.85, "kg", "Manufacturing"),
            ("Raw Plastic", "MAT_PLASTIC", 2.00, "kg", "Manufacturing")
        ]
        cursor.executemany("""
            INSERT INTO emission_factors (name, code, factor, unit, category)
            VALUES (?, ?, ?, ?, ?)
        """, emission_factors)

        # 5. Product ESG Profiles
        product_profiles = [
            ("Eco-Bottle 500ml", "ECO-BOT-01", 0.12, 85.0, 100.0),
            ("Standard PET Bottle 500ml", "STD-BOT-02", 0.45, 10.0, 80.0),
            ("Sustainable Shipping Box", "SUS-BOX-03", 0.08, 90.0, 95.0),
            ("Heavy-Duty Crates", "CRT-HD-04", 1.95, 40.0, 90.0)
        ]
        cursor.executemany("""
            INSERT INTO product_esg_profiles (product_name, sku, carbon_footprint, recycled_content, recyclability_rate)
            VALUES (?, ?, ?, ?, ?)
        """, product_profiles)

        # 6. Environmental Goals
        # Deadlines in the future
        goals = [
            ("Reduce Fleet Carbon Emissions", "Reduce operational fleet carbon emissions by 15% before year-end.", 5000.0, 4210.0, "kg CO2", "2026-12-31", "On Track"),
            ("Zero Single-Use Plastic in Office", "Transition all office single-use plastics to biodegradable alternatives.", 0.0, 15.0, "items/week", "2026-09-30", "At Risk"),
            ("Optimize Manufacturing Energy Efficiency", "Reduce manufacturing energy consumption by 20% compared to previous year.", 80000.0, 52000.0, "kWh", "2026-11-30", "On Track")
        ]
        cursor.executemany("""
            INSERT INTO environmental_goals (title, description, target_value, current_value, unit, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, goals)

        # 7. ESG Policies
        policies = [
            ("Code of Business Conduct & Ethics", "Provides standards for governance, professional conduct, conflict of interest, and anti-bribery policies.", "Governance", "2026-01-01", "1.0", "Active"),
            ("Zero Waste & Recycling Policy", "Establishes sorting guidelines for paper, electronics, compost, and plastic waste across all offices.", "Environmental", "2026-02-15", "1.2", "Active"),
            ("Fair Labor & Equal Opportunity Policy", "Ensures diversity, non-harassment, work hours compliance, and equal opportunities for advancement.", "Social", "2025-06-01", "2.0", "Active")
        ]
        cursor.executemany("""
            INSERT INTO esg_policies (title, description, category, effective_date, version, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, policies)

        # 8. Badges
        # Unlock rules are descriptions
        badges = [
            ("Carbon Crusader", "Complete at least 1 Carbon Footprint challenge.", "Completed Challenges >= 1", "Completed Challenges", 1, "🍀"),
            ("Eco Enthusiast", "Amass 100 XP from sustainability activities.", "XP >= 100", "XP", 100, "🌱"),
            ("ESG Champion", "Amass 500 XP from sustainability activities.", "XP >= 500", "XP", 500, "🏆"),
            ("Green Commuter", "Complete 3 Fleet or Commuting challenges.", "Completed Challenges >= 3", "Completed Challenges", 3, "🚲"),
            ("CSR Star", "Participate in 3 or more CSR Activities.", "CSR Participations >= 3", "CSR Participations", 3, "🌟")
        ]
        cursor.executemany("""
            INSERT INTO badges (name, description, unlock_rule, metric, threshold, icon)
            VALUES (?, ?, ?, ?, ?, ?)
        """, badges)

        # 9. Rewards
        rewards = [
            ("Reusable Bamboo Coffee Cup", "Sleek bamboo cup with heat-protective sleeve. Perfect for commuting.", 50, 15, "Active"),
            ("Solar-Powered Phone Charger", "Eco-friendly portable charger. Dual USB ports.", 200, 4, "Active"),
            ("Plant-a-Tree Donation Certificate", "A tree planted in your name in the Amazon rainforest.", 30, 999, "Active"),
            ("EcoSphere Organic Cotton Hoodie", "Super comfortable hoodie made from 100% recycled organic cotton.", 150, 8, "Active"),
            ("Extra Day of Paid Leave", "Add 1 additional day of paid time off to your annual balance.", 500, 2, "Active")
        ]
        cursor.executemany("""
            INSERT INTO rewards (name, description, points_required, stock, status)
            VALUES (?, ?, ?, ?, ?)
        """, rewards)

        # 10. Employees
        # IDs 1 to 5
        employees = [
            ("Sarah Jenkins", "sarah@ecosphere.com", 1, 0, 0, "Admin"),
            ("David Miller", "david@ecosphere.com", 3, 0, 0, "Auditor"),
            ("Alice Johnson", "alice@ecosphere.com", 2, 180, 180, "Employee"),
            ("Bob Smith", "bob@ecosphere.com", 3, 90, 40, "Employee"),
            ("Charlie Brown", "charlie@ecosphere.com", 4, 380, 280, "Employee"),
            ("Emma Watson", "emma@ecosphere.com", 5, 250, 150, "Employee")
        ]
        cursor.executemany("""
            INSERT INTO employees (name, email, department_id, xp, points, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, employees)

        # --- Transactional Data Seeding ---

        # 11. Mock ERP Records (Processed or Pending)
        today = datetime.now()
        erp_data = [
            # Type, Desc, Amount, Unit, Dept, Date, FactorID, Status
            ("Expense", "R&D Office Electricity (May)", 12000.0, "kWh", 2, (today - timedelta(days=45)).strftime("%Y-%m-%d"), 1, "Processed"),
            ("Expense", "R&D Office Electricity (June)", 11500.0, "kWh", 2, (today - timedelta(days=15)).strftime("%Y-%m-%d"), 1, "Processed"),
            ("Expense", "Ops Factory Electricity (June)", 48000.0, "kWh", 3, (today - timedelta(days=15)).strftime("%Y-%m-%d"), 1, "Processed"),
            ("Expense", "Marketing Office Natural Gas (June)", 800.0, "m3", 5, (today - timedelta(days=18)).strftime("%Y-%m-%d"), 2, "Processed"),
            ("Fleet", "Ops Logistics Fleet Petrol", 3500.0, "liter", 3, (today - timedelta(days=10)).strftime("%Y-%m-%d"), 3, "Processed"),
            ("Fleet", "Ops Delivery Fleet Diesel", 2800.0, "liter", 3, (today - timedelta(days=5)).strftime("%Y-%m-%d"), 4, "Processed"),
            ("Purchase", "R&D Lab Office Printing Paper", 250.0, "kg", 2, (today - timedelta(days=22)).strftime("%Y-%m-%d"), 5, "Processed"),
            ("Manufacturing", "Steel Sheet Stock used in Prod", 15000.0, "kg", 3, (today - timedelta(days=12)).strftime("%Y-%m-%d"), 6, "Processed"),
            ("Manufacturing", "Plastic granules used in molding", 6000.0, "kg", 3, (today - timedelta(days=8)).strftime("%Y-%m-%d"), 7, "Processed"),
            
            # Pending records for simulation demo
            ("Fleet", "Weekly Sales Team Travel Expense", 420.0, "liter", 5, (today - timedelta(days=1)).strftime("%Y-%m-%d"), 3, "Pending"),
            ("Purchase", "Logistics Shipping Cartons Order", 600.0, "kg", 3, today.strftime("%Y-%m-%d"), 5, "Pending")
        ]
        cursor.executemany("""
            INSERT INTO erp_records (type, description, amount, unit, department_id, date, emission_factor_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, erp_data)

        # 12. Carbon Transactions (Coinciding with the 'Processed' ERP records)
        carbon_txs = [
            # Date, Dept, Type, Ref, Amt, FactorID, calculated_emissions
            ((today - timedelta(days=45)).strftime("%Y-%m-%d"), 2, "Expense", "1", 12000.0, 1, 12000.0 * 0.85),
            ((today - timedelta(days=15)).strftime("%Y-%m-%d"), 2, "Expense", "2", 11500.0, 1, 11500.0 * 0.85),
            ((today - timedelta(days=15)).strftime("%Y-%m-%d"), 3, "Expense", "3", 48000.0, 1, 48000.0 * 0.85),
            ((today - timedelta(days=18)).strftime("%Y-%m-%d"), 5, "Expense", "4", 800.0, 2, 800.0 * 2.03),
            ((today - timedelta(days=10)).strftime("%Y-%m-%d"), 3, "Fleet", "5", 3500.0, 3, 3500.0 * 2.31),
            ((today - timedelta(days=5)).strftime("%Y-%m-%d"), 3, "Fleet", "6", 2800.0, 4, 2800.0 * 2.68),
            ((today - timedelta(days=22)).strftime("%Y-%m-%d"), 2, "Purchase", "7", 250.0, 5, 250.0 * 0.50),
            ((today - timedelta(days=12)).strftime("%Y-%m-%d"), 3, "Manufacturing", "8", 15000.0, 6, 15000.0 * 1.85),
            ((today - timedelta(days=8)).strftime("%Y-%m-%d"), 3, "Manufacturing", "9", 6000.0, 7, 6000.0 * 2.00)
        ]
        cursor.executemany("""
            INSERT INTO carbon_transactions (transaction_date, department_id, source_type, source_reference, activity_amount, emission_factor_id, calculated_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, carbon_txs)

        # 13. CSR Activities
        csr_activities = [
            ("Local Beach Cleanup Campaign", "Join the marketing and R&D teams for a beach waste collection drive this Saturday.", 1, (today - timedelta(days=20)).strftime("%Y-%m-%d"), 50, "Completed"),
            ("Tree Plantation Drive", "Help plant 500 trees in the city industrial park. Equipment provided.", 2, (today - timedelta(days=2)).strftime("%Y-%m-%d"), 60, "Active"),
            ("Mental Health & Mindfulness Workshop", "HR is organizing a mindfulness and mental wellness workspace session. Interactive.", 3, (today + timedelta(days=5)).strftime("%Y-%m-%d"), 30, "Active"),
            ("E-Waste Recycling Drop-Off", "Bring old laptops, phones, cables for safe eco-friendly recycling.", 2, (today + timedelta(days=15)).strftime("%Y-%m-%d"), 40, "Active")
        ]
        cursor.executemany("""
            INSERT INTO csr_activities (title, description, category_id, date, points_value, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, csr_activities)

        # 14. Employee CSR Participations
        # Alice, Bob, Charlie, Emma (IDs 3, 4, 5, 6)
        csr_participations = [
            # EmpID, ActivityID, Proof, Status, Points, Date
            (3, 1, "beach_cleanup_alice.jpg", "Approved", 50, (today - timedelta(days=20)).strftime("%Y-%m-%d")),
            (4, 1, "beach_cleanup_bob.jpg", "Approved", 50, (today - timedelta(days=20)).strftime("%Y-%m-%d")),
            (5, 1, "beach_cleanup_charlie.jpg", "Approved", 50, (today - timedelta(days=20)).strftime("%Y-%m-%d")),
            (6, 1, "beach_cleanup_emma.jpg", "Approved", 50, (today - timedelta(days=20)).strftime("%Y-%m-%d")),
            (3, 2, "tree_planting_alice.png", "Approved", 60, (today - timedelta(days=2)).strftime("%Y-%m-%d")),
            (5, 2, "tree_planting_charlie.png", "Pending", 0, None),
            (6, 2, "tree_planting_emma.png", "Approved", 60, (today - timedelta(days=2)).strftime("%Y-%m-%d")),
            (4, 3, None, "Pending", 0, None)
        ]
        cursor.executemany("""
            INSERT INTO employee_participations (employee_id, activity_id, proof_file, approval_status, points_earned, completion_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, csr_participations)

        # 15. Challenges
        challenges = [
            ("Cycle to Work Week", "Swap your car ride with cycling for 5 consecutive days. Track via Strava.", 4, 100, "Medium", 1, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Completed"),
            ("Meatless Mondays Challenge", "Eat fully vegetarian or vegan meals every Monday for a month to lower food emissions.", 4, 80, "Easy", 0, (today + timedelta(days=10)).strftime("%Y-%m-%d"), "Active"),
            ("Zero Waste Workspace Checklist", "Implement office sorting guidelines at your desk. Require picture evidence.", 5, 120, "Medium", 1, (today - timedelta(days=12)).strftime("%Y-%m-%d"), "Completed"),
            ("Professional Safety & Ethics Training", "Complete the compliance modules for workplace safety and ethical operations.", 6, 150, "Hard", 0, (today + timedelta(days=20)).strftime("%Y-%m-%d"), "Active")
        ]
        cursor.executemany("""
            INSERT INTO challenges (title, category_id, description, xp, difficulty, evidence_required, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, challenges)

        # 16. Challenge Participations
        challenge_parts = [
            # ChallengeID, EmpID, Progress, Proof, Approval, XP, CompletionDate
            (1, 3, 100, "cycle_strava_alice.png", "Approved", 100, (today - timedelta(days=6)).strftime("%Y-%m-%d")),
            (1, 5, 100, "cycle_strava_charlie.png", "Approved", 100, (today - timedelta(days=5)).strftime("%Y-%m-%d")),
            (1, 6, 100, "cycle_strava_emma.png", "Approved", 100, (today - timedelta(days=5)).strftime("%Y-%m-%d")),
            (3, 3, 30, None, "Pending", 0, None),
            (3, 5, 100, "desk_sorting_charlie.png", "Approved", 120, (today - timedelta(days=13)).strftime("%Y-%m-%d")),
            (3, 6, 100, "desk_sorting_emma.png", "Approved", 120, (today - timedelta(days=12)).strftime("%Y-%m-%d")),
            (4, 5, 100, None, "Approved", 150, (today - timedelta(days=1)).strftime("%Y-%m-%d")),
            (2, 4, 50, None, "Pending", 0, None)
        ]
        cursor.executemany("""
            INSERT INTO challenge_participations (challenge_id, employee_id, progress, proof_file, approval_status, xp_awarded, completion_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, challenge_parts)

        # 17. Policy Acknowledgements
        policy_acks = [
            (1, 3, (today - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")),
            (1, 4, (today - timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S")),
            (1, 5, (today - timedelta(days=29)).strftime("%Y-%m-%d %H:%M:%S")),
            (1, 6, (today - timedelta(days=27)).strftime("%Y-%m-%d %H:%M:%S")),
            (2, 3, (today - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
            (2, 5, (today - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 5, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 6, (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
            INSERT INTO policy_acknowledgements (policy_id, employee_id, acknowledgement_date)
            VALUES (?, ?, ?)
        """, policy_acks)

        # 18. Audits
        audits = [
            ("Q1 Environmental Audit", "R&D and Ops facilities (GHG tracking protocols & energy data)", "GreenAudit Corp", (today - timedelta(days=60)).strftime("%Y-%m-%d"), 92.5, "Strong data collection processes; slight leak found in compressor line 3 which was noted.", "Completed"),
            ("Q2 Corporate Governance Review", "Executive & HR Departments (policies, anti-bribery & whistleblowing)", "CompliGuard LLC", (today - timedelta(days=10)).strftime("%Y-%m-%d"), 98.0, "All standard policies updated and published; active training program verified.", "Completed"),
            ("H1 Workplace Safety Audit", "All operational offices and assembly lines (safety equipment, signage & drills)", "SafeWorks Authority", today.strftime("%Y-%m-%d"), 78.0, "Several safety issues noted: fire exit partially blocked in warehouse, missing safety goggles sign in lab.", "Completed")
        ]
        cursor.executemany("""
            INSERT INTO audits (title, scope, auditor, audit_date, score, findings, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, audits)

        # 19. Compliance Issues
        # David Miller (ID 2) is the Auditor who owns some checking, but other employees are owners
        # Owner IDs: 3 (Alice), 4 (Bob), 5 (Charlie)
        compliance_issues = [
            (1, "Critical", "Blockage in Warehouse Fire Exit Lane 3 needs clearing immediately", 4, (today + timedelta(days=3)).strftime("%Y-%m-%d"), "Open"),
            (1, "Medium", "Update safety goggles warning signage in R&D Lab Room 402", 3, (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Overdue"),
            (1, "Low", "Repair compressor line 3 minor air leak reported in audits", 4, (today + timedelta(days=15)).strftime("%Y-%m-%d"), "Open"),
            (2, "Low", "Perform whistleblowing mock-test report compilation", 1, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Resolved")
        ]
        cursor.executemany("""
            INSERT INTO compliance_issues (audit_id, severity, description, owner_id, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, compliance_issues)

        # 20. Employee Badges
        # Prepopulate a couple of badges for employees who reached the metric thresholds
        # Alice (ID 3): Completed challenges: challenge 1 (Strava) -> Carbon Crusader. Also XP is 180 -> Eco Enthusiast.
        # Bob (ID 4): XP is 90 -> none.
        # Charlie (ID 5): Completed challenges: challenge 1 (Strava), challenge 3 (Zero Waste Desk), challenge 4 (safety/ethics) -> 3 completed challenges -> Green Commuter, Carbon Crusader. XP is 380 -> Eco Enthusiast.
        # Emma (ID 6): Completed challenges: challenge 1 (Strava), challenge 3 (Zero Waste Desk) -> 2 completed -> Carbon Crusader. XP is 250 -> Eco Enthusiast.
        emp_badges = [
            (3, 1, (today - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 2, (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 1, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 2, (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 4, (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (6, 1, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
            (6, 2, (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("INSERT INTO employee_badges (employee_id, badge_id, awarded_at) VALUES (?, ?, ?)", emp_badges)

        # 21. Notifications
        notifications = [
            (3, "Congratulations! You have unlocked the 'Carbon Crusader' badge!", "Badge", (today - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, "Congratulations! You have unlocked the 'Eco Enthusiast' badge!", "Badge", (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, "A new compliance issue regarding 'Workplace Safety' has been assigned to you. Due date is approaching.", "Compliance", (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (4, "Urgent: A critical compliance issue regarding 'Warehouse Fire Exit' has been assigned to you. Action required before due date.", "Compliance", today.strftime("%Y-%m-%d %H:%M:%S")),
            (5, "Your submission for challenge 'Zero Waste Workspace Checklist' has been approved. +120 XP!", "Challenge", (today - timedelta(days=13)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, "Your submission for activity 'Local Beach Cleanup Campaign' has been approved. +50 Points!", "CSR", (today - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
            INSERT INTO notifications (recipient_id, message, type, created_at, is_read)
            VALUES (?, ?, ?, ?, 0)
        """, notifications)

        # 22. Seed Initial Department Scores Cache
        # Just write dummy values that will be updated by calculations
        dept_scores = [
            (1, 100.0, 100.0, 100.0, 100.0, today.strftime("%Y-%m-%d %H:%M:%S")),
            (2, 95.0, 80.0, 90.0, 89.0, today.strftime("%Y-%m-%d %H:%M:%S")),
            (3, 85.0, 85.0, 75.0, 82.0, today.strftime("%Y-%m-%d %H:%M:%S")),
            (4, 100.0, 90.0, 85.0, 92.5, today.strftime("%Y-%m-%d %H:%M:%S")),
            (5, 90.0, 75.0, 95.0, 87.0, today.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        cursor.executemany("""
            INSERT INTO department_scores (department_id, environmental_score, social_score, governance_score, total_score, last_calculated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, dept_scores)

        conn.commit()
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_data(force=True)
