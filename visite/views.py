from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Destination, Reservation
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import io,os

@login_required(login_url='accounts:login')
def index(request):
    return render(request, 'index.html')

def destinations(request):
    destinations = Destination.objects.all()
    return render(request, 'destinations.html', {
        'destinations': destinations
    })

def booking(request):
    destinations = Destination.objects.filter(available=True)

    if request.method == "POST":
        destination = get_object_or_404(
            Destination,
            id=request.POST.get("destination")
        )

        reservation = Reservation.objects.create(
            destination=destination,
            nom_client=request.POST.get("nom_client"),
            email=request.POST.get("email"),
            telephone=request.POST.get("telephone"),
            nb_personnes=request.POST.get("nb_personnes"),
            total_price=request.POST.get("total_price"),
        )

        # Automatic email
        send_mail(
            subject="Booking Confirmation",
            message=(
                f"Hello {reservation.nom_client},\n\n"
                f"Your booking for {destination.nom} has been confirmed.\n"
                f"Number of people: {reservation.nb_personnes}\n"
                f"Total: {reservation.total_price} €\n\n"
                f"Thank you for your trust.\nKüresel Turizm ✈️"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.email],
            fail_silently=False,
        )

        return redirect("visite:confirmation", reservation.id)

    return render(
        request,
        "booking.html",
        {"destinations": destinations}
    )


def confirmation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    return render(
        request,
        "confirmation.html",
        {"reservation": reservation}
    )

def delete_booking(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        email_entered = request.POST.get('email_verif', '').strip()
        
        if email_entered.lower() != reservation.email.lower():
            messages.error(request, "❌ Incorrect email. Deletion cancelled.")
            return redirect('visite:confirmation', reservation_id=reservation.id)
        
        reservation.delete()
        messages.success(request, "✅ Reservation successfully deleted.")

        return redirect('visite:my_bookings') 
    
    return render(request, 'delete_booking.html', {'reservation': reservation})

def my_bookings(request):
    email = request.GET.get('email')  
    if email:
        bookings = Reservation.objects.filter(email=email).order_by('-created_at')
    else:
        bookings = []
    return render(request, 'my_bookings.html', {
        'bookings': bookings, 
        'searched_email': email
    })

def ticket_pdf(request, reservation_id):
    # Get the reservation
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Create buffer for PDF
    buffer = io.BytesIO()
    
    # Create PDF canvas
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- HEADER ---
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, height - 100, "🎫 BOOKING TICKET")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 120, f"Booking No: #{reservation.id}")
    
    # Separator line
    p.line(50, height - 140, width - 50, height - 140)
    
    # --- LOGO (optional) ---
    try:
        logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            p.drawImage(logo, width - 150, height - 120, width=100, height=50)
    except:
        pass
    
    # --- CUSTOMER INFORMATION ---
    y_position = height - 180
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "CUSTOMER INFORMATION")
    y_position -= 30
    
    p.setFont("Helvetica", 12)
    customer_info = [
        ("Name:", reservation.nom_client),
        ("Email:", reservation.email),
        ("Phone:", reservation.telephone),
        ("Booking Date:", reservation.created_at.strftime("%d/%m/%Y %H:%M")),
    ]
    
    for label, value in customer_info:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y_position, label)
        p.setFont("Helvetica", 11)
        p.drawString(150, y_position, str(value))
        y_position -= 25
    
    # --- TRAVEL DETAILS ---
    y_position -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "TRAVEL DETAILS")
    y_position -= 30
    
    travel_details = [
        ("Destination:", reservation.destination.nom),
        ("Duration:", reservation.destination.duration),
        ("Number of people:", str(reservation.nb_personnes)),
        ("Unit price:", f"{reservation.destination.final_price()} €"),
        ("Total price:", f"{reservation.total_price} €"),
    ]
    
    for label, value in travel_details:
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y_position, label)
        p.setFont("Helvetica", 11)
        p.drawString(150, y_position, str(value))
        y_position -= 25
    
    # --- BARCODE/QR CODE (simulated) ---
    y_position -= 40
    p.rect(50, y_position - 30, width - 100, 40, fill=0)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y_position - 10, f"CODE: RES{reservation.id:06d}")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y_position - 25, "Present this code at check-in")
    
    # --- TERMS AND CONDITIONS ---
    y_position -= 80
    p.setFont("Helvetica-Oblique", 9)
    conditions = [
        "This ticket is valid only for the booked date.",
        "Present an ID card with this ticket.",
        "Cancellation possible up to 48h before departure.",
        "Contact: contact@voyages.com | +33 1 23 45 67 89",
    ]
    
    for condition in conditions:
        p.drawString(50, y_position, condition)
        y_position -= 15
    
    # --- FOOTER ---
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, 50, "Thank you for choosing our services!")
    p.drawCentredString(width / 2, 40, f"Document generated on: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Finalize PDF
    p.showPage()
    p.save()
    
    # Retrieve buffer
    buffer.seek(0)
    
    # Return PDF response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_ticket_{reservation.id}.pdf"'
    return response