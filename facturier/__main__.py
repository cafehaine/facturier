import argparse
import json
from datetime import date
import sys

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

from facturier import entities
from facturier import tui

def handle_create(**kwargs):
    print(kwargs)

def handle_list(**kwargs):
    print(kwargs)

def handle_generate(**kwargs):
    print(kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands')

    # Create new client or bill
    create_parser = subparsers.add_parser('create',
                                          aliases=['c'],
                                          help="Create a client or a new bill.")
    create_parser.set_defaults(func=handle_create)
    create_parser.add_argument('type',
                               nargs=1,
                               choices=['client', 'c', 'bill', 'b'])

    # List clients or bills
    list_parser = subparsers.add_parser('list',
                                        aliases=['l'],
                                        help="List clients or bills.")
    list_parser.set_defaults(func=handle_list)
    list_parser.add_argument('type',
                             nargs=1,
                             choices=['client', 'c', 'bill', 'b'])

    # Generate a bill's PDF
    gen_parser = subparsers.add_parser(
        'generate',
        aliases=['gen', 'g'],
        help="Generate a pdf for one or many bills.")
    gen_parser.set_defaults(func=handle_generate)

    namespace = vars(parser.parse_args())
    if 'func' not in namespace:
        parser.print_help()
        sys.exit()
    namespace['func'](**namespace)

    #TODO Demo code
    # remove when DB bindings are working, and cli is implemented
    #entities.DB.bind(provider='sqlite', filename=':memory:')
    #entities.DB.generate_mapping(create_tables=True)
    #entities.generateRandomClients()
    #tui.new_bill()

    #env = Environment(loader=FileSystemLoader('.'), autoescape=True)

    #template = env.get_template('template.html')
    #with open('config.json') as config:
    #    own = json.load(config)
    #rendered_html = template.render(own=own,
    #                                bill={
    #                                    'date': date.today(),
    #                                    'id': 42,
    #                                    'total': 50
    #                                },
    #                                client=own)
    #css = CSS('style.css')
    #HTML(string=rendered_html).write_pdf('/tmp/template.pdf',
    #                                     stylesheets=[css])
