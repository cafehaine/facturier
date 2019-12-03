import argparse
import json
from datetime import date

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from facturier import entities
from facturier import tui

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands')
    reg_parser = subparsers.add_parser('register',
                                       aliases=['reg', 'r'],
                                       help="Register a client or a new bill.")
    list_parser = subparsers.add_parser('list',
                                        aliases=['l'],
                                        help="List clients or bills.")
    gen_parser = subparsers.add_parser(
        'generate',
        aliases=['gen', 'g'],
        help="Generate a pdf for one or many bills.")
    args = parser.parse_args()
    print(args)

    #TODO Demo code
    # remove when DB bindings are working, and cli is implemented
    entities.DB.bind(provider='sqlite', filename=':memory:')
    entities.DB.generate_mapping(create_tables=True)
    entities.generateRandomClients()
    from pony.orm import db_session
    with db_session():
        entities.Client.select().show()
    tui.new_bill()

    env = Environment(loader=FileSystemLoader('.'), autoescape=True)

    template = env.get_template('template.html')
    with open('config.json') as config:
        own = json.load(config)
    rendered_html = template.render(own=own,
                                    bill={
                                        'date': date.today(),
                                        'id': 42,
                                        'total': 50
                                    },
                                    client=own)
    css = CSS('style.css')
    HTML(string=rendered_html).write_pdf('/tmp/template.pdf',
                                         stylesheets=[css])
