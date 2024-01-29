import os
from flask import Flask, render_template, request, flash
from database.keywords import TechKeywords, ENGINE, Keywords
from source.tech_words import upload_data
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField

app = Flask(__name__)
app.config['SECRET_KEY'] = "This is my Content search app"
app.config['UPLOAD_FOLDER'] = "static_files"

@app.context_processor
def base():
    form = SearchKeywordForm()
    return dict(form=form)
class AddKeywordForm(FlaskForm):
    keyword = StringField('Keyword')
    tech_words = StringField('Tech_words')
    save = SubmitField("Save")

class SearchKeywordForm(FlaskForm):
    keyword = StringField('Keyword')
    submit = SubmitField("Search")

@app.route('/')
def home():
    # dbase = TechKeywords()
    keywords = [] #dbase.get_data()
    return render_template('index_home.html', keywords_=keywords)


@app.route('/test')
def testing():
    flash("Server is Running", category='success')
    return render_template('test.html')


@app.route('/search', methods=['GET'])
def search():
    print(f"\n\n\n*******************\n\t\t{request.args}\n*******************")
    query_ = request.args.get("q", None)
    dbase = TechKeywords()
    if query_ == '':
        result = dbase.get_data()
    else:
        result = dbase.find(keyword_=query_.lower())
    return render_template('index_home.html', keywords_=result)


@app.route('/new_search', methods=['GET', 'POST'])
def new_search():
    print(f"\n\n\n*******************\n\t\t{request.args}\n*******************")
    form = SearchKeywordForm()
    if form.validate_on_submit():
        query_ = form.keyword.data
    # query_ = request.args.get("q", None)
        dbase = TechKeywords()
        if query_ == '':
            result = dbase.get_data()
        else:
            result = dbase.find(keyword_=query_.lower())
        return render_template('index_home.html', keywords_=result, form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = None if request.form.get("csv_file") == '' else request.form.get("csv_file")
        if file:
            res, status = upload_data(file)
            if status == 200:
                flash(f"Successfully Uploaded the {file}'s data", category='success')
            else:
                flash(res, category='error')
            return render_template('upload.html')
        else:
            flash("Please choose a file", category='error')
    return render_template('upload.html')


@app.route('/create_db')
# @login_required
def create_db():
    try:
        dbase = TechKeywords()
        dbase.create_db()
        return "<h1> Database created</h1>"
    except Exception as e:
        return render_template(f'Failed due to {e}')


@app.route('/add_keyword', methods=['GET', 'POST'])
def add_keyword():
    form = AddKeywordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            keyword = form.keyword.data.lower()
            tech_words = form.tech_words.data.lower().split(',')
            dbase = TechKeywords()
            try:
                record = dbase.find(keyword_=keyword)
                if record:
                    existing_words = record[0]['tech_words'].split(',')
                    existing_words += tech_words
                    existing_words = [x.strip() for x in existing_words if x != '']
                    dbase.update(keyword_=record[0]['keyword'], tech_words=', '.join(set(existing_words)))
                    flash(f"Successfully Updated the keyword {keyword}", category="success")
                else:
                    dbase.add_keyword(keyword_=keyword, tech_words=form.tech_words.data.lower())
                    flash(f"Successfully Added the keyword {keyword}", category="success")
            except:
                flash("Error while storing", category="error")

    return render_template('add_keyword.html', form=form)


@app.route('/delete_keyword', methods=['GET', 'POST'])
def delete_keyword():
    form = AddKeywordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            keyword = form.keyword.data.lower().split(',')
            dbase = TechKeywords()
            try:
                dbase.delete_keywords(keywords=keyword)
                flash(f"Successfully Deleted the keyword {keyword}", category="success")
            except Exception as e:

                flash(f"{e}", category="error")

    return render_template('delete_keyword.html', form=form)


@app.route('/delete_tech_words', methods=['GET', 'POST'])
def delete_tech_words():
    form = AddKeywordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            keyword = form.keyword.data.lower().strip()
            tech_words = form.tech_words.data.lower().split(',')
            tech_words = [x.strip() for x in tech_words]
            dbase = TechKeywords()
            try:
                record = dbase.find(keyword_=keyword)
                if record:
                    existing_words = [x.strip() for x in record[0]['tech_words'].split(',')]
                    for word in tech_words:
                        if word in existing_words:
                            existing_words.remove(word)
                    dbase.update(keyword_=keyword, tech_words=', '.join(existing_words))

                    flash(f"Successfully Deleted Synonyms {tech_words} for keyword {keyword}", category="success")
            except Exception as e:

                flash(f"{e}", category="error")

    return render_template('delete_tech_words.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, port=5006)
