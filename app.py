from flask import Flask, render_template, request
import AlphaBot

app = Flask(__name__)
robot = AlphaBot.AlphaBot()
robot.stop()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "Avanti" in request.form:
            robot.forward()
        elif "Indietro" in request.form:
            robot.backward()
        elif "Destra" in request.form:
            robot.right()
        elif "Sinistra" in request.form:
            robot.left()
        elif "Stop" in request.form:
            robot.stop()
        
        return render_template("index.html")
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")