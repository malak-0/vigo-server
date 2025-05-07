from flask import Flask

server = Flask(__name__)

# Define a route
@server.route('/beeb')
def home():
    return "Hello, Flask server is running!"

@server.route('/about')
def about():
    return "This is the About page."

# Run the server
if __name__ == '__main__':
    server.run(debug=True)