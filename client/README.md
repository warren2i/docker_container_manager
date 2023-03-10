## Introduction

This Python script allows you to create or stop Docker containers on a remote server. You can choose to create a container by specifying the parameters, or stop and remove running containers on the server.

## Requirements

The script requires Python 3 to be installed on your local machine, as well as the `argparse` and `logging` Python modules. The remote server must have Docker installed and running, and you must have SSH access to the server with the appropriate permissions to create and manage Docker containers.

## Usage

The script can be run from the command line with the following arguments:


--ssh-key: The filename of the SSH key to use for the remote connection.

--server-ip: The IP address of the remote server.

--action: The action to perform, either "create" to create a new Docker container, or "stop" to stop and remove existing containers.


## Creating a Container

To create a new Docker container, use the following command:

```commandline
python3 docker_container_manager.py --ssh-key <SSH_KEY_FILENAME> --server-ip <SERVER_IP_ADDRESS> --action create
```


When prompted, enter the following information:

- First user number: Enter a number between 10-50 to specify the first user ID for the container.
- Last user number: Enter a number between 10-50 to specify the last user ID for the container.
- User expiry date: Enter the expiry date for the container users in the format YYYY-MM-DD.
- Name of docker container: Enter a name for the Docker container.
- Hostname/IP of machine: Enter the hostname or IP address of the machine to connect to. This is usually `kali.notsohackable.com`.
- Port to expose container ssh on: Enter a port number to use for SSH connections to the container.

The script will then clone the necessary repository on the remote server, run the Docker container creation script, and download the output file to your local machine.

## Stopping and Removing Containers

To stop and remove existing Docker containers, use the following command:

```commandline
python3 docker_container_manager.py --ssh-key <SSH_KEY_FILENAME> --server-ip <SERVER_IP_ADDRESS> --action stop
```


The script will list all running containers on the remote server and prompt you to enter the container IDs you wish to stop and remove. Enter a comma-separated list of container IDs, or leave blank to exit without stopping or removing any containers.

## Functions

The script includes the following functions:

- `create_ssh_connection(ssh_key_filename, server_ip_address)`: Creates an SSH connection to the specified server using the provided SSH key filename and IP address.
- `clone_repository(ssh_command, remote_script_dir)`: Checks if the necessary repository is cloned on the remote server and clones it if it is not already present.
- `run_remote_script(ssh_command, remote_script_path, **kwargs)`: Runs the Docker container creation script on the remote server with the provided parameters.
- `download_output_file(ssh_command, remote_file_path, local_file_path, server_ip_address)`: Downloads the output file from the remote server to your local machine.
- `delete_remote_file(ssh_command, remote_file_path)`: Deletes the specified file from the remote server.
- `list_running_containers(ssh_command)`: Lists all running Docker containers on the remote server.
- `stop_and_remove_containers(ssh_command, container_list)`: Stops and removes the Docker containers with the specified IDs on the remote server.
- `stop_container(ssh_key_filename, server_ip_address)`: Prompts the user to enter the container IDs they wish to stop and remove on the remote server.
- `parse_args()`:
