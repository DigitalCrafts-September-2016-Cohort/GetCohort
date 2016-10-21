from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
import pg, os
from werkzeug import secure_filename

db = pg.DB(
    dbname=os.environ.get("PG_DBNAME"),
    host=os.environ.get("PG_HOST"),
    user=os.environ.get("PG_USERNAME"),
    passwd=os.environ.get("PG_PASSWORD")
)


db.debug = True

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask("Get Cohort", template_folder = tmp_dir)

app.config['UPLOAD_FOLDER'] = './static/images'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.secret_key = os.environ.get("SECRET_KEY")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



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

# Route might not be needed. Will delete later
# @app.route('/profile')
# def student_profile_login():
#     name = request.form.get('name')
#
#     return redirect('/layout.html')

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
        cohort_list = cohort_list,
    )

@app.route('/profile/<id>')
def profile(id):
    query = db.query('''
        select
        	id,
        	first_name,
        	last_name,
        	email,
        	web_page,
        	github,
        	bio,
        	users.password,
            current_location
        from
        	users
        where users.id = $1;
    ''', id)
    result_list = query.namedresult()
    project_query = db.query('''
        select
            project.name,
            project.id
        from
            users,
            users_link_project,
            project
        where
            users.id = users_link_project.users_id and users_link_project.project_id = project.id and
            users.id = $1;
    ''', id).namedresult()
    skill_query = db.query('''
        select
            name,
            skill.id
        from
            users,
            users_link_skill,
            skill
        where
            users.id = users_link_skill.users_id and users_link_skill.skill_id = skill.id and users.id = $1;
    ''', id).namedresult()
    return render_template(
        "profile.html",
        user = result_list[0],
        project_query = project_query,
        skill_query = skill_query
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

@app.route("/submit_login", methods=["POST"])
def submit_login():
    email = request.form.get('email')
    password = request.form.get('password')
    query = db.query("select * from users where email = $1", email)
    admin_query = db.query('''
    select
    	users.email,
    	user_type.type
    from
    	users,
    	users_link_type,
    	user_type
    where
    	users.id = users_link_type.user_id and
    	users_link_type.user_type_id = user_type.id
    	and user_type.type = 'Admin';
    ''')
    result_list = query.namedresult()
    admin_list = admin_query.namedresult()
    print "result_list: %s\n\n\n" % result_list
    if len(result_list) > 0:
        user = result_list[0]
        if user.password == password:
            session['first_name'] = user.first_name
            session['email'] = user.email
            session['id'] = user.id
            #new session variable
            for entry in admin_list:
                if entry.email == session['email']:
                    session['is_admin'] = True
                else:
                    session['is_admin'] = False
            flash("%s, you have successfully logged into the application" % session["first_name"])
            return redirect('/profile/%d' % user.id)
        else:
            return redirect("/")
    else:
        return redirect("/")

@app.route("/submit_logout", methods = ["POST"])
def submit_logout():
    del session['first_name']
    del session['email']
    del session['id']
    del session['is_admin']
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
                return redirect('/profile/%d' % result_list[0])
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
                return redirect('/profile/%d' % result_list[0].id)
            elif len(result_list) >= 2:
                return render_template(
                    "disambiguation.html",
                    result_list = result_list
                    )
            else:
                return redirect('/')
    else:
        return redirect('/')

@app.route("/all_projects")
def all_projects():
    query = db.query("select * from project;")
    project_list = query.namedresult()
    return render_template(
        "all_projects.html",
        project_list = project_list
    )

@app.route("/project_profile/<id>")
def project_profile(id):
    query_projects = db.query("select * from project where id = $1;", id)
    print "This is the query %s:" % query_projects
    project_list = query_projects.namedresult()
    print "This is the project list %s:" % project_list
    query_skills = db.query("""
        select
        	project.id as project_identifier,
        	project.name as project_name,
        	project.link,
        	project.image,
        	project.description,
        	skill.id as skill_identifier,
        	skill.name as skill_name,
        	project_link_skill.project_id,
        	project_link_skill.skill_id
        from
            project,
            skill,
            project_link_skill
        where
        	project.id = project_link_skill.project_id and
        	skill.id = project_link_skill.skill_id and
        	project.id = $1
        ;""", id)
    skills = query_skills.namedresult()
    query_contributors = db.query("""
        select
            users.first_name,
            users.last_name,
            project.name as project_name,
            users_link_project.users_id as users_link_id,
            users_link_project.project_id as project_link_id
        from
            users,
            project,
            users_link_project
        where
            users.id = users_link_project.users_id and
            project.id = users_link_project.project_id and
            project.id = $1
        ;""", id)
    contributors = query_contributors.namedresult()
    return render_template(
        "project_profile.html",
        project = project_list[0],
        skills = skills,
        contributors = contributors
    )


@app.route('/upload', methods=['POST'])
def upload():
    # user_id = request.form.get("id")
    # user_id = int(user_id)
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    print "we're uploading"
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basically show on the browser the uploaded file
        print "we uploaded?"
        return redirect('/'
            # filename=filename
        )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
        filename)

@app.route('/profile/upload', methods=['POST'])
def profile_upload():
    print "did we upload?"
    return redirect('/all_students'
        )

if __name__ == "__main__":
    app.run(debug=True)
