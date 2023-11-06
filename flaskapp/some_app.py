from flask import Flask
from flask import render_template
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import net as neuronet
from flask import request
from flask import Response
import base64
from PIL import Image
from io import BytesIO
import json
import lxml.etree as ET
import glob
import cv2
from noise_elimination import color_distribution, apply_gaussian_blur, generate_noise_histogram, apply_median_blur

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
bootstrap = Bootstrap(app)

def generate_table_of_contents(app):
    routes = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and "static" not in rule.rule:
            endpoint = rule.endpoint
            path = rule.rule
            if endpoint != "static":
                routes.append((endpoint, path))

    table_of_contents = "<h1>List of Pages (Task variation 1)</h1><ul>"
    for endpoint, path in routes:
        table_of_contents += f'<li><a href="{path}">{endpoint}</a></li>'
    table_of_contents += "</ul>"

    return table_of_contents


@app.route("/data_to")
def data_to():
    some_pars = {'user':'Ivan','color':'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html',some_str = some_str, some_value = some_value,some_pars=some_pars)


class NetForm(FlaskForm):
    method = SelectField('Select Blurring Method', choices=[('gaussian', 'Gaussian Blur'), ('median', 'Median Blur')])
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    recaptcha = RecaptchaField()
    submit = SubmitField('send')

#@app.route("/net",methods=['GET', 'POST'])
#def net():
#    form = NetForm()
#    filename=None
#    neurodic = {}
#    if form.validate_on_submit():
#        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
#        fcount, fimage = neuronet.read_image_files(10,'./static')
#        decode = neuronet.getresult(fimage)
#        for elem in decode:
#            neurodic[elem[0][1]] = elem[0][2]
#        form.upload.data.save(filename)
#    return render_template('net.html',form=form,image_name=filename,neurodic=neurodic)

@app.route("/apinet",methods=['GET', 'POST'])
def apinet():
    if request.mimetype == 'application/json':
       data = request.get_json()
       filebytes = data['imagebin'].encode('utf-8')
       cfile = base64.b64decode(filebytes)
       img = Image.open(BytesIO(cfile))
       decode = neuronet.getresult([img])
       neurodic = {}
       for elem in decode:
           neurodic[elem[0][1]] = str(elem[0][2])
           print(elem)
       ret = json.dumps(neurodic)
       resp = Response(response=ret,
                   status = 200,
                   mimetype = "application/json")
       return resp

@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile


@app.route("/bluring", methods=['GET', 'POST'])
def bluring():
    form = NetForm()
    filename = None
    smoothed_image_filename = None
    color_histogram_filename = None
    noise_histogram_filename = None
    img_proc_dir = './static/imgs_processing'

    if not os.path.exists(img_proc_dir):
        os.makedirs(img_proc_dir)
    else:
        for fname in glob.glob(f'{img_proc_dir}/*'):
            os.remove(fname)

    if form.validate_on_submit():
        filename = os.path.join(img_proc_dir, secure_filename(form.upload.data.filename))
        form.upload.data.save(filename)
        image = cv2.imread(filename)
        selected_method = (form.method.data)
        if selected_method == "gaussian":
            smoothed_image = apply_gaussian_blur(image)
        elif selected_method == "median":
            smoothed_image = apply_median_blur(image)
        smoothed_image_filename = f'{img_proc_dir}/result_' \
                       f'{form.upload.data.filename}'
        cv2.imwrite(smoothed_image_filename, smoothed_image)

        color_histogram_filename = f'{img_proc_dir}/color_' \
                       f'{form.upload.data.filename}'
        color_distribution(image,color_histogram_filename)

        noise_histogram_filename = f'{img_proc_dir}/noise_' \
                                   f'{form.upload.data.filename}'
        generate_noise_histogram(image, smoothed_image, noise_histogram_filename)

    return render_template('images.html', form=form, image=filename,
                           smoothed_image=smoothed_image_filename,
                           color_histogram=color_histogram_filename,
                           noise_histogram=noise_histogram_filename)

@app.route("/")
def hello():
    return """
    <html>
    <head></head>
    <body>
    {}
    <h1>Hello World!</h1>
    </body>
    </html>
    """.format(generate_table_of_contents(app))

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000)