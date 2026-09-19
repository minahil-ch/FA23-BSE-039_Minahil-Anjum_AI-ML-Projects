from django.db.models import Q
from rest_framework import viewsets, permissions
from documents.models import Document
from documents.serializers import DocumentSerializer
from users.permissions import IsOwnerOrAdminOrManager
from activity_logs.models import ActivityLog

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be uploaded and managed.
    """
    serializer_class = DocumentSerializer
    filterset_fields = ['department', 'uploaded_by', 'is_public']
    search_fields = ['title']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        # Admins see everything
        if user.is_superuser or user.role == 'ADMIN':
            return Document.objects.all().order_by('-created_at')
        
        # Non-admins see public docs, docs from their department, or docs they uploaded
        q_filter = Q(is_public=True) | Q(uploaded_by=user)
        if user.department:
            q_filter |= Q(department=user.department)
            
        return Document.objects.filter(q_filter).distinct().order_by('-created_at')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        document = serializer.save(uploaded_by=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action="DOCUMENT_UPLOAD",
            details={"message": f"Uploaded document: {document.title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        # Queue background AI processing: extract text → chunk → embed
        from ai.tasks import process_document_task
        try:
            process_document_task.delay(document.id)
        except Exception:
            # If Redis/Celery unavailable, process synchronously for dev
            process_document_task(document.id)

    def perform_update(self, serializer):
        document = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="DOCUMENT_UPDATE",
            details={"message": f"Updated document metadata: {document.title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def perform_destroy(self, instance):
        title = instance.title
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="DOCUMENT_DELETE",
            details={"message": f"Deleted document: {title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
