import json
import logging

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .populate import initiate
from .models import CarMake, CarModel
from .restapis import (
    get_request,
    analyze_review_sentiments,
    post_review,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated",
        }
    return JsonResponse(response_data)


def logout_request(request):
    # Terminate user session
    logout(request)
    # Return empty username
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    # Read JSON from body
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is new user", username)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        response_data = {
            "userName": username,
            "status": "Authenticated",
        }
        return JsonResponse(response_data)

    response_data = {
        "userName": username,
        "error": "Already Registered",
    }
    return JsonResponse(response_data)


def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append(
            {
                "CarModel": car_model.name,
                "CarMake": car_model.car_make.name,
            }
        )
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state

    dealerships = get_request(endpoint)
    return JsonResponse(
        {
            "status": 200,
            "dealers": dealerships,
        }
    )


def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            sentiment_response = analyze_review_sentiments(
                review_detail["review"]
            )
            print(sentiment_response)
            if sentiment_response:
                review_detail["sentiment"] = sentiment_response["sentiment"]

        return JsonResponse(
            {
                "status": 200,
                "reviews": reviews,
            }
        )

    return JsonResponse(
        {
            "status": 400,
            "message": "Bad Request",
        }
    )


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse(
            {
                "status": 200,
                "dealer": dealership,
            }
        )

    return JsonResponse(
        {
            "status": 400,
            "message": "Bad Request",
        }
    )


def add_review(request):
    # Avoid `== False` (E712)
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            # We call post_review but don't assign it,
            # so we don't trigger F841.
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse(
                {
                    "status": 401,
                    "message": "Error in posting review",
                }
            )

    return JsonResponse(
        {
            "status": 403,
            "message": "Unauthorized",
        }
    )
