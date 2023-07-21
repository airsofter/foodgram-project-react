from rest_framework import permissions, exceptions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.serializers import SubscriptionSerializer
from users.models import User, Subscription


class CustomUserViewSet(UserViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()

    @action(
        methods=('get',),
        detail=False,
        serializer_class=SubscriptionSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(author_subscription__user=user)
        paginate_authors = self.paginate_queryset(authors)
        serializer = self.get_serializer(paginate_authors, many=True)
        return Response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=SubscriptionSerializer,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        follover = request.user
        subscription = follover.user_subscription.filter(
            author=author
        ).exists()

        if request.method == 'POST':
            if subscription:
                raise exceptions.ValidationError(
                    'Вы уже подписаны на этого автора'
                )
            print(author)
            Subscription.objects.create(user=follover, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscription:
            raise exceptions.ValidationError(
                'Вы не подписаны на этого автора'
            )
        get_object_or_404(
            Subscription,
            user=follover,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
