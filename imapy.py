import imaplib, email
from pprint import pprint as pp
from email.header import decode_header
import re
import os
from configparser import ConfigParser
config_file_path=os.path.join(os.path.expanduser('~'),"imap_virus_marvin.ini")

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

def get_subject(num,imap):
    res, data = imap.fetch(num,'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
    x,y = data[0]
    y=force_decode(y)
    y=y[9:]
    return decode(y)

def main():
    config=get_config()
    im=imaplib.IMAP4_SSL(config["SERVER"]["host"],config["SERVER"]["port"])
    # im=imaplib.IMAP4_SSL(imap_url,imap_port)
    im.login(config["CREDENTIALS"]["username"],config["CREDENTIALS"]["password"])
    im.select(config["SERVER"]["mailbox"])


    typ, nums = im.search(None, 'ALL')
    for n in nums[0].split():
        print(get_subject(n, im))

    im.close()
    im.logout()

main()
