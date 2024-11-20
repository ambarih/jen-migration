import paramiko
from scp import SCPClient
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Migrate Jenkins jobs between servers.")
parser.add_argument("--source_host", required=True, help="Source Jenkins server IP")
parser.add_argument("--dest_host", required=True, help="Destination Jenkins server IP")
args = parser.parse_args()

# Configuration
source_host = args.source_host
dest_host = args.dest_host
username = 'ec2-user'         # SSH user
pem_file_path = './ma-jen.pem' # Path to the PEM file
jenkins_jobs_path = '/var/lib/jenkins/jobs/'  # Jenkins jobs directory
temp_backup_path = '/tmp/jobs_backup'        # Temporary backup path

def create_ssh_client(hostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, key_filename=pem_file_path)
    return ssh

def transfer_files():
    try:
        print(f"Connecting to source server: {source_host}")
        source_ssh = create_ssh_client(source_host)
        with SCPClient(source_ssh.get_transport()) as scp:
            print(f"Downloading {jenkins_jobs_path} from source server...")
            scp.get(jenkins_jobs_path, recursive=True, local_path="./jobs_backup")
            print("Download complete.")
        source_ssh.close()

        print(f"Connecting to destination server: {dest_host}")
        dest_ssh = create_ssh_client(dest_host)
        with SCPClient(dest_ssh.get_transport()) as scp:
            print(f"Uploading ./jobs_backup to {dest_host}:{temp_backup_path}...")
            scp.put("./jobs_backup", recursive=True, remote_path=temp_backup_path)
            print("Upload complete.")

        print(f"Moving {temp_backup_path} to {jenkins_jobs_path} on destination server...")
        stdin, stdout, stderr = dest_ssh.exec_command(
            f"sudo mv {temp_backup_path}/* {jenkins_jobs_path} && sudo rm -rf {temp_backup_path}"
        )
        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Files moved successfully.")

        dest_ssh.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    transfer_files()
