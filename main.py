from jinja2 import Environment, FileSystemLoader
from scripts import custom

def main():
    format_time, tag_time = custom.fetch_time()
    pdf = custom.create_pdf(format_time)

    custom.update_data()         
    custom.get_metadata(pdf,format_time,tag_time)
    # custom.send_mail(format_time,tag_time)

    template_vars = custom.generate_html(format_time)
    env = Environment(loader=FileSystemLoader("template"))
    template = env.get_template("template.html")
    output_from_parsed_template = template.render(template_vars)

    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)


if __name__ == "__main__":
    main()