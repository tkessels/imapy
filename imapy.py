import imaplib, email
from pprint import pprint as pp
from email.header import decode_header
import re
import os
import time
from configparser import ConfigParser
from cursesmenu import *
from cursesmenu.items import *
import dialog
config_file_path=os.path.join(os.path.expanduser('~'),".imap_virus_marvin.ini")
dialog=dialog.Dialog()
# dialog.set_background_title("IMAP-Mail-Renamer")
marvin_pattern=re.compile('MARVIN#\d{14}_')

def edit(num):
    pass

def get_config():
    if not os.path.isfile(config_file_path):
        #write default config and exit
        config_instance = ConfigParser()
        config_instance["CREDENTIALS"] = {
            "username": "virus-user",
            "password": "whambamBW"
        }

        config_instance["SERVER"] = {
            "host": "mail.server.dom",
            "port": 993,
            "mailbox": "INBOX"
        }
        with open(config_file_path, 'w') as conf:
            config_instance.write(conf)
        print("No Config found!")
        print("Example Config written to {}".format(config_file_path))
        print("Please Edit and Repeat")
        exit(1)
    else:
        config_instance = ConfigParser()
        config_instance.read(config_file_path)
        if config_instance["CREDENTIALS"]["password"]=="whambamBW":
            print("Looks like you haven't changed the default config")
            print("Example Config written to {}".format(config_file_path))
            print("Please Edit and Repeat")
            exit(1)
        else:
            return config_instance

def force_decode(string, codecs=['utf8', 'cp1252']):
    for i in codecs:
        try:
            return string.decode(i)
        except UnicodeDecodeError:
            pass
    raise Exception("Could not decode")

def decode(data):
    if isinstance(data,bytes):
        data=force_decode(data)
    tmp=decode_header(data)
    res=""
    for part in tmp:
        if part[1]==None:
            if isinstance(part[0],str):
                res+= part[0]
            else:
                try:
                    res+= part[0].decode('ascii')
                except:
                    print(part[0])
        else:
            res+= part[0].decode(part[1])
    return "".join(res.split())

def get_subject(num):
    global im
    res, data = im.fetch(num,'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
    x,y = data[0]
    y=force_decode(y)
    y=y[9:]
    return decode(y)

def get_mail(num):
    global im
    res, data = im.fetch(num,'(RFC822)')
    try:
        eml=email.message_from_bytes(data[0][1])
        return eml
    except:
        return None

def delete_mail(num):
    global im
    im.store(num, '+FLAGS', '\\Deleted')
    im.expunge()

def search_mails(key,value):
    global im
    _, nums = im.search(None,key,'"{}"'.format(value))
    return nums[0].split()

def print_mail(num):
    eml=get_mail(num)
    dialogit(str(eml))

def edit_mail(num):
    global im
    global config
    eml=get_mail(num)
    old_subject=eml['Subject']
    action,new_subject=dialog.inputbox("Edit Subject",init=old_subject)
    if action == "OK":
        eml.replace_header('Subject',new_subject)
        # c.append('INBOX', '', imaplib.Time2Internaldate(time.time()), str(new_message))
        c,d = im.append('INBOX','', imaplib.Time2Internaldate(time.time()),str(eml).encode('utf-8'))
        # c= OK
        # d= [b'[APPENDUID 1252405521 2655] APPEND Ok.']
        # if append ok delete original mailbox
        if "OK" in c:
            delete_mail(num)

def quit():
    exit(0)

def dialogit(text):
    dialog.scrollbox(text,height=60,width=110)

def main():
    global config
    global im
    config=get_config()
    im=imaplib.IMAP4_SSL(config["SERVER"]["host"],config["SERVER"]["port"])
    im.login(config["CREDENTIALS"]["username"],config["CREDENTIALS"]["password"])
    im.select(config["SERVER"]["mailbox"])

    # Create the menu
    menu = CursesMenu("Mails - INBOX", "0 - 10")

    typ, nums = im.search(None, 'ALL')
    for n in nums[0].split():
        subject_line=get_subject(n)
        if not marvin_pattern.match(subject_line):
            function_item = FunctionItem(subject_line, edit_mail , [n] ,should_exit=True)
            menu.append_item(function_item)
    returnval=menu.show()




    im.close()
    im.logout()

if __name__ == "__main__":
    main()
