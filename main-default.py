import os, logging, yaml, NetworkDeviceBackup,  sendmail

class Config:
    file_path = 'config/device_list.yaml'

class LoginAccount:
    username = "backup"
    password = "ookamimiosaikou"

class Mail_setting:
    subject_prefix = "Firewall"
    smtp_server_str = "Your SMTP Server"
    port = 25 #因為許多原因，所以我用SMTP
    sender_email = "Sender Mail"
    receiver_email = "Receiver Mail"

def main():
    print("Starting the main program....")
    device_info_list, backup_status = NetworkDeviceBackup.main(Config, LoginAccount)

    if backup_status == "Backup Completed successfully.":
        sendmail_result = sendmail.main(Config, LoginAccount)
    else:
        print("NetworkDeviceBackup did not complete successfully. Skipping snedmail.")

    print("Main program Completed.")
    print("Result from NetworkDeviceBackup:", backup_status)

if __name__ == "__main__":
    main()