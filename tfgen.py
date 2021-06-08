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

    specials = ['data', 'local', 'provider', 'terraform', 'variable']

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


def dict2hcl(obj, obj_type='', hcl_block='', indent_size=2, recursive=False):

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
                        
                        items = dict2hcl(item, obj_type, items, indent_size, True)
                        
                        indent_size -= 4
                        
                        items += '{}{},\n'.format(indent + '  ', '}')
                    
                    else:
                        items += '{}{},\n'.format(indent + '  ', item)

                items += '{}{}'.format(indent, ']')

                value = items

        if isinstance(value, dict):
            if obj_type == 'variable':
                hcl_block += '{}{} = {}\n'.format(indent, key, '{')

            elif key == 'tags':
                hcl_block += '{}{:<30} = {}\n'.format(indent, key, '{')

            elif key.startswith('provisioner'):
                provisioner, executer = key.split('.')

                hcl_block += '\n{}{} "{}" {}\n'.format(indent, provisioner, executer, '{')

            elif key.startswith('backend'):
                backend, backend_type = key.split('.')

                hcl_block += '\n{}{} "{}" {}\n'.format(indent, backend, backend_type, '{')

            elif 'ingress' in key or 'egress' in key:
                hcl_block += '\n{}{} {}\n'.format(indent, key.split('.')[0], '{')

            elif key == 'dimensions':
                hcl_block += '{}{} = {}\n'.format(indent, key, '{')

            else:
                hcl_block += '{}{}{}\n'.format(indent, key, ' {')

            indent_size += 2

            hcl_block = dict2hcl(value, obj_type, hcl_block, indent_size, True)

            indent_size -= 2

            hcl_block += '{}{}\n'.format(indent, '}')

        else:
            if not recursive:
                if obj_type == 'variable':
                    hcl_block += '{}{} = {}\n'.format(indent, key, value)

                else:
                    hcl_block += '{}{:<30} = {}\n'.format(indent, key, value)
            else:
                hcl_block += '{}{} = {}\n'.format(indent, key, value)

    return hcl_block.replace('\'', '')


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
        os.remove(os.path.join('output', file))

    print('\nTerraform is set for:')
    print('=====================')
    
    print('Account: {}'.format(account))
    
    print('Region: {}'.format(region))
    
    targets = get_targets(config, account, region, target)

    if not target == '*':
        print('\nTerraform selected targets:')
        print('===========================')

        if not list(filter(lambda x: target in x, targets)):
            print('{}No target were found.\n{}'.format('\033[91m', '\033[0m'))

            exit(1)

    else:
        for item in targets:
            item_suffix = None

            if item.startswith('resource.'):
                item_suffix = item.removeprefix('resource.')

            if item.startswith('module.'):
                item_suffix = item
            
            if not target == '*' and item_suffix:
                with open ('output/.targets', 'a') as targets_file:
                    targets_file.write('{}\n'.format(item_suffix))

                print('{}{}{}'.format('\033[92m', item_suffix, '\033[0m'))

            block_type = item.split('.')[0]

            attributes = config[account][region][item]

            templating('templates', '{}.j2'.format(block_type), block_header=item, attributes=dict2hcl(attributes, block_type))

        print('\n')


if __name__ == '__main__':
    main()