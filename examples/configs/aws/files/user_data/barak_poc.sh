#! /bin/bash
set -ex
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo yum -y install amazon-ecr-credential-helper
sudo usermod -a -G docker ec2-user
sudo service docker start
sudo mkdir -p /root/.docker
sudo su - root -c 'echo "{ \"credsStore\": \"ecr-login\" }" > /root/.docker/config.json'
sudo docker pull ${var.aws_account}.dkr.ecr.eu-west-1.amazonaws.com/barak_poc_get_hello_world:latest
sudo docker run -p 8080:80 ${var.aws_account}.dkr.ecr.eu-west-1.amazonaws.com/barak_poc_get_hello_world:latest