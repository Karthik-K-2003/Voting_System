# 🗳️ Online Voting System

A secure and user-friendly web-based voting system built using **Flask** and **Firebase Firestore**.
This application allows users to vote once and enables admins to manage participants, monitor voting activity, and analyze results with interactive dashboards.

---

## 🚀 Features

### 👤 User Features

* User Registration & Login
* View participants
* Vote for a participant (only once)
* Duplicate vote prevention (backend enforced)

---

### 🛠️ Admin Features

* Admin Dashboard
* Add / Delete participants
* Manage users
* Voting Status:

  * Users who voted
  * Users who have not voted
* Analytics Dashboard:

  * Total votes
  * Vote percentage
  * Winner detection 🏆 (supports tie cases)
  * Bar chart (votes per participant)
  * Pie charts (vote distribution & participation)
* Export results as CSV

---

## 🧠 Tech Stack

* **Backend:** Flask (Python)
* **Database:** Firebase Firestore
* **Frontend:** HTML, Tailwind CSS, JavaScript
* **Charts:** Chart.js
* **Testing:** unittest (Python)

---

## 📂 Project Structure

```
ONLINE_VOTING_SYSTEM/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── safe_keys/            # Firebase key (ignored)
│
├── static/
│   └── js/
│       └── vote.js
│
├── templates/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   │
│   └── dashboard/
│       ├── admin/
│       └── user/
│
├── tests/
│   └── test_vote.py
│
└── venv/                 # Virtual environment (ignored)
```

---

## 🔧 Requirements

The project uses the following core dependencies:

```
Flask
firebase-admin
python-dotenv
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```
git clone https://github.com/Karthik-K-2003/Voting_System.git
cd Voting_System
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Firebase Setup

* Place your Firebase service account key in:

```
safe_keys/serviceAccountKey.json
```

⚠️ This file is ignored using `.gitignore` for security.

---

### 5️⃣ Run Application

```
python app.py
```

---

## 🧪 Running Tests

Run backend tests using:

```
python -m tests.test_vote
```

---

## 🔐 Security Highlights

* Session-based authentication
* Backend validation for voting
* Duplicate vote prevention
* Sensitive files protected via `.gitignore`

---

## 📊 Analytics Overview

* Real-time vote counting
* Winner detection (supports ties)
* Voting participation tracking
* Interactive charts using Chart.js

---

## 📁 Export Feature

* Export voting results as CSV
* Includes participant names and vote counts

---

## 🏁 Future Improvements

* Real-time voting updates
* PDF export
* Email verification
* Deployment (Render / Railway)

---

## 👨‍💻 Author

**Karthik K**

---

## ⭐ Final Note

This project demonstrates:

* Full-stack development
* Secure backend design
* Real-world feature implementation
* Testing and validation

---
