import re
import requests
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import datetime
import os
from fpdf import FPDF
import yake
# import docx
# from docx.shared import Inches
# from docx.enum.text import WD_ALIGN_PARAGRAPH

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
pdf.add_font('DejaVu', '', 'Tinos-Regular.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)

#Setting credentials
pdf.set_text_color(0,0,0)  
txt_1="FENS Job Market Weekly Feed"
txt_2="Timestamp: "+str(current_time)+" UTC"
txt_3="Follow on LinkedIn for more! linkedin.com/in/pradhanhitesh"
pdf.cell(200, 10, txt = txt_1,ln = 1, align = 'C')
pdf.cell(200, 10, txt = txt_2,ln = 2, align = 'C')
pdf.cell(200, 10, txt = txt_3,ln = 2, align = 'C')
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
                print("Title: ",title)
                # para=doc.add_paragraph(title)
                # # Adding linspace of 0.5 inches in the paragraph
                # para.paragraph_format.line_spacing = Inches(0.1)
                pdf.set_text_color(0,0,0) 
                # pdf.write(4,"Title: ")
                # pdf.write(4,str(title_tags).split('>')[1].split('<')[0])
                title_text="Title: "+str(title_tags).split('>')[1].split('<')[0]
                pdf.multi_cell(w=190, h=5, txt=title_text, border=0, align='L', fill=False)

                keywords=['<p>Job ID:','<p><b>Position:','<p><b>Deadline:',
                        '<p><b>Employment Start Date:','<p><b>Country:','<p><b>Institution:','URL:',
                        "<p><b>Department:"]
                data=[]
                for j in range(len(list(soup.find_all('p')))):
                    for keys in keywords:
                        if str(soup.find_all('p')[j]).find(keys) != -1:
                            #print(soup.find_all('p')[j])
                            print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            # para=doc.add_paragraph(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            # # Adding linspace of 0.5 inches in the paragraph
                            # para.paragraph_format.line_spacing = Inches(0.1)
                            pdf.write(4,re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            pdf.ln(h=5)

                save_des=["<p><b>Description:"]
                for j in range(len(list(soup.find_all('p')))):
                    for keys in save_des:
                        if str(soup.find_all('p')[j]).find(keys) != -1:
                            # print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                            text_save = re.sub('<[^<]+?>', '',str(soup.find_all('p')[j]))
                            kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
                            keywords = kw_extractor.extract_keywords(text_save)
                            text="Keywords: "
                            # pdf.ln(h=3)
                            # pdf.write(4,text)
                            for kw in range(len(keywords)):
                                text=text+keywords[kw][0]+"; "
                                if kw == 9:
                                    print(text)
                                    pdf.multi_cell(w=190, h=5, txt=text, border=0, align='L', fill=False)
                                    pdf.ln(h=5)
                                # para=doc.add_paragraph(keywords[kw][0])
                                # pdf.write(4,keywords[kw][0])
                                # pdf.write(4,";")


            

# # Now save the document to a location
# doc.save('gfg.docx')

# print('URL:',url_job,' DONE!')
pdf.output("FENS_Weekly.pdf")

msg = EmailMessage()
msg["From"] = 'ihiteshpradhan@gmail.com' #Sender email ID
msg["Subject"] = "FENS Weekly Update" 
msg["To"] = "ihiteshpradhan@gmail.com" #Google Group IDD
msg.set_content("Please find attached the FENS weekly update")
# msg.add_attachment(open("Test.pdf").read(), filename="Test.pdf")

with open('FENS_Weekly.pdf', 'rb') as content_file:
    content = content_file.read()
    msg.add_attachment(content, maintype='application', subtype='pdf', filename='FENS_Weekly.pdf')

s = smtplib.SMTP_SSL('smtp.gmail.com')
s.login(os.environ.get('EMAIL'), os.environ.get('LOGIN_KEY')) #Add your credentials

os.rename(file_name,"FENS_Output.txt")
