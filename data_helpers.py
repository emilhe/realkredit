import urllib.parse
import xml.etree.ElementTree as ET
import requests

from dateutil import parser

url = "http://www.nasdaqomxnordic.com/webproxy/DataFeedProxy.aspx"
header_template = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "http://www.nasdaqomxnordic.com",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "http://www.nasdaqomxnordic.com/bonds/denmark/microsite?Instrument={Instrument}",
    "Cookie": "JSESSIONID=B5C2693879EED34FE5D72E7ADE811986; NSC_MC_Obtebrpnyopsejd_IUUQ=ffffffff09be0e1e45525d5f4f58455e445a4a423660; ASP.NET_SessionId=3nwskr455k2zpdq3vrgjalmr",
}
query_template = 'xmlquery=%3Cpost%3E%0A%3Cparam+name%3D%22SubSystem%22+value%3D%22Prices%22%2F%3E%0A%3Cparam+name%3D%22Action%22+value%3D%22GetTrades%22%2F%3E%0A%3Cparam+name%3D%22Exchange%22+value%3D%22NMF%22%2F%3E%0A%3Cparam+name%3D%22ext_xslt_tableId%22+value%3D%22danish-bond-trade-history-table%22%2F%3E%0A%3Cparam+name%3D%22ext_xslt%22+value%3D%22%2FnordicV3%2Ft_table_simple.xsl%22%2F%3E%0A%3Cparam+name%3D%22ext_xslt_lang%22+value%3D%22en%22%2F%3E%0A%3Cparam+name%3D%22Instrument%22+value%3D%22{Instrument}%22%2F%3E%0A%3Cparam+name%3D%22t__a%22+value%3D%221%2C2%2C4%2C6%2C7%2C8%2C18%22%2F%3E%0A%3Cparam+name%3D%22showall%22+value%3D%221%22%2F%3E%0A%3Cparam+name%3D%22FromDate%22+value%3D%22{FromDate}%22%2F%3E%0A%3Cparam+name%3D%22ToDate%22+value%3D%22{ToDate}%22%2F%3E%0A%3Cparam+name%3D%22app%22+value%3D%22%2Fbonds%2Fdenmark%2Fmicrosite%22%2F%3E%0A%3C%2Fpost%3E'
dt_format = "%Y-%m-%d"


def fetch_data(dt_from, dt_to, instrument):
    key = urllib.parse.quote_plus(instrument)
    q = query_template.format(FromDate=dt_from.strftime(dt_format), ToDate=dt_to.strftime(dt_format), Instrument=key)
    h = dict(header_template)
    h["Referer"].format(Instrument=instrument)
    r = requests.post(url, headers=h, data=q)
    return r.text


def parse_data(data):
    root = ET.fromstring(data)
    body = root[1]
    times = [parser.parse(item[2].text) for item in body]
    prices = [float(item[0].text) for item in body]
    xy = sorted(zip(times, prices))
    return [x for x, y in xy], [y for x, y in xy]
