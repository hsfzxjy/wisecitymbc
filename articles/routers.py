from .views import StatusAPIViewSet, CommentAPIViewSet

routers = (
    (r'^statuses/(?P<status_id>\d+)/comments', CommentAPIViewSet),
    (r'^statuses', StatusAPIViewSet),
)