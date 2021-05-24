import os
import re
import yaml
import argparse
import glob
from jinja2 import Environment, FileSystemLoader



def merge_configs(account, region):

    merged_configs = { account: { region : {}}}

    yaml_files = sorted(glob.glob('configs/**/*.yaml', recursive=True))

    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as config_file:
            content = yaml.safe_load(config_file)

        try:
            merged_configs[account][region].update(content[account][region])

        except (KeyError, TypeError):
            continue

    return merged_configs


def get_targets(config, account, region, pattern):

    targets = []

    specials = ['local', 'provider', 'terraform', 'variable']

    if pattern == '*':
        targets = list(config[account][region])

    else:
        pattern = '.*{}.*'.format(pattern)

        for item in list(config[account][region]):
            if re.search(pattern, item) or item.split('.')[0] in specials:
                targets.append(item)

    return sorted(targets)
    

def templating(template_dir, template_file, **kwargs):

    file_loader = FileSystemLoader('.')

    env = Environment(loader=file_loader, extensions=['jinja2.ext.loopcontrols'], lstrip_blocks=True, trim_blocks=True)

    template = env.get_template(os.path.join(template_dir, template_file))

    render = '\n{}\n'.format(template.render(kwargs))

    filename = kwargs['block_header'].split('.')[0]

    with open(os.path.join('output', '{}.tf'.format(filename)), 'a') as tf_file:
        tf_file.write(render)


def dict2hcl(obj, hcl='', indent_size=2, recursive=False):

    indent = ' ' * indent_size

    for key, value in obj.items():
        if isinstance(value, bool):
            if value == True:
                value = 'true'
        
            else:
                value = 'false'
        
        if isinstance(value, list):
            if len(value) > 1:
                items = '[\n'

                for item in value:
                    if isinstance(item, bool):
                        if item == True:
                            item = 'true'

                        else:
                            item = 'false'

                    if isinstance(item, dict):
                        items += '{}{}\n'.format(indent + '  ', '{')

                        indent_size += 4
                        
                        items = dict2hcl(item, items, indent_size, True)
                        
                        indent_size -= 4
                        
                        items += '{}{},\n'.format(indent + '  ', '}')
                    
                    else:
                        items += '{}{},\n'.format(indent + '  ', item)

                items += '{}{}'.format(indent, ']')

                value = items

        if isinstance(value, dict):
            if key == 'tags':
                hcl += '{}{:<30} = {}\n'.format(indent, 'tags', '{')

            elif key.startswith('provisioner'):
                provisioner, executer = key.split('.')

                hcl += '\n{}{} "{}" {}\n'.format(indent, provisioner, executer, '{')

            elif key.startswith('backend'):
                backend, backend_type = key.split('.')

                hcl += '\n{}{} "{}" {}\n'.format(indent, backend, backend_type, '{')

            elif 'ingress' in key or 'egress' in key:
                hcl += '\n{}{} {}\n'.format(indent, key.split('.')[0], '{')

            else:
                hcl += '{}{}{}\n'.format(indent, key, ' {')

            indent_size += 2

            hcl = dict2hcl(value, hcl, indent_size, True)

            indent_size -= 2

            hcl += '{}{}\n'.format(indent, '}')

        else:
            if not recursive:
                hcl += '{}{:<30} = {}\n'.format(indent, key, value)
            else:
                hcl += '{}{} = {}\n'.format(indent, key, value)

    return hcl.replace('\'', '')


def get_args():

    cli_parser = argparse.ArgumentParser()

    cli_parser.add_argument('--account', type=str, help='Set account', required=True)

    cli_parser.add_argument('--region', type=str, help='Set region', required=True)

    cli_parser.add_argument('--target', type=str, help='Set targets based on regex', default='*')

    return cli_parser.parse_args()


def main():

    args = get_args()

    account = args.account
    region = args.region
    target = args.target

    config = merge_configs(account, region)

    for file in os.listdir('output/'):
        if file.endswith('.tf'):
            os.remove(os.path.join('output', file))

    print('\nTerraform is set for:')
    print('=====================')
    
    print('Account: {}'.format(account))
    
    print('Region: {}'.format(region))
    
    targets = get_targets(config, account, region, target)

    print('\nTerraform selected targets:')
    print('===========================')

    if not target == '*' and not list(filter(lambda x: target in x, targets)):
        print('{}No target were found.\n{}'.format('\033[91m', '\033[0m'))

        exit(1)

    else:
        for target in targets:
            target_suffix = None

            if target.startswith('resource.'):
                target_suffix = target.removeprefix('resource.')

            if target.startswith('module.'):
                target_suffix = target
            
            if target_suffix:
                print('{}{}{}'.format('\033[92m', target_suffix, '\033[0m'))

            target_type = target.split('.')[0]

            attributes = config[account][region][target]

            templating('templates', '{}.j2'.format(target_type), block_header=target, attributes=dict2hcl(attributes))

        print('\n')


if __name__ == '__main__':
    main()