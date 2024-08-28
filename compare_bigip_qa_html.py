#This Script is compatiable to python 2.7
#if you want to make it compatiable to 3.6, change the following:

#raw_input to input method.
#format method to f-string. 
#subprocess.call to subprocess.run , add the line : shell=True, check=True after scp_command in the ()
#server = smtplib.SMTP(smtp_server,smtp_port) -> with .... as server  


#script by shlomi lory
##########################################################################


#MODULES TO IMPORT
import subprocess
import smtplib
from email.mime.text import MIMEText
import time

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
    
def generate_html_table(diff):
    html_content = """
    <html>
    <head>
        <h1> Here Are The Changes I Found Team:</h1>
        <style>
            table {
            font-family: Arial, sans-serif; border-collapse:collapse; width: 100%; 10.31.10.171
            }
            td, th {
            border: 1px
            solid #dddddd; text-align: left;
            padding: 8px;
            }
            tr:first-child{
            background-color: red;
            }
            .diff-added{
            background-color: #d4ffdc;
            }
            .diff-removed{
            background-color: #ffd4d4;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Line Number</th>
                <th>Local Server</th>
                <th>Remote Server</th>
            </tr>
"""
    for line in diff:
        num = line[0]
        Local_srv = line[1]
        Remote_srv = line[2]
        line_class = 'diff-removed'
        html_content += '<tr class="{}"><td>{}</td><td>{}</td><td>{}</td></tr>'.format(line_class, num, Local_srv, Remote_srv)
    html_content += """
        </table>
    </body
    </html>
    """
    return html_content
def no_changes():
    html_content = """
    <html>
    <head>
    <h1>There is no Diffrences between the files !</h1>
    </head>
    </html>"""
    return html_content

def compare_files(remote_content, local_content):
    diff = []
    for line_num,(line1, line2) in enumerate(zip(local_content,remote_content),start=1):
        if line1 != line2:
            diff.append((line_num,line1.strip(),line2.strip()))
            html_table = generate_html_table(diff)
    
    if not diff: 
        html_table = no_changes()
    return html_table

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port):
    msg = MIMEText(body, "html")
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    server = smtplib.SMTP(smtp_server,smtp_port)
    isuccessful = False
    while not isuccessful:
        try:
            result = server.connect(smtp_server)
            isuccessful = True
            print("Command connect is successfully:{}".format(result))
            break
        except Exception as e:
            print("{}".format(e))
            time.sleep(1)
    server.sendmail(from_email,[to_email],msg.as_string())
    server.quit()
           
def main():        
    remote_server = raw_input("please enter the ip of the remote server")
    remote_file_path = '/config/bigip.conf'
    from_remote_to_local_file_path= '/var/tmp/{}_BIGIP.'.format(remote_server) 
    source_local_file_path =  '/config/bigip.conf' 
    remote_username =raw_input("Please enter your username For connection")
    remote_content = copy_file_from_remote(remote_username, remote_server, remote_file_path, from_remote_to_local_file_path)
    local_content = read_local_file(source_local_file_path)
    recp = ['shlomilo@payoneer.com']#,'guyas@payoneer.com','felixzu@payoneer.com','dmitryma@payoneer.com','itayzo@payoneer.com','guyel@payoneer.com','williamwi@payoneer.com','shiranag@payoneer.com','idoad@payoneer.com','oried@payoneer.com','hilawe@payoneer.com']
    to_email = ", ".join(recp)
    from_email = 'test@payoneer.com'
    smtp_server = '192.168.0.193'
    smtp_port = 25
    subject = "BIG_IP.CONF COMPARISON - Test - please ignore this mail!!!!"
    compared_files = compare_files(remote_content, local_content)
    send_email(subject,compared_files,to_email,from_email,smtp_server,smtp_port)
    

if __name__ == "__main__":
    main()

