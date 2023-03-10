#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess


def create_ssh_connection(ssh_key_filename, server_ip_address):
    ssh_command = f"ssh -i {ssh_key_filename} ubuntu@{server_ip_address}"
    logging.info(f"Creating SSH connection: {ssh_command}")
    return ssh_command


def clone_repository(ssh_command, remote_script_dir):
    check_dir_command = f"{ssh_command} [ -d '{remote_script_dir}' ] && echo 'exists' || echo 'not exists'"
    check_dir_output = subprocess.run(
        check_dir_command, shell=True, capture_output=True, text=True).stdout.strip()

    if check_dir_output == "not exists":
        clone_repo_command = f"{ssh_command} git clone https://github.com/warren2i/docker_container_manager.git {remote_script_dir}"
        logging.info(f"Cloning repository: {clone_repo_command}")
        subprocess.run(clone_repo_command, shell=True, check=True)


def run_remote_script(ssh_command, remote_script_path, **kwargs):
    args = " ".join([f"-{k} {v}" for k, v in kwargs.items()])
    run_script_command = f"{ssh_command} sudo python3 {remote_script_path} {args}"
    logging.info(f"Running remote script: {run_script_command}")
    subprocess.run(run_script_command, shell=True, check=True)

def download_output_file(ssh_command, remote_file_path, local_file_path, server_ip_address):
    key_filename = ssh_command.split(" ")[2]
    ip_address = ssh_command.split(" ")[3]
    scp_command = f"scp -i {key_filename} ubuntu@{server_ip_address}:{remote_file_path} {local_file_path}"
    logging.info(f"Downloading output file with command: {scp_command}")
    try:
        subprocess.run(scp_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download output file: {e}")
        raise e


def delete_remote_file(ssh_command, remote_file_path):
    delete_command = f"{ssh_command} rm {remote_file_path}"
    logging.info(f"Deleting remote file: {delete_command}")
    subprocess.run(delete_command, shell=True, check=True)


def create_container(ssh_key_filename, server_ip_address):
    first = input("First user number between (10-50): ")
    last = input("Last user number between (10-50): ")
    expiry = input("User expiry date format YYYY-MM-DD: ")
    name = input("Name of docker container: ")
    ip = input("Enter hostname/IP of machine (Usually kali.notsohackable.com): ")
    port = input("Port to expose container ssh on: ")

    ssh_command = create_ssh_connection(ssh_key_filename, server_ip_address)
    remote_script_dir = "/home/ubuntu/docker_container_manager"
    remote_script_path = f"{remote_script_dir}/main.py"

    clone_repository(ssh_command, remote_script_dir)

    run_remote_script(
        ssh_command,
        remote_script_path,
        f=first,
        l=last,
        e=expiry,
        n=name,
        i=ip,
        p=port,
    )

    remote_file_path = f"{remote_script_dir}/{name}_{expiry}.zip"
    local_file_path = f"./{name}_{expiry}.zip"
    download_output_file(ssh_command, remote_file_path, local_file_path, server_ip_address)

    delete_remote_file(ssh_command, remote_file_path)


def list_running_containers(ssh_command):
    command = f"{ssh_command} sudo docker ps"
    output = subprocess.check_output(command, shell=True)
    logging.info(f"Listing running containers: {command}")
    print(output.decode())


def stop_and_remove_containers(ssh_command, container_list):
    for container in container_list:
        print(f"Stopping and removing container {container}")
        stop_command = f"{ssh_command} sudo docker stop {container}"
        subprocess.run(stop_command, shell=True)
        rm_command = f"{ssh_command} sudo docker rm {container}"
        subprocess.run(rm_command, shell=True)


def stop_container(ssh_key_filename, server_ip_address):
    ssh_command = create_ssh_connection(ssh_key_filename, server_ip_address)
    list_running_containers(ssh_command)
    stop_containers = input("Do you want to stop any containers? (yes or no): ")
    if stop_containers.lower() == "yes":
        containers = input(
            "Enter the container IDs you want to stop and remove (comma-separated): "
        )
        if containers:
            container_list = containers.split(",")
            stop_and_remove_containers(ssh_command, container_list)
        else:
            print("No container IDs provided. Exiting...")
    else:
        print("No containers will be stopped or removed. Exiting...")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create or stop a Docker container on a remote server."
    )
    parser.add_argument(
        "--ssh-key",
        required=True,
        metavar="SSH_KEY_FILENAME",
        help="the filename of the SSH key to use for the remote connection",
    )
    parser.add_argument(
        "--server-ip",
        required=True,
        metavar="SERVER_IP_ADDRESS",
        help="the IP address of the remote server",
    )
    parser.add_argument(
        "--action",
        required=True,
        metavar="ACTION",
        choices=["create", "stop"],
        help="the action to perform (create or stop)",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    args = parse_args()

    if args.action == "create":
        create_container(args.ssh_key, args.server_ip)
    elif args.action == "stop":
        stop_container(args.ssh_key, args.server_ip)


if __name__ == "__main__":
    main()