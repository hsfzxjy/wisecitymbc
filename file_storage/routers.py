from .views import FileAPIViewSet

routers = (
    (r'^storage/files', FileAPIViewSet),
)