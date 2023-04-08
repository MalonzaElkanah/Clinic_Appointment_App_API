from django.urls import path, include

from rest_framework.routers import DefaultRouter
from clinic.doctor import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"education", views.EducationViewSet)
router.register(r"experience", views.ExperienceViewSet)
router.register(r"awards", views.AwardViewSet)
router.register(r"membership", views.MembershipViewSet)
router.register(r"registration", views.RegistrationViewSet)
router.register(r"schedule", views.DoctorScheduleViewSet)
router.register(r"timeslots", views.TimeSlotViewSet)
router.register(r"social-links", views.SocialMediaViewSet)
router.register(r"appointments", views.AppointmentViewSet)
router.register(r"reviews", views.ReviewViewSet)

router2 = DefaultRouter()
router2.register(r"replies", views.ReviewReplyViewSet)

app_name = "doctor"

urlpatterns = [
    path("", views.ListCreateDoctor.as_view(), name="doctor_list_create"),
    path(
        "<int:pk>/",
        views.RetrieveUpdateDestroyDoctor.as_view(),
        name="doctor_retrieve_update",
    ),
    path("<int:doctor_pk>/", include(router.urls)),
    path("<int:doctor_pk>/reviews/<int:review_pk>/", include(router2.urls)),
]
