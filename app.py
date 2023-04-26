from flask import Flask, session, redirect, url_for, request, render_template
from db_operations import *


app = Flask(__name__)
app.secret_key = b"arjuna17"


@app.route("/", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/validate_login", methods=["POST"])
def validate_login():
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            user_data = find_user(attempted_username)
            if user_data is None:
                return redirect(url_for("login"))
            elif user_data["password"] == attempted_password:
                session["user_id"] = user_data["id"]
                return redirect(url_for("home"))
            else:
                return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    data, length = get_dash_baord_data(session["user_id"])
    return render_template("dashboard.html", data=data, length=length)

@app.route('/dashboard/filter', methods=["POST"])
def filter_dashboard():
    data, length = get_dash_baord_filter_data(session["user_id"], request.form)
    return render_template("dashboard.html", data=data, length=length)

@app.route("/new_order", methods=["GET"])
def order_form():
    return render_template("order_form.html")

@app.route("/save_order", methods=["POST"])
def save_order_input():
    try:
        if request.method == "POST":
            item_num = request.form["item_num"]
            style_num = request.form["style_num"]
            colour_code = request.form["colour_code"]
            quantity = int(request.form["order_qty"])
            sizes = request.form["order_size"]
            buyer = request.form["buyer"]
            issue_date = request.form["issue_date"]
            delivery_date = request.form["delivery_date"]

            if add_order(session["user_id"], item_num, style_num, colour_code, sizes, quantity, buyer, issue_date, delivery_date):
                return redirect(url_for("saved_orders"))
        return redirect(url_for("home"))
    except:
        return redirect(url_for("home"))

@app.route("/orders", methods=["GET", "POST"])
def saved_orders():
    data = get_saved_order_details(session["user_id"])
    return render_template("saved_orders.html", data=data)

@app.route("/orders/<order_id>/inputs", methods=["GET"])
def inputs(order_id):
    return render_template("inputs.html", order_id=order_id)

@app.route("/orders/<order_id>/inputs/<stage>", methods=["GET"])
def stage_input(order_id, stage):
    data = get_input_auto_fill(session["user_id"], order_id)
    return render_template(f"{stage}_input.html", data=data, order_id=order_id)

@app.route("/orders/<order_id>/inputs/<stage>/save", methods=["POST"])
def save_stage_input(order_id, stage):
    try:
        if request.method == "POST":
            data = request.form
            if stage == "cut":
                save_cut_input_constant(session["user_id"], order_id, data)
                save_cut_input_variable(session["user_id"], order_id, data)
            elif stage == "sew":
                save_sew_input_constant(session["user_id"], order_id, data)
                save_sew_input_variable(session["user_id"], order_id, data)
            elif stage == "wash":
                save_wash_input_constant(session["user_id"], order_id, data)
                save_wash_input_variable(session["user_id"], order_id, data)
            elif stage == "finish":
                save_finish_input_constant(session["user_id"], order_id, data)
                save_finish_input_variable(session["user_id"], order_id, data)
            elif stage == "packing":
                save_packing_input_constant(session["user_id"], order_id, data)
                save_packing_input_variable(session["user_id"], order_id, data)
            return redirect(url_for("saved_orders"))
    except Exception as e:
        return redirect(url_for("saved_orders"))

@app.route("/orders/<order_id>/inputs/<stage>/mark_complete", methods=["GET"])
def stage_mark_complete(order_id, stage):
    colour = request.form["colour_code"]
    size = request.form["sizes"]
    mark_stage_complete(session["user_id"], order_id, colour, size, stage)
    return redirect(url_for("inputs", order_id=order_id))

@app.route("/orders/<order_id>/inputs/<stage>/scan", methods=["GET"])
def stage_barcode_scan(order_id, stage):
    return render_template("scan.html", order_id=order_id, stage=stage)

@app.route("/orders/<order_id>/inputs/<stage>/scan/save", methods=["POST"])
def stage_barcode_scan_save(order_id, stage):
    completed_pieces = int(request.form["completed_pieces"])
    if save_completed_stage_pieces(session["user_id"], order_id, completed_pieces, stage, request.form["colour_code"], request.form["sizes"]):
        return redirect(url_for("saved_orders"))
    return redirect(url_for("saved_orders"))

@app.route("/orders/<order_id>/<stage>/report", methods=["GET"])
def order_stage_report(order_id, stage):
    base_data, colours, sizes, count_dict, constant_data, variable_data, recent_actual_output, total_actual_output, stage_complete_date = get_stage_order_details(session["user_id"], order_id, stage)
    return render_template(f"{stage}_report.html", base_data=base_data, colours=colours, sizes=sizes, 
                           count_dict=count_dict, constant_data=constant_data, variable_data=variable_data, 
                           recent_actual_output=recent_actual_output, total_actual_output=total_actual_output, 
                           stage_complete_date=stage_complete_date, order_id=order_id)

@app.route("/<stage>/all_reports", methods=["GET"])
def all_stage_reports(stage):
    all_order_stage_details, length = get_stage_all_order_details(session["user_id"], stage)
    return render_template(f"all_{stage}_report.html", all_order_stage_details=all_order_stage_details, length=length)

@app.route("/daily_production_report", methods=["GET"])
def dpr():
    data = get_dpr(session["user_id"])
    return render_template("dpr.html", data=data)

@app.route("/orders/<order_id>/delete", methods=["GET"])
def delete_given_order(order_id):
    delete_order(session["user_id"], order_id)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
