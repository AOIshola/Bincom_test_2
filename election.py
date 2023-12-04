import http.server
import socketserver
import mysql.connector
from urllib.parse import urlparse, parse_qs

PORT = 8000

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ishola',
    'database': 'Bincom'
}

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path.startswith('/polling_unit'):
            polling_unit_id = int(parsed_path.path.split('/')[-1])
            results = self.get_polling_unit_results(polling_unit_id)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.get_html(results).encode('utf-8'))
        elif parsed_path.path == '/sum_polling_units':
            self.handle_sum_polling_units(query)
        elif parsed_path.path == '/new_polling_unit':
            self.handle_new_polling_unit(query)
        else:
            super().do_GET()

    def get_polling_unit_results(self, polling_unit_id):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT * FROM announced_pu_results WHERE polling_unit_uniqueid = %s"
        cursor.execute(query, (polling_unit_id,))
        results = cursor.fetchall()

        connection.close()

        return results

    def get_html(self, results):
        html_content = "<!DOCTYPE html>"
        html_content += "<html><head><title>Polling Unit Results</title></head><body>"
        html_content += "<h1>Polling Unit Results</h1>"
        html_content += "<table border='1'><tr><th>Result ID</th><th>Polling Unit ID</th><th>Party Abbreviation</th><th>Party Score</th></tr>"
        for result in results:
            html_content += f"<tr><td>{result[0]}</td><td>{result[1]}</td><td>{result[2]}</td><td>{result[3]}</td></tr>"
        html_content += "</table></body></html>"

        return html_content

    def handle_sum_polling_units(self, query):
        if 'lga_id' in query:
            lga_id = int(query['lga_id'][0])
            total_score = self.get_sum_of_polling_units(lga_id)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Summed Polling Unit Result</title>
                </head>
                <body>
                    <h1>Summed Result for the Selected Local Government</h1>
                    <p>Total Score: {total_score}</p>
                </body>
                </html>
            """
            self.wfile.write(result_html.encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing 'lga_id' parameter.")

    def get_sum_of_polling_units(self, lga_id):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"SELECT SUM(party_score) FROM announced_pu_results WHERE polling_unit_uniqueid IN (SELECT uniqueid FROM polling_unit WHERE lga_id={lga_id})"
        cursor.execute(query)
        total_score = cursor.fetchone()[0] or 0

        connection.close()
        return total_score

    def handle_new_polling_unit(self, query):
        if 'polling_unit_name' in query:
            polling_unit_name = query['polling_unit_name'][0]
            self.create_new_polling_unit_page(polling_unit_name)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"New polling unit page created.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing 'polling_unit_name' parameter.")

    def create_new_polling_unit_page(self, polling_unit_name):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        insert_query = "INSERT INTO polling_unit (polling_unit_name) VALUES (%s)"
        cursor.execute(insert_query, (polling_unit_name,))
        connection.commit()

        polling_unit_id = cursor.lastrowid

        html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>{polling_unit_name} Results</title>
            </head>
            <body>
                <h1>{polling_unit_name} Results</h1>
                <!-- Add your form or content for storing results for all parties -->
            </body>
            </html>
        """

        file_name = f"{polling_unit_id}_{polling_unit_name.replace(' ', '_')}.html"
        with open(file_name, 'w') as file:
            file.write(html_content)

        connection.close()

if __name__ == "__main__":
    handler = MyRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server started at localhost:{PORT}")
        httpd.serve_forever()