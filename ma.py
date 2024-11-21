import paramiko
from scp import SCPClient
import os
 
# Configuration
source_host = "54.227.61.123"
dest_host = "54.159.2.137"
username = "ec2-user"
pem_file_path = "./ma-jen.pem"
jenkins_jobs_path = "/var/lib/jenkins/jobs/"
temp_backup_path = "/tmp/jobs_backup"
 
def create_ssh_client(hostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, key_filename=pem_file_path)
    return ssh
 
def transfer_files():
    try:
        # Step 1: Connect to the source server and download the jobs directory
        print(f"Connecting to source server: {source_host}")
        source_ssh = create_ssh_client(source_host)
        with SCPClient(source_ssh.get_transport()) as scp:
            print(f"Downloading {jenkins_jobs_path} from source server...")
            scp.get(jenkins_jobs_path, recursive=True, local_path="./jobs_backup")
            print("Download complete.")
        source_ssh.close()
 
        # Step 2: Connect to the destination server and upload to a temporary location
        print(f"Connecting to destination server: {dest_host}")
        dest_ssh = create_ssh_client(dest_host)
        with SCPClient(dest_ssh.get_transport()) as scp:
            print(f"Uploading ./jobs_backup to {dest_host}:{temp_backup_path}...")
            scp.put("./jobs_backup", recursive=True, remote_path=temp_backup_path)
            print("Upload complete.")
       
        # Step 3: Move the uploaded directory to the final destination using sudo
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