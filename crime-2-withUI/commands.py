import click
from flask.cli import with_appcontext

from report import db
from report.models import User, Report

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
