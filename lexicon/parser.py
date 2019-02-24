"""Parsers definition for the Lexicon command-line interface"""
import argparse
import importlib
import pkgutil

import pkg_resources
from lexicon import providers as providers_package


def generate_base_provider_parser():
    """Function that generates the base provider to be used by all dns providers."""

    # parser.add_argument('action', help='specify the action to take', default='list', choices=['create', 'list', 'update', 'delete'])

    global_provider_parser = argparse.ArgumentParser(add_help=False)
    global_provider_parser.add_argument('--ttl', type=int, help='specify the record time-to-live')
    global_provider_parser.add_argument('--log_level', help='specify the log level', default='ERROR', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])
    global_provider_parser.add_argument('--output', help=('specify the type of output: by default a formatted table (TABLE), a formatted table without header (TABLE-NO-HEADER), a JSON string (JSON) or no output (QUIET)'), default='TABLE', choices=['TABLE', 'TABLE-NO-HEADER', 'JSON', 'QUIET'])

    # Provider parser.
    parser = argparse.ArgumentParser(add_help=False)

    # Create a subparser for the action arguments so we can specify different requirements for each.
    action_subparsers = parser.add_subparsers(dest='action')

    create_domain_parser = action_subparsers.add_parser('create_domain', help='Create a domain zone', parents=[global_provider_parser])
    create_domain_parser.add_argument('domain', help='specify the domain')
    create_domain_parser.add_argument('--email_address', help='specify the domain email address (required)', required=True)

    delete_domain_parser = action_subparsers.add_parser('delete_domain', help='Delete a domain zone', parents=[global_provider_parser])
    delete_domain_parser.add_argument('domain', help='specify the domain, supports subdomains as well')

    create_parser = action_subparsers.add_parser('create', help='Create a domain record', parents=[global_provider_parser])
    create_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    create_parser.add_argument('type', help='specify the entry type (exclude to create a new domain)', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    create_parser.add_argument('--name', help='specify the record name (required)', required=True)
    create_parser.add_argument('--content', help='specify the record content (required)', required=True)
    create_parser.add_argument('--priority', help='specify the record priority (required for MX and SRV types)')

    list_parser = action_subparsers.add_parser('list', help='List all domains or the records in a specified domain', parents=[global_provider_parser])
    list_parser.add_argument('domain', help='specify the domain, supports subdomains as well (optional)', nargs='?')
    list_parser.add_argument('type', help='specify the entry type (optional)', type=str.upper, nargs='?', choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])

    update_parser = action_subparsers.add_parser('update', help='Update a domain record', parents=[global_provider_parser])
    update_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    update_parser.add_argument('type', help='specify the entry type', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    update_parser.add_argument('--name', help='specify the record name (required)', required=True)
    update_parser.add_argument('--content', help='specify the record content (required)', required=True)
    update_parser.add_argument('--identifier', help='specify the ID of the record to update')
    update_parser.add_argument('--priority', help='specify the record priority (required for MX and SRV types)')

    delete_parser = action_subparsers.add_parser('delete', help='Delete a domain record', parents=[global_provider_parser])
    delete_parser.add_argument('domain', help='specify the domain, supports subdomains as well')
    delete_parser.add_argument('type', help='specify the entry type', type=str.upper, choices=['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT', 'SRV', 'LOC'])
    delete_parser.add_argument('--name', help='specify the record name')
    delete_parser.add_argument('--content', help='specify the record content')
    delete_parser.add_argument('--identifier', help='specify the ID of the record to delete')

    return parser


def generate_cli_main_parser():
    """Using all providers available, generate a parser that will be used by Lexicon CLI"""
    providers = []
    for _, modname, _ in pkgutil.iter_modules(providers_package.__path__):
        if modname != 'base':
            providers.append(modname)
    providers = sorted(providers)

    parser = argparse.ArgumentParser(
        description='Create, Update, Delete, List DNS entries')
    try:
        version = pkg_resources.get_distribution('dns-lexicon').version
    except pkg_resources.DistributionNotFound:
        version = 'unknown'
    parser.add_argument('--version', help='show the current version of lexicon',
                        action='version', version='%(prog)s {0}'.format(version))
    parser.add_argument('--delegated', help='specify the delegated domain')
    subparsers = parser.add_subparsers(
        dest='provider_name', help='specify the DNS provider to use')
    subparsers.required = True

    for provider in providers:
        provider_module = importlib.import_module(
            'lexicon.providers.' + provider)
        provider_parser = getattr(provider_module, 'provider_parser')

        subparser = subparsers.add_parser(provider, help='{0} provider'.format(provider),
                                          parents=[generate_base_provider_parser()])
        provider_parser(subparser)

    return parser
