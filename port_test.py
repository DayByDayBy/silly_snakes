from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

if __name__ == "__main__":
    app.run(port=5173)
    
    
    
#    yep, this works fine, turns out the 5000 bug was apple being 'helpful' dicks again: the control centre is now hanging on to 5000 for airplay 