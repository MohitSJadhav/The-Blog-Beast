from flask import Flask,render_template
import numpy
import pandas

app = Flask(__name__)

@app.route('/')
def main_file():
    return render_template('index.html')

@app.route('/about-us.html')
def about_us():
    return render_template('about-us.html')

@app.route('/blog.html')
def blog():
    return render_template('blog.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/portfolio.html')
def portfolio():
    return render_template('portfolio.html')

@app.route('/services.html')
def services():
    return render_template('services.html')

@app.route('/single-blog.html')
def single_blog():
    return render_template('single-blog.html')

app.run(debug=True)
