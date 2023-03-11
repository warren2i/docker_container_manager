#!/usr/bin/python3

import argparse
import datetime
import os
import secrets
import shutil
import string
from pathlib import Path
from zipfile import ZipFile
from urllib import request
import docker
from prettytable import PrettyTable


def test_internet_speed(image_size):
    # this function is not ready to be used, but it is simply here as a placeholder
    """times 1MB file download and calculated basic internet speed test"""
    url = f"http://speedtest.tele2.net/10MB.zip"
    start_time = datetime.datetime.now()
    response = request.urlopen(url)
    size = int(response.headers["Content-Length"])
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(duration)
    speed = size / duration / 1000000
    approx_time = (image_size / (speed / 8) / 60)
    print(f"Image file is {image_size}MB in size, this will take approx {approx_time}"
          f" minuites @ your tested download speed: {speed} Mbps\n")
    return approx_time


def list_containers():
    """Lists running containers"""
    client = docker.from_env()
    container_list = client.containers.list(all=True)
    print(f"These are the currently running containers on the host\n")
    table = PrettyTable(['Id', 'Image', 'Name', 'Status'])
    num_running_containers = len(container_list)
    if num_running_containers == 0:
        return num_running_containers, str('')
    else:
        for container in container_list:
            id = container.id[:12]
            image = container.image.tags[0]
            name = container.name
            status = container.status
            labels = container.labels
            table.add_row([id, image, name, status])
        return num_running_containers, str(table)


def create_container(name, port, image, command, detach=True):
    """Spins up the host container"""
    client = docker.from_env()

    if not client.images.list(name=image):
        print("image doest exist locally, fetching image this might take a while")
        # placeholder for approx download wait time
        # test_internet_speed()
    else:
        print(f"Image already exists locally")
    port_dict = {i: i for i in range(4010, 4050)}
    port_dict['22'] = port
    print(image)
    container = client.containers.run(
        image=image,
        name=name,
        command=command,
        ports=port_dict,
        detach=detach,
        user=0
    )
    return container


def create_credential_file(username, password, ip, port, date_expire):
    """Creates a txt file containing user credentials and SSH command"""
    with open(f"creds/{username}.txt", "w") as f:
        try:
            with open('asci.txt', 'r') as f1:
                file_contents = f1.read()
                f.write(file_contents)
        except FileNotFoundError:
            print('Error: Could not find file asci.txt')

        f.write("#####################################################################\n")
        f.write("###                          Credentials                          ###\n")
        f.write("#####################################################################\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write(f'ssh command: ssh {username}@{ip} -p {port}\n')
        f.write(f'Your account will expire on {date_expire}\n\n')

        try:
            with open('disclaimer.txt', 'r') as f2:
                file_contents = f2.read()
                f.write(file_contents)
        except FileNotFoundError:
            print('Error: Could not find file disclaimer.txt')

        f.close()
        print(f'Created credential file for {username} in location creds/{username}.txt')


def create_user_accounts(first, last, container, port, ip, date_expire):
    """Creates user accounts with random passwords"""
    creds_dir = Path('creds')
    creds_dir.mkdir(exist_ok=True)
    with (creds_dir / "user-list.txt").open("w") as f:
        f.write("#####################################################################\n")
        f.write("###                       User Credentials                        ###\n")
        f.write("#####################################################################\n")
        f.write(f'{list_containers()[1]}\n')
        for user in range(first, last):
            letters_digits = string.ascii_letters + string.digits
            passwd_len = 12
            password = ''.join(secrets.choice(letters_digits) for _ in range(passwd_len))
            username = f'user{user:02d}'
            print(f'Username: {username} Password: {password}\n')
            f.write(f'Username: {username} Password: {password}\n')
            container.exec_run(f'sudo useradd -e {date_expire} -m {username} -s /bin/bash')
            container.exec_run(f'sudo touch /home/{username}/.hushlogin')
            container.exec_run(f"""/bin/bash -c 'echo "{username}:{password}" | sudo chpasswd'""")
            container.exec_run(f"/bin/bash -c 'usermod -a -G tools user{username}'")
            container.exec_run(f"/bin/bash -c 'for x in $(seq {first} {last}); do cp /root/* /home/user$x/; done'")
            create_credential_file(username, password, ip, port, date_expire)
        f.write(f'accounts will expire on {date_expire}\n')
        print(f'\nCreated master file of user credentials in location user-list.txt')


def main():
    print(f'detected os: {os.name}')
    linux = not (os.name == 'nt')

    parser = argparse.ArgumentParser(
        description="Command line automation of docker container launch and SSH user assignment")
    parser.add_argument('-f', '--first', metavar='', type=int, help="First user number between (10-50)",
                        choices=range(10, 50), required=True)
    parser.add_argument('-l', '--last', metavar='', type=int, help='Last user number between (10-50)',
                        choices=range(10, 50), required=True)
    parser.add_argument('-e', '--expiry', metavar='', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
                        help="User expiry date format YYYY-MM-DD", required=True)
    parser.add_argument('-n', '--name', metavar='', type=str, help="Name of Docker container", required=True)
    parser.add_argument('-i', '--ip', metavar='', type=str, help="IP of machine", required=True)
    parser.add_argument('-p', '--port', metavar='', type=int, help="Port to expose container SSH on", required=True)
    parser.add_argument('-I', '--image', metavar='', type=str,
                        help="Docker image default (notsosecure/rsh_kali:latest)",
                        default='notsosecure/rsh_kali:latest', required=False)
    args = parser.parse_args()

    container_expire = (datetime.datetime.fromisoformat(str(args.expiry)) - datetime.datetime.now()).total_seconds()
    date_expire = str(args.expiry)

    # Print current running containers
    print(list_containers()[1])

    print('###################################################################y')
    print('Is the container you would like to configure already running? (Y/N)\n')

    while True:
        user_input = input("Select y or n: \n")
        if user_input == "y":
            print("You selected yes.")
            container_id = input('Please enter the container ID: ')
            container = docker.from_env().containers.get(container_id)
            create_user_accounts(args.first, args.last, container, args.port, args.ip, date_expire)
            break
        elif user_input == "n":
            print('Spinning up a new container')
            host = create_container(
                name=args.name,
                port=args.port,
                image=args.image,
                command=f'timeout {container_expire} /usr/sbin/sshd -D')
            create_user_accounts(args.first, args.last, host, args.port, args.ip, date_expire)
            break
        else:
            print("Invalid input. Please select y or n.")

    os.chmod('creds', 0o777)
    for root, directories, files in os.walk('creds'):
        for directory in directories:
            os.chmod(os.path.join(root, directory), 0o777)
        for file in files:
            os.chmod(os.path.join(root, file), 0o777)

    output_name = f"{args.name}_{args.expiry}"
    output_path = Path(output_name).with_suffix('.zip')

    with ZipFile(output_path, 'w') as zip_file:
        for root, directories, files in os.walk('creds'):
            for file in files:
                zip_file.write(os.path.join(root, file), file)

    shutil.rmtree('creds')
    if linux:
        os.chown(output_path, 1000, 1000)
    print(f"Credential archive saved at {output_path}")


if __name__ == '__main__':
    main()
