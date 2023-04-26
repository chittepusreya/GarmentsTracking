from random_operations import id_generator
from datetime import datetime

import pymongo

MONGODB_DATABASE = "GarmentsTracking"
USERS_COLLECTION = "Users"
USERS_ORDERS_COLLECTION = "UserOrders"
ORDERS_COLLECTION = "Orders"
DETAIL_ORDERS_COLLECTION = "DetailOrder"
ORDERS_HISTORY = "History"
PASSWORD = "6309Er0q21ODWl3C"
MONGODB_URL = "mongodb+srv://vssandeeppasumarthi:6309Er0q21ODWl3C@cluster0.ksz6bin.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(MONGODB_URL)
db = client[MONGODB_DATABASE]

users_collection = db[USERS_COLLECTION]
orders_collection = db[ORDERS_COLLECTION]
detail_order_collection = db[DETAIL_ORDERS_COLLECTION]
orders_history = db[ORDERS_HISTORY]


def find_user(user_name):
    data = users_collection.find_one({"name": user_name}, {"password": 1, "id": 1})
    return data

def add_order(user_id, item_num, style_num, colour_code, sizes, quantity, buyer, issue_date, delivery_date):
    new_id = id_generator(20)
    order_data = dict()
    order_data["order_id"] = new_id
    order_data["user_id"] = user_id
    order_data["item_num"] = item_num
    order_data["style_num"] = style_num
    order_data["colour_code"] = colour_code
    order_data["sizes"] = sizes
    order_data["quantity"] = quantity
    order_data["buyer"] = buyer
    order_data['issue_date'] = issue_date
    order_data["delivery_date"] = delivery_date
    order_data["status"] = "recieved"
    for colour in colour_code.split(","):
        for size in sizes.split(","):
            temp_data = dict()
            for stage in ["cut", "sew", "wash", "finish", "packing"]:
                temp_data["order_id"] = new_id
                temp_data["user_id"] = user_id
                temp_data["colour"] = colour
                temp_data["size"] = size
                temp_data[f"{stage}_total_actual_output"] = 0
            detail_order_collection.insert_one(temp_data)

    orders_collection.insert_one(order_data)
    return True

def get_saved_order_details(user_id):
    orders_data = orders_collection.find({"user_id": user_id}, {"_id": 0})
    data = [order for order in orders_data]
    return data

def get_input_auto_fill(user_id, order_id):
    return orders_collection.find_one({"user_id": user_id, "order_id": order_id}, {"_id": 0, "item_num": 1, "style_num": 1})

def update_status(user_id, order_id, new_status):
    current_status = orders_collection.find_one({"user_id": user_id, "order_id": order_id}, {"status": 1})["status"]
    status = ["recieved", "cut", "sew", "wash", "finish", "packing"]
    current_index = status.index(current_status)
    new_index = status.index(new_status)
    if new_index > current_index:
        orders_collection.update({"user_id": user_id, "order_id": order_id}, {"$set": {"status": new_status}})
    return True

def save_cut_input_constant(user_id, order_id, data):
    cut_data_constant = dict()
    cut_data_constant["lays"] = int(data["lays"])
    cut_data_constant["p_s_c_d"] = data["p_s_c_d"]
    cut_data_constant["p_e_c_d"] = data["p_e_c_d"]
    cut_data_constant["a_s_c_d"] = data["a_s_c_d"]
    cut_data_constant["planned_output"] = int(data["total_output"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                                   {"$set": {"cut_data_constant": cut_data_constant}})
    update_status(user_id, order_id, "cut")
    return True

def save_cut_input_variable(user_id, order_id, data):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    cut_data_variable = dict()
    cut_data_variable["cutting_table"] = int(data["cutting_table"])
    cut_data_variable["planned_output_per_day"] = int(data["output_per_day"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                                   {"$set": {"recent_cut_data_variable": cut_data_variable, "recent_cut_date": today_date}})
    if orders_history.find_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}) is None:
        orders_history.insert_one({"user_id": user_id, "order_id": order_id, "date": today_date, "colour": data["colour_code"], "size": data["sizes"]})
    orders_history.update_one({"user_id": user_id, "order_id": order_id, "date": today_date, "colour": data["colour_code"], "size": data["sizes"]}, 
                              {"$set": {"cut_data_variable": cut_data_variable}})
    update_status(user_id, order_id, "cut")
    return True

def save_sew_input_constant(user_id, order_id, data):
    sew_data_constant = dict()
    sew_data_constant["p_s_s_d"] = data["p_s_s_d"]
    sew_data_constant["p_e_s_d"] = data["p_e_s_d"]
    sew_data_constant["a_s_s_d"] = data["a_s_s_d"]
    sew_data_constant["planned_wip"] = int(data["planned_wip"])
    sew_data_constant["planned_output"] = int(data["planned_output"])
    sew_data_constant["days"] = int(data["days"])
    sew_data_constant["eff"] = int(data["eff"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"sew_data_constant": sew_data_constant}})
    update_status(user_id, order_id, "sew")
    return True

def save_sew_input_variable(user_id, order_id, data):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    sew_data_variable = dict()
    sew_data_variable["sewing_line"] = int(data["sewing_line"])
    sew_data_variable["sam"] = int(data["sam"])
    sew_data_variable["man_power"] = int(data["man_power"])
    sew_data_variable["helpers"] = int(data["helpers"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"recent_sew_data_variable": sew_data_variable, "recent_sew_date": today_date}})
    if orders_history.find_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}) is None:
        orders_history.insert_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date})
    orders_history.update_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}, {"$set": {"sew_data_variable": sew_data_variable}})
    update_status(user_id, order_id, "sew")
    return True

def save_wash_input_constant(user_id, order_id, data):
    wash_data_constant = dict()
    wash_data_constant["p_s_w_d"] = data["p_s_w_d"]
    wash_data_constant["p_e_w_d"] = data["p_e_w_d"]
    wash_data_constant["a_s_w_d"] = data["a_s_w_d"]
    wash_data_constant["planned_output"] = int(data["output"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"wash_data_constant": wash_data_constant}})
    update_status(user_id, order_id, "wash")
    return True

def save_wash_input_variable(user_id, order_id, data):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    wash_data_variable = dict()
    wash_data_variable["output_per_day"] = int(data["output_per_day"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                                   {"$set": {"recent_wash_data_variable": wash_data_variable, "recent_wash_date": today_date}})
    if orders_history.find_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}) is None:
        orders_history.insert_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date})
    orders_history.update_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}, 
                              {"$set": {"wash_data_variable": wash_data_variable}})
    update_status(user_id, order_id, "wash")
    return True

def save_finish_input_constant(user_id, order_id, data):
    finish_data_constant = dict()
    finish_data_constant["p_s_f_d"] = data["p_s_f_d"]
    finish_data_constant["p_e_f_d"] = data["p_e_f_d"]
    finish_data_constant["a_s_f_d"] = data["a_s_f_d"]
    finish_data_constant["cluster_number"] = int(data["cluster_num"])
    finish_data_constant["planned_output"] = int(data["output"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"finish_data_constant": finish_data_constant}})
    update_status(user_id, order_id, "finish")
    return True

def save_finish_input_variable(user_id, order_id, data):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    finish_data_variable = dict()
    finish_data_variable["output_per_day"] = int(data["output_per_day"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"recent_finish_data_variable": finish_data_variable, "recent_finish_date": today_date}})
    if orders_history.find_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}) is None:
        orders_history.insert_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date})
    orders_history.update_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}, 
                              {"$set": {"finish_data_variable": finish_data_variable}})
    update_status(user_id, order_id, "finish")
    return True

def save_packing_input_constant(user_id, order_id, data):
    packing_data_constant = dict()
    packing_data_constant["p_s_p_d"] = data["p_s_p_d"]
    packing_data_constant["p_e_p_d"] = data["p_e_p_d"]
    packing_data_constant["a_s_p_d"] = data["a_s_p_d"]
    packing_data_constant["planned_output"] = int(data["output"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"packing_data_constant": packing_data_constant}})
    update_status(user_id, order_id, "packing")
    return True

def save_packing_input_variable(user_id, order_id, data):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    packing_data_variable = dict()
    packing_data_variable["num_cartons"] = int(data["num_cartons"])
    packing_data_variable["output_per_day"] = int(data["output_per_day"])
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"]}, 
                             {"$set": {"recent_packing_data_variable": packing_data_variable, "recent_packing_date": today_date}})
    if orders_history.find_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}) is None:
        orders_history.insert_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date})
    orders_history.update_one({"user_id": user_id, "order_id": order_id, "colour": data["colour_code"], "size": data["sizes"], "date": today_date}, 
                              {"$set": {"packing_data_variable": packing_data_variable}})
    update_status(user_id, order_id, "packing")
    return True

def save_completed_stage_pieces(user_id, order_id, completed_pieces, stage, colour, size):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    order_data = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {f"{stage}_total_actual_output": 1})
    detail_order_collection.update_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, 
                                       {"$set": {f"recent_{stage}_actual_output": completed_pieces, f"recent_{stage}_date": today_date, 
                                                 f"{stage}_total_actual_output": order_data[f"{stage}_total_actual_output"]+completed_pieces}})

    orders_history.update_one({"user_id":user_id, "order_id": order_id, "colour": colour, "size": size, "date":today_date}, 
                              {"$set": {f"{stage}_actual_output": completed_pieces}})
    return True

def get_stage_order_details(user_id, order_id, stage):
    base_data = orders_collection.find_one({"user_id": user_id, "order_id": order_id}, {"_id": 0})
    colours = base_data["colour_code"].split(",")
    sizes = base_data["sizes"].split(",")
    count = 0
    count_dict = dict()
    constant_data = dict()
    variable_data = dict()
    recent_actual_output = dict()
    total_actual_output = dict()
    stage_complete_date = dict()
    for colour in colours:
        count_dict[colour] = dict()
        constant_data[colour] = dict()
        variable_data[colour] = dict()
        recent_actual_output[colour] = dict()
        total_actual_output[colour] = dict()
        stage_complete_date[colour] = dict()
        for size in sizes:
            count_dict[colour][size] = dict()
            constant_data[colour][size] = dict()
            variable_data[colour][size] = dict()
            recent_actual_output[colour][size] = dict()
            total_actual_output[colour][size] = dict()
            stage_complete_date[colour][size] = dict()

            temp = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"_id": 0, f"{stage}_data_constant": 1})
            if temp:
                constant_data[colour][size][f"{stage}_data_constant"] = temp[f"{stage}_data_constant"]
            else:
                constant_data[colour][size][f"{stage}_data_constant"] = "N/A"
            
            temp = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"_id": 0, f"recent_{stage}_data_variable": 1})
            if temp:
                variable_data[colour][size][f"recent_{stage}_data_variable"] = temp[f"recent_{stage}_data_variable"]
            else:
                variable_data[colour][size][f"recent_{stage}_data_variable"] = "N/A"
            
            temp = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"_id": 0, f"recent_{stage}_actual_output": 1})
            if temp:
                recent_actual_output[colour][size]["recent_actual_output"] = temp[f"recent_{stage}_actual_output"]
            else:
                recent_actual_output[colour][size]["recent_actual_output"] = "N/A"
            
            temp = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"_id": 0, f"{stage}_total_actual_output": 1})
            if temp:
                total_actual_output[colour][size]["total_actual_output"] = temp[f"{stage}_total_actual_output"]
            else:
                total_actual_output[colour][size]["total_actual_output"] = "N/A"
            
            temp = detail_order_collection.find_one({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"_id": 0, f"{stage}_completed_date": 1})
            if temp:
                stage_complete_date[colour][size]["completed_date"] = temp[f"{stage}_completed_date"]
            else:
                stage_complete_date[colour][size]["completed_date"] = "N/A"

            count+=1
            count_dict[colour][size]["count"] = count
    return base_data, colours, sizes, count_dict, constant_data, variable_data, recent_actual_output, total_actual_output, stage_complete_date

def mark_stage_complete(user_id, order_id, colour, size, stage):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    detail_order_collection.update({"user_id": user_id, "order_id": order_id, "colour": colour, "size": size}, {"$set": {f"{stage}_completed_date": today_date}})
    return True

def get_stage_all_order_details(user_id, stage):
    all_order_ids = orders_collection.find({"user_id": user_id}, {"_id": 0, "order_id": 1})
    all_order_ids = [order["order_id"] for order in all_order_ids]
    length = len(all_order_ids)
    if length == 0:
        return None, length

    all_order_stage_details = [get_stage_order_details(user_id, order_id, stage) for order_id in all_order_ids]
    return all_order_stage_details, length

def get_dash_baord_data(user_id):
    all_order_ids = orders_collection.find({"user_id": user_id}, {"_id": 0, "order_id": 1})
    all_order_ids = [order["order_id"] for order in all_order_ids]
    length = len(all_order_ids)
    if length == 0:
        return None, length
    
    data = []
    for order_id in all_order_ids:
        base_data = orders_collection.find_one({"user_id": user_id, "order_id": order_id}, {"_id": 0})
        line_nos = []
        man_power = []
        eff = []
        planned_output = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        actual_output = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        rejected_pieces = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        recent_sew_data_variable = detail_order_collection.find({"user_id": user_id, "order_id": order_id, "recent_sew_data_variable": {"$exists": True}}, 
                                                                {"_id": 0, "recent_sew_data_variable": 1})
        for i in recent_sew_data_variable:
            line_nos.append(str(i["recent_sew_data_variable"]["sewing_line"]))
            man_power.append(str(i["recent_sew_data_variable"]["man_power"]))
        
        sew_data_constant = detail_order_collection.find({"user_id": user_id, "order_id": order_id, "sew_data_constant": {"$exists": True}}, 
                                                         {"_id": 0, "sew_data_constant": 1})
        for i in sew_data_constant:
            eff.append(str(i["sew_data_constant"]["eff"]))
        
        for stage in ["cut", "sew", "wash", "finish", "packing"]:
            stage_data_constant = detail_order_collection.find({"user_id": user_id, "order_id": order_id, f"{stage}_data_constant": {"$exists": True}}, 
                                                               {"_id": 0, f"{stage}_data_constant": 1})
            for i in stage_data_constant:
                planned_output[stage] += i[f"{stage}_data_constant"]["planned_output"]
            
            temp_actual_output = detail_order_collection.find({"user_id": user_id, "order_id": order_id, f"{stage}_total_actual_output": {"$exists": True}}, 
                                                                  {"_id": 0, f"{stage}_total_actual_output": 1})
            for i in temp_actual_output:
                actual_output[stage] += i[f"{stage}_total_actual_output"]

        for stage in ["cut", "sew", "wash", "finish", "packing"]:
            if planned_output[stage] == 0:
                planned_output[stage] = "N\A"
                rejected_pieces[stage] = "N\A"
            else:
                rejected_pieces[stage] = planned_output[stage] - actual_output[stage]
        if line_nos == []:
            line_nos = ["N\A"]
        if man_power == []:
            man_power = ["N\A"]
        if eff == []:
            eff = ["N\A"]
        temp_order_data = {"item_num": base_data["item_num"], "style_num": base_data["style_num"], "colour_code": base_data["colour_code"], "buyer": base_data["buyer"], 
                           "quantity": base_data["quantity"], "sizes": base_data["sizes"], "start_date": base_data["issue_date"], 
                           "shipment_date": base_data["delivery_date"], "line_num": ",".join(line_nos), "man_power": ",".join(man_power), 
                           "eff": ",".join(eff), "planned_output": planned_output, "actual_output": actual_output, "rejected_output": rejected_pieces, "status": base_data["status"]}
        data.append(temp_order_data)
    return data, length

def get_dash_baord_filter_data(user_id, request):
    filter_buyer = request["buyer_filter"]
    filter_style = request["style_filter"]
    filter_colour = request["colour_filter"]
    filters = ["buyer", "style_num", "colour_code"]
    total_filters = 0
    filter_array = []
    filter_indexes = []
    if filter_buyer != "ALL":
        total_filters += 1
        filter_array.append(filter_buyer)
        filter_indexes.append(0)
    if filter_style != "ALL":
        total_filters += 1
        filter_array.append(filter_style)
        filter_indexes.append(1)
    if filter_colour != "ALL":
        total_filters += 1
        filter_array.append(filter_colour)
        filter_indexes.append(2)
    
    if total_filters == 3:
        all_order_ids = orders_collection.find({"user_id": user_id, "buyer": filter_buyer, "style_num": filter_style, "colour_code": filter_colour}, {"_id": 0, "order_id": 1})
    elif total_filters == 2:
        all_order_ids = orders_collection.find({"user_id": user_id, f"{filters[filter_indexes[0]]}": filter_array[0], f"{filters[filter_indexes[1]]}": filter_array[1]}, {"_id": 0, "order_id": 1})
    elif total_filters == 1:
        all_order_ids = orders_collection.find({"user_id": user_id, f"{filters[filter_indexes[0]]}": filter_array[0]}, {"_id": 0, "order_id": 1})
    else:
        all_order_ids = orders_collection.find({"user_id": user_id}, {"_id": 0, "order_id": 1})
    
    all_order_ids = [order["order_id"] for order in all_order_ids]
    length = len(all_order_ids)
    if length == 0:
        return None, length
    
    data = []
    for order_id in all_order_ids:
        base_data = orders_collection.find_one({"user_id": user_id, "order_id": order_id}, {"_id": 0})
        line_nos = []
        man_power = []
        eff = []
        planned_output = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        actual_output = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        rejected_pieces = {"cut": 0, "sew": 0, "wash": 0, "finish": 0, "packing": 0}
        recent_sew_data_variable = detail_order_collection.find({"user_id": user_id, "order_id": order_id, "recent_sew_data_variable": {"$exists": True}}, 
                                                                {"_id": 0, "recent_sew_data_variable": 1})
        for i in recent_sew_data_variable:
            line_nos.append(str(i["recent_sew_data_variable"]["sewing_line"]))
            man_power.append(str(i["recent_sew_data_variable"]["man_power"]))
        
        sew_data_constant = detail_order_collection.find({"user_id": user_id, "order_id": order_id, "sew_data_constant": {"$exists": True}}, 
                                                         {"_id": 0, "sew_data_constant": 1})
        for i in sew_data_constant:
            eff.append(str(i["sew_data_constant"]["eff"]))
        
        for stage in ["cut", "sew", "wash", "finish", "packing"]:
            stage_data_constant = detail_order_collection.find({"user_id": user_id, "order_id": order_id, f"{stage}_data_constant": {"$exists": True}}, 
                                                               {"_id": 0, f"{stage}_data_constant": 1})
            for i in stage_data_constant:
                planned_output[stage] += i[f"{stage}_data_constant"]["planned_output"]
            
            temp_actual_output = detail_order_collection.find({"user_id": user_id, "order_id": order_id, f"{stage}_total_actual_output": {"$exists": True}}, 
                                                                  {"_id": 0, f"{stage}_total_actual_output": 1})
            for i in temp_actual_output:
                actual_output[stage] += i[f"{stage}_total_actual_output"]

        for stage in ["cut", "sew", "wash", "finish", "packing"]:
            if planned_output[stage] == 0:
                planned_output[stage] = "N\A"
                rejected_pieces[stage] = "N\A"
            else:
                rejected_pieces[stage] = planned_output[stage] - actual_output[stage]
        if line_nos == []:
            line_nos = ["N\A"]
        if man_power == []:
            man_power = ["N\A"]
        if eff == []:
            eff = ["N\A"]
        temp_order_data = {"item_num": base_data["item_num"], "style_num": base_data["style_num"], "colour_code": base_data["colour_code"], "buyer": base_data["buyer"], 
                           "quantity": base_data["quantity"], "sizes": base_data["sizes"], "start_date": base_data["issue_date"], 
                           "shipment_date": base_data["delivery_date"], "line_num": ",".join(line_nos), "man_power": ",".join(man_power), 
                           "eff": ",".join(eff), "planned_output": planned_output, "actual_output": actual_output, "rejected_output": rejected_pieces, "status": base_data["status"]}
        data.append(temp_order_data)
    return data, length


def get_dpr(user_id):
    today_date = datetime.now().date().strftime("%Y-%d-%m")
    all_order_ids = orders_history.find({"user_id": user_id, "date": today_date}, {"_id": 0, "order_id": 1})
    all_order_ids = [order["order_id"] for order in all_order_ids]
    all_order_ids = list(set(all_order_ids))
    length = len(all_order_ids)
    if length == 0:
        return None
    data = []
    for order_id in all_order_ids:
        data_template = {"date": today_date, "item_num": None, "style_num": None, "colour_code": None, "sizes": None, "quantity": None, "till_date_cut": 0, 
                         "till_date_sew": 0, "till_date_wash": 0, "till_date_finish": 0, "till_date_packing": 0, "today_cut": 0, "today_sew": 0, "today_wash": 0, 
                         "today_finish": 0, "today_packing": 0}
        base_data = orders_collection.find_one({"user_id": user_id, "order_id": order_id})
        data_template["item_num"] = base_data["item_num"]
        data_template["style_num"] = base_data["style_num"]
        data_template["colour_code"] = base_data["colour_code"]
        data_template["sizes"] = base_data["sizes"]
        data_template["quantity"] = base_data["quantity"]
        for stage in ["cut", "sew", "wash", "finish", "packing"]:
            today_actual = orders_history.find({"user_id": user_id, "order_id": order_id, "date": today_date, f"{stage}_actual_output": {"$exists": True}}, {"_id": 0, f"{stage}_actual_output": 1})
            for i in today_actual:
                data_template[f"today_{stage}"] += i[f"{stage}_actual_output"]
            
            till_date_actual = detail_order_collection.find({"user_id": user_id, "order_id": order_id, f"{stage}_total_actual_output": {"$exists": True}}, {"_id": 0, f"{stage}_total_actual_output": 1})
            for i in till_date_actual:
                data_template[f"till_date_{stage}"] += i[f"{stage}_total_actual_output"]
        data.append(data_template)
    return data

def delete_order(user_id, order_id):
    orders_collection.delete_many({"user_id": user_id, "order_id": order_id})
    detail_order_collection.delete_many({"user_id": user_id, "order_id": order_id})
    orders_history.delete_many({"user_id": user_id, "order_id": order_id})
    return True
