from flask import Flask,render_template
app = Flask(__name__)

@app.route('/<name>.html')
def getResource(name):
    return render_template(name+'.html')

if __name__ == '__main__':
    app.run(debug=True)
