# docker_container_manager
A quick python cli script to spin up &amp; or manage ssh users on a docker container

# How to use

### Machine Setup
**git clone repo**
```
git clone https://github.com/warren2i/docker_container_manager
```

**add execute perms to setup scripts**
```commandline
sudo chmod +x install_docker.sh py_env_setup.sh
```

### Usage

```commandline
usage: main.py [-h] -f  -l  -e  -n  -i  -p  [-I]

command line automation of docker container launch and ssh user assignment

optional arguments:
  -h, --help      show this help message and exit
  -f , --first    First user number between (10-50)
  -l , --last     Last user number between (10-50)
  -e , --expiry   User expiry date format YYYY-MM-DD
  -n , --name     Name of docker container
  -i , --ip       IP of machine
  -p , --port     port to expose container ssh on
  -I , --image    docker image default (example/rsh_kali:v.01)

```

**example command**

```commandline
sudo python3 main.py -f 10 -l 20 -n dockerhost2 -i kali.example.com -p 23 -e 2023-03-11
```

**-f 10** - create user accounts from user10

**-l 20** - create user accounts upto user20

**-n dockerhost2** - create new container with name 'dockerhost2'

**-i kali.example.com**

**-p 23** ssh port will be mapped: 23:22

**-e 2023-03-11** user accounts will expire on data: 2023-03-11

## further arguments
when you run the script it will ask you if you would like to configure a container that is already running.

if your container is already running press y, this will allow you to configure a running container.

if your container is not running press n to first spinup a container and configure

```commandline
###################################################################
is the container you would like to configure already running? (Y/N)
Select y or n: y
You selected yes.
Please select the container you would wish to configure
Found 1 containers on the host

+--------------+---------------------------+-------------+---------+
|      Id      |           Image           |     Name    |  Status |
+--------------+---------------------------+-------------+---------+
| 074264649d6a | example/rsh_kali:v.01     | dockerhost2 | running |
+--------------+---------------------------+-------------+---------+
please enter the id

074264649d6a

```

if this is the first time the image has been pulled the script will take some time to run, dont exit, future updates will provide the user status updates.

Once complete a directory will be created \creds, this will contain individual user credentials txt files

```commandline
#####################################################################
###                          Credentials                          ###
#####################################################################
Username: user10
Password: w1BdKBOAPHiG
ssh command: ssh user10@kali.example.com -p 23
Your account will expire on 2023-03-11
```
also a userlist.txt file will be created in the working directory containing all credentials.

### adding disclaimer

the script will check in the working directory is disclaimer.txt exits, if it exists it will append the contents to the end of the user credentials.txt files

### adding asci

the script will check in the working directory is asci.txt exits, if it exists it will append the contents to the start of the user credentials.txt files
