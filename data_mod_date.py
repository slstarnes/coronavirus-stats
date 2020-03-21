import requests
from dateutil.parser import parse as date_parser
from lxml import html as html_parser
import pytz




def get_data_mod_date(url):
    r = requests.get(url)
    if r.status_code == 200:
        tree = html_parser.fromstring(r.content)
        t = tree.xpath('/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/span[2]/relative-time')
        d = date_parser(t[0].attrib['datetime'])
        tz = pytz.timezone('America/New_York')
        d = d.astimezone(tz)
        return f'{d:%m-%d-%Y @ %-I:%M %p %Z}'
    return
