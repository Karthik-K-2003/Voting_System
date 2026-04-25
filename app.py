from flask import Flask, render_template, request, redirect, session, Response
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import csv

# to secure data
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# firebase setup
cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH"))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
API_KEY = os.getenv("API_KEY")

# Helper function for checking user in session
def login_required():
    if "user_id" not in session:
        return False
    return True

# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Basic Validation
        if not name or not email or not password:
            return "ALL fields are required."

        if len(password) < 6:
            return "Password must be atleast 6 characters."

        try:
            # create user in database(firebase auth)
            user = auth.create_user(
                email=email,
                password=password
            )

            # assigning role
            role = "admin" if email == ADMIN_EMAIL else "user"

            # store in firestore
            db.collection("users").document(user.uid).set({
                "name": name,
                "email": email,
                "role": role
            })

            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
    return render_template("auth/register.html")

# login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # firebase auth rest api
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()
        if "idToken" in data:
            uid = data["localId"]

            # store session
            session["user_id"] = uid

            session.permanent = True

            # get role
            user_doc = db.collection("users").document(uid).get()

            if user_doc.exists:
                role = user_doc.to_dict().get("role")

                if role == "admin":
                    return redirect("/admin_dashboard")
                else:
                    return redirect("/participants")
            else:
                return "User not found!!!"

        else:
            error = data.get("error", {}).get("message", "Invalid Credentials")
            return f"Error: {error}"
    return render_template("auth/login.html")

# user dashboard
@app.route("/user_dashboard")
def user_dashboard():
    return redirect('/participants')

# participants
@app.route("/participants")
def participants():
    if not login_required():
        return redirect("/")

    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")
    email = user_doc.to_dict().get("email")

    # get participants
    participants_ref = db.collection("participants").stream()
    participants = []
    for p in participants_ref:
        data = p.to_dict()
        data["id"] = p.id
        participants.append(data)

    return render_template("dashboard/user/participants.html", email=email, participants=participants, active_page="participants")

# Voting
@app.route("/voting")
def voting():
    if not login_required():
        return redirect("/")

    user_id = session["user_id"]

    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")

    email = user_doc.to_dict().get("email")

    # participants
    participants_ref = db.collection("participants").stream()
    participants = []

    for p in participants_ref:
        data = p.to_dict()
        data["id"] = p.id
        participants.append(data)

    vote_doc = db.collection("votes").document(user_id).get()
    voted_participant = None

    if vote_doc.exists:
        voted_participant = vote_doc.to_dict().get("participant_id")

    return render_template("dashboard/user/voting.html", email=email, participants=participants, voted_participant=voted_participant, active_page="voting")

# Vote
@app.route("/vote", methods=["POST"])
def vote():
    if not login_required():
        return {"status": "error", "message": "Login required"}

    data = request.get_json(silent=True)
    participant_id = data.get("participant_id")

    if not participant_id:
        return {"status": "error", "message": "Invalid request"}

    user_id = session["user_id"]

    # checking if the user had already voted
    vote_doc = db.collection("votes").document(user_id).get()

    if vote_doc.exists:
        return {"status": "error", "message": "You already voted!"}

    db.collection("votes").document(user_id).set({
        "user_id": user_id,
        "participant_id": participant_id
    })
    return {"status": "success"}

# admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if not login_required():
        return redirect("/")

    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")

    user_data = user_doc.to_dict()
    if user_data.get("role") != "admin":
        return "Access Denied!!!"

    email = user_data.get("email")

    #fetch participants
    participants_ref = db.collection("participants").stream()
    participants = []
    for p in participants_ref:
        data = p.to_dict()
        data["id"] = p.id
        participants.append(data)

    #fetch users
    users_ref = db.collection("users").stream()
    users = []
    for u in users_ref:
        data = u.to_dict()
        data["id"] = u.id
        users.append(data)
    return render_template("dashboard/admin/admin_dashboard.html", email=email, participants=participants, users=users, title="Admin Dashboard", active_page="dashboard")


#Add participant by admin
@app.route("/add_participant", methods=["GET", "POST"])
def add_participant():
    if not login_required():
        return redirect("/")
    
    user_id = session["user_id"]

    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")
    
    user_data = user_doc.to_dict()
    if user_data.get("role") != "admin":
        return "Access Denied"

    email = user_doc.to_dict().get("email")

    if request.method == "POST":
        name = request.form.get("name")
        image_url = request.form.get("image_url")

        if not name or not image_url:
            return "All fields required!"
        
        try:
            db.collection("participants").add({
                "name": name,
                "image_url": image_url
            })
            return redirect("/admin_dashboard?success=1")
        except Exception as e:
            return f"Error: {e}"
        
    return render_template("dashboard/admin/add_participant.html", email=email,title="Add Participant", active_page="add_participant")


#delete participant
@app.route("/delete_participant/<id>")
def delete_participant(id):
    if not login_required():
        return redirect("/")

    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    
    if not user_doc.exists:
        return redirect("/")
    
    if user_doc.to_dict().get("role") != "admin":
        return "Access Denied"

    participant_doc = db.collection("participants").document(id).get()
    if not participant_doc.exists:
        return "Participant not found"
    
     #delete related votes
    votes = db.collection("votes").where("participant_id", "==", id).stream()
    for v in votes:
        db.collection("votes").document(v.id).delete()

    db.collection("participants").document(id).delete()
    return redirect("/admin_dashboard?deleted=1")


#delete user
@app.route("/delete_user/<id>")
def delete_user(id):
    if not login_required():
        return redirect("/")

    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")

    user_data = user_doc.to_dict()

    if user_data.get("role") != "admin":
        return "Access Denied"

    #prevent deleting admin
    user_to_delete = db.collection("users").document(id).get()
    if not user_to_delete.exists:
        return "User not found"

    delete_data = user_to_delete.to_dict()
    if delete_data.get("role") == "admin":
        return "Cannot delete admin"

    db.collection("users").document(id).delete()
    return redirect("/admin_dashboard?deleted=1")


#voting status or voters
@app.route("/voting_status")
def voting_status():
    if not login_required():
        return redirect("/")
    
    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")
    
    user_data = user_doc.to_dict()

    if user_data.get("role") != "admin":
        return "Access Denied"
    
    email = user_data.get("email")

    #get all users
    users_ref = db.collection("users").stream()
    all_users = []
    user_map = {}

    for u in users_ref:
        data = u.to_dict()
        data["id"] = u.id
        all_users.append(data)
        user_map[u.id] = data

    #get voted users
    votes_ref = db.collection("votes").stream()
    voted_ids = set()

    for v in votes_ref:
        voted_ids.add(v.to_dict().get("user_id"))

    voted_users = []
    non_voted_users = []

    for uid, user in user_map.items():
        print(uid, user.get("role"))
        role = user.get("role")
        if role != "user": #skip for admin
            continue
        if uid in voted_ids:
            voted_users.append(user)
        else:
            non_voted_users.append(user)
    return render_template("dashboard/admin/voting_status.html", email=email, voted_users=voted_users, non_voted_users=non_voted_users, title="Voting Status", active_page="voting_status")


#analytics
@app.route("/analytics")
def analytics():
    if not login_required():
        return redirect("/")
    
    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return redirect("/")
    
    user_data = user_doc.to_dict()
    if user_data.get("role") != "admin":
        return "Access Denied"
    
    email = user_data.get("email")

    #get participants
    participants_ref = db.collection("participants").stream()
    participants = {}
    for p in participants_ref:
        data = p.to_dict()
        participants[p.id] = data.get("name")

    #count votes
    votes_ref = db.collection("votes").stream()
    vote_count = {}

    for v in votes_ref:
        pid = v.to_dict().get("participant_id")
        vote_count[pid] = vote_count.get(pid, 0) + 1

    # get total users (excluding admin)
    users_ref = db.collection("users").stream()
    total_users = 0

    for u in users_ref:
        if u.to_dict().get("role") == "user":
            total_users += 1

    #charts
    labels = []
    values = []

    for pid, name in participants.items():
        labels.append(name)
        values.append(vote_count.get(pid, 0))

    total_votes = sum(values)

    # total_votes = sum(values)
    # calculate percentage
    vote_percentage = 0
    if total_users > 0:
        vote_percentage = round((total_votes / total_users) * 100, 2)

    # find winner
    max_votes = max(vote_count.values()) if vote_count else 0

    winners = []

    for pid, count in vote_count.items():
        if count == max_votes and max_votes > 0:
            winner_doc = db.collection("participants").document(pid).get()
            
            if winner_doc.exists:
                data = winner_doc.to_dict()
                data["id"] = pid
                data["votes"] = count
                winners.append(data)
    return render_template("dashboard/admin/analytics.html", email=email, labels=labels, values=values, total_votes=total_votes, vote_percentage=vote_percentage, winners=winners, total_users=total_users , title="Analytics", active_page="analytics")


#Export Results
@app.route("/export_results")
def export_results():
    if not login_required():
        return redirect("/")
    
    user_id = session["user_id"]
    user_doc = db.collection("users").document(user_id).get()
    role = user_doc.to_dict()

    if not user_doc.exists or role.get("role") != "admin":
        return "Access Denied!"
    
    #get participants
    participants_ref = db.collection("participants").stream()
    participants = {}

    for p in participants_ref:
        participants[p.id] = p.to_dict().get("name")

    #count votes
    votes_ref = db.collection("votes").stream()
    vote_count = {}

    for v in votes_ref:
        pid = v.to_dict().get("participant_id")
        vote_count[pid] = vote_count.get(pid, 0) + 1

    #create csv
    def generate():
        yield "Name,Votes\n"

        for pid,name in participants.items():
            votes = vote_count.get(pid, 0)
            yield f"{name},{votes}\n"
    
    return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=results.csv"})


# logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
