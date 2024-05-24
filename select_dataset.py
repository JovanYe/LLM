import paramiko
from random import shuffle

# Example configuration
hostname = '10.108.0.25'
port = 32404
username = 'yes'
password = '123456'

def connect_to_server(hostname, port, username, password):
    """Establish an SSH connection to the remote server."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)
    return client


def get_files_from_server(client, data_requirements, root_dir):
    """Retrieve file paths from the server based on the size requirements."""
    selected_files = {}
    sftp = client.open_sftp()

    for category, size_gb in data_requirements.items():
        path = f"{root_dir}/{category}"
        try:
            files = sftp.listdir(path)
        except IOError as e:
            print(f"Error accessing {path}: {e}")
            continue

        files = [f for f in files if f.endswith('.npy')]
        shuffle(files)  # Randomize the file order

        total_size = 0
        target_size_bytes = size_gb * 1024 ** 3  # Convert GB to bytes
        category_files = []

        for file in files:
            file_path = f"{path}/{file}"
            file_attrs = sftp.stat(file_path)
            file_size = file_attrs.st_size
            if total_size + file_size <= target_size_bytes:
                category_files.append("- " + file_path)
                total_size += file_size
            if total_size >= target_size_bytes:
                break

        selected_files[category] = category_files

    sftp.close()
    return selected_files


if __name__ == "__main__":
    client = connect_to_server(hostname, port, username, password)

    data_requirements = {
        'RedPajamaCommonCrawl/npy': 6,
        'RedPajamaWikipedia': 8,
        'RedPajamaStackExchange': 5,
        # 'RedPajamaGithub':
        'RedPajamaBook': 5,
        'RedPajamaArXiv': 10,
        'RedPajamaC4/npy': 50
    }

    root_dir = "/mnt/geogpt-gpfs/llm-course/ossutil_output/public/datasets/npy_data"

    # Establish connection and retrieve files
    client = connect_to_server(hostname, port, username, password)
    try:
        selected_files = get_files_from_server(client, data_requirements, root_dir)
        # print(selected_files)
    finally:
        client.close()

    for data_type in selected_files:
        print(data_type, len(selected_files[data_type]))
        # for npy_name in selected_files[data_type]:
        #     print(npy_name)


