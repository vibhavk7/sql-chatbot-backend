from datetime import datetime
import json

#This function does the final formatting of the result
def build_and_format_graph_data(x_label,y_label,result):
    #arrange it into a ist of objects with x and y coordinates
    keys = list(result.keys())
    values = list(result.values())
    graph_format = []
    for i in range(len(keys)):
        obj = {}
        obj[x_label] = keys[i]
        obj[y_label] = values[i]
        graph_format.append(obj)
    return graph_format

#This function dumps the data into the json file
def dump_into_json(data,x_label,y_label,x,y):
    #dump the original response data from the odoo api into a json file. 
    #This is because the duration of the data will not change
    with open("data.json", "w") as json_file:
        file_dict = {}
        file_dict["data"] = data
        file_dict["x"] = x
        file_dict["y"] = y
        file_dict["x_label"] = x_label
        file_dict["y_label"] = y_label
        json.dump(file_dict, json_file)


# This function is responsible for aggregating the available data per year and returning the formatted data
def year_wise_data(data,x_label,y_label,x,y):
    #before doing anything, dump the original data into the json file
    dump_into_json(data,x_label,y_label,x,y)
    #first sort the data
    data = sorted(data, key=lambda item: item[x])
    result = {}
    for i in data:
        #create the key as the year
        key = datetime.strptime(i[x], "%Y-%m-%d").year
        #build the dictionary
        if key in result:
            result[key] += (1 if y=="count" else i[y])
        else: 
            result[key] = (1 if y=="count" else i[y])
    formatted_graph_data = build_and_format_graph_data(x_label,y_label,result)
    return formatted_graph_data


# This function is responsible for aggregating the available data per quarter and returning the formatted data
def quarter_wise_data(data,x_label,y_label,x,y):
    #before doing anything, dump the original data into the json file
    dump_into_json(data,x_label,y_label,x,y)
    #first sort the data
    data = sorted(data, key=lambda item: item[x])
    result = {}
    for i in data:
        #create the key as the quarter name
        month = datetime.strptime(i[x], "%Y-%m-%d").month
        quarter = (month - 1) // 3 + 1
        key = "Quarter " + str(quarter)        
        #build the dictionary
        if key in result:
            result[key] += (1 if y=="count" else i[y])
        else: 
            result[key] = (1 if y=="count" else i[y])
    formatted_graph_data = build_and_format_graph_data(x_label,y_label,result)
    return formatted_graph_data


# This function is responsible for aggregating the available data per month and returning the formatted data
def month_wise_data(data,x_label,y_label,x,y):
    #before doing anything, dump the original data into the json file
    dump_into_json(data,x_label,y_label,x,y)
    #first sort the data
    data = sorted(data, key=lambda item: item[x])
    result = {}
    for i in data:
        #create the key as the month name
        key = datetime.strptime(i[x], "%Y-%m-%d").strftime("%B")
        #build the dictionary
        if key in result:
            result[key] += (1 if y=="count" else i[y])
        else: 
            result[key] = (1 if y=="count" else i[y])
    formatted_graph_data = build_and_format_graph_data(x_label,y_label,result)
    return formatted_graph_data


# This function is responsible for aggregating the available data per week and returning the formatted data
def week_wise_data(data,x_label,y_label,x,y):
    #before doing anything, dump the original data into the json file
    dump_into_json(data,x_label,y_label,x,y)
    #first sort the data
    data = sorted(data, key=lambda item: item[x])
    result = {}
    for i in data:
        #create the key as the week name
        key = "Week " + str(datetime.strptime(i[x], "%Y-%m-%d").isocalendar()
        [1]) #this returns year and week. 0th index stores year
        #This was working earlier the commented one
        # key = "Week " + str(datetime.strptime(i["date_order"], "%Y-%m-%d").isocalendar()[1]) #this returns year and week. 0th index stores year
        #build the dictionary
        if key in result:
            result[key] += (1 if y=="count" else i[y])
        else: 
            result[key] = (1 if y=="count" else i[y])
    formatted_graph_data = build_and_format_graph_data(x_label,y_label,result)
    return formatted_graph_data


# This function is responsible for aggregating the available data per day and returning the formatted data
def day_wise_data(data,x_label,y_label,x,y):
    #before doing anything, dump the original data into the json file
    dump_into_json(data,x_label,y_label,x,y)
    #first sort the data
    data = sorted(data, key=lambda item: item[x])
    result = {}
    for i in data:
        #create the key as the date
        key = i[x]
        #build the dictionary
        if key in result:
            result[key] += (1 if y=="count" else i[y])
        else: 
            result[key] = (1 if y=="count" else i[y])
    formatted_graph_data = build_and_format_graph_data(x_label,y_label,result)
    return formatted_graph_data

# #This function is responsible for getting the quarter from the date. 
# #Input: relative number for quarter
# #       0 - this quarter
# #       1 - last quarter
# #       2 - 2 quarters back....
# #Output: The start and end dates for that quarter
# def get_quarter(relative):
#     # Get the current date
#     current_date = datetime.now()
#     current_month = current_date.month

#     # Calculate the last quarter's start and end dates
#     if month in [1, 2, 3]:
#         # If the current month is in the first quarter, the last quarter is in the previous year
#         last_quarter_start = datetime(current_date.year - 1, 10, 1)
#         last_quarter_end = datetime(current_date.year - 1, 12, 31)
#     else:
#         # Otherwise, the last quarter is in the same year
#         quarter = (current_date.month - 1) // 3  # Determine the current quarter
#         last_quarter_start = datetime(current_date.year, quarter * 3 + 1, 1)
#         last_quarter_end = datetime(current_date.year, quarter * 3 + 3, 31)

#     print("Last Quarter Start Date:", last_quarter_start)
#     print("Last Quarter End Date:", last_quarter_end)

# def quarter_start_date(relative):


# def quarter_end_date(relative):
