from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Image
from io import BytesIO
import os

from django.contrib.auth.decorators import user_passes_test
from .models import Egresado
from .auth import is_egresado

from django.contrib import messages
from django.shortcuts import redirect

@user_passes_test(is_egresado)
def cni(request):
    egresado = Egresado.objects.get(usuario=request.user)
    saludo = 'Bienvenida' if egresado.genero == 'F' else 'Bienvenido'
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create canvas
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add logo (place your logo.png in static/images)
    logo_path = os.path.join('titulacion', 'static', 'titulacion', 'images', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
        logo.drawOn(p, 100, height - 150)
    
    # Set font and write text
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height - 200, f"{saludo} {egresado.nombre_completo()}")
    
    p.setFont("Helvetica", 14)
    p.drawString(100, height - 250, f"Número de control: {egresado.numero_control}")
    
    # Close PDF
    p.showPage()
    p.save()
    
    # Get PDF value from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bienvenida_{egresado.numero_control}.pdf"'
    response.write(pdf)
    return response


# Aqui se registran los documento con la funcion que los genera
REGISTRO_DOCUMENTOS = {
    'cni': cni,
}

def generar_documento(request):
    clave_documento = request.POST.get('clave_documento')

    if clave_documento in REGISTRO_DOCUMENTOS:
        # Ejecuta la función asociada y retorna su resultado
        return REGISTRO_DOCUMENTOS[clave_documento](request)
    else:
        messages.error(request, f'No se encontró función para generar documento {clave_documento}')
        return redirect('egresado')  # O la vista que prefieras

