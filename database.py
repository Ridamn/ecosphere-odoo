import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecosphere.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=(), commit=False):
    """Execute a single query with optional parameters."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor.fetchall()

def execute_write(query, params=()):
    """Execute a write query and return the last inserted row ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

def execute_many(query, params_list):
    """Execute a query against multiple parameter sets."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()

def init_db():
    """Create all required tables for the ESG platform if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Master Tables ---

        # 1. Departments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            head TEXT,
            parent_department_id INTEGER,
            employee_count INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (parent_department_id) REFERENCES departments(id) ON DELETE SET NULL
        );
        """)

        # 2. Categories (for CSR activities and challenges)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL, -- 'CSR Activity' or 'Challenge'
            status TEXT NOT NULL DEFAULT 'Active'
        );
        """)

        # 3. Emission Factors
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emission_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            factor REAL NOT NULL, -- kg CO2 per unit
            unit TEXT NOT NULL, -- e.g., 'kWh', 'liter', 'km', 'kg'
            category TEXT NOT NULL -- 'Purchase', 'Manufacturing', 'Expense', 'Fleet'
        );
        """)

        # 4. Product ESG Profiles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_esg_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL UNIQUE,
            sku TEXT NOT NULL UNIQUE,
            carbon_footprint REAL NOT NULL, -- kg CO2
            recycled_content REAL NOT NULL DEFAULT 0.0, -- percentage
            recyclability_rate REAL NOT NULL DEFAULT 0.0 -- percentage
        );
        """)

        # 5. Environmental Goals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS environmental_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            target_value REAL NOT NULL,
            current_value REAL NOT NULL DEFAULT 0.0,
            unit TEXT NOT NULL,
            deadline TEXT NOT NULL, -- YYYY-MM-DD
            status TEXT NOT NULL DEFAULT 'On Track' -- 'On Track', 'At Risk', 'Achieved'
        );
        """)

        # 6. ESG Policies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS esg_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL, -- 'Environmental', 'Social', 'Governance'
            effective_date TEXT NOT NULL, -- YYYY-MM-DD
            version TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active' -- 'Active', 'Archived'
        );
        """)

        # 7. Badges
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            unlock_rule TEXT NOT NULL, -- description of unlocking condition
            metric TEXT NOT NULL, -- 'XP', 'Completed Challenges', 'CSR Participations'
            threshold INTEGER NOT NULL,
            icon TEXT NOT NULL -- Emoji or SVG class
        );
        """)

        # 8. Rewards
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            points_required INTEGER NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active' -- 'Active', 'Out of Stock'
        );
        """)

        # 9. Employees
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            department_id INTEGER,
            xp INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            role TEXT NOT NULL DEFAULT 'Employee', -- 'Admin', 'Auditor', 'Employee'
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
        );
        """)

        # --- Transactional Tables ---

        # 10. ERP Records (Mock source records)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS erp_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, -- 'Purchase', 'Manufacturing', 'Expense', 'Fleet'
            description TEXT,
            amount REAL NOT NULL,
            unit TEXT NOT NULL,
            department_id INTEGER,
            date TEXT NOT NULL, -- YYYY-MM-DD
            emission_factor_id INTEGER,
            status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Processed'
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
            FOREIGN KEY (emission_factor_id) REFERENCES emission_factors(id) ON DELETE SET NULL
        );
        """)

        # 11. Carbon Transactions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT NOT NULL, -- YYYY-MM-DD
            department_id INTEGER,
            source_type TEXT NOT NULL, -- 'Purchase', 'Manufacturing', 'Expense', 'Fleet', 'Manual'
            source_reference TEXT, -- ID of ERP record or manual description
            activity_amount REAL NOT NULL,
            emission_factor_id INTEGER,
            calculated_emissions REAL NOT NULL, -- kg CO2
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
            FOREIGN KEY (emission_factor_id) REFERENCES emission_factors(id) ON DELETE SET NULL
        );
        """)

        # 12. CSR Activities
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS csr_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            date TEXT NOT NULL, -- YYYY-MM-DD
            points_value INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active', -- 'Draft', 'Active', 'Completed'
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
        """)

        # 13. Employee Participations (CSR)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            proof_file TEXT,
            approval_status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
            points_earned INTEGER DEFAULT 0,
            completion_date TEXT, -- YYYY-MM-DD
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (activity_id) REFERENCES csr_activities(id) ON DELETE CASCADE,
            UNIQUE(employee_id, activity_id)
        );
        """)

        # 14. Challenges
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            xp INTEGER NOT NULL,
            difficulty TEXT NOT NULL, -- 'Easy', 'Medium', 'Hard'
            evidence_required INTEGER DEFAULT 1, -- 0 or 1
            deadline TEXT NOT NULL, -- YYYY-MM-DD
            status TEXT NOT NULL DEFAULT 'Draft', -- 'Draft', 'Active', 'Under Review', 'Completed', 'Archived'
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
        """)

        # 15. Challenge Participations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenge_participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            progress INTEGER DEFAULT 0, -- 0 to 100
            proof_file TEXT,
            approval_status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
            xp_awarded INTEGER DEFAULT 0,
            completion_date TEXT, -- YYYY-MM-DD
            FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE(challenge_id, employee_id)
        );
        """)

        # 16. Policy Acknowledgements
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_acknowledgements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            acknowledgement_date TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
            FOREIGN KEY (policy_id) REFERENCES esg_policies(id) ON DELETE CASCADE,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE(policy_id, employee_id)
        );
        """)

        # 17. Audits
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            scope TEXT,
            auditor TEXT NOT NULL,
            audit_date TEXT NOT NULL, -- YYYY-MM-DD
            score REAL NOT NULL, -- 0.0 to 100.0
            findings TEXT,
            status TEXT NOT NULL DEFAULT 'Planned' -- 'Planned', 'In Progress', 'Completed'
        );
        """)

        # 18. Compliance Issues
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id INTEGER,
            severity TEXT NOT NULL, -- 'Low', 'Medium', 'High', 'Critical'
            description TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            due_date TEXT NOT NULL, -- YYYY-MM-DD
            status TEXT NOT NULL DEFAULT 'Open', -- 'Open', 'Resolved', 'Overdue'
            FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE SET NULL,
            FOREIGN KEY (owner_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        """)

        # 19. Employee Badges
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_badges (
            employee_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            awarded_at TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
            PRIMARY KEY (employee_id, badge_id),
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
        );
        """)

        # 20. Notifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL, -- 'Compliance', 'CSR', 'Challenge', 'Policy', 'Badge'
            created_at TEXT NOT NULL, -- YYYY-MM-DD HH:MM:SS
            is_read INTEGER DEFAULT 0, -- 0 or 1
            FOREIGN KEY (recipient_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        """)

        # 21. Settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

        # 22. Department Scores cache (aggregated cache)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS department_scores (
            department_id INTEGER PRIMARY KEY,
            environmental_score REAL NOT NULL DEFAULT 100.0,
            social_score REAL NOT NULL DEFAULT 100.0,
            governance_score REAL NOT NULL DEFAULT 100.0,
            total_score REAL NOT NULL DEFAULT 100.0,
            last_calculated TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
        );
        """)

        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database schema initialized successfully at:", DB_PATH)
