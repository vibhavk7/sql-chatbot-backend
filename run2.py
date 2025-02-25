import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import mysql.connector
import json
from datetime import date, datetime
from decimal import Decimal

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.json.sort_keys = False

# Initialize Azure AI Inference Client for GPT-4
client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",  # Azure endpoint
    credential=AzureKeyCredential("<Api key from github token>")  # Replace with api key from github
)

# Database connection
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",
    database="classicmodels"
)
mycursor = mydb.cursor()

# SQL prompt template
sql_temp = """You are an expert python-sql developer who generates a single python dictionary.
You will be given a question which can expect a response in a tabular or graphical format.
If you receive any short forms like 'merc', you must understand that it refers to 'Mercedes' and create a final question accordingly.
The database is 'classicmodels'.
{prompt_data}
Please do not add any other key to this dictionary.
Please don't add any extra text other than the dictionary."""

# Load SQL prompt file
with open("sql_prompt.txt", "r") as file:
    prompt_data = file.read()

def memory(final_question, prev, question):
    response = client.complete(
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content=f"""
                You will be provided with either one or two questions.
                If only one question is given, return that question.
                If two questions are given:
                    If there is explicit context between them (e.g., words like 'among those', 'previous', 'same'),
                    create a new question combining both.
                    If NO context, return only the second question.
                Always return {question} if it's not contextual for {prev}.
                Generate only the question, no extra text.
                Questions: {final_question}
            """)
        ],
        model="gpt-4o",
        temperature=0.1,
        max_tokens=512,
        top_p=1
    )
    return response.choices[0].message.content

@app.route("/query", methods=["POST"])
def process_query():
    data = request.get_json()
    question = data.get("question")
    print(f"Question: {question}")

    if not question:
        return jsonify({"error": 'Missing parameter "question"'})

    try:
        # Generate final question using memory function
        final_quest = memory(question, "", question)
        print(f"Final Question: {final_quest}")

        # Create the full prompt
        full_prompt = sql_temp.format(prompt_data=prompt_data)
        
        # Get GPT-4 response
        response = client.complete(
            messages=[
                SystemMessage(content="You are a SQL expert."),
                UserMessage(content=full_prompt + "\nQuestion: " + final_quest)
            ],
            model="gpt-4o",
            temperature=0.1,
            max_tokens=512,
            top_p=1
        )
        resp_val = response.choices[0].message.content
        print(f"GPT-4 Response: {resp_val}")

        # Process the response
        output = process_gpt_response(resp_val)
        return jsonify(output)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."})

def process_gpt_response(gpt_response):
    try:
        response_dict = json.loads(gpt_response)
        sql_query = response_dict["query"]
        mycursor.execute(sql_query)
        result = mycursor.fetchall()

        if response_dict["type"] == "graph":
            formatted_data = [{"x": row[0], "y": row[1]} for row in result]
            return {
                "outstr": response_dict["outstr"],
                "type": "graph",
                "data": formatted_data,
                "x_label": response_dict.get("x", "x"),
                "y_label": response_dict.get("y", "y"),
            }
        elif response_dict["type"] == "table":
            columns = response_dict["columns"]
            formatted_data = [dict(zip(columns, row)) for row in result]
            return {
                "outstr": response_dict["outstr"],
                "type": "table",
                "data": formatted_data,
            }
        return {"error": "Unknown response type"}

    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from GPT-4"}
    except KeyError as e:
        return {"error": f"Missing key in response: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
