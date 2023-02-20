from email.message import EmailMessage
import ssl
import smtplib

def send_email01(subject,email_receiver,name,due_date,amount):
    
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['subject'] = subject
    # em.set_content(body)
    
    email_sender = 'tebogo.selepe001@gmail.com'
    email_password = 'svccwyhwhygsyfjz'
    email_receiver = 'wafarow465@fsouda.com'
    
    em.set_content(
    f"""\
    Hi {name}
    this is a payment reminder of R{amount} due on {due_date}
    """
    )
    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver, em.as_string())


def send_email(subject,email_receiver,name,due_date,amount):
    
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['subject'] = subject
    # em.set_content(body)
    
    email_sender = 'tebogo.selepe001@gmail.com'
    email_password = 'svccwyhwhygsyfjz'
    email_receiver = 'tebogo.selepe001@gmail.com'
    
    em.set_content(
    f"""\
    Hi {name}
    this is a payment reminder of R{amount} due on {due_date}
    """
    )


    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver, em.as_string())
        
if __name__ == "__main__":
    send_email(
        subject="Invoice",
        name="John",
        email_receiver='tebogo.selepe001@gmail.com',
        due_date="29-01-2023",
        amount="5"
    )