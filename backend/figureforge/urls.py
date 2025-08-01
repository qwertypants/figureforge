"""
URL configuration for figureforge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'figureforge-api'})


def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'FigureForge API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'images': '/api/images/',
            'subscriptions': '/api/subscriptions/',
            'webhooks': '/api/webhooks/'
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check, name='health_check'),
    path('', api_root, name='api_root'),
]
