from app import app

@app.route('/')
@app.route('/index')
def index():
    return("""<head><meta http-equiv="refresh" content="600"></head><body><img src="static/plot.png"></body>""")

