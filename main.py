#!/usr/bin/python3

import docker
import argparse
from datetime import date, datetime
import secrets
import string
from prettytable import PrettyTable
import os
import shutil

client = docker.from_env()


def listContainer():
    '''lists running containers'''
    containerList = client.containers.list(all)
    print(f"Found {len(containerList)} containers on the host\n")
    table = PrettyTable(['Id', 'Image', 'Name', 'Status'])
    num_running_containers = len(containerList)
    if len(containerList) == 0:
        pass
    else:
        for container in containerList:
            id, image, name, status, labels = container.id, container.image.tags[0], container.name, container.status, container.labels
            table.add_row([id[0:12],image,name,status])
    return num_running_containers,(str(table))


def createContainer(name, port, image,command, cexpire, detach=True):
    '''spins up the host container'''
    portdict = {i:i for i in range(4010,4050)}
    portdict['22']=port
    container = client.containers.run(
        image = image,
        name = name,
        command = command,
        ports = portdict,
        detach=detach,
        user=0
    )
    return container

def createCredentialFile(username,userpass, ip, port, dateexpire):
    ''' creates a txt file containing user credentials and ssh command'''
    with open(f"creds/{username}.txt", "w") as f:
        if os.path.isfile('asci.txt'):
            with open('asci.txt', 'r') as file:
                # Do something with the file object
                file_contents = file.read()
                f.write(file_contents)
        f.write("#####################################################################\n")
        f.write("###                          Credentials                          ###\n")
        f.write("#####################################################################\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {userpass}\n")
        f.write(f'ssh command: ssh {username}@{ip} -p {port}\n')
        f.write(f'Your account will expire on {dateexpire}\n\n')
        if os.path.isfile('disclaimer.txt'):
            with open('disclaimer.txt', 'r') as file:
                # Do something with the file object
                file_contents = file.read()
                f.write(file_contents)
        f.close()
        print(f'created credential file for {username} in location creds/{username}.txt')

def userAdd(first,last,container,port,ip,dateexpire):
    '''creates a user account and random password'''
    with open(f"userlist.txt", "w") as f:
        f.write("#####################################################################\n")
        f.write("###                       User Credentials                        ###\n")
        f.write("#####################################################################\n")
        f.write(f'{listContainer()[1]}\n')
        for user in range(first,last):
            letters = string.ascii_letters
            digits = string.digits
            passwd = letters + digits
            passwd_len = 12
            pwd = ''
            for i in range(passwd_len):
                pwd += ''.join(secrets.choice(passwd))
            username = f'user{format(user)}'
            userpass = format(pwd)
            print(f'Username: {username} Password: {userpass}\n')
            f.write(f'Username: {username} Password: {userpass}\n')

            container.exec_run(f'sudo useradd -e {dateexpire} -m {username} -s /bin/bash')
            ## the below command copies files from root directory into user directory
            container.exec_run(f'sudo touch /home/{username}/.hushlogin')
            container.exec_run(f"""/bin/bash -c 'echo "{username}:{userpass}" | sudo chpasswd'""")
            container.exec_run(f'sudo usermod -a -G tools user{username}')
#            container.exec_run(f"/bin/bash -c 'cp /home/user10/* /home/{username}/'")
            container.exec_run(f"/bin/bash -c 'for x in $(seq {first} {last}); do cp /root/* /home/user$x/; done'")

            createCredentialFile(username, userpass, ip, port,dateexpire)
        f.write(f'accounts will expire on {dateexpire}')
        f.close()
        print(f'\ncreated master file of user credentials in location userlist.txt')

try:
    os.makedirs("creds")
except FileExistsError:
    # directory already exists
    pass

parser = argparse.ArgumentParser(description="command line automation of docker container launch and ssh user assignment")
parser.add_argument('-f', '--first', metavar='', type=int, help="First user number between (10-50)",choices = range(10,50), required=True)
parser.add_argument('-l', '--last', metavar='', type=int, help='Last user number between (10-50)',choices = range(10,50), required=True)
parser.add_argument('-e', '--expiry', metavar='', type=date.fromisoformat, help="User expiry date format YYYY-MM-DD", required=True)
parser.add_argument('-n', '--name', metavar='', type=str, help="Name of docker container", required=True)
parser.add_argument('-i', '--ip', metavar='', type=str, help="IP of machine", required=True)
parser.add_argument('-p', '--port', metavar='', type=int, help="port to expose container ssh on", required=True)
parser.add_argument('-I', '--image', metavar='', type=str, help="docker image default (notsosecure/rsh_kali:latest)", default='notsosecure/rsh_kali:latest', required=False)
args = parser.parse_args()

t = format(args.expiry)
cexpire = (datetime.fromisoformat(t) - datetime.now()).total_seconds()
dateexpire = format(args.expiry)

print('###################################################################')
print('is the container you would like to configure already running? (Y/N)')

user_input = input("Select y or n: ")

if user_input == "y":
    print("You selected yes.")
    print('Please select the container you would wish to configure')
    print(listContainer()[1])
    print('please enter the id\n')
    containerId = input()
    container = client.containers.get(containerId)
    userAdd(args.first, args.last, container, args.port, args.ip, dateexpire)
elif user_input == "n":
    print('Spinning up a new container')
    host = createContainer(name=args.name, port=args.port, image=args.image, command='/usr/sbin/sshd -D',
                           cexpire=100)
    userAdd(args.first, args.last, host, args.port, args.ip, dateexpire)
else:
    print("Invalid input. Please select y or n.")

shutil.make_archive('creds', 'zip', 'creds')


