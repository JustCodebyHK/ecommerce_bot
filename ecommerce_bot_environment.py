import logging
import sqlite3
import sys
from pathlib import Path
from typing import Tuple, Dict, Any

# 1. Professional Logger Setup
logging.basicConfig(
    filename='bot_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add project root to path to ensure models can be imported
sys.path.append(str(Path(__file__).parent.parent))
from models import Action, Observation

DB_PATH = "orders.db"

def init_db():
    """Initializes the database with advanced state tracking columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            status TEXT,
            address TEXT,
            price REAL,
            requires_human INTEGER DEFAULT 0
        )
    ''')
    
    # Seed data strictly aligned with openenv.yaml tasks
    seed_data = [
        ('101', 'Processing', '123 Mumbai St', 500.0, 0),
        ('102', 'Shipped', '456 Delhi Rd', 1200.0, 0),
        ('103', 'Delayed', '789 Bandra West', 500.0, 0)
    ]
    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?)", seed_data)
    conn.commit()
    conn.close()

init_db()

class EcommerceBotEnvironment:
    def _get_connection(self):
        return sqlite3.connect(DB_PATH)

    def reset(self) -> Observation:
        """Standard OpenEnv Reset Protocol."""
        logging.info("System Reset: Database state verified.")
        return Observation(status_msg="Database Connected & Ready", success=True)

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        OpenEnv Compliant Step Function.
        Returns: (Observation, reward, done, info)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Initialize OpenEnv tracking variables
        reward = 0.0
        done = False
        info = {"task_id": action.order_id}

        logging.info(f"EXECUTION: {action.action_type} on Order {action.order_id}")

        # --- TASK 0: DYNAMIC ONBOARDING (Registration) ---
        if action.action_type == "create_order":
            try:
                addr, prc = action.data.split(",")
                cursor.execute(
                    "INSERT INTO orders (id, status, address, price, requires_human) VALUES (?, ?, ?, ?, ?)",
                    (action.order_id, "Processing", addr, float(prc), 0)
                )
                conn.commit()
                conn.close()
                return Observation(status_msg="Order Created", success=True), 1.0, True, info
            except Exception as e:
                conn.close()
                return Observation(status_msg=str(e), success=False), 0.0, False, info

        # Validate Order Existence
        cursor.execute("SELECT status, address, price, requires_human FROM orders WHERE id = ?", (action.order_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return Observation(status_msg="Order Not Found", success=False), 0.0, False, info
        
        status, address, price, requires_human = row

        # --- SAFETY GUARDRAIL: HITL LOCK ---
        if requires_human == 1 and action.action_type != "query_order":
            conn.close()
            # Penalize for ignoring a security lock
            return Observation(status_msg="Order locked for Human Review.", success=False), -0.5, True, info

        # --- TASK 1 (MEDIUM): STATUS QUERY ---
        if action.action_type == "query_order":
            conn.close()
            details = {"status": status, "address": address, "price": price}
            # Partial reward for information retrieval
            if action.order_id == "102" and status == "Shipped":
                reward = 1.0
                done = True
            else:
                reward = 0.2 
            return Observation(status_msg="Found", order_details=details, success=True), reward, done, info

        # --- TASK 2 (EASY): ADDRESS UPDATE ---
        if action.action_type == "update_address":
            # Guardrail: Non-manipulatable state
            if status == "Shipped":
                conn.close()
                return Observation(status_msg="Cannot update shipped order", success=False), 0.0, True, info
            
            # Guardrail: Logistics Constraints
            restricted = ["International", "Restricted", "No-Go Zone"]
            if any(zone.lower() in action.data.lower() for zone in restricted):
                conn.close()
                # Reward for identifying a boundary correctly
                return Observation(status_msg="Restricted Area detected", success=False), 0.5, True, info

            cursor.execute("UPDATE orders SET address = ? WHERE id = ?", (action.data, action.order_id))
            conn.commit()
            conn.close()
            
            # Grader: Match goal in openenv.yaml
            if action.order_id == "101" and action.data == "789 Bandra West":
                reward = 1.0
                done = True
            else:
                reward = 0.5
            return Observation(status_msg="Address Updated", success=True), reward, done, info

        # --- TASK 3 (HARD): REFUND PROCESSING ---
        if action.action_type == "issue_refund":
            try:
                refund_amt = float(action.data)
                limit = price * 0.5
                
                # Grader: Escalation Logic
                if refund_amt > limit:
                    cursor.execute("UPDATE orders SET requires_human = 1 WHERE id = ?", (action.order_id,))
                    conn.commit()
                    conn.close()
                    # Reward for identifying high-risk correctly
                    return Observation(status_msg="Escalated to Human", success=True), 0.8, True, info
                
                cursor.execute("UPDATE orders SET status = 'Refunded' WHERE id = ?", (action.order_id,))
                conn.commit()
                conn.close()

                # Grader: Task Goal
                if action.order_id == "103" and refund_amt == 250.0:
                    reward = 1.0
                    done = True
                else:
                    reward = 0.4
                return Observation(status_msg="Refund Processed", success=True), reward, done, info
            except ValueError:
                conn.close()
                return Observation(status_msg="Invalid Amount", success=False), 0.0, False, info

        conn.close()
        return Observation(status_msg="Unknown Action", success=False), 0.0, False, info