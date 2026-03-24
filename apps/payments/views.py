from django.http import JsonResponse
def placeholder(request):
    return JsonResponse({'status': 'ok'})
