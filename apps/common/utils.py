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
        self.style4.fontSize = 11
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
        self.style_art.fontSize = 6.5
        self.style_art.leading = 9
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

    def obtener_fecha_capacitacion(self, fecha_inicio, fecha_fin):
        # Si la capacitación fue entre dos años, retornar fecha completo
        if int(fecha_inicio.year) != int(fecha_fin.year):
            return "del {} de {} de {} al {} de {} de {}".format(
                fecha_inicio.day,
                self.meses[fecha_inicio.month],
                fecha_inicio.year,
                fecha_fin.day,
                self.meses[fecha_fin.month],
                fecha_fin.year
            )

        # La capacitación fue en el mismo año
        # Si la capacitación fue en diferentes meses, del mismo año
        if int(fecha_inicio.month) != int(fecha_fin.month):
            return "del {} de {} al {} de {} de {}".format(
                fecha_inicio.day,
                self.meses[fecha_inicio.month],
                fecha_fin.day,
                self.meses[fecha_fin.month],
                fecha_inicio.year
            )

        # Si la capacitación fue en diferentes dias, del mismo mes y año
        if int(fecha_inicio.day) != int(fecha_fin.day):
            return "del {} al {} de {} de {}".format(
                fecha_inicio.day,
                fecha_fin.day,
                self.meses[fecha_inicio.month],
                fecha_inicio.year
            )

        # La capacitacion fue el mismo dia, mismo mes y año
        return "el {} de {} de {}".format(fecha_inicio.day, self.meses[fecha_inicio.month], fecha_inicio.year)


class Textos:
    def __init__(self):
        self.cuerpo = '''Por haber participado en calidad de {} en el Curso-Taller "{}"{}, llevado a cabo
                        {} {}, con una duración de {} horas académicas.'''
        self.fecha_lugar = 'Huaraz, {} de {} de {}'
        self.articulo = 'El presente certificado y las firmas consignados en él han sido emitidos a través de medios digitales, al amparo de lo dispuesto en el artículo 141-A del Código Civil:<br/>"Artículo 141-A.- En los casos en que la ley establezca que la manifestación de voluntad debe hacerse a través de alguna formalidad expresa o requerida de firma, ésta podrá ser generada o comunicada a través de medios electrónicos, ópticos o cualquier otro análogo. Tratándose de instrumentos públicos, la autoridad competente deberá dejar constancia del medio empleado y conservar una versión íntegra para su ulterior consulta."'
        self.autenticidad = 'Verifique la autenticidad de este documento digital a través del código QR.'

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