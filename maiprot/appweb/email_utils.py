from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def enviar_correo_html(subject, template_html, template_txt, context, recipient):
    """
    Envía correos HTML correctamente usando SendGrid.
    """
    # Renderizar contenido
    html_content = render_to_string(template_html, context)
    text_content = render_to_string(template_txt, context)

    # Crear el mensaje MULTIPART (texto + HTML)
    correo = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[recipient]
    )

    # Adjuntar versión HTML
    correo.attach_alternative(html_content, "text/html")

    # Enviar
    correo.send()
