from django.utils.deprecation import MiddlewareMixin
from apps.accounts.models import UserActivity

class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not request.path.startswith('/admin/'):
            UserActivity.objects.create(
                user=request.user,
                activity_type='page_visit',
                details={
                    'path': request.path,
                    'method': request.method
                }
            )