# coding=utf8

"""   
    Peer to Peer Chat Application
    
    Copyright (C) 2017 Sakayan Sitsabesan <ssit662@aucklanduni.ac.nz>
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """

import smtplib
import random


"""
    Sends an email to a particular user with the secret code
    that is passed into it. The email is sent via Google's SMTP
    servers.
"""


def sendemail(username, code):
    header = 'From: Sakayan Sitsabesan <tamilnewzealand96@gmail.com>\n'
    header += 'To: ' + username + '@aucklanduni.ac.nz\n'
    header += 'Subject: Chat Application Security Code\n\n'
    message = 'Please enter the below code to login to your account:\n' + code
    message = header + message

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login('tamilnewzealand96@gmail.com', 'p_?r^P[`7h56sZ%cCvVA')
    problems = server.sendmail(
        'tamilnewzealand96@gmail.com', username + '@aucklanduni.ac.nz', message)
    server.quit()
    return problems


"""
    Generates a new random code and emails it to
    the user and then returns the code for checking.
"""


def tfainit(username):
    code = str(random.randrange(100000, 999999))
    sendemail(username, code)
    return code
