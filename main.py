import re
import requests
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import datetime
import os
from fpdf import FPDF

# using now() to get current time
current_time = datetime.datetime.now()

#Filename
file_name="FENS"+"_"+ str(current_time.day) + "_" + str(current_time.month) + "_" + str(current_time.year)+".txt"

#Convert txt to PDF
pdf = FPDF()

# Add a page
pdf.add_page()
  
# set style and size of font
# that you want in the pdf
pdf.set_font("Arial", size = 15)

#Setting credentials
pdf.set_text_color(0,0,0)  
txt_1="FENS Job Market Weekly Feed"
txt_2="Timestamp: "+str(current_time)+" UTC"
pdf.cell(200, 10, txt = txt_1,ln = 1, align = 'C')
pdf.cell(200, 10, txt = txt_2,ln = 2, align = 'C')
pdf.ln(h=6)


with open(file_name,'wt') as f :
    # #urls=["https://www.fens.org/careers/job-market","https://www.fens.org/careers/job-market/page/2",
    #     "https://www.fens.org/careers/job-market/page/3"]

    urls=["https://www.fens.org/careers/job-market"]
    for url in urls:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()
        print("REQUEST SENT!")

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        href_tags = soup.find_all(href=True)

        job_links=[]
        job_url=[]
        for i in range(len(href_tags)):
            fullstring = str(href_tags[i])
            substring = "https://www.fens.org/careers/job-market/job/"
            try:
                fullstring.index(substring)
            except ValueError:
                continue
            else:
                # print(fullstring)
                job_links.append(fullstring)

        print("JOBS FETCHED!")
        for k in range(len(job_links)):
            if re.sub('<[^<]+?>', '', str(job_links[k])).isdigit():
                url_job="https://www.fens.org/careers/job-market/job/" + re.sub('<[^<]+?>', '', str(job_links[k])) + "/"
                print(url_job,file=f)
                pdf.set_text_color(0,0,255) 
                pdf.write(4,url_job)
                pdf.ln(h=5)
                
                # Send a request to the URL
                response = requests.get(url_job)
                response.raise_for_status()

                # Parse the content using BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                #Get title
                title_tags = soup.find_all('title')
                title=str(title_tags).split('>')[1].split('<')[0]
                print("Title: ",title,file=f)
                keywords=['<p>Job ID:','<p><b>Position:','<p><b>Deadline:',
                        '<p><b>Employment Start Date:','<p><b>Country:','<p><b>Institution:','URL:',
                        "<p><b>Department:"]
                data=[]
                for j in range(len(list(soup.find_all('p')))):
                    for keys in keywords:
                        if str(soup.find_all('p')[j]).find(keys) != -1:
                            #print(soup.find_all('p')[j])
                            print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])),file=f)
                            print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            pdf.set_text_color(0,0,0) 
                            pdf.write(4,re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            pdf.ln(h=5)
                
                print('\n',file=f)
                pdf.ln(h=8)
                print('URL:',url_job,' DONE!')

print("FETCH COMPLETE!")
pdf.output("FENS_Weekly.pdf")

msg = EmailMessage()
msg["From"] = 'ihiteshpradhan@gmail.com'
msg["Subject"] = "FENS Weekly Update"
# msg["To"] = "fens_scrappingtest@googlegroups.com"
msg["To"] = "htshpradhan5@gmail.com"
msg.set_content("Please find attached the FENS weekly update")
# msg.add_attachment(open("Test.pdf").read(), filename="Test.pdf")

with open('FENS_Weekly.pdf', 'rb') as content_file:
    content = content_file.read()
    msg.add_attachment(content, maintype='application', subtype='pdf', filename='FENS_Weekly.pdf')

s = smtplib.SMTP_SSL('smtp.gmail.com')
s.login('ihiteshpradhan@gmail.com', "nacgchovphdkoujl")
s.send_message(msg)

os.rename(file_name,"FENS_Output.txt")