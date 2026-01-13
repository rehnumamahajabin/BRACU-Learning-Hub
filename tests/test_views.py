# In your views.py
from django.contrib import messages

def material_upload(request):
    if request.method == 'POST':
        # ... save material
        messages.success(request, 'Material uploaded successfully!')
        return redirect('material_detail', pk=material.pk)