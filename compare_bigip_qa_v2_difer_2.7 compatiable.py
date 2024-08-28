#MODULES TO IMPORT
##########################################################################################

import subprocess
import difflib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import zipfile

#FUNCTIONS
###########################################################################################
def copy_file_from_remote(remote_username, remote_server, remote_file_path, from_remote_to_local_file_path):
    # Copy file from remote server to local server using scp
    scp_command = "scp {}@{}:{} {}".format(remote_username,remote_server,remote_file_path,from_remote_to_local_file_path)
    try:
        subprocess.call(scp_command, shell=True)
        print("File copied successfully from {}:{} to {}".format(remote_server, remote_file_path, from_remote_to_local_file_path))

        # Read the content of the file
        with open(from_remote_to_local_file_path, 'r') as remote_file:
            remote_content = remote_file.readlines()
    except subprocess.CalledProcessError as e:
        print("Error occurred: {}".format(e))
    return remote_content

def read_local_file(source_local_file_path):
    with open(source_local_file_path, 'r') as local_file:
        return local_file.readlines()

def compare_files(remote_content, local_content, from_remote_to_local_file_path, source_local_file_path):
    differ = difflib.HtmlDiff(tabsize=3)
    with open("compare.html", "w") as file:
        html_compare = differ.make_file(fromlines=local_content, tolines=remote_content, fromdesc=source_local_file_path, todesc=from_remote_to_local_file_path)
        file.write(html_compare)
    with zipfile.ZipFile ('comparezip.zip', 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('compare.html')          
      
def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(body,'html'))
    with open('comparezip.zip' , 'rb') as attach:
        part = MIMEBase('application' , 'octet-stream')
        part.set_payload(attach.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition','attachment', filename='comparezip.zip'.split("/")[-1])
        msg.attach(part)

    server = smtplib.SMTP(smtp_server,smtp_port)
    isuccessful = False
    while not isuccessful:
        try:
            result = server.connect(smtp_server)
            isuccessful = True
            print("Connection to mail server is successfull:{}".format(result))
            break
        except Exception as e:
            print("{}".format(e))
            time.sleep(1)
    server.sendmail(from_email,[to_email],msg.as_string())
    server.quit()
           
def main():        
    remote_server = raw_input("please enter the ip of the remote server") # change to parameter!
    remote_file_path =  '/config/bigip.conf' #'/test_shlomilo/test.txt'
    from_remote_to_local_file_path= '/config/{}_BIGIP_File'.format(remote_server)
    source_local_file_path =  '/config/bigip.conf' #'C:\\myProjects\\pythoncompare\\test1.txt' #'/var/tmp/test.txt' 
    remote_username = raw_input("Please enter your username For connection") # change to parameter!
    remote_content = copy_file_from_remote(remote_username, remote_server, remote_file_path, from_remote_to_local_file_path)
    local_content = read_local_file(source_local_file_path)
    recp = ['shlomilo@payoneer.com']#,'guyas@payoneer.com','felixzu@payoneer.com','dmitryma@payoneer.com','itayzo@payoneer.com','guyel@payoneer.com','williamwi@payoneer.com','shiranag@payoneer.com','idoad@payoneer.com','oried@payoneer.com','hilawe@payoneer.com'
    to_email = ", ".join(recp)
    from_email = 'test1@payoneer.com'
    smtp_server = '192.168.0.193'
    smtp_port = 25
    subject = "BIG_IP.CONF COMPARISON - Test - please ignore this mail!!!!"
    body = """ 
    <html>
        <head>
            <h1> Here Are The Changes I Found Team.</h1>
        </head>
    </html>    
    """
    compare_files(remote_content, local_content,from_remote_to_local_file_path,source_local_file_path)
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port)
    

if __name__ == "__main__":
    main()

#enter outputs : info about actions in script!
#logs inside the script about process of script!
#error handling on critical commands so we wont get ssh error ! - try - catch error handling 
#critical aspects. !!!! -> error handling!
#save the configuration files to configuration folder and the logs to logs folder sepreatley !
#check if certificates and passwords are saved in bigip.conf!