# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

from flask import Flask, redirect, render_template, request, session

import pg, os
# tmp_dir = os.path.join(os.path.abspath(__file__)), 'templates')
# app = Flask("Get Cohort", template_folder=tmp_dir)
app = Flask("Get Cohort")
# db = pg.DB(
#     dbname=os.environ.get('PG_DBNAME'),
#     host=os.environ.get('PG_HOST'),
#     user=os.environ.get('PG_USERNAME'),
#     passwd=os.environ.get('PG_PASSWORD')
# )

db = pg.DB(dbname = 'getcohort_db')
db.debug = True



app.secret_key = "whatever"

@app.route('/')
def home():
    return render_template(
        "index.html"
    )

@app.route('/all_students')
def all_students():
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
        	cohort.name = 'September 2016' and
        	user_type.type = 'Student'
        ;
    '''
    )
    result_list = query.namedresult()
    print result_list
    return render_template(
        "all_students.html",
        result_list = result_list
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
    print result_list
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



if __name__ == "__main__":
    app.run(debug=True)
