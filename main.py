from flask import Flask, request, render_template
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)


def process_store_data(store_data, target_year, target_field):
    fetched_data = {}
    for month_year, data in store_data.items():
        if month_year.startswith(target_year):
            month = datetime.strptime(month_year, '%Y-%m').strftime('%B')
            fetched_data[month] = data[target_field]
    return fetched_data


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    target_year = request.form['target_year']
    store = request.form['store']
    target_field = request.form['field']

    csv_path = 'Walmart_sales.csv'  # Replace with your actual CSV path
    stores_data = {}

    with open(csv_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            store_name = row['Store']
            date = datetime.strptime(row['Date'], '%d-%m-%Y')  # Assuming Date format
            month_year = date.strftime('%Y-%m')

            if store_name not in stores_data:
                stores_data[store_name] = {}

            if month_year not in stores_data[store_name]:
                stores_data[store_name][month_year] = {}

            stores_data[store_name][month_year][target_field] = row[target_field]

    fetched_data = process_store_data(stores_data.get(store, {}), target_year, target_field)

    plt.bar(fetched_data.keys(), fetched_data.values())
    plt.xlabel('Month')
    plt.ylabel(target_field)
    plt.title(f'{target_field} by Month for Target Year')

    # Save plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close()

    # Convert image to base64 string
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    return f'<img src="data:image/png;base64,{image_base64}">'


if __name__ == '__main__':
    app.run(debug=True)
