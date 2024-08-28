#This Script is compatiable to python 3.6
#if you want to make it compatiable to 2.7, change the following:

#raw_input to input method.
#format method to f-string. 
#subprocess.call to subprocess.run , add the line : shell=True, check=True after scp_command in the ()
#server = smtplib.SMTP(smtp_server,smtp_port) -> with .... as server  

#MODULES TO IMPORT
##########################################################################################

import os
import subprocess
import difflib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import zipfile
import logging
import re

#Create the necesarry directories
# Specify the directory path
directory_l = "logs"
directory_c = "configurations"

# Check if the directory already exists
if not os.path.exists(directory_l):
    # Create the directory
    os.makedirs(directory_l)
if not os.path.exists(directory_c):
    # Create the directory
    os.makedirs(directory_c) 

#Define Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs//info.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
open('file.txt', 'w').close()

#FUNCTIONS
###########################################################################################

def copy_file1_from_remote(remote_username, remote_server_1, remote_file_path, from_remote_to_local_file_path):
    # Copy file from remote server to local server using scp
    scp_command = f"scp {remote_username}@{remote_server_1}:{remote_file_path} {from_remote_to_local_file_path}"
    try:
        subprocess.run(scp_command, shell=True, check=True)
        logger.info(f"File copied successfully from {remote_server_1}:{remote_file_path} to {from_remote_to_local_file_path}")

        # Read the content of the file
        with open(from_remote_to_local_file_path, 'r') as remote_file:
            remote_content_1 = remote_file.readlines()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return remote_content_1

def copy_file2_from_remote(remote_username, remote_server_2, remote_file_path, from_remote_to_local_file_path_2):
    # Copy file from remote server to local server using scp
    scp_command = f"scp {remote_username}@{remote_server_2}:{remote_file_path} {from_remote_to_local_file_path_2}"
    try:
        subprocess.run(scp_command, shell=True, check=True)
        logger.info(f"File copied successfully from {remote_server_2}:{remote_file_path} to {from_remote_to_local_file_path_2}") 

        # Read the content of the file
        with open(from_remote_to_local_file_path_2, 'r') as remote_file:
            remote_content_2 = remote_file.readlines()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return remote_content_2

def mask_passwords(remote_content_1 ,from_remote_to_local_file_path_1 ,remote_content_2, from_remote_to_local_file_path_2):
    logger.info("Masking Passwords On Files....")
    lines = remote_content_1
    masked_passwords = []
    for line in lines:
        # Using a loop to itirate the lines and using RegEx and lambda to mask the passwords
        masked_line = re.sub(r"(\w*password +|\w*bind-pw +)(.*)", lambda x : x.group(1) + '*'*len(x.group(2)), line, flags=re.IGNORECASE) 
        masked_passwords.append(masked_line)
    with open(from_remote_to_local_file_path_1, 'w') as remote_file:
        remote_file.writelines(masked_passwords)
#-------------------------------------------------------------------- itirate the content from the second bigip file:
    lines2 = remote_content_2
    masked_passwords2 = []
    for line in lines2:
        # Using a loop to itirate the lines and using RegEx and lambda to mask the passwords
        masked_line2 = re.sub(r"(\w*password +|\w*bind-pw +)(.*)", lambda x : x.group(1) + '*'*len(x.group(2)), line, flags=re.IGNORECASE)
        masked_passwords2.append(masked_line2)
    with open(from_remote_to_local_file_path_2, 'w') as remote_file2:
        remote_file2.writelines(masked_passwords2)
                             
def compare_files(from_remote_to_local_file_path_1, from_remote_to_local_file_path_2):
    logger.info("Begining To Compare Files....")
    differ = difflib.HtmlDiff(tabsize=2)
    with open(from_remote_to_local_file_path_1, 'r') as remote_file:
            remote_content_1 = remote_file.readlines()
    with open(from_remote_to_local_file_path_2, 'r') as remote_file:
            remote_content_2 = remote_file.readlines()
    with open("compare.html", "w") as file:
        html_compare = differ.make_file(fromlines=remote_content_1, tolines=remote_content_2, fromdesc=from_remote_to_local_file_path_1, todesc=from_remote_to_local_file_path_2, context=True)
        file.write(html_compare)
    with zipfile.ZipFile ('comparezip.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9 ) as zipf:
        zipf.write('compare.html')          
      
def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    logger.info("Working On Sending Mail....")
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
            logger.info(f"Connection to mail server is successfull:{result}")
            break
        except Exception as e:
            logger.info(f"{e}")
            time.sleep(5)
    server.sendmail(from_email,[to_email],msg.as_string())
    server.quit()
           
def main(): 
    remote_server_1 = input("please enter the ip of first the remote server")
    remote_server_2 = input("please enter the ip of second the remote server")
    remote_file_path = '/config/bigip.conf' #'C:\\myProjects\\pythoncompare\\local_source_file.txt' 
    from_remote_to_local_file_path_1 = f'C:\\myProjects\\pythoncompare\\configurations\\{remote_server_1}_BIGIP_File.txt'
    from_remote_to_local_file_path_2 = f'C:\\myProjects\\pythoncompare\\configurations\\{remote_server_2}_BIGIP_File.txt'
    remote_username = input("Please enter your username For connection")
    remote_content_1 = copy_file1_from_remote(remote_username, remote_server_1, remote_file_path, from_remote_to_local_file_path_1)
    remote_content_2 = copy_file2_from_remote(remote_username, remote_server_2, remote_file_path, from_remote_to_local_file_path_2)
    recp = ['shlomilo@payoneer.com']#,'guyas@payoneer.com','felixzu@payoneer.com','dmitryma@payoneer.com','itayzo@payoneer.com','guyel@payoneer.com','williamwi@payoneer.com','shiranag@payoneer.com','idoad@payoneer.com','oried@payoneer.com','hilawe@payoneer.com'
    to_email = ", ".join(recp)
    from_email = 'F5@payoneer.com'
    smtp_server = '192.168.0.193'
    smtp_port = 25
    subject = "BIG_IP.CONF COMPARISON"
    body = """ 
    <html>
        <head>
            <h1> Here Are The Changes I Found Team.</h1>
        </head>
    </html>    
    """
    mask_passwords(remote_content_1, from_remote_to_local_file_path_1 ,remote_content_2, from_remote_to_local_file_path_2)
    time.sleep(5)
    compare_files(from_remote_to_local_file_path_1, from_remote_to_local_file_path_2)
    send_email(subject, body,to_email,from_email,smtp_server,smtp_port)

if __name__ == "__main__":
    main()

