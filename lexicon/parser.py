"""Parsers definition for the Lexicon command-line interface"""
import argparse
import importlib
import os

from lexicon import discovery


def generate_base_provider_parser():
    """Function that generates the base provider to be used by all dns providers."""
    # Provider parser.
    parser = argparse.ArgumentParser(add_help=False)

    # Create a subparser for the action arguments so we can specify different requirements for each.
    action_subparsers = parser.add_subparsers(dest='action')

    create_domain_parser = action_subparsers.add_parser('create_domain', help='Create a domain zone')
    create_domain_parser.add_argument('domain', help='specify the domain')
    create_domain_parser.add_argument('--email_address', help='specify the domain email address (required)', required=True)
    create_domain_parser.add_argument('--ttl', type=int, help='specify the record time-to-live')

    delete_domain_parser = action_subparsers.add_parser('delete_domain', help='Delete a domain zone')
    delete_domain_parser.add_argument('domain', help='specify the domain, supports subdomains as well')

    create_parser = action_subparsers.add_parser('create', help='Create a domain record')
    create_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    create_parser.add_argument('type', help='specify the entry type (exclude to create a new domain)', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    create_parser.add_argument('--name', help='specify the record name (required)', required=True)
    create_parser.add_argument('--content', help='specify the record content (required)', required=True)
    create_parser.add_argument('--priority', help='specify the record priority (required for MX and SRV types)')
    create_parser.add_argument('--ttl', type=int, help='specify the record time-to-live')

    list_parser = action_subparsers.add_parser('list', help='List all domains or the records in a specified domain')
    list_parser.add_argument('domain', help='specify the domain, supports subdomains as well (optional)', nargs='?')
    list_parser.add_argument('type', help='specify the entry type (optional)', type=str.upper, nargs='?', choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    list_parser.add_argument('--name', help='specify the record name (optional)')

    update_parser = action_subparsers.add_parser('update', help='Update a domain record')
    update_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    update_parser.add_argument('type', help='specify the entry type', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    update_parser.add_argument('--name', help='specify the record name (required)', required=True)
    update_parser.add_argument('--content', help='specify the record content (required)', required=True)
    update_parser.add_argument('--identifier', help='specify the ID of the record to update')
    update_parser.add_argument('--priority', help='specify the record priority (required for MX and SRV types)')
    update_parser.add_argument('--ttl', type=int, help='specify the record time-to-live')

    delete_parser = action_subparsers.add_parser('delete', help='Delete a domain record')
    delete_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    delete_parser.add_argument('type', help='specify the entry type', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    delete_parser.add_argument('--name', help='specify the record name')
    delete_parser.add_argument('--content', help='specify the record content')
    delete_parser.add_argument('--identifier', help='specify the ID of the record to delete')

    return parser


def generate_cli_main_parser():
    """Using all providers available, generate a parser that will be used by Lexicon CLI"""
    parser = argparse.ArgumentParser(
        description='Create, Update, Delete, List DNS entries')

    parser.add_argument('--version', help='show the current version of lexicon',
                        action='version', version='%(prog)s {0}'
                        .format(discovery.lexicon_version()))
    parser.add_argument('--delegated', help='specify the delegated domain')
    parser.add_argument('--log_level', help='specify the log level', default='ERROR',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])
    parser.add_argument('--output',
                        help=('specify the type of output: by default a formatted table (TABLE), '
                              'a formatted table without header (TABLE-NO-HEADER), '
                              'a JSON string (JSON) or no output (QUIET)'),
                        default='TABLE', choices=['TABLE', 'TABLE-NO-HEADER', 'JSON', 'QUIET'])
    parser.add_argument('--config-dir', default=os.getcwd(),
                        help='specify the directory where to search lexicon.yml and '
                             'lexicon_[provider].yml configuration files '
                             '(default: current directory).')
    subparsers = parser.add_subparsers(
        dest='provider_name', help='specify the DNS provider to use')
    subparsers.required = True

    for provider, available in discovery.find_providers().items():
        provider_module = importlib.import_module(
            'lexicon.providers.' + provider)
        provider_parser = getattr(provider_module, 'provider_parser')

        subparser = subparsers.add_parser(provider, help='{0} provider'.format(provider),
                                          parents=[generate_base_provider_parser()])
        provider_parser(subparser)

        if not available:
            subparser.epilog = ('WARNING: some required dependencies for this provider are not '
                                'installed. Please install lexicon[{0}] first before using it.'
                                .format(provider))

    return parser
