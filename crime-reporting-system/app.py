#!/usr/bin/env python3.9 
from flask import Flask, render_template, redirect, url_for 

app = Flask(__name__)
app.debug = True 
@app.route('/')
@app.route('/home')
def home():
    ''' This Funcation renders the home page '''
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    '''This funcation renders the aboutus page ''' 
    return "<h1>This is a about Us page</h1>"

@app.route('/contactus')
def contactus():
    '''This fincation will render the contact us page'''
    return "<h1><i>This is contact us Page</i></h1>"

@app.route('/login')
def login():
    '''This page is for login '''
    return "<center>This is login page </center>"

@app.route('/signup')
def signup():
    '''This will redirect signup page '''
    return "<h1><center>Signup Form</center></h1>"    

if __name__ == "__main__" :
    app.run(host='localhost',port=5000)
