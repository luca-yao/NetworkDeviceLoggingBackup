import os, logging, telnetlib, time, yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException
from datetime import datetime, timedelta

def save_backup_log(hostname, backup_output, backup_directory, host):
     # 檢查 backup_directory 的類型
     if isinstance(backup_directory, list):
          for multi_directory in backup_directory:
               save_backup_for_directory(hostname, backup_output, multi_directory, host)
     elif isinstance(backup_directory, str):
          save_backup_for_directory(hostname, backup_output,backup_directory, host)
     else:
          raise ValueError("Backup_directory should be a String or a list of Strings.")

def save_backup_for_directory(hostname, backup_output, backup_directory, host):
    message = f'{hostname} Configuration Backup saved successfully.' if backup_output else f'{hostname} Failed to save Configuration Backup.'
    logging.info(message)

    timestamp = datetime.now().strftime('%Y-%m-%d')
    year_month = datetime.now().strftime('%Y-%m')

    year_month_directory = os.path.join(backup_directory, year_month)

    if not os.path.exists(year_month_directory):
         os.makedirs(year_month_directory)

    print(f"Debug: hostname={hostname}, host={host}")
    backup_filename = f'{year_month_directory}/{hostname}_{host}_{timestamp}.conf'

    with open(backup_filename, 'w', encoding='utf-8') as backup_file:
        backup_file.write(backup_output)
    logging.info(f"End save running-config for {hostname}...")

def backup_aruba_device(net_connect, hostname, backup_directory, host):
    logging.info(f"Start save running-config for {hostname}...")
    backup_output = net_connect.send_command_timing(command_string="no page")
    backup_output += net_connect.send_command_timing(command_string="show logging")
    save_backup_log(hostname, backup_output, backup_directory, host)
    net_connect.disconnect()

def backup_cisco_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     backup_output = net_connect.send_command_expect('show logging')
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def backup_hpe_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     backup_output = net_connect.send_command_timing('display log')
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def backup_hpe_telnet_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     tn = telnetlib.Telnet(net_connect["host"], net_connect["port"])
     tn.read_until(b"login:")
     tn.write((net_connect["username"] + "\r\n").encode("ascii"))
     tn.read_until(b"Password:")
     tn.write((net_connect["password"] + "\r\n").encode("ascii"))
     tn.write("display log\r\n".encode("ascii"))
     time.sleep(15)
     backup_output = tn.read_very_eager().decode("ascii")
     save_backup_log(hostname, backup_output, backup_directory, host)
     tn.close() 

def backup_hpe_1910_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     backup_output = net_connect.send_command_timing('_cmdline-mode on')
     backup_output = net_connect.send_command_timing('Y')
     backup_output = net_connect.send_command_timing('512900')
     backup_output = net_connect.send_command_timing('display log')
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def backup_hpe_1950_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     backup_output = net_connect.send_command_timing('xtd-cli-mode')
     backup_output = net_connect.send_command_timing('Y')
     backup_output = net_connect.send_command_timing('foes-bent-pile-atom-ship')
     backup_output = net_connect.send_command_timing('display log')
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def backup_forti_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     backup_output = net_connect.send_command_expect('execute log display', read_timeout=90)
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def backup_supermicro_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save running-config for {hostname}...")
     tn = telnetlib.Telnet(net_connect["host"], net_connect["port"])
     tn.read_until(b"Username:", timeout=5)
     tn.write((net_connect["username"] + "\r\n").encode("ascii"))
     tn.read_until(b"Password:", timeout=5)
     tn.write((net_connect["password"] + "\r\n").encode("ascii"))
     tn.write("ter len 0\r\n".encode("ascii"))
     tn.write("show logging\r\n".encode("ascii"))
     tn.write(" ".encode("ascii"))
     tn.write(" ".encode("ascii"))
     tn.write(" ".encode("ascii"))
     tn.write(" ".encode("ascii"))
     tn.write(" ".encode("ascii"))
     tn.write(" ".encode("ascii"))
     time.sleep(15)
     backup_output = tn.read_very_eager().decode("ascii")
     save_backup_log(hostname, backup_output, backup_directory, host)
     tn.close() 

def backup_paloalto_device(net_connect, hostname, backup_directory, host):
     logging.info(f"Start save logging for {hostname}...")
     backup_output = net_connect.send_command_expect('show log config', read_timeout=300, expect_string=r">")
     save_backup_log(hostname, backup_output, backup_directory, host)
     net_connect.disconnect()

def load_device_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        device_info = yaml.safe_load(file)
    return device_info

def main(Config, LoginAccount):
    devices = []
    device_info_list = load_device_info(Config.file_path)

    for device_info in device_info_list:
        hostname = device_info["hostname"]
        device_type = device_info["device_type"]
        host = device_info["host"]
        backup_directory = device_info["directory"]

        if "tags" not in device_info or not device_info["tags"]:
            tags = "SSH"
        else:
            tags = device_info["tags"]

        devices.append((device_info, hostname, backup_directory, host, tags))

    for device_info, hostname, backup_directory, host, tags in devices:
        if device_info["device_type"] == 'aruba_os':
                net_connect = ConnectHandler(
                    device_type = device_info["device_type"],
                    host = device_info["host"],
                    username = LoginAccount.username,
                    password = LoginAccount.password
                )
                backup_aruba_device(net_connect, hostname, backup_directory, host)

        elif device_info["device_type"] == 'cisco_ios':
                 net_connect = ConnectHandler(
                      device_type = device_info["device_type"],
                      host = device_info["host"],
                      username = LoginAccount.username,
                      password = LoginAccount.password
                 )
                 backup_cisco_device(net_connect, hostname, backup_directory, host)

        elif device_info["device_type"] == 'hp_comware':
             print(tags)
             if tags == 'Telnet':
                net_connect = {
                    "device_type": device_info["device_type"],
                    "host": device_info["host"],
                    "port": 23,
                    "username": LoginAccount.username,
                    "password": LoginAccount.password,
                 }
                backup_hpe_telnet_device(net_connect, hostname, backup_directory, host)

             else:
                if device_info["hostname"] == 'HPE-1910':
                 net_connect = ConnectHandler(
                      device_type = device_info["device_type"],
                      host = device_info["host"],
                      username = LoginAccount.username,
                      password = LoginAccount.password
                 )
                 backup_hpe_1910_device(net_connect, hostname, backup_directory, host)
                elif device_info["hostname"] == 'HPE-1950':
                 net_connect = ConnectHandler(
                      device_type = device_info["device_type"],
                      host = device_info["host"],
                      username = LoginAccount.username,
                      password = LoginAccount.password
                 )
                 backup_hpe_1950_device(net_connect, hostname, backup_directory, host)

                else:
                 net_connect = ConnectHandler(
                      device_type = device_info["device_type"],
                      host = device_info["host"],
                      username = LoginAccount.username,
                      password = LoginAccount.password
                 )
                 backup_hpe_device(net_connect, hostname, backup_directory, host)

        elif device_info["device_type"] == 'fortinet':
            net_connect = ConnectHandler(
                   device_type = device_info["device_type"],
                   host = device_info["host"],
                   username = LoginAccount.username,
                   password = LoginAccount.password,
                   read_timeout_override = 90
            )
            backup_forti_device(net_connect, hostname ,backup_directory ,host)

        elif device_info["device_type"] == 'supermicro_smis_telnet':
             net_connect = {
                  "device_type": device_info["device_type"],
                  "host": device_info["host"],
                  "port": 23,
                  "username": "ADMIN",
                  "password": "ADMIN",
             }             
             backup_supermicro_device(net_connect, hostname, backup_directory, host)
             
        elif device_info["device_type"] == 'paloalto_panos':
             net_connect = ConnectHandler(
                   device_type = device_info["device_type"],
                   host = device_info["host"],
                   username = LoginAccount.username,
                   password = LoginAccount.password,
                   read_timeout_override = 90
            )
             backup_paloalto_device(net_connect, hostname, backup_directory, host)

    return device_info_list, "Backup Completed successfully."
    
if __name__ == '__main__':
    result = main()
    print(result)
