from app import app
from flask import flash, render_template, request, redirect,session, url_for
from db import db
import users, restaurants,employees

@app.route("/")
def index():
    # List all restaurants currently added to the website by this user
    all_restaurants = []
    if "user_id" in session:
        user = session["user_id"]
        all_restaurants = restaurants.get_all(user)
    return render_template("index.html", all_restaurants=all_restaurants)


@app.route("/restaurant/<int:id>")
def restaurant(id):
    restaurant = restaurants.get_restaurant(id)
    shifts = restaurants.get_shifts(id)
    all_employees = employees.get_employees(id)
    return render_template("restaurant.html", restaurant=restaurant, shifts=shifts, employees=all_employees)

@app.route("/employee")
def employee():
    id = request.args["id"]
    employee = employees.get_employee(id)
    restaurant = restaurants.get_restaurant(employee[3])
    return render_template("employee.html",employee=employee,restaurant=restaurant)

@app.route("/restaurant/dayview")
def restaurant_dayview():
    id = request.args["id"]
    date = request.args["date"]
    restaurant = restaurants.get_restaurant(id)
    shifts = restaurants.get_shifts_by_date(id,date)
    return render_template('restaurant_dayview.html', restaurant=restaurant, shifts=shifts, date=date)

@app.route("/restaurant/staff_strength_calendar")
def staff_strength_calendar():
    week = request.args["week"]
    restaurantID = request.args["restaurantID"]
    calendar = restaurants.create_staff_strength_calendar(week,restaurantID)
    restaurant = restaurants.get_restaurant(restaurantID)
    return render_template("staff_strength_calendar.html", calendar=calendar, week=week, restaurant=restaurant)

@app.route("/restaurant/roster")
def roster():
    week = request.args["week"]
    restaurantID = request.args["restaurantID"]
    restaurant = restaurants.get_restaurant(restaurantID)
    (roster,unused_hours,assigned_shifts, not_assigned) = restaurants.create_roster(week,restaurant.id)
    return render_template("roster.html", roster=roster, unused_hours=unused_hours, 
                                                            week=week, 
                                                            restaurant=restaurant, 
                                                            assigned_shifts=assigned_shifts,
                                                            not_assigned=not_assigned)

@app.route("/employee/schedule")
def personal_schedule():
    week = request.args["week"]
    employeeID = request.args["employeeID"]
    restaurantID = request.args["restaurantID"]
    restaurant = restaurants.get_restaurant(restaurantID)
    employee = employees.get_employee(employeeID)
    schedule = employees.own_shifts(employeeID,week)
    return render_template("personal_schedule.html", schedule=schedule, week=week, employee=employee,restaurant=restaurant)


@app.route("/employee/workreport")
def work_report():
    week = request.args["week"]
    employeeID = request.args["employeeID"]
    restaurantID = request.args["restaurantID"]
    restaurant = restaurants.get_restaurant(restaurantID)
    employee = employees.get_employee(employeeID)
    hours = employees.work_report(restaurantID,employeeID,week)
    return render_template("workreport.html", hours=hours, week=week, employee=employee, restaurant=restaurant)



# Routes for forms

@app.route("/add/restaurant",methods=["GET","POST"])
def add_restaurant():
    if request.method == "GET":
        return render_template("add_restaurant.html")
    if request.method == "POST":
        name = request.form["name"]
        owner = request.form["owner"]
        if restaurants.add_restaurant(name,owner):
            id = restaurants.get_last(name)
            flash("Ravintolan lisäys onnistui!")
            return redirect(url_for("restaurant", id=id))
        else:
            return render_template("error.html", message="Ravintolan lisäys epäonnistui")

@app.route("/update/restaurant", methods=["GET","POST"])
def update_restaurant():
    if request.method == "GET":
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        return render_template("update_restaurant.html", restaurant=restaurant)
    if request.method == "POST":
        id = request.form["id"]
        new_name = request.form["new_name"]
        if restaurants.update_restaurant(id, new_name):
            flash("Ravintolan päivitys onnistui!")
            return redirect(url_for('restaurant', id=id))
        else:
            return render_template("error.html", message="Ravintolan muokkaus epäonnistui")


@app.route("/remove/restaurant", methods=["GET", "POST"])
def remove_restaurant():
    if request.method == "GET":
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        return render_template("remove_restaurant.html", id=id, restaurant=restaurant)
    if request.method == "POST":
        id = request.form["id"]
        if restaurants.remove_restaurant(id):
            flash("Ravintolan poisto onnistui!")
            return redirect("/")
        else:
            return render_template("error.html", message="Ravintolan poisto epäonnistui")

@app.route("/restaurant/add/shift",methods=["GET","POST"])
def add_shift():
    if request.method == "GET":
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        return render_template("add_shift.html", restaurant=restaurant)

    if request.method == "POST":
        name = request.form["name"]
        restaurantID = request.form["restaurantID"]
        role = request.form["role"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        duration = request.form["duration"]
        reps = request.form["reps"]
        repetition = request.form["repetition"]
        if restaurants.add_shift(name, restaurantID, role, date, start_time, duration, reps,repetition):
            flash("Työvuoron lisäys onnistui!")
            return redirect(url_for("restaurant", id=restaurantID))
        else:
            return render_template("error.html", message="Työvuoron lisäys epäonnistui")


@app.route("/update/shift", methods=["GET","POST"])
def update_shift():
    if request.method == "GET":
        id = request.args.get("id")
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        shift = restaurants.get_shift(id)
        return render_template("update_shift.html", shift=shift, restaurant=restaurant )

    if request.method == "POST":
        id = request.form["id"]
        new_name = request.form["new_name"]
        new_role = request.form["new_role"]
        new_date = request.form["new_date"]
        new_start_time = request.form["new_start_time"]
        new_duration = request.form["new_duration"]
        restaurantID = request.form["restaurantID"]
        keep_employee = request.form["keep_employee"]
        if restaurants.update_shift(id, new_name, new_role, new_date, new_start_time, new_duration,keep_employee):
            flash("Työvuoron päivitys onnistui!")
            return redirect(url_for('restaurant', id=restaurantID))
        else:
            return render_template("error.html", message="Työvuoron muokkaus epäonnistui")

@app.route("/remove/shift", methods=["GET", "POST"])
def remove_shift():
    if request.method == "GET":
        id = request.args.get("id")
        shift = restaurants.get_shift(id)
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        return render_template("remove_shift.html", id=id, shift=shift, restaurant=restaurant)
    if request.method == "POST":
        id = request.form["id"]
        if restaurants.remove_shift(id):
            flash("Työvuoron poisto onnistui!")
            return redirect("/")
        else:
            return render_template("error.html", message="Työvuoron poisto epäonnistui")

@app.route("/restaurant/add/employee",methods=["GET","POST"])
def add_employee():
    if request.method == "GET":
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        return render_template("add_employee.html", restaurant=restaurant)

    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]        
        restaurantID = request.form["restaurantID"]
        role = request.form["role"]
        max_hours = request.form["max_hours"]

        if employees.add_employee(firstname,lastname,restaurantID, role, max_hours):
            flash("Työntekijän lisäys onnistui!")
            return redirect(url_for("restaurant", id=restaurantID))
        else:
            return render_template("error.html", message="Työntekijän lisäys epäonnistui")


@app.route("/update/employee", methods=["GET","POST"])
def update_employee():
    if request.method == "GET":
        id = request.args.get("id")
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        employee = employees.get_employee(id)
        return render_template("update_employee.html", employee=employee, restaurant=restaurant)

    if request.method == "POST":
        id = request.form["id"]
        new_firstname = request.form["new_firstname"]
        new_lastname = request.form["new_lastname"]
        new_role = request.form["new_role"]
        new_max_hours = request.form["new_max_hours"]
        restaurantID = request.form["restaurantID"]
        if employees.update_employee(id, new_firstname, new_lastname, new_role, new_max_hours):
            flash("Työntekijän päivitys onnistui!")
            return redirect("/")
        else:
            return render_template("error.html", message="Työntekijän muokkaus epäonnistui")

@app.route("/remove/employee", methods=["GET", "POST"])
def remove_employee():
    if request.method == "GET":
        id = request.args.get("id")
        restaurantID = request.args["restaurantID"]
        restaurant = restaurants.get_restaurant(restaurantID)
        employee = employees.get_employee(id)
        return render_template("remove_employee.html",employee=employee, restaurant=restaurant)
    if request.method == "POST":
        id = request.form["id"]
        if employees.remove_employee(id):
            flash("Työntekijän poisto onnistui!")
            return redirect("/")
        else:
            return render_template("error.html", message="Työntekijän poisto epäonnistui")

@app.route("/add/dayoff", methods=["GET", "POST"])
def add_dayoff():
    if request.method == "GET":
        id = request.args.get("id")
        employee = employees.get_employee(id)
        restaurant = restaurants.get_restaurant(employee[3])
        return render_template("add_dayoff.html", employee=employee,restaurant=restaurant)
    if request.method == "POST":
        date = request.form["date"]
        reason = request.form["reason"]
        employeeID = request.form["employeeID"]        
        restaurantID = request.form["restaurantID"]        
        if employees.add_dayoff(employeeID,date,reason):
            flash("Vapaapäivän lisääminen onnistui!")
            return redirect(url_for("restaurant", id=restaurantID))
        else:
            return render_template("error.html", message="Vapaapäivän lisäys epäonnistui")

@app.route("/remove/dayoff", methods=["GET", "POST"])
def remove_dayoff():
    if request.method == "GET":
        employeeID = request.args.get("id")
        employee = employees.get_employee(employeeID)
        restaurant = restaurants.get_restaurant(employee[3])
        return render_template("remove_dayoff.html",employee=employee, restaurant=restaurant)
    if request.method == "POST":
        date = request.form["date"]
        employeeID = request.form["employeeID"]        
        restaurantID = request.form["restaurantID"]        
        if employees.remove_dayoff(employeeID,date):
            flash("Sisäänkirjautuminen onnistui!")
            return redirect("/")
        else:
            return render_template("error.html", message="Vapaapäivän poisto epäonnistui")

# Register/login/logout 

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.register(username,password):
            flash("Rekisteröinti onnistui!")
            return redirect("/")
        else:
            return render_template("error.html",message="Rekisteröinti ei onnistunut")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username,password):
            flash("Sisäänkirjautuminen onnistui!")
            return redirect("/")
        else:
            return render_template("error.html",message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    if "user_id" in session:
        users.logout()
        flash("Uloskirjautuminen onnistui!")
    users.logout()
    return redirect("/")
