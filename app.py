from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle
import statistics
from collections import Counter
from sqlalchemy.orm import load_only

app = Flask(__name__,template_folder='Templates')

app.secret_key = "some_password"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///FormDataTest.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFIACTIONS"] = True

db = SQLAlchemy(app)


class OrderedCounter(Counter, dict):
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self))

    def __reduce__(self):
        return self.__class__, (dict(self),)


class FormData(db.Model):
    __tablename__ = 'formdata'
    _id = db.Column("id", db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    _ip = db.Column(db.Integer)

    email = db.Column(db.String(100))
    is_student = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    hours_comp = db.Column(db.String(20))
    hours_comp_before = db.Column(db.String(20))
    consequences = db.Column(db.PickleType())
    defect = db.Column(db.String(25))
    glasses = db.Column(db.String(25))
    oculist = db.Column(db.String(25))
    eye_pain = db.Column(db.Integer)
    head_pain = db.Column(db.Integer)
    breaks = db.Column(db.String(10))
    droplets = db.Column(db.String(10))

    def __init__(self, is_student, sex, hours_comp, hours_comp_before, consequences, defect, glasses, oculist, eye_pain,
                 head_pain, breaks, droplets):
        self._ip = get_ip()

        self.is_student = is_student
        self.sex = sex
        self.hours_comp = hours_comp
        self.hours_comp_before = hours_comp_before
        self.consequences = consequences
        self.defect = defect
        self.glasses = glasses
        self.oculist = oculist
        self.eye_pain = eye_pain
        self.head_pain = head_pain
        self.breaks = breaks
        self.droplets = droplets

    def get(self, attr_name):
        return getattr(self, attr_name)


# @app.route('/get_ip', methods=['GET'])
def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR']

    return ip
    # return jsonify({'ip': ip}), 200


@app.route("/")
def welcome():
    return render_template('._welcome.html')


@app.route("/form")
def form():
    users_ip = db.session.query(FormData._ip).all()
    current_user = get_ip()
    for i in range(len(users_ip)):
        if current_user in users_ip[i][0]:
            flash("Formularz został już przez Ciebie wypełniony!", "info")
            return redirect(url_for("results"))

    return render_template('._form.html')


@app.route("/raw")
def raw():
    users_data = db.session.query(FormData).all()
    if request.remote_addr == "83.22.206.218":
        return render_template('._raw.html', formdata=users_data)
    else:
        flash("Nie posiadasz uprawnień, żeby wyświetlić zawartość tej strony!")
        return render_template('._raw.html', formdata=False)


@app.route("/form", methods=['POST'])
def save():
    try:
        is_student = request.form['studentStatus']
        sex = request.form['gender']
        hours_comp = request.form['screenTime']
        hours_comp_before = request.form['screenTime2']

        consequences_list = request.form.getlist('consequence[]')
        consequences = pickle.dumps(consequences_list)

        defect = request.form['visionProblems']
        glasses = request.form['glasses']
        oculist = request.form['oculist']
        eye_pain = request.form['eyePain']
        head_pain = request.form['headache']
        breaks = request.form['computerBreaks']
        droplets = request.form['eyeDrops']

        if not is_student == "no":
            user_data = FormData(is_student, sex, hours_comp, hours_comp_before, consequences, defect, glasses, oculist,
                                 eye_pain, head_pain, breaks, droplets)
            db.session.add(user_data)
            db.session.commit()
            flash("Formularz został wypełniony prawidłowo!\nPrzejdź do wyników", 'info')
            return redirect('/')
        else:
            flash("Nie jesteś studentem - Twoje odpowiedzi nie zostały zapisane!", 'error')
            return redirect(url_for("form"))

    except Exception:
        flash("Błędnie wypełniony formularz! Spróbuj jeszcze raz.", 'error')
        return redirect(url_for("form"))


@app.route('/results')
def results():
    percentages_all = []
    fields = ["sex", "hours_comp", "hours_comp_before", "consequences", "defect", "glasses", "oculist", "eye_pain",
              "head_pain", "breaks", "droplets"]

    for name in fields:
        if name != "consequences":
            column = db.session.query(FormData).options(load_only(name)).all()
            test = [i.get(name) for i in column]
            count = list(OrderedCounter(test).values())
            print(test)
        else:
            users_data = db.session.query(FormData).all()
            cons_final = []
            for i in range(len(users_data)):
                cons = pickle.loads(users_data[i].consequences)
                cons_final.extend(cons)

            count = list(OrderedCounter(cons_final).values())
        percentages = [int(float(y) / len(test) * 100) for y in count]
        percentages_all.append(percentages)

    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))  # to jeszcze do wypróbowania

    return render_template('._result.html', data=percentages_all)


@app.route("/charts")
def charts():
    counts_all = []
    fields = ["sex", "hours_comp", "hours_comp_before",
              "consequences", "defect", "glasses", "oculist",
              "eye_pain", "head_pain", "breaks", "droplets"]

    for name in fields:
        if name != "consequences":
            column = db.session.query(FormData).options(load_only(name)).all()
            test = [i.get(name) for i in column]
            count = list(OrderedCounter(test).values())
        else:
            users_data = db.session.query(FormData).all()
            cons_final = []
            for i in range(len(users_data)):
                cons = pickle.loads(users_data[i].consequences)
                cons_final.extend(cons)

            count = list(OrderedCounter(cons_final).values())
        counts_all.append(count)

    return render_template('._charts.html', data=counts_all)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)