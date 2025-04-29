import functools

from django.conf import settings
from django.utils import timezone
from django.views.generic import DetailView

from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse
from django_weasyprint.utils import django_url_fetcher


class PrintDetailView(DetailView):
    # vanilla Django DetailView
    template_name = 'mymodel.html'



class CustomWeasyTemplateResponse(WeasyTemplateResponse):

    # customized response class to pass a kwarg to URL fetcher
    # def get_url_fetcher(self):
    #     # disable host and certificate check
    #     context = ssl.create_default_context()
    #     context.check_hostname = False
    #     context.verify_mode = ssl.CERT_NONE
    #     return functools.partial(custom_url_fetcher, ssl_context=context)
    pass

class PrintView(WeasyTemplateResponseMixin, PrintDetailView):
    # output of MyDetailView rendered as PDF with hardcoded CSS
    pdf_stylesheets = [
        settings.STATIC_ROOT,
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False
    # custom response class to configure url-fetcher
    response_class = CustomWeasyTemplateResponse

class DownloadView(WeasyTemplateResponseMixin, PrintDetailView):
    # suggested filename (is required for attachment/download!)
    pdf_filename = 'foo.pdf'
    # set PDF variant to 'pdf/ua-1' (see weasyprint.DEFAULT_OPTIONS)
    pdf_options = {'pdf_variant': 'pdf/ua-1'}

class DynamicNameView(WeasyTemplateResponseMixin, PrintDetailView):
    # dynamically generate filename
    def get_pdf_filename(self):
        return 'foo-{at}.pdf'.format(
            at=timezone.now().strftime('%Y%m%d-%H%M'),
        )