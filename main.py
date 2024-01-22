from scripts import custom

def main():
    format_time, tag_time = custom.fetch_time()
    pdf = custom.create_pdf(format_time)

    custom.update_data()         
    custom.get_metadata(pdf,format_time,tag_time)
    custom.send_mail(format_time,tag_time)

    return

if __name__ == "main":
    main()