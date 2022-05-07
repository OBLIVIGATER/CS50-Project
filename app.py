import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, redirect,jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required, lookup, usd
import uuid as uuid

app = Flask(__name__)

db = SQL("sqlite:///nba.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
@login_required
def index():
    gameid = session.get("gameid")
    return render_template("index.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        #validate name
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username").upper()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not firstname:
            error= "First Name not entered"
            return render_template("register.html",error=error)
        if not lastname:
            error= "Last Name not entered"
            return render_template("register.html",error=error)
        if not username:
            error = "Username not entered"
            return render_template("register.html",error=error)
        elif not password:
            error = "Password not entered"
            return render_template("register.html",error=error)
        elif not confirmation:
            error = "Password confirmation not entered"
            return render_template("register.html",error=error)

        elif password != confirmation:
             error = "Passwords do not match"
             return render_template("register.html",error=error)
        #hash password
        #add username and hashed password into sql db
        #check if username is in the database already

        else:
            try:
                hash = generate_password_hash(password)
                db.execute("INSERT INTO users (firstname,lastname,username,hash) VALUES(?,?,?,?);",firstname,lastname,username,hash)
                return redirect("/")
            except:
                error = "Username already exists, try another one!"
                return render_template("register.html",error=error)

    #if get
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Input a Username"
            return render_template("login.html",error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Input a Password"
            return render_template("login.html",error=error)

        # Query database for username
        username= request.form.get("username").upper()
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = "Username or Password not found. Please try again."
            return render_template("login.html",error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/addgames", methods=["GET", "POST"])
def addgames():
    if request.method == "POST":

        user_id= session["user_id"]

        team1 = request.form.get("team1")
        score1 = request.form.get("score1")
        team2 = request.form.get("team2")
        score2 = request.form.get("score2")
        date = request.form.get("date")
        gs= request.form.get("gs")
        mp = request.form.get("mp")
        fg = request.form.get("fg")
        fga = request.form.get("fga")
        threep= request.form.get("threep")
        threepa = request.form.get("threepa")
        twop= request.form.get("twop")
        twopa = request.form.get("twopa")
        ft= request.form.get("ft")
        fta= request.form.get("fta")
        orb= request.form.get("orb")
        drb = request.form.get("drb")
        ast= request.form.get("ast")
        stl= request.form.get("stl")
        blk= request.form.get("blk")
        tov= request.form.get("tov")
        pf = request.form.get("pf")



        if not team1 or not score1 or not team2 or not score2 or not date or not gs or not mp or not threep or not threepa or not twop or not twopa or not ft or not fta or not orb or not drb or not ast or not stl or not blk or not tov or not pf:
            error = "All fields required."
            return render_template("addgames.html",error=error,team1=team1,
            score1=score1, team2=team2, score2=score2, date=date, gs=gs, mp=mp,
            threep=threep,threepa=threepa,twop=twop,twopa=twopa,ft=ft,fta=fta,
            orb=orb,drb=drb,ast=ast,stl=stl,blk=blk,tov=tov,pf=pf)

        if  int(score1)<0 or int(score2)<0 or int(mp)<0 or int(threep)<0 or int(threepa)<0 or int(twop)<0 or int(twopa)<0 or int(ft)<0 or int(fta)<0 or int(orb)<0 or int(drb)<0 or int(ast)<0 or int(stl)<0 or int(blk)<0 or  int(tov)<0 or int(pf)<0:
            error = "No negative numbers."
            return render_template("addgames.html",error=error,team1=team1,
            score1=score1, team2=team2, score2=score2, date=date, gs=gs, mp=mp,
            threep=threep,threepa=threepa,twop=twop,twopa=twopa,ft=ft,fta=fta,
            orb=orb,drb=drb,ast=ast,stl=stl,blk=blk,tov=tov,pf=pf)

        if  int(threep)>int(threepa) or int(twop)>int(twopa) or int(ft)>int(fta):
            error= "Stats are not possible. Try again."
            return render_template("addgames.html",error=error)

        trb= int(drb)+int(orb)
        if int(threep) == 0 or int(threepa) == 0:
            THREEPPercent=0
        else:
            THREEPPercent= round((int(threep)/int(threepa))*100,2)
        if int(twop) == 0 or int(twopa) == 0:
            TWOPPercent=0
        else:
            TWOPPercent= round((int(twop)/int(twopa))*100,2)

        pts=(int(threep)*3)+(int(twop)*2)+int(ft)
        fga=int(threepa)+int(twopa)
        fg=int(threep)+int(twop)
        if int(fg) == 0 or int(fga) == 0:
            THREEPPercent=0
        else:
            FGPercent= round((int(fg)/int(fga))*100,2)
        if int(ft) == 0 or int(fta) == 0:
            FTPercent=0
        else:
            FTPercent= round((int(ft)/int(fta))*100,2)
        if int(fga) == 0:
            eFGPercent = 0
        else:
            eFGPercent=  round((int(fg) + 0.5 * int(threep))/int(fga),2)


        try: #insert first input data into user total stats as you cant update without any input
            db.execute("INSERT INTO usertotalstats(user_id,G,GS,MP,FG,FGA,THREEP,THREEPA,TWOP,TWOPA,FT,FTA,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS) VALUES(?,1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",user_id,gs,mp,fg,fga,threep,threepa,twop,twopa,ft,fta,orb,drb,trb,ast,stl,blk,tov,pf,pts)
            db.execute("INSERT INTO userpergamestats(pergame_user_id,G,GS,MP,FG,FGA,FGPercent,THREEP,THREEPA,THREEPPERCENT,TWOP,TWOPA,TWOPPERCENT,eFGPERCENT,FT,FTA,FTPercent,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS) VALUES(?,1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",user_id,gs,mp,fg,fga,FGPercent,threep,threepa,THREEPPercent,twop,twopa,TWOPPercent,eFGPercent,ft,fta,FTPercent,orb,drb,trb,ast,stl,blk,tov,pf,pts)

        except:# if its not the first data the try will get rejected since the user_id colulmn is unique. then just update and gamestats will be as normal
            db.execute("INSERT INTO gamestats (user_id,team1,score1,team2,score2,date,GS,MP,FG,FGA,FGPercent,THREEP,THREEPA,THREEPPercent,TWOP,TWOPA,TWOPPercent,eFGPercent,FT,FTA,FTPercent,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",user_id,team1,score1,team2,score2,date,gs,mp,fg,fga,FGPercent,threep,threepa,THREEPPercent,twop,twopa,TWOPPercent,eFGPercent,ft,fta,FTPercent,orb,drb,trb,ast,stl,blk,tov,pf,pts)
            db.execute("UPDATE usertotalstats SET G = (SELECT COUNT(id) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET GS = (SELECT SUM(GS) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET MP = (SELECT SUM(MP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET FG = (SELECT SUM(FG) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET FGA = (SELECT SUM(FGA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET THREEP = (SELECT SUM(THREEP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET THREEPA = (SELECT SUM(THREEPA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET TWOP = (SELECT SUM(TWOP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET TWOPA = (SELECT SUM(TWOPA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET FT = (SELECT SUM(FT) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET FTA = (SELECT SUM(FTA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET ORB = (SELECT SUM(ORB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET DRB = (SELECT SUM(DRB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET AST = (SELECT SUM(AST) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET STL = (SELECT SUM(STL) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET BLK = (SELECT SUM(BLK) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET TOV = (SELECT SUM(TOV) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET PF = (SELECT SUM(PF) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET PTS = (SELECT SUM(PTS) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
            db.execute("UPDATE usertotalstats SET TRB = (SELECT SUM(TRB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)

            db.execute("UPDATE userpergamestats SET G = (SELECT COUNT(id) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET GS = (SELECT SUM(GS) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET MP = (SELECT AVG(MP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FG = (SELECT AVG(FG) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FGA = (SELECT AVG(FGA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FGPercent = (SELECT AVG(FGPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET THREEP = (SELECT AVG(THREEP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET THREEPA = (SELECT AVG(THREEPA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET THREEPPercent = (SELECT AVG(THREEPPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET TWOP = (SELECT AVG(TWOP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET TWOPA = (SELECT AVG(TWOPA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET TWOPPercent = (SELECT AVG(TWOPPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FT = (SELECT AVG(FT) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FTA = (SELECT AVG(FTA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET FTPercent = (SELECT AVG(FTPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET ORB = (SELECT AVG(ORB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET DRB = (SELECT AVG(DRB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET AST = (SELECT AVG(AST) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET STL = (SELECT AVG(STL) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET BLK = (SELECT AVG(BLK) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET TOV = (SELECT AVG(TOV) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET PF = (SELECT AVG(PF) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET PTS = (SELECT AVG(PTS) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
            db.execute("UPDATE userpergamestats SET TRB = (SELECT AVG(TRB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)



        else:#if its the first input of games proceed as normal and update it into gamestats aswell
            db.execute("INSERT INTO gamestats (user_id,team1,score1,team2,score2,date,GS,MP,FG,FGA,FGPercent,THREEP,THREEPA,THREEPPercent,TWOP,TWOPA,TWOPPercent,eFGPercent,FT,FTA,FTPercent,ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
            ,user_id,team1,score1,team2,score2,date,gs,mp,fg,fga,FGPercent,threep,threepa,THREEPPercent,twop,twopa,TWOPPercent,eFGPercent,ft,fta,FTPercent,orb,drb,trb,ast,stl,blk,tov,pf,pts)

        return redirect("/")

    else:
        return render_template("addgames.html")


@app.route("/comparestats")
def comparestats():
    return render_template("comparestats.html")

@app.route("/comparenba", methods=["GET", "POST"])
def comparenba():
    if request.method == "POST":
        player_name=request.form.get("players")

        user_id= session["user_id"]
        stats = db.execute("SELECT G,GS,ROUND(MP,1),ROUND(FG,1),ROUND(FGA,1),ROUND(FGPercent,1),ROUND(THREEP,1),ROUND(THREEPA,1),ROUND(THREEPPercent,1),ROUND(TWOP,1),ROUND(TWOPA,1),ROUND(TWOPPercent,1),ROUND(eFGPercent,1),ROUND(FT,1),ROUND(FTA,1),ROUND(FTPercent,1),ROUND(ORB,1),ROUND(DRB,1),ROUND(TRB,1),ROUND(AST,1),ROUND(STL,1),ROUND(BLK,1),ROUND(TOV,1),ROUND(PF,1),ROUND(PTS,1) FROM userpergamestats WHERE pergame_user_id = ?;",user_id)
        username = db.execute("SELECT username FROM users WHERE id = ?",user_id)[0]["username"]
        try:
            players_id = db.execute("SELECT id FROM players WHERE name LIKE ?",player_name)[0]["id"]
            name= db.execute("SELECT Name FROM players WHERE id = ?",players_id)[0]["Name"]
        except:
            error="Player not found try again."
            return render_template("comparenba.html", error=error,username=username,stats=stats)

        player_stats = db.execute("SELECT G,GS,MP,FG,FGA,ROUND(FGPercent*100,1),THREEP,THREEPA,ROUND(THREEPPercent*100,1),TWOP,TWOPA,ROUND(TWOPPercent*100,1),ROUND(eFGPercent*100,1),FT,FTA,ROUND(FTPercent*100,1),ORB,DRB,TRB,AST,STL,BLK,TOV,PF,PTS FROM pergamestats WHERE Players_id = ?",players_id)
        return render_template("comparenba.html",username=username,stats=stats, name=name, player_stats=player_stats)


    else:
        user_id= session["user_id"]
        stats = db.execute("SELECT G,GS,ROUND(MP,1),ROUND(FG,1),ROUND(FGA,1),ROUND(FGPercent,1),ROUND(THREEP,1),ROUND(THREEPA,1),ROUND(THREEPPercent,1),ROUND(TWOP,1),ROUND(TWOPA,1),ROUND(TWOPPercent,1),ROUND(eFGPercent,1),ROUND(FT,1),ROUND(FTA,1),ROUND(FTPercent,1),ROUND(ORB,1),ROUND(DRB,1),ROUND(TRB,1),ROUND(AST,1),ROUND(STL,1),ROUND(BLK,1),ROUND(TOV,1),ROUND(PF,1),ROUND(PTS,1) FROM userpergamestats WHERE pergame_user_id = ?;",user_id)
        username = db.execute("SELECT username FROM users WHERE id LIKE ?",user_id)[0]["username"]
        return render_template("comparenba.html",username=username,stats=stats)

@app.route("/compareuser", methods=["GET", "POST"])
def compareuser():
    if request.method == "POST":
        player_name=request.form.get("username")
        user_id= session["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = ?",user_id)[0]["username"]
        stats = db.execute("SELECT G,GS,ROUND(MP,1),ROUND(FG,1),ROUND(FGA,1),ROUND(FGPercent,1),ROUND(THREEP,1),ROUND(THREEPA,1),ROUND(THREEPPercent,1),ROUND(TWOP,1),ROUND(TWOPA,1),ROUND(TWOPPercent,1),ROUND(eFGPercent,1),ROUND(FT,1),ROUND(FTA,1),ROUND(FTPercent,1),ROUND(ORB,1),ROUND(DRB,1),ROUND(TRB,1),ROUND(AST,1),ROUND(STL,1),ROUND(BLK,1),ROUND(TOV,1),ROUND(PF,1),ROUND(PTS,1) FROM userpergamestats WHERE pergame_user_id = ?;",user_id)
        try:
            players_id = db.execute("SELECT id FROM users WHERE username LIKE ?",player_name)[0]["id"]
            name = db.execute("SELECT username FROM users WHERE id = ?",players_id)[0]["username"]
        except:
            error="Player not found try again."
            return render_template("comparenba.html", error=error,username=username,stats=stats)
        player_stats= db.execute("SELECT G,GS,ROUND(MP,1),ROUND(FG,1),ROUND(FGA,1),ROUND(FGPercent,1),ROUND(THREEP,1),ROUND(THREEPA,1),ROUND(THREEPPercent,1),ROUND(TWOP,1),ROUND(TWOPA,1),ROUND(TWOPPercent,1),ROUND(eFGPercent,1),ROUND(FT,1),ROUND(FTA,1),ROUND(FTPercent,1),ROUND(ORB,1),ROUND(DRB,1),ROUND(TRB,1),ROUND(AST,1),ROUND(STL,1),ROUND(BLK,1),ROUND(TOV,1),ROUND(PF,1),ROUND(PTS,1) FROM userpergamestats WHERE pergame_user_id = ?;",players_id)
        return render_template("compareuser.html",username=username,stats=stats,name=name,player_stats=player_stats)

    else:
        user_id= session["user_id"]
        stats = db.execute("SELECT G,GS,ROUND(MP,1),ROUND(FG,1),ROUND(FGA,1),ROUND(FGPercent,1),ROUND(THREEP,1),ROUND(THREEPA,1),ROUND(THREEPPercent,1),ROUND(TWOP,1),ROUND(TWOPA,1),ROUND(TWOPPercent,1),ROUND(eFGPercent,1),ROUND(FT,1),ROUND(FTA,1),ROUND(FTPercent,1),ROUND(ORB,1),ROUND(DRB,1),ROUND(TRB,1),ROUND(AST,1),ROUND(STL,1),ROUND(BLK,1),ROUND(TOV,1),ROUND(PF,1),ROUND(PTS,1) FROM userpergamestats WHERE pergame_user_id = ?;",user_id)
        username = db.execute("SELECT username FROM users WHERE id = ?",user_id)[0]["username"]
        return render_template("compareuser.html",username=username,stats=stats)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        user_id= session["user_id"]
        post = request.form.get("text")
        db.execute("INSERT INTO posts (text,posts_user_id) VALUES(?,?)",post,user_id)
        return redirect("/profile")


    else:
        user_id= session["user_id"]
        info = db.execute("SELECT * FROM users WHERE id = ?",user_id)
        profile_pic=db.execute("SELECT picture FROM users WHERE id = ?",user_id)[0]["picture"]
        stats= db.execute("SELECT ROUND(PTS,1), ROUND(AST,1), ROUND(TRB,1) FROM userpergamestats WHERE pergame_user_id = ?", user_id)
        games = db.execute("SELECT * FROM gamestats WHERE user_id =? ORDER BY date DESC LIMIT 5",user_id)
        posts = db.execute("SELECT * FROM posts WHERE posts_user_id = ? ORDER BY time DESC",user_id)
        return render_template("profile.html",info=info,profile_pic=profile_pic,stats=stats,games=games,posts=posts)

@app.route("/settings")
def settings():
        return render_template("settings.html")



@app.route("/information", methods=["GET", "POST"])
def information():
    if request.method == "POST":

        age = request.form.get("age")
        team = request.form.get("team")
        position = request.form.get("position")
        user_id= session["user_id"]
        file = request.files['file']
        if not age or not team:
            error="Age or Team not found try again."
            user_id= session["user_id"]
            position = db.execute("SELECT position from users WHERE id =?",user_id)[0]["position"]
            info =db.execute("SELECT team,age FROM users WHERE id = ?",user_id)
            return render_template("information.html",info=info,position=position,error=error)

        if not file:
            ##pic_name=db.execute("SELECT picture FROM users WHERE id = ?", user_id)[0]["picture"]
            db.execute("UPDATE users SET age = ? , team = ? , position = ? WHERE id=?",age,team,position,user_id)
        else:
            filename = secure_filename(file.filename)

            pic_name = str(uuid.uuid1()) + "_" + filename
            saver = request.files['file']
            file=pic_name
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], file))
            db.execute("UPDATE users SET age = ? , team = ? , position = ?, picture= ? WHERE id=?",age,team,position,pic_name, user_id)



        return redirect("/settings")
    else:
        user_id= session["user_id"]
        position = db.execute("SELECT position from users WHERE id =?",user_id)[0]["position"]
        info =db.execute("SELECT team,age FROM users WHERE id = ?",user_id)
        return render_template("information.html",info=info,position=position)

@app.route("/updategamestats", methods=["GET", "POST"])
def updategamestats():
    if request.method == "POST":
        return render_template("changestats.html")

    else:
        user_id = session["user_id"]
        gameinfo= db.execute("SELECT * FROM gamestats WHERE user_id =? ORDER BY date DESC",user_id)
        return render_template("updategamestats.html",gameinfo=gameinfo)

@app.route("/changestats", methods=["GET", "POST"])
def changestats():
    if request.method == "POST":
        gameid= request.args.get('gameid')
        user_id= session["user_id"]
        team1 = request.form.get("team1")
        score1 = request.form.get("score1")
        team2 = request.form.get("team2")
        score2 = request.form.get("score2")
        date = request.form.get("date")
        gs= request.form.get("gs")
        mp = request.form.get("mp")
        fg = request.form.get("fg")
        fga = request.form.get("fga")
        threep= request.form.get("threep")
        threepa = request.form.get("threepa")
        twop= request.form.get("twop")
        twopa = request.form.get("twopa")
        ft= request.form.get("ft")
        fta= request.form.get("fta")
        orb= request.form.get("orb")
        drb = request.form.get("drb")
        ast= request.form.get("ast")
        stl= request.form.get("stl")
        blk= request.form.get("blk")
        tov= request.form.get("tov")
        pf = request.form.get("pf")
        pts = request.form.get("pts")

        if not team1 or not score1 or not team2 or not score2 or not date or not gs or not mp or not fg or not fga or not threep or not threepa or not twop or not twopa or not ft or not fta or not orb or not drb or not ast or not stl or not blk or not tov or not pf or not pts:
            error = "All fields required."
            gameid = request.args.get('gameid')
            gamestart= db.execute("SELECT GS FROM gamestats WHERE id = ?",gameid)[0]["GS"]
            gameinfo= db.execute("SELECT * FROM gamestats WHERE id = ?",gameid)
            return render_template("changestats.html",error=error,gameinfo=gameinfo,gameid=gameid,gamestart=gamestart)

        if  int(score1)<0 or int(score2)<0 or int(mp)<0 or int(fg)<0 or int(fga)<0 or int(threep)<0 or int(threepa)<0 or int(twop)<0 or int(twopa)<0 or int(ft)<0 or int(fta)<0 or int(orb)<0 or int(drb)<0 or int(ast)<0 or int(stl)<0 or int(blk)<0 or  int(tov)<0 or int(pf)<0 or int(pts)<0:
            error = "No negative numbers."
            gameid = request.args.get('gameid')
            gamestart= db.execute("SELECT GS FROM gamestats WHERE id = ?",gameid)[0]["GS"]
            gameinfo= db.execute("SELECT * FROM gamestats WHERE id = ?",gameid)
            return render_template("changestats.html",error=error,gameinfo=gameinfo,gameid=gameid,gamestart=gamestart)

        if int(fg)>int(fga) or int(threep)>int(threepa) or int(twop)>int(twopa):
            error= "Stats are not possible. Try again."
            gameid = request.args.get('gameid')
            gamestart= db.execute("SELECT GS FROM gamestats WHERE id = ?",gameid)[0]["GS"]
            gameinfo= db.execute("SELECT * FROM gamestats WHERE id = ?",gameid)
            return render_template("changestats.html",error=error,gameinfo=gameinfo,gameid=gameid,gamestart=gamestart)



        trb= int(drb)+int(orb)
        FGPercent= round((int(fg)/int(fga))*100,2)
        FTPercent= round((int(ft)/int(fta))*100,2)
        THREEPPercent= round((int(threep)/int(threepa))*100,2)
        TWOPPercent= round((int(twop)/int(twopa))*100,2)
        eFGPercent=  round((int(fg) + 0.5 * int(threep))/int(fga),2)





        if 'updategame' in request.form:

            db.execute("UPDATE gamestats SET team1 = ? WHERE id = ?",team1,gameid)
            db.execute("UPDATE gamestats SET score1 = ? WHERE id = ?",score1,gameid)
            db.execute("UPDATE gamestats SET team2 = ? WHERE id = ?",team2,gameid)
            db.execute("UPDATE gamestats SET score2 = ? WHERE id = ?",score2,gameid)
            db.execute("UPDATE gamestats SET date = ? WHERE id = ?",date,gameid)
            db.execute("UPDATE gamestats SET gs = ? WHERE id = ?",gs,gameid)
            db.execute("UPDATE gamestats SET mp = ? WHERE id = ?",mp,gameid)
            db.execute("UPDATE gamestats SET fg = ? WHERE id = ?",fg,gameid)
            db.execute("UPDATE gamestats SET fga = ? WHERE id = ?",fga,gameid)
            db.execute("UPDATE gamestats SET threep = ? WHERE id = ?",threep,gameid)
            db.execute("UPDATE gamestats SET threepa = ? WHERE id = ?",threepa,gameid)
            db.execute("UPDATE gamestats SET twop = ? WHERE id = ?",twop,gameid)
            db.execute("UPDATE gamestats SET twopa = ? WHERE id = ?",twopa,gameid)
            db.execute("UPDATE gamestats SET ft = ? WHERE id = ?",ft,gameid)
            db.execute("UPDATE gamestats SET fta = ? WHERE id = ?",fta,gameid)
            db.execute("UPDATE gamestats SET orb = ? WHERE id = ?",orb,gameid)
            db.execute("UPDATE gamestats SET drb = ? WHERE id = ?",drb,gameid)
            db.execute("UPDATE gamestats SET ast = ? WHERE id = ?",ast,gameid)
            db.execute("UPDATE gamestats SET stl = ? WHERE id = ?",stl,gameid)
            db.execute("UPDATE gamestats SET blk = ? WHERE id = ?",blk,gameid)
            db.execute("UPDATE gamestats SET tov = ? WHERE id = ?",tov,gameid)
            db.execute("UPDATE gamestats SET pf = ? WHERE id = ?",pf,gameid)
            db.execute("UPDATE gamestats SET pts = ? WHERE id = ?",pts,gameid)
            db.execute("UPDATE gamestats SET trb = ? WHERE id = ?",trb,gameid)
            db.execute("UPDATE gamestats SET FGPercent = ? WHERE id = ?",FGPercent,gameid)
            db.execute("UPDATE gamestats SET FTPercent = ? WHERE id = ?",FTPercent,gameid)
            db.execute("UPDATE gamestats SET THREEPPercent = ? WHERE id = ?",THREEPPercent,gameid)
            db.execute("UPDATE gamestats SET TWOPPercent = ? WHERE id = ?",TWOPPercent,gameid)
            db.execute("UPDATE gamestats SET eFGPercent = ? WHERE id = ?",eFGPercent,gameid)





        if 'deletegame' in request.form:
            db.execute("DELETE FROM gamestats WHERE id = ?",gameid)

        db.execute("UPDATE usertotalstats SET G = (SELECT COUNT(id) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET GS = (SELECT SUM(GS) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET MP = (SELECT SUM(MP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET FG = (SELECT SUM(FG) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET FGA = (SELECT SUM(FGA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET THREEP = (SELECT SUM(THREEP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET THREEPA = (SELECT SUM(THREEPA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET TWOP = (SELECT SUM(TWOP) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET TWOPA = (SELECT SUM(TWOPA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET FT = (SELECT SUM(FT) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET FTA = (SELECT SUM(FTA) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET ORB = (SELECT SUM(ORB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET DRB = (SELECT SUM(DRB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET AST = (SELECT SUM(AST) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET STL = (SELECT SUM(STL) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET BLK = (SELECT SUM(BLK) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET TOV = (SELECT SUM(TOV) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET PF = (SELECT SUM(PF) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET PTS = (SELECT SUM(PTS) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)
        db.execute("UPDATE usertotalstats SET TRB = (SELECT SUM(TRB) FROM gamestats WHERE user_id=?) WHERE user_id = ?",user_id,user_id)

        db.execute("UPDATE userpergamestats SET G = (SELECT COUNT(id) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET GS = (SELECT SUM(GS) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET MP = (SELECT AVG(MP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FG = (SELECT AVG(FG) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FGA = (SELECT AVG(FGA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FGPercent = (SELECT AVG(FGPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET THREEP = (SELECT AVG(THREEP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET THREEPA = (SELECT AVG(THREEPA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET THREEPPercent = (SELECT AVG(THREEPPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET TWOP = (SELECT AVG(TWOP) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET TWOPA = (SELECT AVG(TWOPA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET TWOPPercent = (SELECT AVG(TWOPPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FT = (SELECT AVG(FT) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FTA = (SELECT AVG(FTA) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET FTPercent = (SELECT AVG(FTPercent) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET ORB = (SELECT AVG(ORB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET DRB = (SELECT AVG(DRB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET AST = (SELECT AVG(AST) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET STL = (SELECT AVG(STL) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET BLK = (SELECT AVG(BLK) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET TOV = (SELECT AVG(TOV) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET PF = (SELECT AVG(PF) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET PTS = (SELECT AVG(PTS) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)
        db.execute("UPDATE userpergamestats SET TRB = (SELECT AVG(TRB) FROM gamestats WHERE user_id=?) WHERE pergame_user_id = ?",user_id,user_id)


        return redirect("/updategamestats")

    else:
        gameid = request.args.get('gameid')
        gamestart= db.execute("SELECT GS FROM gamestats WHERE id = ?",gameid)[0]["GS"]
        gameinfo= db.execute("SELECT * FROM gamestats WHERE id = ?",gameid)
        return render_template("changestats.html",gameinfo=gameinfo,gameid=gameid,gamestart=gamestart)

@app.route("/glossary")
def glossary():

    acroynm = db.execute("SELECT * FROM glossary")
    return render_template("glossary.html", acroynm=acroynm)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        pass
    else:
        input = request.args.get("search").upper()
        if not input:
            attention="Attention"
            error="An error occured when searching for users."
            tryagain="Please try again."
            return render_template("search.html",error=error,attention=attention,tryagain=tryagain)

        try:
            stats= db.execute("SELECT * FROM userpergamestats INNER JOIN users ON userpergamestats.pergame_user_id=users.id WHERE username LIKE ?", "%" + input + "%" )
        except:
            attention="Attention"
            error="An error occured when searching for users."
            tryagain="Please try again."
            return render_template("search.html",error=error,attention=attention,tryagain=tryagain)
        return render_template("search.html",stats=stats)

@app.route("/userprofile", methods=["GET", "POST"])
def userprofile():
    if request.method == "POST":
        pass
    else:
        id = request.args.get("userid")
        username = db.execute("SELECT username FROM users WHERE id = ?",id)[0]["username"]
        info = db.execute("SELECT * FROM users WHERE id = ?",id)
        profile_pic=db.execute("SELECT picture FROM users WHERE id = ?",id)[0]["picture"]
        stats = db.execute("SELECT * FROM userpergamestats WHERE pergame_user_id = ?",id)
        posts = db.execute("SELECT * FROM posts WHERE posts_user_id = ? ORDER BY time DESC",id)
        games = db.execute("SELECT * FROM gamestats WHERE user_id =? ORDER BY date DESC LIMIT 5",id)
        return render_template("userprofile.html",stats=stats,posts=posts,games=games,info=info,profile_pic=profile_pic,username=username)


@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
    if request.method == "POST":
        req = request.args.get("stat")
        stats = db.execute("SELECT pergame_user_id,G,? FROM userpergamestats ORDER BY ? DESC",req,req)
        return render_template("leaderboard.html",stats=stats,req=req)
    else:
        req = request.args.get("stat")
        ts = request.form.get("ts")

        if req:

            if req == 'G':
                sname= " Total Games Played"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.G  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'GS':
                sname= " Total Games Started"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.GS  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'MP':
                sname= "Total Minutes Played"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.MP  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FG':
                sname= "Total Field Goals Made"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.FG  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FGA':
                sname="Total Field Goal Attempts"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.FGA  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'THREEPA':
                sname="Total Three Point Attempts"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.THREEPA  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'THREEP':
                sname="Total Three Points Made"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.THREEP  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TWOP':
                sname="Total Two Points Made"
                stats = db.execute("SELECT users.username AS nameusertotalstats.G AS G,usertotalstats.TWOP  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TWOPA':
                sname="Total Two Point Attempts"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.TWOPA  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FT':
                sname="Total Free Throws Made"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.FT  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FTA':
                sname="Total Free Throw Attempts"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.FTA  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'ORB':
                sname="Total Offensive Rebounds"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.ORB  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'DRB':
                sname="Total Defensive Rebounds"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.DRB  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TRB':
                sname="Total Rebounds"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.TRB  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'AST':
                sname="Total Assists"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.AST  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'STL':
                sname="Total Steals"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.STL  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'BLK':
                sname="Total Blocks"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.BLK  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TOV':
                sname="Total Turnovers"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.TOV  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'PF':
                sname="Total Personal Fouls"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.PF  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'PTS':
                sname="Total Points"
                stats = db.execute("SELECT users.username AS name,usertotalstats.G AS G,usertotalstats.PTS  AS num FROM users INNER JOIN usertotalstats ON users.id=usertotalstats.user_id ORDER BY CAST(num AS int) DESC")

            elif req == 'MPx':
                sname= " Average Minutes Played Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.MP  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FGx':
                sname= "Average Field Goals Made Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FG  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FGAx':
                sname="Average Field Goal Attempts Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FGA  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'THREEPAx':
                sname="Average Three Point Attempts Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.THREEPA  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'THREEPx':
                sname="Average Three Points Made Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.THREEP  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TWOPx':
                sname="Average Two Points Made Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.TWOP  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TWOPAx':
                sname="Average Two Point Attempts Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.TWOPA AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FTx':
                sname="Average Free Throws Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FT  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FTAx':
                sname="Average Free Throws Attempts Per game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FTA  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'ORBx':
                sname="Average Offenive Rebounds Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.ORB  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'DRBx':
                sname="Average Defensive Rebounds Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.DRB  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TRBx':
                sname="Average Total Rebounds Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.TRB  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'ASTx':
                sname="Average Assists Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.AST  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'STLx':
                sname="Average Steals Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.STL  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'BLKx':
                sname="Average Blocks Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.BLK  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TOVx':
                sname=" Average Total Turnovers Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.TOV  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'PFx':
                sname="Average Personal Fouls Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.PF  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'PTSx':
                sname=" Average Points Per Game"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.PTS  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FGPercent':
                sname="FG%"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FGPercent  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'THREEPPercent':
                sname="3P%"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.THREEPPercent AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'FTPercent':
                sname="FT%"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.FTPercent  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'TWOPPercent':
                sname="2P%"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.TWOPPercent  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            elif req == 'eFGPercent':
                sname="eFG%"
                stats = db.execute("SELECT users.username AS name,userpergamestats.G AS G,userpergamestats.eFGPercent  AS num FROM users INNER JOIN userpergamestats ON users.id=userpergamestats.pergame_user_id ORDER BY CAST(num AS int) DESC")
            return render_template("leaderboard.html",stats=stats,req=req,ts=ts,sname=sname)
        else:
            return render_template("leaderboard.html")




if __name__ == '__main__':
    app.run(debug=True)