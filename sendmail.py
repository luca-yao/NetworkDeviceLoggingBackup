import smtplib, NetworkDeviceBackup
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
 
def main(Config, LoginAccount, Mail_setting):
    timestamp = datetime.now().strftime('%Y-%m-%d')

    device_info_list, backp_status = NetworkDeviceBackup.main(Config, LoginAccount)

    message_text = "\n".join([f"Hostname: {info['hostname']}, IP: {info['host']}" for info in device_info_list])
    message = MIMEText(message_text, 'plain', 'utf-8')
    subject = f'Daily-{Mail_setting.subject_prefix}-{timestamp}'
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = Mail_setting.sender_email
    message['To'] = Mail_setting.receiver_email

    smtpObj = smtplib.SMTP(Mail_setting.smtp_server_str)
    smtpObj.sendmail(Mail_setting.sender_email, Mail_setting.receiver_email, message.as_string())

if __name__ == "__main__":
    main()
