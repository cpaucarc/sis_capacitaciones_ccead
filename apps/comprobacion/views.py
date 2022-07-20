from django.shortcuts import render, get_object_or_404
from apps.capacitacion.models import Capacitacion, HistorialRevision, Modulo, EquipoProyecto, ActaAsistencia, NotaParticipante
from apps.persona.models import Persona
from django.urls import reverse

def comprobacion_certificado_view(request, capacitacion_id, persona_id):

    capacitacion = get_object_or_404(Capacitacion, pk=capacitacion_id)
    fecha_emision = HistorialRevision.objects.filter(capacitacion=capacitacion).last().fecha_creacion.strftime("%d/%m/%Y")
    persona = get_object_or_404(Persona, pk=persona_id)
    modulos = Modulo.objects.filter(capacitacion=capacitacion)

    total_horas = 0
    for modulo in modulos:
        total_horas += modulo.horas_academicas

    # Verificamos si la persona es participante
    actas = ActaAsistencia.objects.filter(modulo__in=modulos)
    es_participante = NotaParticipante.objects.filter(persona=persona, acta_asistencia__in=actas).exists()

    # Verificamos si la persona tiene otros cargos
    cargos_persona = []
    cargos = EquipoProyecto.objects.filter(capacitacion=capacitacion, persona=persona)
    for cargo in cargos:
        cargos_persona.append(cargo.cargo.upper())

    if es_participante:
        cargos_persona.append("ASISTENTE")

    cantidad_cargos = len(cargos_persona)

    context = {
        'capacitacion': capacitacion,
        'fecha_emision': fecha_emision,
        'total_horas': total_horas,
        'persona' : persona,
        'cantidad_cargos' : cantidad_cargos,
        'cargos': ', '.join(cargos_persona)
    }

    return render(request, 'capacitacion/comprobacion_certificado.html', context)
