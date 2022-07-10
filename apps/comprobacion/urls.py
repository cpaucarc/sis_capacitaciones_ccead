from django.urls import path
from .views import (comprobacion_certificado_view)

app_name = 'comprobacion'

urlpatterns = [
    path('certificaciones/<int:capacitacion_id>/<int:persona_id>/', comprobacion_certificado_view, name='certificaciones'),
]