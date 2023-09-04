import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import boto3 as boto3
import pymysql
import pandas
from dateutil.relativedelta import relativedelta
from flask import Flask, request, render_template, session


# conn = pymysql.connect(host="localhost", user="root", password="123", db="movieBookingAWS")
conn = pymysql.connect(host="movieticketdb.cqgqnbqgj5iv.us-east-2.rds.amazonaws.com", user="admin", password="admin123", db="movieBookingAWS")
cursor = conn.cursor()
app = Flask(__name__)
app.secret_key = "movieTicket"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

aws_access_key_id = "AKIA4FQP3W4EUVRXCE2Q"
aws_secret_access_key = "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"
region_name = 'us-east-2'
source_email = 'prasanthsagar70@gmail.com'
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
ses_client = boto3.client('ses', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
BUCKET = "newsrirambucket"


def ses_send_email(receiver_email, subject, html_message):
    ses_client.send_email(
        Source=source_email,
        Destination={'ToAddresses': [receiver_email]},
        Message={'Subject': {'Data': subject, 'Charset': 'utf-8'}, 'Body': {'Html': {'Data': html_message, 'Charset': 'utf-8'}}})

def retrieve_image_object_from_s3_bucket(product_image):
    print(product_image)
    product_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': product_image},ExpiresIn=100)
    print(product_url)
    return product_url

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/adminLogin.html")
def adminLogin():
    return render_template("adminLogin.html")

@app.route("/adminLogin1",methods=['post'])
def adminLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    if email == 'admin@gmail.com' and password == 'admin':
        session['role'] = 'Admin'
        return render_template("adminHome.html")
    elif email != 'admin@gmail.com' and password == 'admin':
        return render_template("msg.html", message="Wrong Email",color='alert-danger')
    elif email == 'admin@gmail.com' and password != 'admin':
        return render_template("msg.html", message="Wrong Password",color='alert-danger')
    elif email != 'admin@gmail.com' and password != 'admin':
        return render_template("msg.html", message="Invalid Credentials",color='alert-danger')

@app.route("/adminLogout")
def adminLogout():
    session.clear()
    return render_template("index.html")

@app.route("/adminHome")
def adminHome():
    return render_template("adminHome.html")

@app.route("/theatreLogin.html")
def theatreLogin():
    return render_template("theatreLogin.html")

@app.route("/theatreLogin1",methods=['post'])
def theatreLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from theatre where email='" + str(email) + "' and password='" + str(password) + "'")
    if count == 0:
        return render_template("msg.html", message="invalid Login Details",color='alert-danger')
    else:
        # theatre = Theatre_col.find_one(query)
        theatres = cursor.fetchall()
        session['theatre_id'] = str(theatres[0][0])
        session['role'] = 'Theatre'
        return render_template("theatreHome.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/addTheatre")
def addTheatre():
    return render_template("addTheatre.html")

@app.route("/addTheatre1", methods=['post'])
def addTheatre1():
    theatre_Name = request.form.get("theatre_Name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    location = request.form.get("location")
    address = request.form.get("address")
    password = request.form.get("password")
    count = cursor.execute("select * from theatre where email='"+str(email)+"' and phone='"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into theatre(theatre_Name,email,phone,location,address,password) values('"+str(theatre_Name)+"', '"+str(email)+"', '"+str(phone)+"', '"+str(location)+"', '"+str(address)+"', '"+str(password)+"')")
        conn.commit()
        ses_client.verify_email_address(EmailAddress=email)
        return render_template("A_msg.html", message="Theatre Added",color='alert-success')
    else:
        return render_template("A_msg.html", message="Email already Exist. Try another Email",color='alert-danger')

@app.route("/theatreHome")
def theatreHome():
    return render_template("theatreHome.html")

@app.route("/customerHome")
def customerHome():
    return render_template("customerHome.html")

@app.route("/customerLogin.html")
def customerLogin():
    return render_template("customerLogin.html")

@app.route("/customerLogin1",methods=['post'])
def customerLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from customer where email='"+str(email)+"' and password='"+str(password)+"'")
    if count == 0:
        return render_template("C_msg.html", message="Invalid login Details")
    else:
        customers = cursor.fetchall()
        session['customer_id'] = str(customers[0][0])
        session['role'] = 'Customer'
        return render_template("customerHome.html")

@app.route("/customerRegistration.html")
def customerRegistration():
    return render_template("customerRegistration.html")

@app.route("/addCustomer",methods=['post'])
def addCustomer():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    password = request.form.get("password")
    count = cursor.execute("select * from customer where email='"+str(email)+"' or phone='"+str(phone)+"'")
    if count == 0:
        count = cursor.execute("insert into customer(name,email,phone,address,password) values('"+str(name)+"', '"+str(email)+"', '"+str(phone)+"', '"+str(address)+"','"+str(password)+"')")
        conn.commit()
        ses_client.verify_email_address(EmailAddress=email)
        return render_template("msg.html", message="Customer Registration Successful!",color='alert-success')
    else:
        return render_template("msg.html", message="Customer Already Exist",color='alert-danger')

@app.route("/customerLogout")
def customerLogout():
    session.clear()
    return render_template("index.html")

@app.route("/viewTheatres")
def viewTheatres():
    cursor.execute("select * from theatre")
    theatres = cursor.fetchall()
    return render_template("viewTheatres.html", theatres=theatres)

@app.route("/addMovie")
def addMovie():
    return render_template("addMovie.html")

@app.route("/addMovie1", methods=['post'])
def addMovie1():
    movie_Name = request.form.get("movie_Name")
    poster = request.files['poster']
    path1 = APP_ROOT+"/static/moviePosters/"+poster.filename
    poster.save(path1)
    certificate = request.files['certificate']
    path2 = APP_ROOT+"/static/certificates/"+certificate.filename
    certificate.save(path2)
    certificate_type = request.form.get("certificate_type")
    supported_formats = request.form.get("supported_formats")
    duration_in_minutes = request.form.get("duration_in_minutes")
    count = cursor.execute("select * from movies where movie_Name='"+str(movie_Name)+"'")
    if count == 0:
        cursor.execute("insert into movies(movie_Name,poster,certificate,certificate_type,supported_formats,duration_in_minutes) values('"+str(movie_Name)+"', '"+str(poster.filename)+"', '"+str(certificate.filename)+"','"+str(certificate_type)+"','"+str(supported_formats)+"','"+str(duration_in_minutes)+"')")
        conn.commit()
        upload_movie_poster(path1, poster.filename)
        upload_movie_poster(path2, certificate.filename)
        return render_template("A_msg.html", message="Movie Added!",color='alert-success')
    else:
        return render_template("A_msg.html", message="Movie Already Added!",color='alert-danger')


def upload_movie_poster(current_path, post_name):
    response = s3_client.upload_file(current_path, BUCKET, post_name)
    return response


@app.route("/viewMovies")
def viewMovies():
    cursor.execute("select * from movies order by movie_id desc")
    movies = cursor.fetchall()
    return render_template("viewMovies.html", movies=movies, retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket)

@app.route("/addMovieCast")
def addMovieCast():
    movie_id = request.args.get("movie_id")
    return render_template("addMovieCast.html", movie_id=movie_id)

@app.route("/addMovieCast1", methods=['post'])
def addMovieCast1():
    movie_id = request.form.get("movie_id")
    caste_Title = request.form.get("caste_Title")
    name = request.form.get("name")
    Age = request.form.get("Age")
    about = request.form.get("about")
    picture = request.files.get('picture')
    path = APP_ROOT+"/static/moviePosters/"+picture.filename
    picture.save(path)
    cursor.execute("insert into casting(movie_id,caste_Title,name,age,about,picture) values('"+str(movie_id)+"', '"+str(caste_Title)+"', '"+str(name)+"', '"+str(Age)+"', '"+str(about)+"', '"+str(picture.filename)+"')")
    conn.commit()
    return render_template("A_msg.html", message="Movie Cast Added!",color='alert-success')

@app.route("/viewMovieCast")
def viewMovieCast():
    movie_id = request.args.get("movie_id")
    count = cursor.execute("select * from casting where movie_id='"+str(movie_id)+"'")
    if count == 0:
        return render_template("A_msg.html", message="Cast Doesn't Added yet!",color='alert-danger')
    else:
        casting = cursor.fetchall()
        return render_template("viewMovieCast.html", casting=casting)

@app.route("/addScreen")
def addScreen():
    return render_template("addScreen.html")

@app.route("/addScreen1",methods=['post'])
def addScreen1():
    theatre_id = session['theatre_id']
    number_of_seats = request.form.get("number_of_seats")
    screen_Title = request.form.get("screen_Title")
    screen_size = request.form.get("screen_size")
    screen_Type = request.form.get("screen_Type")
    show1_timing = request.form.get("show1_timing")
    show2_timing = request.form.get("show2_timing")
    show3_timing = request.form.get("show3_timing")
    show4_timing = request.form.get("show4_timing")
    count = cursor.execute("select * from screens where screen_Title='"+str(screen_Title)+"' and theatre_id='"+str(theatre_id)+"'")
    if count > 0:
        return render_template("tmsg.html", message="Screen Exists!", color='alert-danger')
    else:
        cursor.execute("insert into screens(theatre_id, screen_Title, screen_size, screen_Type, show1_timing, show2_timing, show3_timing, show4_timing, number_of_seats) values('"+str(theatre_id)+"', '"+str(screen_Title)+"', '"+str(screen_size)+"', '"+str(screen_Type)+"', '"+str(show1_timing)+"', '"+str(show2_timing)+"','"+str(show3_timing)+"','"+str(show4_timing)+"','"+str(number_of_seats)+"')")
        conn.commit()
        return render_template("tmsg.html", message="Screen Added!",color='alert-success')

@app.route("/viewScreens")
def viewScreens():
    theatre_id = session['theatre_id']
    count = cursor.execute("select * from screens where theatre_id='"+str(theatre_id)+"'")
    if count > 0:
        screens = cursor.fetchall()
        return render_template("viewScreens.html", screens=screens)
    else:
        return render_template("T_error.html", message="No Screens To Show")

@app.route("/assignMovie")
def assignMovie():
    screen_id = request.args.get("screen_id")
    cursor.execute("select * from movies order by movie_id desc")
    movies = cursor.fetchall()
    return render_template("assignMovie.html", screen_id=screen_id, movies=movies)

@app.route("/addSchedule",methods=['post'])
def addSchedule():
    screen_id = request.form.get("screen_id")
    movie_id = request.form.get("movie_id")
    price_per_seat = request.form.get("price_per_seat")
    movie_Type = request.form.get("movie_Type")
    from_date_time = request.form.get("from_date_time")
    to_date_time = request.form.get("to_date_time")
    from_date_time = from_date_time.replace("T", ' ')
    to_date_time = to_date_time.replace("T", ' ')
    from_date_time1 = request.form.get("from_date_time")
    to_date_time1 = request.form.get("to_date_time")
    from_date_time = datetime.datetime.strptime(from_date_time, "%Y-%m-%d %H:%M")
    to_date_time = datetime.datetime.strptime(to_date_time, "%Y-%m-%d %H:%M")
    from_date_time1 = from_date_time1.replace("T", ' ')
    to_date_time1 = to_date_time1.replace("T", ' ')
    new_from_date_time1 = datetime.datetime.strptime(from_date_time1, "%Y-%m-%d %H:%M")
    new_to_date_time1 = datetime.datetime.strptime(to_date_time1, "%Y-%m-%d %H:%M")
    from_date = new_from_date_time1.strptime(from_date_time1,"%Y-%m-%d %H:%M").date()
    to_date = new_to_date_time1.strptime(to_date_time1,"%Y-%m-%d %H:%M").date()
    dates = pandas.date_range(from_date,to_date - relativedelta(days=0), freq='d')
    dates = dates.strftime('%Y-%m-%d').tolist()
    cursor.execute("select * from schedule where screen_id='"+str(screen_id)+"'")
    schedules = cursor.fetchall()
    for schedule in schedules:
        old_from_date_time =  datetime.datetime.strptime(schedule[3][:-3], "%Y-%m-%d %H:%M")
        old_to_date_time = datetime.datetime.strptime(schedule[4][:-3], "%Y-%m-%d %H:%M")
        print(type(old_from_date_time))
        print(type(old_to_date_time))
        if(old_from_date_time >= from_date_time and old_from_date_time <= to_date_time) and (old_to_date_time >= from_date_time and old_to_date_time >= to_date_time):
            print("k")
            return render_template("T_error.html", message="Timing Colloids Already Movie Assigned in These Dates. Unable to add")
        elif(old_from_date_time <= from_date_time and old_from_date_time <= to_date_time) and (old_to_date_time >= from_date_time and old_to_date_time <= to_date_time):
            print("l")
            return render_template("T_error.html", message="Timing Colloids Already Movie Assigned in These Dates. Unable to add")
        elif(old_from_date_time <= from_date_time and old_from_date_time <= to_date_time) and (old_to_date_time >= from_date_time and old_to_date_time >= to_date_time):
            print("m")
            return render_template("T_error.html", message="Timing Colloids Already Movie Assigned in These Dates. Unable to add")
        elif(old_from_date_time >= from_date_time and old_from_date_time <= to_date_time) and (old_to_date_time >= from_date_time and old_to_date_time <= to_date_time):
            print("n")
            return render_template("T_error.html", message="Timing Colloids Already Movie Assigned in These Dates. Unable to add")
    print("insert into schedule(screen_id, movie_id, from_date_time, to_date_time, price_per_seat, movie_Type) values('"+str(screen_id)+"', '"+str(movie_id)+"', '"+str(from_date_time)+"', '"+str(to_date_time)+"', '"+str(price_per_seat)+"', '"+str(movie_Type)+"')")
    cursor.execute("insert into schedule(screen_id, movie_id, from_date_time, to_date_time, price_per_seat, movie_Type) values('"+str(screen_id)+"', '"+str(movie_id)+"', '"+str(from_date_time)+"', '"+str(to_date_time)+"', '"+str(price_per_seat)+"', '"+str(movie_Type)+"')")
    conn.commit()
    schedule_id = cursor.lastrowid
    for day in dates:
        cursor.execute("insert into schedule_dates(schedule_id, date) values('"+str(schedule_id)+"', '"+str(day)+"')")
        conn.commit()
    return render_template("tmsg.html", message="Movie Assigned, and schedule added",color='alert-success')

@app.route("/viewSchedule")
def viewSchedule():
    screen_id = request.args.get("screen_id")
    cursor.execute("select * from schedule where screen_id='"+str(screen_id)+"'")
    Schedules = cursor.fetchall()
    return render_template("viewSchedule.html",retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket, Schedules=Schedules,get_movie_by_schedule2=get_movie_by_schedule2)

def get_movie_by_schedule2(movie_id):
    cursor.execute("select * from movies where movie_id='"+str(movie_id)+"'")
    movies = cursor.fetchall()
    return movies[0]

@app.route("/view_assigned_movies")
def view_assigned_movies():
    cursor.execute("select * from screens where theatre_id='"+str(session['theatre_id'])+"' order by screen_id desc")
    screens = cursor.fetchall()
    return render_template("view_assigned_movies.html",retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket,get_schedule_by_assign_screen=get_schedule_by_assign_screen,screens=screens,get_screen_by_assignMovie_schedule=get_screen_by_assignMovie_schedule, get_movie_by_schedule=get_movie_by_schedule)


def get_movie_by_schedule(movie_id):
    cursor.execute("select * from movies where movie_id='" + str(movie_id) + "'")
    movies = cursor.fetchall()
    return movies

def get_schedule_by_assign_screen(screen_id):
    cursor.execute("select * from schedule where screen_id='" + str(screen_id) + "'")
    Schedules = cursor.fetchall()
    return Schedules


def get_screen_by_assignMovie_schedule(screen_id):
    cursor.execute("select * from screens where screen_id='"+str(screen_id)+"'")
    screens = cursor.fetchall()
    return screens[0]

@app.route("/view_scheduled_movies")
def view_scheduled_movies():
    today = datetime.datetime.now().date()
    return render_template("view_scheduled_movies.html",today=today, retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket)

@app.route("/get_scheduled_movies")
def get_scheduled_movies():
    movie_Name = request.args.get("movie_Name")
    booking_date = request.args.get("booking_date")
    query = ""
    if movie_Name == '':
        query = "select * from movies where movie_id in  (select movie_id from schedule where schedule_id in (select schedule_id from schedule_dates where date='"+str(booking_date)+"'))"
    else:
        query = "select * from movies where movie_id in (select movie_id from schedule where schedule_id in (select schedule_id from schedule_dates where date='"+str(booking_date)+"') and movie_id in (select movie_id from movies where movie_Name like '%"+str(movie_Name)+"%'))"
    print(query)
    cursor.execute(query)
    movies = cursor.fetchall()
    if len(movies) == 0:
        return '''
                <div class="row">
	                <div class="col-md-4"></div>
		            <div class="col-md-4 mt-5">
			            <div class="alert alert-danger">
		    	            <strong>Movies Not Available</strong>
		   	            </div>
		   	        </div>
                    <div class="col-md-4"></div>
                </div>
        '''
    return render_template("get_scheduled_movies.html",retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket, movies=movies,get_movie_by_schedule1=get_movie_by_schedule1,booking_date=booking_date)

def get_movie_by_schedule1(movie_id):
    # movie = Movie_col.find_one({'_id':ObjectId(movie_id)})
    cursor.execute("select * from movies where movie_id='"+str(movie_id)+"'")
    movies = cursor.fetchall()
    return movies[0]


@app.route("/view_scheduled_Theaters")
def view_scheduled_Theaters():
    booking_date = request.args.get("booking_date")
    theatre_id = request.args.get("theatre_id")
    movie_id = request.args.get("movie_id")
    if theatre_id == None:
        query = "select * from schedule where movie_id='"+str(movie_id)+"' and schedule_id in (select schedule_id from schedule_dates where date='"+str(booking_date)+"')"
    else:
        query = "select * from schedule where screen_id in (select screen_id from screens where theatre_id='"+str(theatre_id)+"') and movie_id='"+str(movie_id)+"' and schedule_id in (select schedule_id from schedule_dates where date='"+str(booking_date)+"')"
    print(query)
    cursor.execute(query)
    schedules = cursor.fetchall()
    return render_template("view_scheduled_Theaters.html",get_screen_by_schedules=get_screen_by_schedules,movie_id=movie_id,schedules=schedules,get_theater_by_schedule_screen=get_theater_by_schedule_screen,booking_date=booking_date,can_display_show=can_display_show)



def get_theater_by_schedule_screen(screen_id):
    cursor.execute("select * from theatre where theatre_id in (select theatre_id from screens where screen_id='"+str(screen_id)+"')")
    theatres = cursor.fetchall()
    return theatres


def get_screen_by_schedules(screen_id):
    cursor.execute("select * from screens where screen_id='"+str(screen_id)+"'")
    screens = cursor.fetchall()
    return screens[0]


@app.route("/view_seats")
def view_seats():
    booking_date = request.args.get("booking_date")
    screen_id = request.args.get("screen_id")
    schedule_id = request.args.get("schedule_id")
    show_time = request.args.get("show_time")
    cursor.execute("select * from screens where screen_id='"+str(screen_id)+"'")
    screens = cursor.fetchall()
    screen = screens[0]
    return render_template("view_seats.html", str=str, isSeatBooked=isSeatBooked, show_time=show_time,booking_date=booking_date,screen=screen,screen_id=screen_id,schedule_id=schedule_id,int=int,get_schedule_by_screen_id=get_schedule_by_screen_id)


def isSeatBooked(screen_id,i,booking_date,show_time):
    cursor.execute("select * from booked_seats where booking_id in (select booking_id from bookings where screen_id='"+str(screen_id)+"' and booking_date='"+str(booking_date)+"' and show_time='"+str(show_time)+"') ")
    booked_seats = cursor.fetchall()
    for booked_seat in booked_seats:
        if(str(booked_seat[2])) == str(i):
            return True
    return False



def get_schedule_by_screen_id(screen_id):
    cursor.execute("select * from schedule where screen_id='"+str(screen_id)+"'")
    schedules = cursor.fetchall()
    print(schedules)
    return schedules




@app.route("/bookSeats",methods=['post'])
def addbooking1():
    booking_date = request.form.get("booking_date")
    show_time = request.form.get("show_time")
    schedule_id = request.form.get("schedule_id")
    screen_id = request.form.get("screen_id")
    cursor.execute("select * from schedule where screen_id='"+str(screen_id)+"'")
    schedules = cursor.fetchall()
    schedules = schedules[0]
    conn.commit()
    cursor.execute("select * from movies where movie_id in (select movie_id from schedule where screen_id='"+str(screen_id)+"')")
    movies = cursor.fetchall()
    conn.commit()
    movie = movies[0]
    cursor.execute("select * from screens where screen_id='"+str(screen_id)+"'")
    screens = cursor.fetchall()
    conn.commit()
    screen = screens[0]
    selected_seats = []
    ticketAmount = 0
    for i in range(int(screen[9])):
        seat = request.form.get(str(screen[0]) + "seat" + str(i))
        if seat == 'on':
            seatDetails = {"seat":  str(i),"price_per_seat": int(schedules[5])}
            selected_seats.append(seatDetails)
            ticketAmount = ticketAmount + int(schedules[5])
    selected_seats = list(selected_seats)
    if len(selected_seats) > 6:
        return render_template("C_msg.html",message='You Can Not Book More Than 6 Tickets',color='alert-danger')
    cursor.execute("insert into bookings(schedule_id, screen_id,booking_date,show_time,totalPrice,customer_id,status) values('"+str(schedule_id)+"', '"+str(screen[0])+"', '"+str(booking_date)+"', '"+str(show_time)+"', '"+str(ticketAmount)+"', '"+str(session['customer_id'])+"', 'Payment Pending')")
    conn.commit()
    booking_id = cursor.lastrowid
    for selected_seat in selected_seats:
        cursor.execute("insert into booked_seats(booking_id,seat_number) values('"+str(booking_id)+"', '"+str(selected_seat['seat'])+"')")
        conn.commit()
    return render_template("bookSeats1.html",booking_id=booking_id,movie=movie,booking_date=booking_date,show_time=show_time,selected_seats=selected_seats,ticketAmount=ticketAmount,schedule_id=schedule_id)



@app.route("/bookSeats2",methods=['post'])
def bookSeats2():
    booking_id = request.form.get("booking_id")
    cursor.execute("select * from customer where customer_id='"+str(session['customer_id'])+"'")
    customers = cursor.fetchall()
    email = customers[0][2]
    query = {'$set':{"status":'Movie Booked'}}
    # msg = MIMEMultipart('alternative')
    # message = """
    #     <html>
    #         <body>
    #             <h1>Daily S&P 500 prices report</h1>
    #             <p>Hello, welcome to your report!</p>
    #         </body>
    #     </html>
    #    """
    # msg.attach(MIMEText(message, 'html'))
    # with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
    #     send_email("hii", msg.as_string(), email)
    cursor.execute("update bookings set status ='Movie Booked' where booking_id='"+str(booking_id)+"'")
    conn.commit()
    cursor.execute("select * from customer where customer_id='" + str(session['customer_id']) + "'")
    customers = cursor.fetchall()
    print(customers[0][2])
    ses_send_email(customers[0][2], "Tickets Booked Successfully",creating_html_ticket(booking_id))
    return render_template("C_msg.html",message='Movie Booked Successfully',color='alert-success')


def creating_html_ticket(booking_id):
    cursor.execute("select * from bookings where booking_id='"+str(booking_id)+"'")
    bookings = cursor.fetchall()
    return render_template("view_bookings2.html",retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket,get_booked_seats_by_booking_id=get_booked_seats_by_booking_id, get_customer_by_bookings=get_customer_by_bookings, get_screen_by_bookings=get_screen_by_bookings, get_theater_by_booking_id=get_theater_by_booking_id, get_ticket_by_bookings=get_ticket_by_bookings, bookings=bookings, get_movie_id_by_scheduled_bookings=get_movie_id_by_scheduled_bookings, get_time_gap_to_cancel_ticket=get_time_gap_to_cancel_ticket, len=len)


@app.route("/view_bookings")
def view_bookings():
    query = ""
    if session['role'] == 'Theatre':
        schedule_id = request.args.get("schedule_id")
        show_time = request.args.get("show_time")
        booking_date = request.args.get("booking_date")
        query = "select * from bookings where schedule_id='"+str(schedule_id)+"' and show_time='"+str(show_time)+"' and '"+str(booking_date)+"'"
    elif session['role'] == 'Customer':
        query = "select * from bookings where customer_id='"+str(session['customer_id'])+"' and (status='Movie Booked' or status='Booking Cancelled')"
    cursor.execute(query)
    bookings = cursor.fetchall()
    if session['role'] == 'Customer':
        if len(bookings) == 0:
            return render_template("C_msg.html", message='No Bookings', color='alert-primary')
    elif session['role'] == 'Theatre':
        if len(bookings) == 0:
            return render_template("tmsg.html", message='No Bookings', color='alert-primary')
    return render_template("view_bookings.html", retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket,get_booked_seats_by_booking_id=get_booked_seats_by_booking_id, get_customer_by_bookings=get_customer_by_bookings, get_screen_by_bookings=get_screen_by_bookings, get_theater_by_booking_id=get_theater_by_booking_id, get_ticket_by_bookings=get_ticket_by_bookings, bookings=bookings, get_movie_id_by_scheduled_bookings=get_movie_id_by_scheduled_bookings, get_time_gap_to_cancel_ticket=get_time_gap_to_cancel_ticket, len=len)

def get_customer_by_bookings(customer_id):
    cursor.execute("select * from customer where customer_id='"+str(customer_id)+"'")
    customers = cursor.fetchall()
    return customers[0]


def get_movie_id_by_scheduled_bookings(schedule_id):
    cursor.execute("select * from movies where movie_id in(select movie_id from schedule where schedule_id='"+str(schedule_id)+"')")
    movies = cursor.fetchall()
    return movies[0]

def get_ticket_by_bookings(booking_id):
    cursor.execute("select * from bookings where booking_id='"+str(booking_id)+"'")

    return 0

def get_theater_by_booking_id(booking_id):
    cursor.execute("select * from theatre where theatre_id in (select theatre_id from screens where screen_id in (select screen_id from schedule where schedule_id in (select schedule_id from bookings where booking_id='"+str(booking_id)+"')))")
    theaters = cursor.fetchall()
    return theaters[0]


def get_screen_by_bookings(booking_id):
    cursor.execute("select * from screens where screen_id in (select screen_id from schedule where schedule_id in (select schedule_id from bookings where booking_id='"+str(booking_id)+"'))")
    screens = cursor.fetchall()
    return screens[0]

@app.route("/cancel_booking",methods=['post'])
def cancel_booking():
    booking_id = request.form.get("booking_id")
    cursor.execute("update bookings set status='Booking Cancelled' where booking_id='"+str(booking_id)+"'")
    return view_bookings()


@app.route("/view_my_bookings")
def view_my_bookings():
    booking_date = request.args.get('booking_date')
    if booking_date==None:
        booking_date = datetime.datetime.now().date()
    cursor.execute("select * from screens where theatre_id='"+str(session['theatre_id'])+"'")
    screens = cursor.fetchall()
    return render_template("view_my_bookings.html",screens=screens,booking_date=booking_date,get_schedule_by_selected_date=get_schedule_by_selected_date)

def get_schedule_by_selected_date(screen_id):
    cursor.execute("select * from schedule where screen_id='"+str(screen_id)+"'")
    schedules = cursor.fetchall()
    return schedules


@app.route("/theaters")
def theaters():
    theatre_Name = request.args.get("theatre_Name")
    query = {}
    booking_date = request.args.get("booking_date")
    if booking_date==None:
        booking_date = datetime.datetime.now().date()
    if theatre_Name == None:
        theatre_Name =''
    if theatre_Name == '':
        query = "select * from theatre"
    else:
        query = "select * from theatre where theatre_Name like '"+str(theatre_Name)+"'"
    cursor.execute(query)
    theaters = cursor.fetchall()
    return render_template("theaters.html",theaters=theaters,booking_date=booking_date,theatre_Name=theatre_Name)


@app.route("/viewTheaterScreens")
def viewTheaterScreens():
    theatre_id = request.args.get("theatre_id")
    booking_date = request.args.get('booking_date')
    cursor.execute("select * from movies where movie_id in (select movie_id from schedule where schedule_id in (select schedule_id from schedule_dates where date='"+str(booking_date)+"') and  screen_id in (select screen_id from screens where theatre_id='"+str(theatre_id)+"'))")
    movies = cursor.fetchall()
    if len(movies) ==0:
        return render_template("C_msg.html", message='No Movies Assigned On This date', color='alert-success')
    return render_template("viewTheaterScreens.html", retrieve_image_object_from_s3_bucket=retrieve_image_object_from_s3_bucket,theatre_id=theatre_id,booking_date=booking_date,movies=movies)


def get_time_gap_to_cancel_ticket(booking):
    booked_show = datetime.datetime.strptime(str(booking[3])+" "+str(booking[4]), "%Y-%m-%d %H:%M")
    today = datetime.datetime.now()
    if booked_show <= today:
        print('ffff')
        return -1
    diff = booked_show - today
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    print(hours, minutes, seconds)
    return hours

def can_display_show(booking_date, show_timing):
    show_time = datetime.datetime.strptime(str(booking_date) + " " + str(show_timing),"%Y-%m-%d %H:%M")
    today = datetime.datetime.now()
    if show_time <= today:
        return False
    return True

def get_booked_seats_by_booking_id(booking_id):
    cursor.execute("select * from booked_seats where booking_id='"+str(booking_id)+"'")
    booked_seats= cursor.fetchall()
    return  booked_seats
app.run(debug=True)

