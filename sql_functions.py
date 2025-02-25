import mysql.connector, re
import json
from timeline_graph_functions import year_wise_data,quarter_wise_data,month_wise_data,week_wise_data,day_wise_data
from flask import jsonify
from datetime import datetime, date
from decimal import Decimal # to eliminate the error which is occurring due to incompatible Decimal format in json

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="mysql09876",
  database="classicmodels"
)

mycursor = mydb.cursor()


tables = ['customers','employees','offices','orderdetails','orders','payments','products']

#This function is intended to be run only once and create th esql prompt file
def create_sql_prompt_file():
    with open("sql_prompt.txt","a") as f:
        # Loop through the tables and retrieve column names
        for table in tables:
            mycursor.execute(f"SHOW COLUMNS FROM {table}")
            myresult = mycursor.fetchall()
            columns = []
            f.write(table)
            f.write(" : ")
            for x in myresult:               
                columns.append(x[0])
            f.write(str(columns))
            f.write("\n")
        print("done")


def table_format(data,columns): 
    # print("final select clause",type(select_clause))
    # column_mapping = re.findall(r'(\w+)(?:,\s*\w+)*', select_clause)
    # column_mapping=select_clause.split(", ")
    # col=[]
    # for i in column_mapping:
    #     col.append(i.split(".")[-1])
    # print(col)
    # print("data = ",data)
    # column_mapping=col
    # print(column_mapping)
    result_data = []
    for row in data:
        row_dict = {}
        for i,value in enumerate(row): 
            #the value should be a string only if it is a date object. Otherwise keep the format as it is      
            if isinstance(value, date):
                row_dict[columns[i].upper()] = str(value)
            elif isinstance(value, Decimal):
                row_dict[columns[i].upper()] = float(value)
            else:
                row_dict[columns[i].upper()] = value
        result_data.append(row_dict)
    return result_data

#update the x_label and y_label for non time related queries
def graph_format(data,columns,x_label,y_label,frequency):
    time = False
    print("inside graph")
    # column_mapping = re.findall(r'(\w+)(?:,\s*\w+)*', select_clause)
    # print(column_mapping)
    result_data = []
    if len(data) == 0:
        return [],time
    #check if any key has a date value 
    for val in data[0]:
        if isinstance(val, date):
            time = True
    for row in data:
        row_dict = {}
        for i, value in enumerate(row):    
            #the value should be a string only if it is a date object. Otherwise keep the format as it is      
            if isinstance(value, date):
                row_dict[columns[i].upper()] = str(value)
            elif isinstance(value, Decimal):
                row_dict[columns[i].upper()] = float(value)
            else:
                row_dict[columns[i].upper()] = value
        result_data.append(row_dict)
    
    #Only update time and result_data if it is time related data
    if time==True:
        keys = list(result_data[0].keys())
        print("keys = ",keys)
        print("result = ",result_data)
        x = keys[0]
        y = keys[1]
        #switch the frequency
        # if frequency == "year_wise_data":
        #     result_data = year_wise_data(result_data,x_label,y_label,x,y)
        # elif frequency == "quarter_wise_data":
        #     result_data = quarter_wise_data(result_data,x_label,y_label,x,y)
        # elif frequency == "month_wise_data":
        #     result_data = month_wise_data(result_data,x_label,y_label,x,y)
        # elif frequency == "week_wise_data":
        #     result_data = week_wise_data(result_data,x_label,y_label,x,y)
        # elif frequency == "day_wise_data":
        #     result_data = day_wise_data(result_data,x_label,y_label,x,y)
    return result_data,time
    

def process_gpt_response(gpt_response):
    try:
        # return sqlquerygenerated
        print(gpt_response)
        response_dict = json.loads(gpt_response)
        print("resp = ",response_dict)
        sqlquerygenerated = response_dict["query"]
        print("query = ",sqlquerygenerated)
        # select_to_from_match = re.search(r'SELECT\s+(.*?)\s+FROM', sqlquerygenerated, re.IGNORECASE)
        # print("Expression",select_to_from_match)
        # if select_to_from_match:
        #     select_clause = select_to_from_match.group(1).strip()
        #     print("select_clause:", select_clause)
        #     print(type(select_clause))
        # else:
        #     print("select_clause not found in the SQL query.")
        #     print(type(sqlquerygenerated))

        mycursor.execute(sqlquerygenerated)
        myresult2 = mycursor.fetchall()
        
        # print(myresult2)
        print("--------------------------------------")

        if response_dict["type"] == 'graph':
            # formatted,time = graph_format(myresult2,select_clause,response_dict["x"],response_dict["y"])
            formatted,time = graph_format(myresult2,response_dict["columns"],response_dict["x"],response_dict["y"],response_dict.get("frequency"))
            final_response={"out_str":response_dict["outstr"],"time":time,"data":{"content":response_dict["type"],"graph_type":"column","data":{"data":formatted}}} 

        elif response_dict["type"] == 'table':
            formatted = table_format(myresult2,response_dict["columns"])
            final_response = {"out_str":response_dict["outstr"],"data":{"content":response_dict["type"],"data":{"data":formatted}}}

    except Exception as e:
        final_response = {"out_str":"Error at execute function ","data":{"content":"text","data":e}}
    print("final = ",final_response)
    return final_response


# column_mapping = []
  # for column in select_clause:
  #    column_mapping.append(column)

  # refined_column_mapping = []
  # for column in column_mapping:
  #     response = openai.Completion.create(
  #         engine="text-davinci-003",
  #         prompt=f"""Refine the column name {column}.
  #                     If column name is in the form of Salary_Amount or Salary-amount or SalaryAmount or salary
  #                     Amount, extract main part of it only. Here it is 'Salary'.   
  #                 """,
  #         temperature = 0.2,
  #         max_tokens=50
  #     )
  #     refined_column = response.choices[0].text.strip()
  #     refined_column_mapping.append(refined_column)
  #     for r in refined_column_mapping:
  #        print(refined_column_mapping[r])
# s='''SELECT orders.orderDate, orders.orderNumber FROM orders JOIN 
#     customers ON orders.customerNumber = customers.customerNumber
# JOIN 
#     employees ON customers.salesRepEmployeeNumber = employees.employeeNumber
# JOIN 
#     offices ON employees.officeCode = offices.officeCode
# WHERE 
#     offices.city = "Tokyo"'''
# a=mycursor.execute(s)
# b = mycursor.fetchall()
# c = quarter_wise_data()
# print(b)
# s = '''SELECT orders.orderDate, orders.orderNumber FROM orders JOIN customers ON orders.customerNumber = customers.customerNumber JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber JOIN offices ON employees.officeCode = offices.officeCode WHERE offices.city = "Tokyo"'''
# a=mycursor.execute(s)
# data = mycursor.fetchall()
# print(graph_format(data,["orderDate","orderNumber"],"Customer","Orders","quarter_wise_data"))
# # print(table_format([(124, 'Mini Gifts Distributors Ltd.', 17), (141, 'Euro+ Shopping Channel', 26)],['customerNumber', 'customerName', 'total_orders']))