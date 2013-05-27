from flask.ext.script import Manager

from app import app
from db import mongo
from scrap import (
    scrap_arena_flowers_xml, scrap_arena_flowers_sitemap,
    scrap_clare_florist)

manager = Manager(app)


@manager.command
def clear():
    mongo.db.flower.remove()


@manager.command
def setup_search():
    from pymongo import Connection
    connection = Connection()
    connection.admin.command(
        {
            'setParameter': "*",
            'textSearchEnabled': True
        }
    )
    mongo.db.flower.create_index(
        [
            ('name', 'text'),
            ('description', 'text'),
        ],
        weight={
            'name': 2,
            'description': 1,
        }
    )


@manager.command
def scrap():
    scrap_arena_flowers_xml()
    scrap_arena_flowers_sitemap()
    scrap_clare_florist()

if __name__ == "__main__":
    manager.run()
