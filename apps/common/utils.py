import io
import os
import uuid
import base64

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views import View
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas

# Clases auxiliares que agrupan elementos repetidos
class EstilosPdf:
    def __init__(self):
        self.style = getSampleStyleSheet()['BodyText']
        self.style.fontName = 'Helvetica-Bold'
        self.style.alignment = TA_CENTER
        self.style.fontSize = 11

        self.style1 = getSampleStyleSheet()['Normal']
        self.style1.fontSize = 6

        self.style2 = getSampleStyleSheet()['Normal']
        self.style2.fontSize = 28
        self.style2.alignment = TA_CENTER
        self.style2.fontName = 'Helvetica-Bold'

        self.style3 = getSampleStyleSheet()['Normal']
        self.style3.fontSize = 12

        self.style_footer = getSampleStyleSheet()['Normal']
        self.style_footer.alignment = TA_CENTER
        self.style_footer.fontSize = 12

        self.style_fecha_lugar = getSampleStyleSheet()['Normal']
        self.style_fecha_lugar.alignment = TA_CENTER
        self.style_fecha_lugar.fontSize = 12

        self.style4 = getSampleStyleSheet()['Normal']
        self.style4.fontSize = 12
        self.style4.leading = 20
        self.style4.alignment = TA_JUSTIFY
        self.style4.padding = '20px'

        self.style5 = getSampleStyleSheet()['Normal']
        self.style5.fontName = 'Helvetica-Bold'
        self.style5.leading = 14
        self.style5.fontSize = 12.5
        self.style5.alignment = TA_CENTER

        self.style_fullname = getSampleStyleSheet()['Normal']
        self.style_fullname.fontSize = 13
        self.style_fullname.alignment = TA_CENTER

        self.style_art = getSampleStyleSheet()['Normal']
        self.style_art.fontSize = 8
        self.style_art.leading = 12
        self.style_art.alignment = TA_JUSTIFY
        self.style_art.padding = '15px'

        self.style_verf = getSampleStyleSheet()['Normal']
        self.style_verf.fontSize = 8
        self.style_verf.alignment = TA_CENTER

        self.table_style1 = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black, None),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
        ]

        self.table_style_firma = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]

class Utilidades:
    def __init__(self):
        self.meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
                      "octubre", "noviembre", "diciembre"]

    def obtener_path_temporal_firma(self, id, firma):
        path = ''
        try:
            decode = base64.b64decode(firma)
            filename = default_storage.save('firma_{}_temp.jpg'.format(id), ContentFile(decode))
            path = default_storage.path(filename)
        except:  # noqa
            pass
        return path

class Textos:
    def __init__(self):
        self.cuerpo = '''Por haber participado en calidad de {} el curso-taller de {}{}, llevado a cabo
                        en forma {} del {} de {} de {} al {} de {} de {} con un total de {} horas acad??micas.'''
        self.fecha_lugar = 'Huaraz, {} de {} de {}'
        self.articulo = 'El presente certificado y las firmas consignados en ??l han sido emitidos a trav??s de medios digitales, al amparo de lo dispuesto en el art??culo 141-A del C??digo Civil:<br/>"Art??culo 141-A.- En los casos en que la ley establezca que la manifestaci??n de voluntad debe hacerse a trav??s de alguna formalidad expresa o requerida de firma, ??sta podr?? ser generada o comunicada a trav??s de medios electr??nicos, ??pticos o cualquier otro an??logo. Trat??ndose de instrumentos p??blicos, la autoridad competente deber?? dejar constancia del medio empleado y conservar una versi??n ??ntegra para su ulterior consulta."'
        self.autenticidad = 'Verifique la autenticidad de este documento digital a trav??s del c??digo QR.'

# Clase principal
class PdfCertView(View, EstilosPdf, Utilidades, Textos):
    filename = ''
    disposition = 'inline'

    def __init__(self):
        EstilosPdf.__init__(self)
        Utilidades.__init__(self)
        Textos.__init__(self)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = '{}; filename={}'.format(self.disposition, self.filename)
        c = Canvas(response)
        c.setFont('Helvetica', 12)
        c._doc.setTitle(self.filename)
        c = self.process_canvas(c)
        c.save()
        return response

    def process_canvas(self, _canvas):
        raise NotImplementedError