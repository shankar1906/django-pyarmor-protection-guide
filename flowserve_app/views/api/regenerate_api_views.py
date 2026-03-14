from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from flowserve_app.decorators import login_required
from flowserve_app.services.regenerate_service import RegenerateService
from flowserve_app.views.pages.pdf_page_views import _build_pdf_context
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML as WeasyprintHTML
import os

@login_required
@require_http_methods(["GET"])
def get_serial_numbers(request):
    """API endpoint to get all serial numbers"""
    try:
        serial_numbers = RegenerateService.get_serial_numbers()
        return JsonResponse({
            'status': 'success',
            'data': serial_numbers
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_reports(request):
    """API endpoint to get reports for a serial number"""
    try:
        serial_number = request.GET.get('serial_number')
        
        if not serial_number:
            return JsonResponse({
                'status': 'error',
                'message': 'Serial number is required'
            }, status=400)
        
        reports = RegenerateService.get_reports_by_serial(serial_number)
        return JsonResponse({
            'status': 'success',
            'data': reports
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def download_pdf(request):
    """API endpoint to download PDF for a specific report using existing pdf.html template"""
    try:
        serial_number = request.GET.get('serial_number')
        count_id = request.GET.get('id')
        
        if not serial_number:
            return JsonResponse({
                'status': 'error',
                'message': 'Serial number is required'
            }, status=400)
        
        # Use the existing _build_pdf_context function to get report data
        tests_data, common_data = _build_pdf_context(serial_number)
        
        if not tests_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No report data found for this serial number'
            }, status=404)
        
        # Build context for pdf.html template
        context = {
            'download': False,
            'tests': tests_data,
            **common_data,
        }
        
        # Render the pdf.html template to HTML string
        html_string = render_to_string('pdf.html', context, request=request)
        
        # Build folder structure: F:/reports/
        reports_dir = os.path.join('D:', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Build filename: Report_{valve_serial}_{count}.pdf
        filename = f"Report_{serial_number}_{count_id}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Generate PDF from HTML string
        WeasyprintHTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(filepath)
        
        # Return success response with file path
        if os.path.exists(filepath):
            return JsonResponse({
                'status': 'success',
                'message': 'PDF saved successfully',
                'filepath': filepath,
                'filename': filename
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'PDF generation failed'
            }, status=500)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating PDF: {str(e)}'
        }, status=500)

