# 前言
其實這個篇是使用 **Version_2** 來改動的，主要是也是為了配合 **[ISO27001]** 的規則進行自動化備份，以便日後稽核的時候有東西可以給稽核員檢查。
<BR>雖然可能不見得大家會用的到，但或許有天你也會想用也說不定呢 (｢･ω･)｢
<BR>主要是因為現在公司的設備種類多種，數量又多，如果因為這備份每天要花時間搞我就覺得 
## 麻煩(〃∀〃)

於是乎 [**小垃圾3號**] 誕生了

因為現在的環境比以前複雜許多，為了方便後續操作與紀錄等需求，這次搭配 Jenkins 來使用，同樣的，為了方便日後**修改**、**控制**、**紀錄**，做了更細的模組化處理

所以[**照理說**]只要調整需要的部分照理說就可以正常運作了
#### ~~大概吧~~ ◝(　ﾟ∀ ﾟ )◟

**GitHub: https://github.com/luca-yao/NetworkDeviceLoggingBackup**

一如既往，本程式主要分成三大設定檔
- NetworkDeviceBackup.py
- sendmail.py
- main-default.py
- config/device_list.yaml

<BR>運行作業系統：Ubuntu 22.04 LTS

Python版本：Python3.12

以下開始一一為各位講解
---
1. Python3安裝
```bash
add-apt-repository ppa:deadsnakes/ppa
apt update && apt upgrade
#更新
 apt install -y software-properties-common build-essential libffi-dev libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev libssl-dev 
#安裝相依套件
apt install -y python3.12 python3.12-venv  
#安裝 Python3.12
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 311
sudo update-alternatives --config python3 
#將3.12改為預設值
```
1. Netmiko安裝
```python
pip3 install netmiko
```

## firewall-list.yaml
採用YAML檔編寫  #這次不太依樣，把帳密統一，這樣好控管
```yaml
- hostname: Forti-60F
  device_type: fortinet
  host: 1.1.1.1
  directory: 
    - /home/backup/A/   #如有兩個路徑這樣填寫即可
    - /home/backup/B/

- hostname: Forti-60F
  device_type: fortinet
  host: 1.1.1.2
  directory: /home/backup/A/

- hostname: Palo-Alto-820
  device_type: paloalto_panos
  host: 1.1.1.3
  directory: 
    -  /home/backup/A/
    -  /home/backup/B/

.................依此類推.............
```

## firewall_backup.py
```python
import os, logging, yaml, NetworkDeviceBackup,  sendmail

class Config:
    file_path = 'config/firewall-list.yaml'   # YAML檔案路徑

class LoginAccount:
    username = "backup"                       #登入帳號
    password = "ookamimiosaikou"              #登入密碼

class Mail_setting:
    subject_prefix = "Firewall"               #信件主旨
    smtp_server_str = "Your SMTP Server"      #SMTP郵件伺服器
    port = 25 #因為許多原因，所以我用SMTP       #通訊埠
    sender_email = "Sender Mail"              #發送者信箱
    receiver_email = "Receiver Mail"          #收件者信箱

def main():
    print("Starting the main program....")
    device_info_list, backup_status = NetworkDeviceBackup.main(Config, LoginAccount)

    if backup_status == "Backup Completed successfully.":
        sendmail_result = sendmail.main(Config, LoginAccount, Mail_setting)
    else:
        print("NetworkDeviceBackup did not complete successfully. Skipping snedmail.")

    print("Main program Completed.")
    print("Result from NetworkDeviceBackup:", backup_status)

if __name__ == "__main__":
    main()
```
因為這次是配合Jenkins來達到自動化，主要原因有點複雜
<BR>一方面也是好控管，所以選擇了透過Jenkins協助進行

## 成品如下圖：
![Imgur](https://i.imgur.com/m2o5e3r.png)

# 後記
---
我個人的習慣是會把`備份用的帳號`跟`平常使用的帳號`分開使用，這樣權限比較好管理。
<BR>~~如果出問題你也好知道是誰在搞鬼~~

這次因為公司的設備數量多，品牌型號都不同，所以比上次的程序又更加龐大了些，因此程式也做了較大的改動，目前嘗試使用上還不錯，沒有什麼意外發生
~~除了沒有通知我的部分~~

這次依樣有碰到部分設備不支援SSH，又不允許為了開啟SSH而重啟設備(一方面非常麻煩)，所以依樣有做了SSH與TELNET確認，部分設備在沒開始SSH的情況下會自動改用TELNET進行連線，這點是測試過的 

同樣的該指令裡面有包含多種設備與型號應該都可以透過這支來處理，有一些可能要微調，但常見的應該都可以直接沿用才對。

## 安啦 σ`∀´)σ
