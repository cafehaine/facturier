import argparse
import json
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


def handle_edit(**kwargs):
    """Show forms to edit an existing client or bill."""
    if kwargs['type'][0] in ['client', 'c']:
        client = None
        client_id = kwargs['id'][0]
        with db_session:
            try:
                client = entities.Client[client_id]
            except ObjectNotFound:
                print("Client with id {} not found.".format(client_id))
                sys.exit(1)
            tui.edit_client(client)
    else:
        bill = None
        bill_id = kwargs['id'][0]
        with db_session:
            try:
                bill = entities.Bill[bill_id]
            except ObjectNotFound:
                print("Bill with id {} not found.".format(bill_id))
                sys.exit(1)
            tui.edit_bill(bill)


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
    bill_id = kwargs['id'][0]
    with db_session:
        try:
            bill = entities.Bill[bill_id]
        except ObjectNotFound:
            print("Bill with id {} not found.".format(bill_id))
            sys.exit(1)

        output_path = "/tmp/template.pdf"

        env = Environment(loader=FileSystemLoader('.'), autoescape=True)
        css = CSS('style.css')
        if kwargs['type'][0] in ['bill', 'b']:
            template = env.get_template('bill.html')
        else:
            template = env.get_template('quote.html')

        with open('config.json') as config:
            own = json.load(config)

        rendered_html = template.render(own=own, bill=bill)
        HTML(string=rendered_html).write_pdf(output_path, stylesheets=[css])
        print("Rendered bill as '{}'.".format(output_path))


def create_parser():
    """Create the argument parser for the main."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands')

    # Create new client or bill
    create_prsr = subparsers.add_parser('create',
                                        aliases=['c'],
                                        help="Create a client or a new bill.")
    create_prsr.set_defaults(func=handle_create)
    create_prsr.add_argument('type',
                             nargs=1,
                             choices=['client', 'c', 'bill', 'b'])

    # Edit a client or bill
    edit_prsr = subparsers.add_parser('edit',
                                      aliases=['e'],
                                      help="Edit a client or bill.")
    edit_prsr.set_defaults(func=handle_edit)
    edit_prsr.add_argument('type',
                           nargs=1,
                           choices=['client', 'c', 'bill', 'b'])
    edit_prsr.add_argument('id', nargs=1, type=int)

    # List clients or bills
    list_prsr = subparsers.add_parser('list',
                                      aliases=['l'],
                                      help="List clients or bills.")
    list_prsr.set_defaults(func=handle_list)
    list_prsr.add_argument('type',
                           nargs=1,
                           choices=['clients', 'c', 'bills', 'b'])

    # Generate a bill's PDF
    gen_prsr = subparsers.add_parser(
        'generate',
        aliases=['gen', 'g'],
        help="Generate a pdf for a bill or a quote.")
    gen_prsr.set_defaults(func=handle_generate)
    gen_prsr.add_argument('type',
                          nargs=1,
                          choices=['bill', 'b', 'quote', 'q'])

    gen_prsr.add_argument('id', nargs=1, type=int)
    return parser


def main():
    """Main code."""
    parser = create_parser()
    namespace = vars(parser.parse_args())

    if 'func' not in namespace:
        parser.print_help()
        sys.exit()

    entities.DB.bind(provider='sqlite', filename='db.sqlite', create_db=True)
    entities.DB.generate_mapping(create_tables=True)
    namespace['func'](**namespace)


if __name__ == "__main__":
    main()
