from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, flash, redirect, render_template, request, session
import pg, os

db = pg.DB(
    dbname=os.environ.get("PG_DBNAME"),
    host=os.environ.get("PG_HOST"),
    user=os.environ.get("PG_USERNAME"),
    passwd=os.environ.get("PG_PASSWORD")
)
db.debug = True

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask("Get Cohort", template_folder = tmp_dir)

app.secret_key = os.environ.get("SECRET_KEY")

@app.route('/')
def home():
    student_query = db.query('''
        select
        	users.id,
        	first_name,
        	last_name,
        	cohort.name as cohort
        from
        	users,
        	users_link_cohort,
        	cohort,
        	users_link_type,
        	user_type
        where
        	users.id = users_link_type.user_id and
        	users_link_type.user_type_id = user_type.id and
        	users.id = users_link_cohort.user_id and
        	users_link_cohort.cohort_id = cohort.id and
            user_type.type = 'Student' and
            cohort.name = 'September 2016'
        ;
    '''
    )
    instructor_query = db.query('''
        select
        	users.id,
        	first_name,
        	last_name,
        	cohort.name as cohort
        from
        	users,
        	users_link_cohort,
        	cohort,
        	users_link_type,
        	user_type
        where
        	users.id = users_link_type.user_id and
        	users_link_type.user_type_id = user_type.id and
        	users.id = users_link_cohort.user_id and
        	users_link_cohort.cohort_id = cohort.id and
            user_type.type = 'Instructor' and
            cohort.name = 'September 2016'
        ;
    '''
    )
    student_result_list = student_query.namedresult()
    instructor_result_list = instructor_query.namedresult()
    return render_template(
        "index.html",
        student_result_list = student_result_list,
        instructor_result_list = instructor_result_list
    )

@app.route('/student_profile')
def student_profile_login():
    name = request.form.get('name')

    return redirect('/layout.html')



# @app.route('/get_cohort', methods=["POST"])
# def get_cohort():
#     query_cohort_name = db.query("select name from cohort;")
#     cohort_list = query_cohort_name.namedresult()
#     print "\n\nCohort: %s\n\n" % cohort_list
#     cohort_name = request.form.get('cohort_name')
#
#     print "\n\n Cohort name: %s \n\n" % cohort_name
#
#     return render_template(
#         "all_students.html",
#         cohort_name = cohort_name
#     )

@app.route('/all_students', methods=["POST", "GET"])
def all_students():
    query_cohort_name = db.query("select name from cohort;")
    cohort_list = query_cohort_name.namedresult()
    print "\n\ncohort_list %s" % cohort_list

    cohort_name = request.form.get('cohort_name')

    query = db.query('''
        select
        	users.id,
        	first_name,
        	last_name,
        	cohort.name
        from
        	users,
        	users_link_cohort,
        	cohort,
        	users_link_type,
        	user_type
        where
        	users.id = users_link_type.user_id and
        	users_link_type.user_type_id = user_type.id and
        	users.id = users_link_cohort.user_id and
        	users_link_cohort.cohort_id = cohort.id and
        	cohort.name = $1 and user_type.type = 'Student'
        ;
    ''', cohort_name
    )
    result_list = query.namedresult()
    return render_template(
        "all_students.html",
        result_list = result_list,
        cohort_list = cohort_list
    )

@app.route('/student_profile/<id>')
def student_profile(id):
    query = db.query("""
        select
        	users.id,
        	first_name,
        	last_name,
        	email,
        	web_page,
        	github,
        	bio,
        	cohort.name
        from
        	users,
        	users_link_cohort,
        	cohort,
        	users_link_type,
        	user_type
        where
        	users.id = users_link_type.user_id and
        	users_link_type.user_type_id = user_type.id and
        	users.id = users_link_cohort.user_id and
        	users_link_cohort.cohort_id = cohort.id and
        	users.id = $1
        ;
    """, id)
    result_list = query.namedresult()

    return render_template(
        "student_profile.html",
        student = result_list[0]
    )

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form.get("id")
    db.delete(
        "users", {
        "id": id
        }
    )
    return redirect("/all_students")

@app.route("/update", methods=["POST"])
def update():
    # email = request.form.get("email")
    user_id = request.form.get("id")
    print "\n\nUser ID: %s\n\n" % user_id

    query_student = db.query("select * from users where id = $1", user_id)
    result_list = query_student.namedresult()
    return render_template(
        "update.html",
        result = result_list[0],
        user_id = user_id
    )

@app.route("/update_entry", methods=["POST"])
def update_entry():
    user_id = request.form.get("id")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    web_page = request.form.get("web_page")
    github = request.form.get("github")
    bio = request.form.get("bio")

    print "\n\nUser ID: %s\n\n" % user_id
    print "\n\nFirst name: %s\n\n" % first_name
    print "\n\nBio: %s\n\n" % bio

    db.update(
        "users", {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "web_page": web_page,
            "github": github,
            "bio": bio
            }
        )

    return redirect('/')

@app.route("/add")
def add():
    return render_template(
        "add.html"
    )

@app.route("/add_entry", methods=["POST"])
def add_entry():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    web_page = request.form.get("web_page")
    github = request.form.get("github")
    company_name = request.form.get("company_name")
    current_location = request.form.get("current_location")
    available_for_work = request.form.get("available_for_work")
    bio = request.form.get("bio")
    cohort_id = request.form.get("cohort_id")
    user_type_id = request.form.get("user_type_id")

    db.insert (
        "users",
        first_name = first_name,
        last_name = last_name,
        email = email,
        web_page = web_page,
        github = github,
        current_location = current_location,
        available_for_work = available_for_work,
        bio = bio
    )

    query_new_entry = db.query("select id from users where email = $1", email)
    result_list = query_new_entry.namedresult()
    user_id = result_list[0].id

    db.insert (
        "users_link_type",
        user_id = user_id,
        user_type_id = user_type_id
    )
    if company_name:
        db.insert(
            "company",
            name = company_name
        )
        company_query = db.query("select id from company where name = $1", company_name).namedresult()
        print "this is the company query: %r", company_query
        company_id = company_query[0].id
        db.insert(
            "users_link_company",
            user_id = user_id,
            company_id = company_id

        )
    else:
        pass

    query_user_type = db.query("""
    select
        users.id
    from
    	users,
    	users_link_type,
    	user_type
    where
    	users.id = users_link_type.user_id and
    	users_link_type.user_type_id = user_type.id and
    	(user_type.type = 'Student' or user_type.type = 'Instructor')
    """)
    user_result_list = query_user_type.namedresult()
    for entry in user_result_list:
        if user_id in entry:
            db.insert (
                "users_link_cohort",
                user_id = user_id,
                cohort_id = cohort_id
            )
        else:
            pass

    return redirect("/all_students")

@app.route('/login')
def display_login():
    return render_template(
        "login.html"
    )

@app.route("/submit_login", methods=["POST"])
def submit_login():
    email = request.form.get('email')
    password = request.form.get('password')
    query = db.query("select * from users where email = $1", email)
    result_list = query.namedresult()
    print "result_list: %s\n\n\n" % result_list
    if len(result_list) > 0:
        user = result_list[0]
        if user.password == password:
            session['first_name'] = user.first_name
            session['email'] = user.email
            session['id'] = user.id
            flash("%s, you have successfully logged into the application" % email)
            return redirect('/student_profile/%d' % user.id)
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@app.route("/submit_logout", methods = ["POST"])
def submit_logout():
    del session['first_name']
    del session['email']
    del session['id']
    return redirect("/")


@app.route("/search_user", methods=["POST"])
def search_user():

    name = request.form.get('search_bar')
    split_name = name.split()
    name_length = len(name)
    split_name_length = len(split_name)
    first_name_to_search = "%"+split_name[0]+"%"
    if name_length >= 3:
        if split_name_length >= 2:
            last_name_to_search = "%"+split_name[1]+"%"
            query = db.query("select * from users where (first_name ilike $1 or last_name ilike $2)", (first_name_to_search, last_name_to_search))
            result_list = query.namedresult()
            if len(result_list) == 1:
                return redirect('/student_profile/%d' % result_list[0])
            elif len(result_list) >= 2:
                return render_template(
                    "disambiguation.html",
                    result_list = return_list
                    )
            else:
                return redirect('/')

        elif split_name_length <= 1:
            query = db.query("select * from users where (first_name ilike $1 or last_name ilike $1)", first_name_to_search)
            result_list = query.namedresult()
            if len(result_list) == 1:
                return redirect('/student_profile/%d' % result_list[0].id)
            elif len(result_list) >= 2:
                return render_template(
                    "disambiguation.html",
                    result_list = result_list
                    )
            else:
                return redirect('/')
    else:
        return redirect('/')




    #name = request.form.get('search_bar')
    #print "\n\nname before split %s \n\n" % name
    #name = name.split()
    #print "\n\nname after split %s \n\n" % name
    #name_length = len(name)
    #print "\n\nname_length %s \n\n" % name_length
    #name_to_search = "%"+name+"%"
    #if name_length >= 3:
        #query = db.query("select id from users where (first_name ilike $1 or last_name ilike $1)", name_to_search)
        #result_list = query.namedresult()
        #if len(result_list) > 0:
            #return redirect('/student_profile/%d' % result_list[0])
        #else:
            #return redirect('/')
    #else:
        #return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
