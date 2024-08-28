#MODULES TO IMPORT
import subprocess
from tabulate import tabulate
import smtplib
from email.mime.text import MIMEText

#FUNCTIONS
###########################################################################################
def copy_file_from_remote(remote_username, remote_server, remote_file_path, from_remote_to_local_file_path):
    # Copy file from remote server to local server using scp
    scp_command = f"scp {remote_username}@{remote_server}:{remote_file_path} {from_remote_to_local_file_path}"
    try:
        subprocess.run(scp_command, shell=True, check=True)
        print(f"File copied successfully from {remote_server}:{remote_file_path} to {from_remote_to_local_file_path}")

        # Read the content of the file
        with open(from_remote_to_local_file_path, 'r') as remote_file:
            remote_content = remote_file.readlines()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return remote_content

def read_local_file(source_local_file_path):
    with open(source_local_file_path, 'r') as local_file:
        return local_file.readlines()
    
def compare_files(remote_content, local_content):
    diff = []
    for line_num,(line1, line2) in enumerate(zip(local_content,remote_content),start=1):
        if line1 != line2:
            diff.append("I have Found some diffrences:")
            diff.append((line_num,line1.strip(),line2.strip()))
        else:
            diff.append("There is no differences between the files")
    return diff

def format_as_table(diff):
    headers = ["Line Number","Source server",'Remote_server']
    return tabulate(diff,headers,tablefmt="grid")

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    msg = MIMEText(body, "plain")
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP(smtp_server,smtp_port) as server:
        server.connect(smtp_server)
        server.starttls()
        server.sendmail(from_email,[to_email],msg.as_string())
        server.quit()

def main():
    remote_server = input("please enter the ip of the remote server")
    remote_file_path = '/config/bigip.conf'
    from_remote_to_local_file_path= f'C:\\myProjects\\pythoncompare\\{remote_server}_BIGIP.txt' 
    source_local_file_path = 'C:\\myProjects\\pythoncompare\\local_source_file.txt' 
    remote_username =input("Please enter your username For connection")
    remote_content = copy_file_from_remote(remote_username, remote_server, remote_file_path, from_remote_to_local_file_path)
    local_content = read_local_file(source_local_file_path)
    recp = ['shlomilo@payoneer.com']#,'guyas@payoneer.com','dmitryma@payoneer.com','itayzo@payoneer.com','guyel@payoneer.com','williamwi@payoneer.com','shiranag@payoneer.com','idoad@payoneer.com',oried@payoneer.com,hilawe@payoneer.com]
    to_email = ", ".join(recp)
    from_email = 'BIG_IP_Compare@payoneer.com'
    smtp_server = 'payoneer-com.mail.protection.outlook.com'
    smtp_port = 25
    subject = "BIG_IP.CONF COMPARISON"
    diff= compare_files(remote_content,local_content)
    table = format_as_table(diff)
    send_email(subject,table,to_email,from_email,smtp_server,smtp_port)


if __name__ == "__main__":
    main()
