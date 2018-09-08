from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify, Markup
from flask_pymongo import PyMongo
from pymongo import MongoClient
import datetime
import threading
from plotly.offline import plot
from plotly.graph_objs import Scatter


app = Flask(__name__)
app.config['SECRET_KEY'] = '8424276c875d016a'
client = MongoClient("mongodb://********************************")
db = client['online_attendence']

time = datetime.date.today()
tname = ''
sname = ''
d=[]

@app.route('/', methods=['POST','GET'])
def this():
	if request.method == 'POST':
		if request.form['choice'] == 'teacher':
			collection = db.teacher
			collection.insert_one({'username':request.form['username'], 'password':request.form['password']})
		elif request.form['choice'] == 'student':
			collection = db.student
			collection.insert_one({'username':request.form['username'], 'password':request.form['password']})
		return redirect(url_for('login'))

	return render_template('signup.html')


@app.route('/login/', methods=['POST','GET'])
def login():
	if request.method == 'POST':
		if request.form['choice'] == 'student':
			data = db.student
			find = data.find_one({'username': request.form['username']})
			if find:
				authu = find['username']
				authp = find['password']
				if authu == request.form['username'] and authp == request.form['password']:
					session['username'] = request.form['username']
					return redirect(url_for('student', sname=authu))
				else:
					msg = 'Invalid Credentials'
					return render_template('login.html', msg=msg)
			else:
				msg = 'Invalid Credentials'
				return render_template('login.html', msg=msg)

		elif request.form['choice'] == 'teacher':
			data = db.teacher
			find = data.find_one({'username': request.form['username']})
			if find:
				authu = find['username']
				authp = find['password']
				if authu == request.form['username'] and authp == request.form['password']:
					session['username'] = request.form['username']
					return redirect(url_for('index', tname=authu))
				else:
					msg = 'Invalid Credentials'
					return render_template('login.html', msg=msg)
			else: 
				msg = 'Invalid Credentials'
				return render_template('login.html', msg=msg)
	return render_template('login.html')

@app.route('/<tname>/', methods=['POST','GET'])
def index(tname):
	if session['username']:
		user = db[tname]
		search = user.find()
		msg = ''
		if request.method == 'POST':
			for document in search:
				if request.form[str(document['_id'])] == 'Present':
					find = user.find_one({'student':document['student']})
					find['present'] = 'Present'
					user.save(find)
				elif request.form[str(document['_id'])] == 'Absent':
					find = user.find_one({'student':document['student']})
					find['present'] = 'Absent'
					user.save(find)

			msg = 'Updated Successfully'
			return render_template('index.html', msg=msg, search=search, tname=tname)

		return render_template('index.html' , search=search, tname=tname)

	return redirect(url_for('login'))

	
@app.route('/<tname>/add/', methods=['POST','GET'])
def add(tname):
	if session['username']:
		data = db[tname]
		if request.method == 'POST':
			data.insert_one({'student':request.form['add'], 'present':'Absent', 'date': str(time)})
			return redirect(url_for('index', tname=tname))

		return render_template('add.html')

	return redirect(url_for('login'))

	
@app.route('/student/<sname>/', methods=['POST','GET'])
def student(sname):
	if session['username']:
		l=[]
		collection = db.teacher
		attend = 0
		total = 0
		search = collection.find()
		for document in search:
			col = db[document['username']]
			find = col.find()
			percent =[]
			dates = []
			for items in find:
				if items['student'] == sname:
					l.append(items)
					total += 1
					if items['present'] == 'Present':
						attend += 1
						per = (attend/total)*100
						percent.append(per)
					dates.append(items['date'])
		p = plot([Scatter(x=dates,y=percent)],output_type="div")
		return render_template('student.html' ,l=l, dates=dates, attend=attend, total=total, percent=percent,div_placeholder=Markup(p))

	return redirect(url_for('login'))

	
@app.route('/<tname>/date/', methods=['POST', 'GET'])
def date(tname):
	if session['username']:
		new = db[tname]
		search = new.find()
		if request.method == 'POST':
			for document in search:
				if request.form['date'] == document['date']:
					d.append(document)
			return redirect(url_for('h', tname=tname))

		return render_template('date.html', search=search, d=d, tname=tname)

	return redirect(url_for('login'))

@app.route('/<tname>/student', methods=['POST','GET'])
def h(tname):
	user = db[tname]
	if request.method == 'POST':
		search = user.find()
		var = d[0]['date']
		for document in search:
			if document['date'] == var:
				if request.form[str(document['_id'])] == 'Present':
					find = user.find_one({'student':document['student']})
					find['present'] = 'Present'
					user.save(find)
				elif request.form[str(document['_id'])] == 'Absent':
					find = user.find_one({'student':document['student']})
					find['present'] = 'Absent'
					user.save(find)

	return render_template('update.html', d=d)

@app.route('/logout/')
def logout():
	session['username'] = None
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)