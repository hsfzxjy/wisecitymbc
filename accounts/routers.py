from .views import UserAPIViewSet

routers = (
    (r'users', UserAPIViewSet),
)