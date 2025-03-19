from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import MealPlan
from .serializers import MealPlanSerializer

@api_view(['GET'])
def get_meal_plans(request):
    """Retrieve all meal plans."""
    meal_plans = MealPlan.objects.all()
    serializer = MealPlanSerializer(meal_plans, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_meal_plan(request):
    """Create a new meal plan."""
    serializer = MealPlanSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)