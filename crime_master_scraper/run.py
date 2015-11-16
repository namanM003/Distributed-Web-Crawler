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

    # Uncomment the following to run scrapy

    # command = "scrapy crawl crime_master -a start_url="+page+" -o links.csv -t csv"
    # print command
    # os.system(command)

    headers = ['A','B','C']
    numbers = ['3','2','4']
    headersPages = {	'headers':headers,
    					'numbers':numbers
    				}
    missingpagesList = [	{'headerName':'A','pages':['example.com/a','example.com/b','wassup.com/hello']},
    						{'headerName':'B','pages':['example.com/a','wassup.com/hi']},
    						{'headerName':'C','pages':['example.com/a','example.com/b','wassup.com/hello','wassup.com/hi']}
    					]
    return render_template('result.html', page=page, headersPages=headersPages, missingpagesList=missingpagesList)

if __name__ == "__main__":
    app.run()