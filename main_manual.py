import re
import requests
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import datetime
import os
from fpdf import FPDF
import yake
import pytz
import glob
import shutil

def _fetch_time():
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    format_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return current_time, format_time

def _create_pdf(current_time):
    #Convert txt to PDF
    pdf = FPDF()
    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.add_font('DejaVu', '', './fonts/Tinos-Regular.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)

    #Setting credentials
    pdf.set_text_color(0,0,0)  
    txt_1="FENS Job Market Weekly Feed"
    txt_2="Last updated on: "+str(current_time[1])+" IST"
    txt_3="github.com/pradhanhitesh"
    pdf.cell(200, 10, txt = txt_1,ln = 1, align = 'C')
    pdf.cell(200, 10, txt = txt_2,ln = 2, align = 'C')
    pdf.cell(200, 10, txt = txt_3,ln = 2, align = 'C')
    pdf.ln(h=6)

    return pdf

def _move_fens():
    fens_files = glob.glob('./FENS*')
    if len(fens_files) > 0:
        # print("FILES FOUND")
        for i in range(len(fens_files)):
            shutil.move(fens_files[i],'./data/')

    return None

def _get_metadata(file_name):
    current_time = _fetch_time()
    pdf = _create_pdf(current_time)
    
    with open(file_name,'wt') as f :

        urls=["https://www.fens.org/careers/job-market"]
        for url in urls:
            # Send a request to the URL
            response = requests.get(url)
            response.raise_for_status()
            print(f"{_fetch_time()[1]} REQUEST SENT!")

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            href_tags = soup.find_all(href=True)

            job_links=[]
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

            print(f"{_fetch_time()[1]} JOBS FETCHED!")

            for k in range(2):
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
                    print("Title: ",title)
                    pdf.set_text_color(0,0,0) 
                    title_text="Title: "+str(title_tags).split('>')[1].split('<')[0]
                    pdf.multi_cell(w=190, h=5, txt=title_text, border=0, align='L', fill=False)

                    keywords=['<p>Job ID:','<p><b>Position:','<p><b>Deadline:',
                            '<p><b>Employment Start Date:','<p><b>Country:','<p><b>Institution:','URL:',
                            "<p><b>Department:"]

                    for j in range(len(list(soup.find_all('p')))):
                        for keys in keywords:
                            if str(soup.find_all('p')[j]).find(keys) != -1:
                                print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                                pdf.write(4,re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                                pdf.ln(h=5)

                    save_des=["<p><b>Description:"]
                    for j in range(len(list(soup.find_all('p')))):
                        for keys in save_des:
                            if str(soup.find_all('p')[j]).find(keys) != -1:
                                text_save = re.sub('<[^<]+?>', '',str(soup.find_all('p')[j]))
                                kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
                                keywords = kw_extractor.extract_keywords(text_save)
                                text="Keywords: "

                                for kw in range(len(keywords)):
                                    text=text+keywords[kw][0]+"; "
                                    if kw == 9:
                                        print(text)
                                        pdf.multi_cell(w=190, h=5, txt=text, border=0, align='L', fill=False)
                                        pdf.ln(h=5)


date = str(current_time[0].day) + str(current_time[0].month) + str(current_time[0].year) + str(current_time[0].hour) + str(current_time[0].minute)

#Filename
file_name="FENS"+"_"+date +".txt"

_move_fens()         
_get_metadata(file_name)
pdf.output("FENS_"+date+".pdf")

msg = EmailMessage()
msg["From"] = os.environ.get('FROM_ID')
msg["Subject"] = "FENS Weekly Update" 
msg["To"] = os.environ.get('TO_ID')
msg.set_content(f"Dear subscriber, \nPlease find attached the FENS Weekly Update. \nGenerated on {current_time[1]} IST. \n\nRegards,\nHitesh Pradhan")

with open("FENS_"+date+".pdf", 'rb') as content_file:
    content = content_file.read()
    msg.add_attachment(content, maintype='application', subtype='pdf', filename="FENS_"+date+".pdf")

s = smtplib.SMTP_SSL('smtp.gmail.com')
s.login(os.environ.get('EMAIL'),os.environ.get('LOGIN_KEY')) #Add your credentials
s.send_message(msg)