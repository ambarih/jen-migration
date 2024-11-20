import argparse
import paramiko
from scp import SCPClient

# SSH client creation
def create_ssh_client(hostname, username, pem_file_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, key_filename=pem_file_path)
    return ssh

# File transfer logic
def transfer_files(source_host, dest_host, username, pem_file_path):
    try:
        # Paths for Jenkins jobs (adjust according to your setup)
        jenkins_jobs_path = "/var/lib/jenkins/jobs"
        temp_backup_path = "/tmp/jobs_backup"

        # Download from the source server
        print(f"Connecting to source server: {source_host}")
        source_ssh = create_ssh_client(source_host, username, pem_file_path)
        with SCPClient(source_ssh.get_transport()) as scp:
            print(f"Downloading Jenkins jobs from {source_host}...")
            scp.get(jenkins_jobs_path, recursive=True, local_path="./jobs_backup")
            print("Download complete.")
        source_ssh.close()

        # Upload to the destination server
        print(f"Connecting to destination server: {dest_host}")
        dest_ssh = create_ssh_client(dest_host, username, pem_file_path)
        with SCPClient(dest_ssh.get_transport()) as scp:
            print(f"Uploading Jenkins jobs to {dest_host}...")
            scp.put("./jobs_backup", recursive=True, remote_path=temp_backup_path)
            print("Upload complete.")

        # Move files into the correct directory on the destination server
        print(f"Moving files to {jenkins_jobs_path} on destination server...")
        stdin, stdout, stderr = dest_ssh.exec_command(
            f"sudo mv {temp_backup_path}/* {jenkins_jobs_path} && sudo rm -rf {temp_backup_path}"
        )
        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Files moved successfully.")
        
        dest_ssh.close()

    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to parse arguments and initiate the process
def main():
    # Setup argument parsing
    parser = argparse.ArgumentParser(description='Migrate Jenkins jobs between servers')
    parser.add_argument('--source_host', required=True, help='Source Jenkins server IP')
    parser.add_argument('--dest_host', required=True, help='Destination Jenkins server IP')
    parser.add_argument('--username', required=True, help='SSH Username')
    parser.add_argument('--pem_file', required=True, help='Path to PEM file')
    
    # Parse arguments
    args = parser.parse_args()

    # Call the file transfer function with parsed arguments
    transfer_files(args.source_host, args.dest_host, args.username, args.pem_file)

# Run the script
if __name__ == '__main__':
    main()
