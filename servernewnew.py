# @Author: Yulong Qiao, Jianpu Ma
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import random

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
#Setting UP URI
DATABASEURI = "postgresql://yq2212:r49zw@104.196.175.120/postgres"
#engine creation
engine = create_engine(DATABASEURI)
#before request
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
  	g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass
###################### REAL CODING START##############################
######################################################################
######################################################################
######################################################################
######################################################################

# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#@another
@app.route('/another')
def another():
	return render_template("anotherfile.html")

@app.route('/return_to_main')
def return_to_main():
	return redirect ('/')
#unchanged

#determine if a query is safe, may be used later
def is_safe(q):
	safe=['DROP TABLE', 'DELETE TABLE','DROP INDEX','DROP DATABASE']
	for elem in safe:
		if elem in s.upper(): return False
	return True

#login, display all legit users
@app.route('/login')
def login():
	cursor = g.conn.execute("select lt.username from ltuser lt")
	usernames = []
	for result in cursor:
		usernames.append(result['username']) 
	cursor.close() #NO SQL INJECTION
	context = dict(data = usernames)
	return render_template("login.html", **context)

#register a new user, jumping from index just to jump to realadd
@app.route('/signup')
def signup():
	return render_template("signup.html")

#real user add process
#!!!!!!NOT IF SOME BLANK IS LEFT EMPTY
@app.route('/realadd',methods=['POST'])
def realadd():
	username=request.form['username']
	password=request.form['password']
	gender=request.form['gender']
	emailaddress=request.form['emailaddress']
	agestr=request.form['age']
	if agestr.isdigit(): age=int(request.form['age'])
	cursor=g.conn.execute("select userid, username from ltuser where username=%s",username)
	print "checking if this new user is legit"
	pivot=[]
	for elem in cursor:
		pivot.append(elem)
	cursor.close() # NO SQL INJECTION
	pivot1=[]
	cursor=g.conn.execute("select userid from ltuser where emailaddress=%s",emailaddress)
	for elem in cursor:
		pivot1.append(elem)
	cursor.close()
	if agestr.isdigit() and len(username)>0 and len(password)>0 and len(gender)>0 and len(emailaddress)>0 and len(agestr)>0 and not pivot and not pivot1 and (emailaddress.find('.com')>emailaddress.find('@')+1 or emailaddress.find('.edu')>emailaddress.find('@')+1) and age>0 and (gender=='F' or gender=='f' or gender=='M' or gender=='m'):
		print "New user is legit"
		newcursor=g.conn.execute("select 2*max(userid) from ltuser")
		for elem in newcursor:
			newuserid=elem[0]
		newcursor.close() # NO SQL INJECTION
		uid=newuserid
		uname=username
		#tmpmessage="Welcome Back, ", uname
		#message=str(tmpmessage)
		message=''
		engine.execute("insert into ltuser values (%s,%s,%s,%s,%s,%s)",newuserid,username,password,gender.upper(),emailaddress,age)
		print "Insert successful"
		context=dict(uid=uid, uname=uname, message=message)
		return render_template('dashboard.html', **context)
		#context=dict
	else:
		print "new user insert is not legit"
		fail_message="Illegal username of age or gender,please try again"
		context=dict(fail_message=fail_message)
		return render_template("signup.html",**context)
#user.islegit
@app.route('/validcheck',methods=['POST'])
def validcheck():
	ninput=request.form['username']
	pinput=request.form['password']
	cursor = g.conn.execute("select userid,username from ltuser where username=%s and password=%s",ninput,pinput)
	print "checking if legit"
	pivot=[]
	for elem in cursor:
		print "!!!!",elem
		pivot.append(elem)
	cursor.close() #NO SQL INJECTION
	#uid=pivot[0][0]
	#uname=pivot[0][1]
	if not pivot:
		signal="Either username or password is wrong, please try again"
		cursor = g.conn.execute("select lt.username from ltuser lt")
		usernames = []
		for result in cursor:
			usernames.append(result['username']) 
		cursor.close() #NO SQL INJECTION
		context=dict(signal=signal,data = usernames)
		return render_template("login.html",**context)
	else:
		uid=pivot[0][0]
		uname=pivot[0][1]
		print "Account is legit, proceed to login"
		print "Legit (userid,username)",(uid,uname)
		#tmpmessage="Welcome Back, ", uname
		message=''
		#message=str(tmpmessage)
		context=dict(uid=uid, uname=uname, message=message)
		#message="Welcome back, %s",pivot[0][1]
		#context=dict(username=pivot[0][1])
		return render_template("dashboard.html",**context)



#@dashboard
@app.route('/dashboard')
def dashboard():
	#username=request.
	print request.args
	#cursor=g.conn.execute("SELECT b.name FROM basketball_team_runned b")
	#names=[]
	#for result in cursor:
	#	names.append(result['name'])
	#cursor.close() # no SQL injection
	#context = dict(data = names)
	return render_template("dashboard.html", **context)

@app.route('/user_change_details')
def user_change_details():
	uid=int(request.args.get('uid',''))
	uname=str(request.args.get('uname',''))
	print "userid"+str(uid)+"is attempting to change its profile"
	userdata=[]
	cursor=g.conn.execute("select username,password,gender,emailaddress,age from ltuser where ltuser.userid = %s", uid)
	for elem in cursor:
		userdata.append(elem)
	msg=""
	context=dict(data=userdata,uid=uid, uname=uname,message=msg)
	return render_template("useractualchange.html",**context)

@app.route('/useractualchange',methods=['POST'])
def useractualchange():
	newusername=request.form['uname']
	newpsd=request.form['password']
	newgender=request.form['gender']
	newemailaddress=request.form['emailaddress']
	newage=request.form['age']
	username_existing=[]
	cursor=g.conn.execute("select username from ltuser")
	for elem in cursor:
		username_existing.append(elem[0])
	cursor.close()
	print username_existing
	emailaddress_existing=[]
	cursor=g.conn.execute("select emailaddress from ltuser")
	for elem in cursor:
		emailaddress_existing.append(elem[0])
	cursor.close()
	print emailaddress_existing
	# boolean needs to be modified, whatif user input some username other people are using?
	uid=int(request.form['uid'])
	usernamejudge=unicode(newusername)
	emailaddressjudge=unicode(newemailaddress)
	print "A judge to test if newusername and newemailaddress already exists in table", usernamejudge
	#for elem in username_existing:
		#if elem==usernamejudge:
		#	print "True"
		#print "False"
	if newage.isdigit() and usernamejudge not in username_existing and emailaddressjudge not in emailaddress_existing and (newemailaddress.find('.com')>newemailaddress.find('@')+1 or newemailaddress.find('.edu')>newemailaddress.find('@')+1) and len(newusername)>0 and len(newpsd)>0 and len(newgender)>0 and len(newemailaddress)>0 and len(newage)>0 and (newgender=='f' or newgender=='F' or newgender=='M' or newgender=='m') and int(newage)>0:
		print "ready to change profile"
		cursor=g.conn.execute("update ltuser set username=%s, password=%s, gender=%s, emailaddress=%s, age=%s where userid=%s",newusername,newpsd,newgender.upper(),newemailaddress,int(newage),uid)
		cursor.close()
		message="your profile has been updated"
		context=dict(uid=uid, uname=newusername, message=message)
		return render_template("dashboard.html",**context)
	else:
		msg="illegal info update, please try again"
		userdata1=[]
		cursor=g.conn.execute("select username,password,gender,emailaddress,age from ltuser where ltuser.userid = %s", uid)
		for elem in cursor:
			uname=elem[0]
			userdata1.append(elem)
		cursor.close()
		context=dict(data=userdata1,uid=uid, uname=uname,message=msg)
		return render_template("useractualchange.html",**context)

@app.route('/user_search_history')
def user_search_history():
	uid=int(request.args.get('uid',''))
	uname=str(request.args.get('uname',''))
	data=[]
	cursor=g.conn.execute("select lt.username, s.searchtime, b.name from ltuser lt, searches s, basketball_team_runned b where lt.userid=%s and s.userid=lt.userid and s.teamid=b.teamid",uid)
	for elem in cursor:
		data.append(elem)
	cursor.close()
	context=dict(data=data,uname=uname)
	return render_template("user_search_history.html",**context)


@app.route('/user_search_basketball_team')
def user_search_basketball_team():
	uid=int(request.args.get('uid',''))
	uname=str(request.args.get('uname',''))
	teamdata=[]
	cursor=g.conn.execute("select b.name from basketball_team_runned b")
	for elem in cursor:
		teamdata.append(elem[0])
	cursor.close()
	for elem in teamdata:
		elem=str(elem)
	print teamdata
	#teams=['Knicks','Laker','Celtics','Nets','Magic','Pacer','Rockets','Hawks','Heat','Oriental Sharks','Ducks','Real Madrid Baloncesto']
	return render_template("user_search_basketball_team.html",uid=uid,uname=uname,teamdata=teamdata)

@app.route('/teamsearched',methods=['GET'])
def teamsearched():
	#1. insert into search table - realized
	#2. display static infomation about team - realized
	#3. search for its player and position - realized
	#!!!!!!4. bugs exists, when query only show beform space
	#bug solved by adding "", obviously HTML look inside "" finding {{}}, can't believe that
	query=request.args.get('query')
	print "!!!!!!"
	print query
	uid=int(request.args.get('uid',''))
	uname=str(request.args.get('uname',''))
	# get teamid according to teamname
	teamidselect=[]
	cursor=g.conn.execute("select b.teamid from basketball_team_runned b where b.name=%s",query)
	for elem in cursor:
		teamidselect.append(elem[0])
	cursor.close()
	teamidselect=[int(elem) for elem in teamidselect]
	teamidone=teamidselect[0]
	#teamidone is the teamid
	#insert into searches table using current timestamp
	cursor=g.conn.execute("insert into searches values (%s,%s,current_timestamp)",uid,teamidone)
	cursor.close()
	#display data

	staticdata=[]
	championdata=[]
	positiondata=[]
	managerdata=[]
	playerdata=[]
	cursor=g.conn.execute("select b.coach, b.mascot, b.languageregion, b.location_city, b.name, b.found_date, b.web from basketball_team_runned b where b.name =%s",query)
	for elem in cursor:
		staticdata.append(elem)
	cursor.close()

	cursor=g.conn.execute("select m.name, m.age, m.dateofbirth, c.companyname, c.address, c. website, b.payment from manager_has m, company c, basketball_team_runned b where b.name=%s and b.managerid=m.managerid and m.companyid=c.companyid",query)
	for elem in cursor:
		managerdata.append(elem)
	cursor.close()

	cursor=g.conn.execute("select c.title, c.presenter from championship_achieved c, basketball_team_runned b where b.name=%s and b.teamid=c.teamid",query)
	for elem in cursor:
		championdata.append(elem)
	cursor.close()

	cursor=g.conn.execute("select p.playername from player p, position_composes_participates p1, basketball_team_runned b where b.name=%s and b.teamid=p1.teamid and p1.playerid=p.playerid",query)
	for elem in cursor:
		playerdata.append(elem[0])
	cursor.close()
	playerdata=[str(elem) for elem in playerdata]
	print playerdata

	cursor=g.conn.execute("select p1.positionname from position_composes_participates p1, basketball_team_runned b where b.name=%s and b.teamid=p1.teamid",query)
	for elem in cursor:
		positiondata.append(elem[0])
	cursor.close()
	positiondata=[str(elem) for elem in positiondata]
	print positiondata

	context=dict(staticdata=staticdata,managerdata=managerdata,uid=uid,tname=query, championdata=championdata,playerdata=playerdata, positiondata=positiondata)

	print "This is query"
	print query
	#print uid
	#print uname
	return render_template("teamsearched.html",**context)

@app.route('/playersearched',methods=['GET'])
def playersearched():
	query=request.args.get('query')
	uid=int(request.args.get('uid',''))
	tname=str(request.args.get('tname',''))
	print query
	print uid 
	print tname
	playerinfo=[]
	cursor=g.conn.execute("select p.playername, p.birthdate, p.nationality, p.height, p.weight, p.shootaccuracy, p1.positionname, p1.job from player p, position_composes_participates p1 where p.playername=%s and p.playerid=p1.playerid",query)
	for elem in cursor:
		playerinfo.append(elem)
	cursor.close()
	context=dict(playerinfo=playerinfo,playername=query)
	return render_template("playersearched.html",**context)


@app.route('/positionsearched',methods=['GET'])
def positionsearched():
	query=request.args.get('query')
	uid=int(request.args.get('uid',''))
	tname=str(request.args.get('tname',''))
	print query
	print uid 
	print tname
	positioninfo=[]
	cursor=g.conn.execute("select p.playername, p.birthdate, p.nationality, p.height, p.weight, p.shootaccuracy, p1.positionname, p1.job from player p, position_composes_participates p1, basketball_team_runned b where b.name= %s and b.teamid=p1.teamid and p1.positionname=%s and p.playerid=p1.playerid",tname, query)
	for elem in cursor:
		positioninfo.append(elem)
	cursor.close()
	context=dict(positioninfo=positioninfo, tname=tname,pos=query)
	return render_template("positionsearched.html",**context)

@app.route('/gamedisplay',methods=['GET'])
def gamedisplay():
	#it seems that real madrid and ducks does not have any game so basically you can not display
	#let's insert one entry
	#!!!form may need to be updated
	#view comment yes
	#add comment, modify comment
	#delete comment
	#HTML keyiqiantaoma?
	#
	uid=int(request.args.get('uid',''))
	tname=str(request.args.get('tname',''))
	print uid 
	print tname
	gamedata=[]
	commentdata=[]
	#idtank=[]
	cursor=g.conn.execute("select g.place, g.gametime, b.name, p.score, g.gameid from game g, basketball_team_runned b, plays p where b.name=%s and g.gameid=p.gameid and p.teamid=b.teamid",tname)
	for elem in cursor:
		print "!!!!"
		print elem
		gamedata.append(elem)
	cursor.close()
	#cursor=g.conn.execute("select g.place, g.gametime, g.gameid, b.name, p.score, c.commenttime, c.content, c.rate, c.commentid from game g, basketball_team_runned b, plays p, comment_written_about c where b.name=%s and g.gameid=p.gameid and p.teamid=b.teamid and c.userid=%s and c.gameid=g.gameid",tname,uid)
	cursor=g.conn.execute("select c.commenttime, c.content, c.rate, c.commentid, g.gameid from game g, basketball_team_runned b, plays p, comment_written_about c where b.name=%s and g.gameid=p.gameid and p.teamid=b.teamid and c.userid=%s and c.gameid=g.gameid",tname,uid)
	for elem in cursor:
		print elem
		commentdata.append(elem)
	cursor.close()
	msg=''
	context=dict(gamedata=gamedata,tname=tname,uid=uid,commentdata=commentdata)
	return render_template("gamedisplay.html",**context)
	
@app.route('/comment_more',methods=['GET'])
def comment_more():
	uid=int(request.args.get('uid',''))
	gameid=int(request.args.get('gameid',''))
	print uid
	print gameid
	print "userid"+str(uid)+"is attempting to add some comment"
	#userdata=[]
	#cursor=g.conn.execute("select username,password,gender,emailaddress,age from ltuser where ltuser.userid = %s", uid)
	#for elem in cursor:
	#	userdata.append(elem)
	#msg=""
	message=""
	context=dict(uid=uid, gameid=gameid,message=message)
	return render_template("comment_more_input.html",**context)

@app.route('/commentcheck',methods=['POST'])
def commentcheck():
	newcontent=request.form['content']
	print newcontent
	newrate=request.form['rate']
	print newrate
	uid=request.form['uid']
	gameid=request.form['gameid']
	#uid=int(request.args.get('uid',''))
	#gameid=int(request.args.get('gameid',''))
	print newcontent
	print "!!!!"
	print newrate
	if newrate.isdigit() and len(newcontent)>0 and len(newrate)>0 and (int(newrate)==1 or int(newrate)==2 or int(newrate)==3 or int(newrate)==4 or int(newrate)==5 or int(newrate)==6 or int(newrate)==7 or int(newrate)==8 or int(newrate)==9 or int(newrate)==10):
		# the design here is to go to dashboard, although some would say that go to last page actually is more wise
		msg="successfully added comment"
		maxid=[]
		#inserting into table comment_written_about
		cursor=g.conn.execute("select max(commentid) from comment_written_about")
		for elem in cursor:
			maxid.append(elem[0])
		cursor.close()
		newid=int(maxid[0])+1
		print "new commentid is ", newid
		cursor=g.conn.execute("insert into comment_written_about values(%s,%s,%s,current_timestamp,%s,%s)",uid,gameid,int(newid),newcontent,int(newrate))
		cursor.close()
		user=[]
		cursor=g.conn.execute("select username from ltuser where userid=%s",uid)
		for elem in cursor:
			user.append((elem))
		cursor.close()
		uname=str(user[0][0])
		context=dict(uid=uid, uname=uname, message=msg)
		#message="Welcome back, %s",pivot[0][1]
		#context=dict(username=pivot[0][1])
		return render_template("dashboard.html",**context)		
	else:
		message="something wrong, please correct your input and try again"
		context=dict(uid=uid, gameid=gameid,message=message)
		return render_template("comment_more_input.html",**context) 
	'''if not pivot:
		signal="Either username or password is wrong, please try again"
		cursor = g.conn.execute("select lt.username from ltuser lt")
		usernames = []
		for result in cursor:
			usernames.append(result['username']) 
		cursor.close() #NO SQL INJECTION
		context=dict(signal=signal,data = usernames)
		return render_template("login.html",**context)'''

#update a specific comment
@app.route('/comment_update',methods=['GET'])
def comment_update():
	uid=int(request.args.get('uid',''))
	commentid=int(request.args.get('commentid',''))
	print "userid"+str(uid)+"is updating commentid"+str(commentid)
	message=""
	context=dict(uid=uid, commentid=commentid,message=message)
	return render_template("comment_update.html",**context)

#check if comment update is legit and process that
@app.route('/update_comment_check',methods=['POST'])
def update_comment_check():
	newcontent=request.form['content']
	print newcontent
	newrate=request.form['rate']
	print newrate
	uid=request.form['uid']
	commentid=request.form['commentid']
	#uid=int(request.args.get('uid',''))
	#gameid=int(request.args.get('gameid',''))
	print newcontent
	print "!!!!"
	print newrate
	print "checking type"
	print newrate==str(newrate)
	if newrate.isdigit() and len(newcontent)>0 and len(newrate)>0 and (int(newrate)==1 or int(newrate)==2 or int(newrate)==3 or int(newrate)==4 or int(newrate)==5 or int(newrate)==6 or int(newrate)==7 or int(newrate)==8 or int(newrate)==9 or int(newrate)==10):
		# the design here is to go to dashboard, although some would say that go to last page actually is more wise
		msg="This comment has been updated"
		#updating into table comment_written_about
		cursor=g.conn.execute("update comment_written_about set content=%s, rate=%s where commentid=%s",newcontent,int(newrate),commentid)
		cursor.close()
		user=[]
		cursor=g.conn.execute("select username from ltuser where userid=%s",uid)
		for elem in cursor:
			user.append((elem))
		cursor.close()
		uname=str(user[0][0])
		context=dict(uid=uid, uname=uname, message=msg)
		#message="Welcome back, %s",pivot[0][1]
		#context=dict(username=pivot[0][1])
		return render_template("dashboard.html",**context)		
	else:
		message="something wrong, please correct your input and try again"
		context=dict(uid=uid, commentid=commentid,message=message)
		return render_template("comment_update.html",**context)


# directly delete one comment
@app.route('/comment_delete',methods=['GET'])
def comment_delete():
	uid=int(request.args.get('uid',''))
	commentid=int(request.args.get('commentid',''))
	print "userid"+str(uid)+"is deleting commentid"+str(commentid)
	msg="This comment has been deleted"
	cursor=g.conn.execute("delete from comment_written_about where commentid=%s",commentid)
	cursor.close()
	user=[]
	cursor=g.conn.execute("select username from ltuser where userid=%s",uid)
	for elem in cursor:
		user.append((elem))
	cursor.close()
	uname=str(user[0][0])
	context=dict(uid=uid, uname=uname, message=msg)
	return render_template("dashboard.html",**context) 

@app.route('/user_view_recommendations',methods=['GET'])
def user_view_recommendations():
	uid=int(request.args.get('uid',''))
	uname=str(request.args.get('uname',''))
	print "the user "+ uname+" is requesting recommendation"
	print uid
	print uname
	#fetch his rate
	ratedata=[]
	teamdata=[]
	cursor=g.conn.execute("select c.rate, b.name from ltuser lt, comment_written_about c, basketball_team_runned b, plays p, game g where lt.userid=%s and lt.userid=c.userid and c.gameid=g.gameid and g.gameid=p.gameid and p.teamid=b.teamid", uid)
	for elem in cursor:
		ratedata.append(float(elem[0]))
		teamdata.append(str(elem[1]))
	cursor.close()

	#raterank is the basis for tracking user's comment behavior
	raterank={}
	print "This user has comment# ", len(ratedata)
	print "On team#",len(teamdata)
	for i in range(len(teamdata)):
		#raterank[teamdata[i]]=ratedata[i]
		if teamdata[i] not in raterank:
			raterank[teamdata[i]]=[ratedata[i]]
		else:
			raterank[teamdata[i]].append(ratedata[i])
	for elem in raterank:
		raterank[elem]=sum(raterank[elem])/len(raterank[elem])
	print ratedata
	print teamdata
	print raterank
	team_highest=sorted(raterank.items(), key=lambda x: x[1])[-1][0]
	highest_rate=raterank[team_highest]
	team_lowest=sorted(raterank.items(), key=lambda x: x[1])[0][0]
	lowest_rate=raterank[team_lowest]
	print "highest rate goes to " + team_highest + " the rate is "+ str(highest_rate)
	print "lowest rate goes to "+team_lowest+" the rate is "+str(lowest_rate)
	#searchrank is the basis for tracking user's search behavior
	teamsearched=[]
	searchdata=[]
	searchrank={}
	cursor=g.conn.execute("select b.name, count(*) from ltuser lt, searches s, basketball_team_runned b where lt.userid=%s and s.userid=lt.userid and s.teamid=b.teamid group by b.name",uid)
	for elem in cursor:
		searchdata.append(int(elem[1]))
		teamsearched.append(str(elem[0]))
	cursor.close()
	for i in range(len(teamsearched)):
		if teamsearched[i] not in searchrank:
			searchrank[teamsearched[i]]=searchdata[i]
		#else:
		#	searchrank[teamsearched[i]].append(searchdata[i])
	print searchrank
	team_search_highest=sorted(searchrank.items(), key=lambda x: x[1])[-1][0]
	highest_search_times=searchrank[team_search_highest]

	team_search_lowest=sorted(searchrank.items(), key=lambda x: x[1])[0][0]
	lowest_search_times=searchrank[team_search_lowest]
	print "highest search times goes to " + team_search_highest + " the times is "+ str(highest_search_times)
	print "lowest search times goes to "+team_search_lowest+" the times is "+str(lowest_search_times)
	#userrank is the basis for user's profile: age and gender
	cursor=g.conn.execute("select lt.age, lt.gender from ltuser lt where lt.userid=%s",uid)
	for elem in cursor:
		 agerank=int(elem[0])
		 genderrank=str(elem[1])
	cursor.close()
	print agerank,genderrank	

	#the algorithm to determine which team to recommend
	#based on the balance of the team you rated highest, "enemy-recommendation":the team you rated lowest so you are its enemy team's fan,your search times for a team and your age and gender
     #the priority is massive searchtimes > highest rate = enemy recommendation> user profile

    #create enemy table(dict)
	enemy={}
	enemy['Laker']='Celtics'
	enemy['Celtics']='Laker'
	enemy['Hawks']='Pacer'
	enemy['Pacer']='Hawks'

	#begin recommendation algorithm
	#little bit of P2P feeling (rarest first,fast connect to fast)
	if highest_search_times>=30: # massive search times threshold=30
		team_recommend=team_search_highest
	elif highest_rate>=7:
		if lowest_rate>=4:
			team_recommend=team_highest
		elif team_lowest in enemy:
			team_recommend=enemy[team_lowest]
		else: team_recommend=team_highest
	elif highest_rate>5 and lowest_rate>3:
		if agerank<16 and genderank.upper()=='M': team_recommend=='Heat'
		elif agerank<16 and genderank.upper()=='F': team_recommend=='Ducks'
	else: team_recommend=team_highest

	print "The team I'm recommending is ", team_recommend
	context=dict(uid=uid, tname=team_recommend)
	return render_template("user_view_recommendations.html",**context)
	'''
	ratedata=[]
	counterdata=[]
	
	cursor=g.conn.execute("select c.rate, r.teamid, r.name  from ltuser lt, Comment_Written_About c, Plays p, Basketball_Team_Runned r   where lt.userid=%s and lt.userid=c.userid and p.gameid=c.gameid and p.teamid=r.teamid and c.rate<5 group by c.rate, r.teamid, r.name order by c.rate asc",uid)
	for elem in cursor:
		ratedata.append(elem)
	cursor.close()

	for elem in ratedata:
		elem=str(elem)
	print ratedata

	counterdata={6:'Heat',15:'Celtics',13:'Laker',9:'Knicks',20:'Pacer',34:'Magic',30:'Hawks',8:'Rockets',25:'Celtics',781:'Ducks',801:'Oriental Sharks',605:'Real Madrid Baloncesto'}
	randnum=random.randint(0,2)  # chose a random one in games user gave low rate
	counter=counterdata[(ratedata[randnum][1])]  #counterteam's name which we recommend to user
	print ratedata[randnum][1]
	print counter'''

	#if(teamid==6):  #knicks -> Heat 25
	#if(teamid==15) #Laker-> Boston 13
	#if (teamid==13) #Boston->Laker 15
	#if (teamid==9) #Nets-> Knicks 6
	#if (teamid==20) #Magic-> Pacer 34
	#if (teamid==34) #pacer -> Magic 20
	#if (teamid==30) #rockets->atlanta 8
	#if (teamid==8)  #atlanta ->rockets 25
	#if (teamid==25) #heats->boston 13
	#if (teamid==781) #shanghai->beijing 801
	#if (teamid==801) #beijing->shanghai 781
	#if (teamid==605) #madrid->madrid 605
	
	#return render_template("user_view_recommendations.html",uid=uid,uname=uname,ratedata=ratedata,counter=counter,randnum=randnum)'''














 #@errors
 #@app.route('/error')
 #def showerror():
 #	return render_template("error.html")

 #@search team
 #@app.route('/searchteam',methods=['GET'])
 #def searchteam():
 #	query=request.args.get('query')
 #	print "the team queried is"
 #	print query
 #	cursor=g.conn.execute("SELECT * FROM  basketball_team_runned b WHERE b.name = %s", query)
 #	rows=cursor.fetchall()
 #	cursor.close() #no SQL injection
 #	return render_template('teaminfo.html',team_data=rows)





# Example of adding new data to the database
#@app.route('/login')
#def login():
#   abort(401)
#    this_is_never_executed()
################################ DO NOT MODIFY###########################################################################
#########################################################################################################################
#########################################################################################################################
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()