from xhtml2pdf import pisa
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from django.conf import settings
import os
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders




def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path



def generate_pdf(context):
    template = get_template('profile_report.html')
    html = template.render(context)

    result_file = open('result.pdf', "w+b")

    pisa_status = pisa.CreatePDF(
        html, dest=result_file, link_callback=fetch_pdf_resources)






