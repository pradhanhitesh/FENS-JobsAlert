import re
import requests
from bs4 import BeautifulSoup
import datetime
import os
from fpdf import FPDF
import yake
import pytz
import glob
import shutil
import smtplib
from email.message import EmailMessage
import json
import seaborn as sns
import matplotlib.pyplot as plt

def fetch_time():
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    format_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    tag_time = str(current_time.day) + str(current_time.month) + str(current_time.year) + str(current_time.hour) + str(current_time.minute) + str(current_time.second)
    
    return format_time, tag_time

def create_pdf(format_time):
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
    txt_2="Last updated on: "+str(format_time)+" IST"
    txt_3="github.com/pradhanhitesh"
    pdf.cell(200, 10, txt = txt_1,ln = 1, align = 'C')
    pdf.cell(200, 10, txt = txt_2,ln = 2, align = 'C')
    pdf.cell(200, 10, txt = txt_3,ln = 2, align = 'C')
    pdf.ln(h=6)

    return pdf

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = []
    dict[key].append(value)

def update_data():
    fens_files = glob.glob('./FENS*')
    if len(fens_files) > 0:
        # print("FILES FOUND")
        for i in range(len(fens_files)):
            shutil.move(fens_files[i],'./data/metadata/')
    img_files = glob.glob('./CountryCount*')
    if len(img_files) > 0:
        # print("FILES FOUND")
        for i in range(len(img_files)):
            shutil.move(img_files[i],'./data/images/')

    return

def get_metadata(pdf,format_time,tag_time):    
    file_name = "FENS_" + tag_time + ".txt"

    # Gather metadata for job-links
    data_dict = {}
    add_element(data_dict,'Timestamp',format_time)
    
    with open(file_name,'wt') as f :
        urls=["https://www.fens.org/careers/job-market"]
        for url in urls:
            # Send a request to the URL
            response = requests.get(url)
            response.raise_for_status()
            print(f"{format_time} REQUEST SENT!")

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            href_tags = soup.find_all(href=True)

            # Fetch job-links
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

            print(f"{format_time} JOBS FETCHED!")

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

                    # Get title
                    title_tags = soup.find_all('title')
                    title=str(title_tags).split('>')[1].split('<')[0]
                    print("Title: ",title)
                    pdf.set_text_color(0,0,0) 
                    title_text="Title: "+str(title_tags).split('>')[1].split('<')[0]
                    pdf.multi_cell(w=190, h=5, txt=title_text, border=0, align='L', fill=False)

                    # Get other info
                    keywords=['<p>Job ID:','<p><b>Position:','<p><b>Deadline:',
                            '<p><b>Employment Start Date:','<p><b>Country:','<p><b>Institution:','URL:',
                            "<p><b>Department:"]
                    
                    local = []
                    for j in range(len(list(soup.find_all('p')))):
                        for keys in keywords:
                            if str(soup.find_all('p')[j]).find(keys) != -1:
                                print(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                                local.append(re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                                pdf.write(4,re.sub('<[^<]+?>', '',str(soup.find_all('p')[j])))
                                pdf.ln(h=5)

                    add_element(data_dict,'JobID',list(filter(lambda x: x.startswith('Job ID'), local))[0].split(': ')[1])
                    add_element(data_dict,'Country',list(filter(lambda x: x.startswith('Country'), local))[0].split(': ')[1])

                    # Generate keywords for each job-links from descirption
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
    pdf.output("FENS_"+tag_time+".pdf")

    return data_dict

def send_mail(format_time,tag_time):
    msg = EmailMessage()
    msg["From"] = os.environ.get('FROM_ID')
    msg["Subject"] = "FENS Weekly Update" 
    msg["To"] = os.environ.get('TO_ID')
    msg.set_content(f"Dear subscriber, \nPlease find attached the FENS Weekly Update. \nGenerated on {format_time} IST. \n\nRegards,\nHitesh Pradhan")

    with open("FENS_"+ tag_time +".pdf", 'rb') as content_file:
        content = content_file.read()
        msg.add_attachment(content, maintype='application', subtype='pdf', filename="FENS_"+ tag_time +".pdf")

    s = smtplib.SMTP_SSL('smtp.gmail.com')
    s.login(os.environ.get('EMAIL'),os.environ.get('LOGIN_KEY')) #Add your credentials
    s.send_message(msg)

    return

def update_data_json(data_dict):
    with open("data/data.json") as doc:
        docObj = json.load(doc)
        docObj.append(
            data_dict
        )
    with open("data/data.json", 'w') as json_file:
        json.dump(docObj, json_file, 
                  indent=4,  
                  separators=(',',': '))
    return

def count_countries():
    def count_frequency(input_list):
        frequency_dict = {}

        for element in input_list:
            if element in frequency_dict:
                frequency_dict[element] += 1
            else:
                frequency_dict[element] = 1

        return frequency_dict

    with open("data/data.json") as doc:
        docObj = json.load(doc)

    unique_id = []
    unique_countries =[]

    for k in range(len(docObj)):
        fetch_ids =  docObj[k]['JobID']
        for idx, job_ids in enumerate(fetch_ids):
            if job_ids not in unique_id:
                unique_id.append(docObj[k]['JobID'][idx])
                unique_countries.append(docObj[k]['Country'][idx])


    store_count = count_frequency(unique_countries)

    return store_count

def generate_plot(count_dict,tag_time,format_time):
    plt.figure(figsize=(12,5))
    plt.xticks(range(len(count_dict)), list(count_dict.keys()), rotation=45)

    ax = sns.barplot(x = list(count_dict.keys()), 
                     y = list(count_dict.values()))
    ax.bar_label(ax.containers[0])
    txt = "Last updated on: " + str(format_time) + " IST"
    plt.text((len(count_dict.keys())/2) + 0.2, max(count_dict.values()), txt, fontsize = 13)

    plt.savefig('CountryCount_' + tag_time +'.png',bbox_inches='tight')
    plt.close()

    return

def generate_html_plot(format_time):
    all_files = os.listdir("./")
    png_files = [file for file in all_files if file.startswith('CountryCount_') and file.endswith('.png')]

    template_vars = {
        'plot' : f'<img src="{png_files[0]}" width="750" height="400">',
        'timestamp' : format_time
        }
    
    return template_vars