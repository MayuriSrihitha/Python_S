from flask import Flask, request, jsonify
import pandas as pd
import os
app = Flask(__name__)
CSV_FILE_PATH = "data.csv"
def read_csv():
    return pd.read_csv(CSV_FILE_PATH)
def write_csv(data):
    data.to_csv(CSV_FILE_PATH, index=False)
@app.route('/employees', methods=['POST'])
def create_employee():
    new_employee = request.json  
    data = read_csv()  
    new_employee_df = pd.DataFrame([new_employee]) 
    data = pd.concat([data, new_employee_df], ignore_index=True) 
    write_csv(data)  
    return jsonify(new_employee), 201   
@app.route('/employees', methods=['GET'])
def get_employees():
    data = read_csv()  
    return jsonify(data.to_dict(orient="records"))  
@app.route('/employees/<int:emp_id>', methods=['GET'])
def get_employee(emp_id):
    data = read_csv()
    employee = data[data['id'] == emp_id]  
    if employee.empty:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee.to_dict(orient="records")[0])
@app.route('/employees/<int:emp_id>', methods=['PUT'])
def update_employee(emp_id):
    update_data = request.json
    data = read_csv()
    if emp_id not in data['id'].values:
        return jsonify({"error": "Employee not found"}), 404
    data.loc[data['id'] == emp_id, update_data.keys()] = update_data.values()
    write_csv(data)
    return jsonify({"message": "Employee updated successfully"})
@app.route('/employees/<int:emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    data = read_csv()
    if emp_id not in data['id'].values:
        return jsonify({"error": "Employee not found"}), 404
    data = data[data['id'] != emp_id]
    write_csv(data)
    return jsonify({"message": "Employee deleted successfully"})

if __name__ == '__main__':
    if not os.path.exists(CSV_FILE_PATH):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["John Doe", "Jane Smith", "Bob Johnson"],
            "position": ["Developer", "Manager", "Analyst"],
            "salary": [60000, 80000, 55000]
        })
        write_csv(df)

    app.run(debug=True)