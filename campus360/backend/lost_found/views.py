from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from campus360_api.supabase_client import upload_to_supabase
from .models import LostFoundItem, Claim
from .serializers import LostFoundItemSerializer, ClaimSerializer


class LostFoundItemListView(generics.ListCreateAPIView):
    serializer_class = LostFoundItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = LostFoundItem.objects.all()
        item_type = self.request.query_params.get('type')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        department = self.request.query_params.get('department')
        date_filter = self.request.query_params.get('date')

        if item_type:
            qs = qs.filter(item_type=item_type.upper())
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        if search:
            qs = qs.filter(item_name__icontains=search) | qs.filter(description__icontains=search) | qs.filter(location__icontains=search)
        if department:
            qs = qs.filter(department__icontains=department)
        if date_filter:
            qs = qs.filter(item_date=date_filter)
        return qs.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Override create to handle frontend field name mapping and auto-assign reporter."""
        data = request.data.copy()

        # Frontend sends 'date' but model field is 'item_date'
        if 'date' in data and 'item_date' not in data:
            data['item_date'] = data['date']

        # Add default status if not provided
        if 'status' not in data:
            data['status'] = 'OPEN'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Assign reporter from authenticated user's profile
        try:
            reporter_profile = request.user.profile
        except AttributeError:
            # Fallback for when profile isn't easily accessible from user object
            from accounts.models import Profile
            reporter_profile = Profile.objects.get(id=request.user.id)
            
        instance = serializer.save(reporter=reporter_profile)

        # Handle image upload if file provided
        if 'image' in request.FILES:
            file = request.FILES['image']
            file_path = f"lost-found/{instance.id}/{file.name}"
            try:
                public_url = upload_to_supabase('lost-found-images', file_path, file.read(), file.content_type)
                instance.image_url = public_url
                instance.save()
            except Exception:
                pass  # Image upload failed, continue without image

        headers = self.get_success_headers(serializer.data)
        return Response(LostFoundItemSerializer(instance).data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_item_image(request, item_id):
    """Upload an item image to Supabase Storage."""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    file_path = f"lost-found/{item_id}/{file.name}"

    try:
        public_url = upload_to_supabase('lost-found-images', file_path, file.read(), file.content_type)
        LostFoundItem.objects.filter(id=item_id).update(image_url=public_url)
        return Response({'image_url': public_url})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClaimListView(generics.ListCreateAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Claim.objects.select_related('item').all()
        item_id = self.request.query_params.get('item_id')
        claimant_id = self.request.query_params.get('claimant_id')
        if item_id:
            qs = qs.filter(item_id=item_id)
        if claimant_id:
            qs = qs.filter(claimant_id=claimant_id)
        return qs


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_claim(request):
    """Submit a claim for a found item."""
    serializer = ClaimSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    item = serializer.validated_data['item']
    if item.item_type != 'FOUND':
        return Response({'error': 'Claims can only be made for FOUND items'}, status=status.HTTP_400_BAD_REQUEST)

    claim = serializer.save(status='PENDING')
    return Response(ClaimSerializer(claim).data, status=status.HTTP_201_CREATED)
