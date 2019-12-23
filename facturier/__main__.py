import argparse
import json
from datetime import date
import sys

from jinja2 import Environment, FileSystemLoader
from pony.orm import db_session
from pony.orm.core import ObjectNotFound
from weasyprint import CSS, HTML

from facturier import entities
from facturier import tui


def handle_create(**kwargs):
    """Show forms to create new clients or bills."""
    if kwargs['type'][0] in ['client', 'c']:
        tui.new_client()
    else:
        tui.new_bill()


def handle_list(**kwargs):
    """List all users or bills."""
    with db_session:
        if kwargs['type'][0] in ['clients', 'c']:
            entities.Client.select().show()
        else:
            entities.Bill.select().show()


def handle_generate(**kwargs):
    """Generate the pdf output for a bill if it exists."""
    bill = None
    client = None
    bill_id = kwargs['id'][0]
    with db_session:
        try:
            bill = entities.Bill[bill_id]
            client = bill.client
        except ObjectNotFound:
            print("Bill with id {} not found.".format(bill_id))
            sys.exit(1)

    output_path = "/tmp/template.pdf"

    env = Environment(loader=FileSystemLoader('.'), autoescape=True)
    css = CSS('style.css')
    template = env.get_template('template.html')

    with open('config.json') as config:
        own = json.load(config)

    rendered_html = template.render(own=own, bill=bill, client=client)
    HTML(string=rendered_html).write_pdf(output_path, stylesheets=[css])
    print("Rendered bill as '{}'.".format(output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands')

    # Create new client or bill
    create_parser = subparsers.add_parser(
        'create', aliases=['c'], help="Create a client or a new bill.")
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
                             choices=['clients', 'c', 'bills', 'b'])

    # Generate a bill's PDF
    gen_parser = subparsers.add_parser(
        'generate',
        aliases=['gen', 'g'],
        help="Generate a pdf for one or many bills.")
    gen_parser.set_defaults(func=handle_generate)
    gen_parser.add_argument('id', nargs=1, type=int)

    namespace = vars(parser.parse_args())
    if 'func' not in namespace:
        parser.print_help()
        sys.exit()

    entities.DB.bind(provider='sqlite', filename='db.sqlite', create_db=True)
    entities.DB.generate_mapping(create_tables=True)
    namespace['func'](**namespace)
