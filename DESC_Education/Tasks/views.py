import logging
from rest_framework import generics, status
from Tasks.permissions import IsCompanyRole
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


from Tasks.serializers import (
    CategorySerializer,
    TaskSerializer
)




class TaskView(generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsCompanyRole]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)

            return Response({
                "data": {"task": serializer.data},
                "message": "Задача добавлена успешно"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        try:

            try:
                instance = Task.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return Response({"message": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer(data=request.data, instance=instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
