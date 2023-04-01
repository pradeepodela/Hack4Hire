from flask import Flask, render_template, request
from xmlrpc import client
from flask import Flask,render_template,request,redirect,url_for,flash
import sqlite3 as sql
import openai

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = "super secret key"
app.config['INC'] = 0  # initialize the counter
app.config['DATA'] = {}
# sess = Session()
openai.api_key = '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'

def generateBlogTopics(prompt1):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt="Generate 10 servay questions on: {}. \n \n 1.  ".format(prompt1),
      temperature=0.7,
      max_tokens=2000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    return response['choices'][0]['text']


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/get")
def get_bot_response():
    app.config['INC'] += 1  # increment the counter
    print(f"Counter value: {app.config['INC']}")

    # get all questions from the database
    con = sql.connect("hac_web.db")
    cur = con.cursor()
    cur.execute("SELECT Question FROM Quesdata")
    questions = cur.fetchall()

    # return the questions one by one
    if app.config['INC'] <= len(questions):
        # userText = str(userText).replace('[','')
        # userText = str(userText).replace(']','')
        # userText = str(userText).replace("'",'')
        # userText = str(userText).replace('[','')
        userText = request.args.get('msg')
        app.config['DATA'][questions[app.config['INC'] - 1][0]]=[userText]
        return questions[app.config['INC'] - 1][0]
    else:
        print(app.config['DATA'])
        app.config['INC']=0
        con=sql.connect("hac_web.db")
        cur=con.cursor()
        cur.execute("insert into resdata(Data) values (?)", (str(app.config['DATA']),))
        con.commit()
        




        # Connect to the database
        conn = sql.connect('hac_web.db')

        # Create a cursor object
        cur = conn.cursor()

        # Execute a SELECT statement to retrieve all data from a table
        cur.execute('SELECT * FROM resdata')

        # Fetch all rows and print them
        rows = cur.fetchall()
        print('-----------------')
        for row in rows:
            print(row)

        # Close the cursor and the database connection
        cur.close()
        conn.close()
        return "No more questions."



@app.route("/responses")
def responses():
    con = sql.connect("hac_web.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM resdata")
    rows = cur.fetchall()
    print(rows)
    return render_template("responses.html", rows=rows)



@app.route('/genrate', methods=["GET", "POST"])
def blogen():

    if request.method == 'POST':

        prompt = request.form['blogTopic']
        blogT = generateBlogTopics(prompt)
        blogTopicIdeas = blogT.replace('\n', '<br>')

        


    return render_template('blog.html', **locals())
@app.route("/login")
def login():
    
    return render_template('login.html')

@app.route("/admin")
def index():
    con=sql.connect("hac_web.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from Quesdata")
    data=cur.fetchall()
    return render_template("qus_index.html",datas=data)

@app.route("/add_user",methods=['POST','GET'])
def add_user():
    if request.method=='POST':
        Question=request.form['Question']

        con=sql.connect("hac_web.db")
        cur=con.cursor()
        cur.execute("insert into Quesdata(Question) values (?)", (Question,))
        con.commit()
        flash('User Added','success')
        return redirect(url_for("index"))
    return render_template("add_user.html")

@app.route("/edit_user/<string:uid>",methods=['POST','GET'])
def edit_user(uid):
    if request.method=='POST':
        Question=request.form['Question']
        con=sql.connect("hac_web.db")
        cur=con.cursor()
        cur.execute("update Quesdata set Question=? where UID=?",(Question,uid))
        con.commit()
        flash('User Updated','success')
        return redirect(url_for("index"))
    con=sql.connect("hac_web.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from Quesdata where UID=?",(uid,))
    data=cur.fetchone()
    return render_template("edit_user.html",datas=data)
    
@app.route("/delete_user/<string:uid>",methods=['GET'])
def delete_user(uid):
    con=sql.connect("hac_web.db")
    cur=con.cursor()
    cur.execute("delete from Quesdata where UID=?",(uid,))
    con.commit()
    flash('User Deleted','warning')
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    # app.secret_key = '09080'
    # app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    app.debug = True
    app.run()
