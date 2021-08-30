import requests
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.conf import settings
from rest_framework.decorators import throttle_classes
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework import status
from django.contrib import messages
from rest_framework.views import APIView


class HomeTemplateView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, *args)

    def post(self, request):
        query = request.POST.get("query", None)
        accepted = request.POST.get("accepted", None)
        body = request.POST.get("body", None)
        closed = request.POST.get("closed", None)
        migrated = request.POST.get("migrated", None)
        notice = request.POST.get("notice", None)
        nottagged = request.POST.get("nottagged", None)
        tagged = request.POST.get("tagged", None)
        title = request.POST.get("title", None)
        user = request.POST.get("user", None)
        url = request.POST.get("url", None)
        wiki = request.POST.get("wiki", None)
        previous_page_no = request.POST.get("previous_page_no", None)

        if previous_page_no is None or previous_page_no == "":
            previous_page_no = 1
        else:
            previous_page_no = int(previous_page_no) + 1

        # request data to fill fields on template
        request_data = {
            "query": query,
            "accepted": accepted,
            "body": body,
            "closed": closed,
            "migrated": migrated,
            "notice": notice,
            "nottagged": nottagged,
            "tagged": tagged,
            "title": title,
            "user": user,
            "url": url,
            "wiki": wiki,
            "previous_page_no": previous_page_no,
        }

        API_ENDPOINT = settings.INTERNAL_URL + "/get_search_results/"
        response = requests.post(url=API_ENDPOINT, data=request_data)
        response_json = response.json()

        if response.status_code == status.HTTP_200_OK:
            return_data = {
                "items": response_json.get("items"),
                "has_more": response_json.get("has_more"),
                "request_data": request_data,
            }
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return_data = {"items": "", "has_more": "", "request_data": request_data}
            messages.warning(request, "Use limit of api is exceeded.")
        else:
            return_data = {"items": "", "has_more": "", "request_data": request_data}
            messages.warning(request, response_json.get("msg"))

        return render(request, self.template_name, return_data)


class SearchView(APIView):
    throttle_classes = [UserRateThrottle]

    @method_decorator(cache_page(60))
    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(
        vary_on_headers(
            "Authorization",
        )
    )
    def post(self, request, format=None):
        query = request.POST.get("query", None)
        accepted = request.POST.get("accepted", None)
        body = request.POST.get("body", None)
        closed = request.POST.get("closed", None)
        migrated = request.POST.get("migrated", None)
        notice = request.POST.get("notice", None)
        nottagged = request.POST.get("nottagged", None)
        tagged = request.POST.get("tagged", None)
        title = request.POST.get("title", None)
        user = request.POST.get("user", None)
        url = request.POST.get("url", None)
        wiki = request.POST.get("wiki", None)
        previous_page_no = request.POST.get("previous_page_no")

        query_string = ""

        if query:
            query_string += f"&query={query}"

        if accepted:
            query_string += f"&accepted={accepted}"

        if body:
            query_string += f"&body={body}"

        if closed:
            query_string += f"&closed={closed}"

        if migrated:
            query_string += f"&migrated={migrated}"

        if notice:
            query_string += f"&notice={notice}"

        if nottagged:
            query_string += f"&nottagged={nottagged}"

        if tagged:
            query_string += f"&tagged={tagged}"

        if title:
            query_string += f"&title={title}"

        if user:
            query_string += f"&user={user}"

        if url:
            query_string += f"&url={url}"

        if wiki:
            query_string += f"&wiki={wiki}"

        if query_string:
            query_string += f"&page={previous_page_no}"
            api_url = settings.API_BASE_URL % query_string
            response = requests.get(api_url)
            response_json = response.json()

            if response.status_code == status.HTTP_200_OK:
                response_json = response.json()

                response_dict = {
                    "items": response_json.get("items"),
                    "has_more": response_json.get("has_more"),
                    "msg": "",
                }
                return Response(response_dict, status=status.HTTP_200_OK)
            elif response.status_code == status.HTTP_400_BAD_REQUEST:
                response_dict = {
                    "msg": "Bad request.",
                }
                return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
            elif response.status_code == status.HTTP_404_NOT_FOUND:
                response_dict = {
                    "msg": "Url Not Found.",
                }
                return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
            elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                response_dict = {
                    "msg": "Use limit of api exceeded.",
                }
                return Response(response_dict, status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                response_dict = {
                    "msg": "Internal Server Error",
                }
                return Response(
                    response_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            response_dict = {
                "msg": "Please add some parameters for search.",
            }
        return Response(response_dict, status=status.HTTP_412_PRECONDITION_FAILED)
