import smtplib
import random


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


def tfainit(username):
    code = str(random.randrange(100000, 999999))
    sendemail(username, code)
    return code
