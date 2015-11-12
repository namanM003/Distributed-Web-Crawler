from flask import Flask, render_template, request, url_for
import os

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('template.html')


@app.route('/submit/', methods=['POST'])
def submit():
    page=request.form['webpage']
    print page
    command = "scrapy crawl crime_master -a start_url="+page+" -o links.csv -t csv"
    print command
    os.system(command)
    return render_template('result.html', page=page)

if __name__ == "__main__":
    app.run()