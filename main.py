import paramiko, os, subprocess

user = 'user'
secret = 'password'
port = 22
command_resource = 'system resource print'
command_backup = 'system backup save dont-encrypt=yes name=ver_2_backup_python_script'
mipsbe_path = 'MIPSBE_6.48.6'
powerpc_path = 'PPC_6.48.6'


def send_command(command):
    resource_list = []
    log.write(f'[i] Send [{command}]\n')
    stdin, stdout, stderr = client.exec_command(command)
    stdin.close()
    for line in stdout.read().splitlines():
        str_line = str(line)
        str_line = str_line.replace("b", "", 1)
        str_line = str_line.replace("'", "")
        resource_list.append(str_line.strip())

    return resource_list


def main():
    with open('ips_mikrotik.txt', 'r+', encoding='UTF-8') as hosts:
        with open('logs.log', 'a+', encoding='UTF-8') as log:
            for host in hosts:
                host = host.strip()
                try:
                    log.write(f'[i] Open SSH\n')
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    log.write(f'[i] Connect to {host}\n')
                    client.connect(hostname=host, username=user, password=secret, port=port)
                    log.write('[i] Connect OK\n')

                    all_resource = send_command(command_resource)
                    status_backup = send_command(command_backup)
                    with open(f'config\\hosts.txt', 'a+', encoding='UTF-8') as file:
                        arch_name = list(filter(lambda x: 'architecture-name' in x, all_resource))
                        arch_name = arch_name[0].split(' ')
                        file.write(f'{host} : {arch_name[-1]} : {status_backup[0]}\n')

                    log.write('[i] Type firmware\n')
                    if arch_name[-1] == 'mipsbe':
                        log.write(f'[i] Firmware is {arch_name[-1]}\n')
                        path = mipsbe_path
                    elif arch_name[-1] == 'powerpc':
                        log.write(f'[i] Firmware is {arch_name[-1]}\n')
                        path = powerpc_path
                    log.write(f'[i] Open directory {path}\n')
                    files_directory = os.listdir(path)
                    ftp_client = client.open_sftp()
                    for i in files_directory:
                        log.write(f'[i] Send files firmware [{i}]\n')
                        ftp_client.put(f'{path}\\{i}', i)
                    log.write('[i] FTP client close\n\n')
                    ftp_client.close()

                except Exception as err:
                    log.write(f'[Err] {err}\n\n')

                log.write('[i] SSH client close\n\n')
                client.close()

if __name__ == "__main__":
    main()
