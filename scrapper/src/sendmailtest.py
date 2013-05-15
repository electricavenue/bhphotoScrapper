import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

msg = MIMEMultipart()
msg['Subject'] = 'BH vs. EA comparation'
msg['From'] = 'cespinosadelosmonteros@gmail.com'
msg['To'] = 'cespinosadelosmonteros@gmail.com'
username = 'cespinosadelosmonteros@gmail.com'
password = '@5M0K137'
s = smtplib.SMTP('smtp.gmail.com:587')
s.starttls()
s.login(username,password)
s.sendmail('cespinosadelosmonteros@gmail.com', ['cespinosadelosmonteros@gmail.com'], msg.as_string())
s.quit()
