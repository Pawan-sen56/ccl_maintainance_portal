# CCL Township & Employee Quarter Maintenance Portal
### Central Coalfields Limited (A Subsidiary of Coal India Limited)

A full-stack facility maintenance and work order management system designed to streamline civil, electrical, and water supply maintenance across CCL residential colonies (Gandhinagar, Jawaharnagar, Rajendra Nagar, Piparwar, Kathara, etc.).

---

## 🚀 How to Run the Project

1. **Activate the Virtual Environment**:
   ```powershell
   cd c:\Users\pawan\Desktop\ccl_maintenance_portal
   .\venv\Scripts\activate
   ```

2. **Start the Development Server**:
   ```powershell
   python manage.py runserver
   ```

3. **Open the Web Portal**:
   👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Town Admin / Superuser** | `admin` | `admin` | Full executive dashboard, database admin panel, SLA monitoring |
| **Junior Engineer (Civil)** | `je_civil` | `ccl123` | Civil & Water supply work desk, dispatch contractors, log materials |
| **Junior Engineer (Electrical)** | `je_elec` | `ccl123` | Electrical repairs, switchboards, wiring, MCB replacements |
| **Resident / Employee** | `resident1` | `ccl123` | Lodge complaints with photos, track status, view OTP, rate service |

---

## 🌟 Key Features Built-In

1. **Role-Based Access Control (RBAC):**
   * Resident portal (mobile-friendly)
   * Junior Engineer (JE) dispatch desk
   * Senior Staff Officer executive oversight

2. **Anti-Pilferage Store Ledger:**
   * JEs log exact materials issued from the CCL store (pipes, cement, MCBs) for every work order.

3. **Two-Way Completion OTP:**
   * A 4-digit OTP is generated per ticket. The resident gives this OTP to the technician only after verifying the repair.

4. **Automated SLA Escalation:**
   * Any ticket unresolved for $>7$ days is flagged with an active **ESCALATED** warning for the Town Administration.

5. **Direct Admin Access:**
   * Access the full Django Admin panel at: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
