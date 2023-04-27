import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import mimetypes


def send_email(name, login, passw):
    sender = login
    password = passw

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)
        # msg = MIMEText(template, 'html')
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = sender
        msg["Subject"] = f'Информация по {name}'

        msg.attach(MIMEText(f'Информация по {name}'))

        a, c = mimetypes.guess_type(f"documents/{name}.docx")
        type, subtype = a.split("/")

        with open(f"documents/{name}.docx", "rb") as f:
            file = MIMEApplication(f.read(), subtype)

        file.add_header('content-disposition', 'attachment', filename=f'{name}.docx')
        msg.attach(file)

        server.sendmail(sender, sender, msg.as_string())

        return "True"
    except Exception as _ex:
        return f'{_ex}\n Ошибка'


