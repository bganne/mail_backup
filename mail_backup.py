# Backup emails from imap account into mbox files
# it will backup AND REMOVE FROM IMAP all emails prior to current year
# Each year is backuped in its own mbox file
#
# Copyright (C) 2017 Benoit Ganne <benoit.ganne@gmail.com>
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
# 
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
# 
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
# 
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
# 
#  0. You just DO WHAT THE FUCK YOU WANT TO.


#!/usr/bin/env python
import sys
import imaplib
import getpass
import email
import email.header
import datetime
import mailbox
from datetime import date

# imap server address
SERVER = "mail.example.com"
# login
ACCOUNT = "example"
# folders to backup
FOLDERS = ('INBOX','Sent')
# date prior to which it should backup (default to current year)
DATE = "01-Jan-%s" % date.today().year

MBOX = dict()

def process_folder(M):
    rv, data = M.search(None, '(BEFORE "%s")' % DATE)
    if rv != 'OK':
        print "No messages found!"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            continue

        msg = email.message_from_string(data[0][1])
        decode = email.header.decode_header(msg['Subject'])[0]
        subject = decode[0]
        print 'Message %s: %s @%s' % (num, msg['Subject'], msg['Date'])
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        print date_tuple[0]
        try:
            mbox = MBOX[date_tuple[0]]
        except KeyError:
            mbox = mailbox.mbox('%s.mbox' % date_tuple[0])
            MBOX[date_tuple[0]] = mbox
        mbox.add(msg)

        # delete mail from imap
        M.store(num, '+FLAGS', '\\Deleted')


M = imaplib.IMAP4_SSL(SERVER)

rv, data = M.login(ACCOUNT, getpass.getpass())
print rv, data

rv, mailboxes = M.list()
if rv == 'OK':
    print "Mailboxes:"
    print mailboxes

for folder in FOLDERS:
    rv, data = M.select(folder)
    if rv == 'OK':
        print "Processing folder...\n"
        process_folder(M)
        M.close()
    else:
        print "ERROR: Unable to open folder", folder, rv

M.logout()
