from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404

from .models import Brand, Campaign, SPEND_STATUS
from .serializers import BrandSerializer, CampaignSerializer, SpendSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

class SpendAPIViewSet(APIView):
    def post(self, request, campaign_id):
        serializer = SpendSerializer(data=request.data)
        if serializer.is_valid():
            campaign = get_object_or_404(Campaign, id=campaign_id)
            amount = serializer.validated_data.get("amount")
            spend_status  = campaign.spend(amount)
            return self.post_response(spend_status)
        else:
            return Response(
                {"message": "Invalid response body.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def post_response(self, spend_status):
        if spend_status == SPEND_STATUS.COMPLETED:
            return Response(
                {"message": "Amount spent successfully."},
                status=status.HTTP_200_OK
            )
        elif spend_status == SPEND_STATUS.DAILY_BUDGET_SPENT:
            return Response(
                {"message": "Daily budget spend."},
                status=status.HTTP_202_ACCEPTED
            )
        elif spend_status == SPEND_STATUS.MONTHLY_BUDGET_SPENT:
            return Response(
                {"message": "Monthly budget spent."},
                status=status.HTTP_202_ACCEPTED
            )
        else:
            return Response(
                {"message": "Out of dayparting range."},
                status=status.HTTP_202_ACCEPTED
            )
