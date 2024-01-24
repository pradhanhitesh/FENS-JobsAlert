from jinja2 import Environment, FileSystemLoader
from scripts import custom

def main():
    format_time, tag_time = custom.fetch_time()
    pdf = custom.create_pdf(format_time)

    custom.update_data()         
    data_dict = custom.get_metadata(pdf,format_time,tag_time)
    custom.update_data_json(data_dict)
    custom.generate_plot(count_dict=custom.count_countries())
    custom.send_mail(format_time,tag_time)

    template_vars = custom.generate_html_plot(format_time)
    env = Environment(loader=FileSystemLoader("template"))
    template = env.get_template("template.html")
    output_from_parsed_template = template.render(template_vars)

    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)


if __name__ == "__main__":
    main()