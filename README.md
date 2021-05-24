# TFGen - Terraform code generator

#### _Introduction_
TFgen is aiming to help you to generate any terraform code decelration based on a provided YAML file.
The YAML configuration file should represent the structure, syntax and data types which terraform is expecting to get as if you were declaring them in HCL.

#### _Application Structure_
```
├── configs
│   ├── aws
│   │   ├── files
│   │   │   ├── policy
│   │   │   └── user_data
│   │   └── services
│   │       ├── ami
│   │       ├── api_gateway
│   │       ├── ec2
│   │       ├── ecr
│   │       ├── elb
│   │       ├── iam
│   │       ├── lambda
│   │       ├── route53
│   │       ├── s3
│   │       ├── security_group
│   │       └── vpc
│   ├── azure
│   └── gcp
├── output
└── templates
```

##### **configs --> <provider_name> --> files:**
**policy:** A folder to place your policy files in json format that you are intend to attache to your services.
```
usage: file('"<location of policy file>"')
```
**user-data:** A folder to place your user data files (shell scripts) that you intend to attache to your services.
```
usage: file('"<location of user data file"')
```

##### **configs --> <provider_name> --> services:**
A list of folders which each of them is representing a service name in the cloud provider. You may, and should add more of them based on your needs, and place your configuration files (.yaml) inside of them.

##### **output:**
A folder which hold the outcome of the generator runs (.tf files for terraform to apply).

##### **templates:**
A folder which hold the templating files that th generator will use to generate the .tf files.


#### _Naming convention_
Resources, modules and data are basic entities and you might name them whatever you like.
When you are aiming for a big entity (constraining a bunch of resources, modules and data entities), naming them with the same name will group them to a project representation which will be much easier to handle and maintain. 

When you are creating your configuration I suggest that you'll assign names with a unified prefix name as follow:
**resource.aws_s3_bucket.my_poc_bucket** and **resource.aws_instance.my_poc_instance**
are both prefixed with **my_poc**, which mean that they are belong to the same big entity/project called my_poc.

#### _YAML_
Why Using YAML?
- Readable Code
- Short Syntax
- Cross-Language data portability
- A consistent data model
- On-pass processing
- Ancors and Aliases
- Ease of use

##### configuration files (.yaml):
As stated before, under each service folder name you should create a yaml file which represent the resource type
as stated in terraform provider resource documentation.
for example:
if you would like to create an S3 bucket the resource type is **aws_s3_bucket**, so the filename should be **aws_s3_bucket.yaml**.
for creating ec2 instance a file named **aws_instance.yaml** should be placed under EC2 service name folder.

Since configuration files are YAML, and YAML have the ability to set anchors and aliases, you can use it to minimize your configuration files by setting and use them elsewhere in your file whenever you want.
You can also override/add some other configurations that is missing from the inheritened configuration.
Saying that, putting all kind of resources names with the same resource type in the same configuration file will allow you to enforce YAML capabilities to your needs. 

#### _Note: To set string variables, enclose double qoute with single qoute. (i.e. '"str"')_

**Every .yaml file should start as follow:**
```
---
<account>:
  <region>:
 ```
 where **<account>** can be 'prod', 'qa', 'dev' or whatever you choose. 
 **<region>** should be set as cloud provider region names like 'us-east-1' etc.
 
resource configuration structure:
 ```
 ---
 <account>:
   <region>:
     resource.<resource_type>.<label>:
```
where:
**resource** represent that you are aming for a resource declearation.
**<resource_type>** represent the cloud provider resource type name as in terraform cloud provider resource documentation.
**<label>** represent the terraform label for this resource (see nameing conventions).

example:
```
---
prod:
  us-east-1:
    resource.aws_s3_bucket.my_poc_bucket:
      acl: '"private"'
      bucket: '"my_poc_bucket"'
      versioning:
        enabled: True
```

module configuration structure:
 ```
 ---
 <account>:
   <region>:
     module.<label>:
```
where:
**module** represent that you are aming for a module declearation.
**<label>** represent the terraform label for this module (see nameing conventions).

example:
```
---
prod:
  us-east-1:
    module.my_poc_vpc:
      source: '"terraform-aws-modules/vpc/aws"'
      name: '"my_poc_vpc"'
      cidr: '"10.0.0.0/16"'
      azs: 
        - '"eu-west-1a"'
        - '"eu-west-1b"'
        - '"eu-west-1c"'
      private_subnets: 
        - '"10.0.1.0/24"'
        - '"10.0.2.0/24"'
        - '"10.0.3.0/24"'
      public_subnets:
        - '"10.0.101.0/24"'
        - '"10.0.102.0/24"'
        - '"10.0.103.0/24"'
      enable_nat_gateway: False
      enable_vpn_gateway: False
```

variable configuration structure:
 ```
 ---
 <account>:
   <region>:
     variable.<label>:
```
where:
**variable** represent that you are aming for a variable declearation.
**<label>** represent the terraform label for this variable (see nameing conventions).

example:
```
---
prod:
  us-east-1:
    variable.region:
      type: string
      description: '"defualt aws region"'
      default: '"us-east-1"'
```

#### _Installation_
```bash
./setup.sh
```
#### _usage_
```bash
Usage: ./tfg -a [account] -r [region] -t [target] -l -v

Options:
  -h  :  This usage.
  -a  :  Set account name.
  -r  :  Set region name.
  -t  :  Set target name as regex. ommiting will use default='*'.
  -l  :  Run on local copy and don't pull from git.
  -v  :  Use terraform validate on the generated code, default is terraform apply.
```
example:
```bash
./tfg -a prod -r use-east-1 -t my_poc -v
```

After first use of tfgen, terraform will instruct you to run terrafrom init.
From the tfgen root folder where .terraform folder will be created, you should run the following command whenever you are adding/changing modules or provider plugins.
```bash
terraform init output/
```

