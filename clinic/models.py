from django.db import models
from django.utils import timezone

from client.models import MyUser
from administrator.models import Speciality

import datetime as dt
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFit

from mylib.image import scramble


class Patient(models.Model):
    BLOOD_GROUP = (
        ("A-", "A-"),
        ("A+", "A+"),
        ("B-", "B-"),
        ("B+", "B+"),
        ("AB-", "AB-"),
        ("AB+", "AB+"),
        ("O-", "O-"),
        ("O+", "O+"),
        ("NS", "Not Set"),
    )
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    blood_group = models.CharField(
        "Blood Group", max_length=5, default="NS", choices=BLOOD_GROUP
    )

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name).title()

    class Meta:
        ordering = ("id",)


class Doctor(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    title = models.CharField("Title", max_length=200, default="Dr.")
    biography = models.CharField("Biography", max_length=1000, blank=True)
    pricing = models.FloatField("Amount", default=0.00)
    services = models.CharField("Services", max_length=1000, blank=True)
    specialization = models.CharField("Specialization", max_length=1000, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)
    clinic_invites = models.ManyToManyField("Clinic")

    def __str__(self):
        return "{} {} {}".format(
            self.title, self.user.first_name, self.user.last_name
        ).title()

    class Meta:
        ordering = ("id",)


class Clinic(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    doctors = models.ManyToManyField(Doctor)
    name = models.CharField("Name", max_length=100)
    phone = models.CharField(max_length=50)
    image = models.ImageField("uploads", upload_to=scramble, null=True, blank=True)
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFit(height=400)],
        format="JPEG",
        options={"quality": 80},
    )
    email = models.EmailField(unique=True)
    country = models.CharField("Country", max_length=100, null=True, blank=True)
    county = models.CharField("County", max_length=100, null=True, blank=True)
    town = models.CharField("Town", max_length=100, null=True, blank=True)
    street = models.CharField("Street", max_length=200, null=True, blank=True)
    address = models.CharField("Address", max_length=200, null=True, blank=True)
    description = models.CharField("Description", max_length=1000, blank=True)

    class Meta:
        ordering = ("id",)


class Education(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    degree = models.CharField("Degree", max_length=50)
    institute = models.CharField("College/Institute", max_length=50)
    date_of_completion = models.DateField("Date of Completion")

    def __str__(self):
        return "{}, {}".format(self.degree, self.institute).title()

    class Meta:
        ordering = ("id",)


class Experience(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    hospital_name = models.CharField("Hospital/Clinic", max_length=50)
    start_date = models.DateField("From")
    end_date = models.DateField("To", blank=True)
    designation = models.CharField("Designation", max_length=50)

    def __str__(self):
        return "{}, {}".format(self.designation, self.hospital_name).title()

    class Meta:
        ordering = ("id",)


class Award(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    award = models.CharField("Award", max_length=50)
    date = models.DateField("Date")

    def __str__(self):
        return "{}, {}".format(self.award, self.date).title()

    class Meta:
        ordering = ("id",)


class Membership(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    membership = models.CharField("Membership", max_length=50)

    def __str__(self):
        return "{}".format(self.membership).title()

    class Meta:
        ordering = ("id",)


class Registration(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField("Date")
    registration = models.CharField("Registration", max_length=50)

    def __str__(self):
        return "{} {}".format(self.registration, self.date).title()

    class Meta:
        ordering = ("id",)


class DoctorSchedule(models.Model):
    DAY = (
        ("Sunday", "Sunday"),
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Holiday", "Holiday"),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.CharField("Day", max_length=10, choices=DAY)
    time_slot = models.ManyToManyField("TimeSlot")

    def __str__(self):
        return "{}".format(self.day).title()

    class Meta:
        ordering = ("id",)


class TimeSlot(models.Model):
    start_time = models.TimeField("Start Time")
    end_time = models.TimeField("End Time")
    number_of_appointments = models.IntegerField("Number Of Appointments", default=1)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.start_time, self.end_time).title()

    class Meta:
        ordering = ("id",)


class SocialMedia(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=30)
    url = models.URLField("URL", max_length=200)

    def __str__(self):
        return "{}".format(self.name).title()

    class Meta:
        ordering = ("id",)


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField("Prescription Date", auto_now_add=True)
    name = models.CharField("Name", max_length=50)
    quantity = models.FloatField("Quantity", default=0.0)
    days = models.FloatField("Prescription Days", default=0.00)
    morning = models.BooleanField("Morning", default=False)
    afternoon = models.BooleanField("Afternoon", default=False)
    evening = models.BooleanField("Evening", default=False)
    night = models.BooleanField("Night", default=False)

    def __str__(self):
        return "{}".format(self.name)

    @property
    def valid(self):
        duration = dt.timedelta(days=self.days)
        end_date = self.date + duration
        now = timezone.now()
        if now < end_date:
            return True
        else:
            return False

    @property
    def end_date(self):
        duration = dt.timedelta(days=self.days)
        end_date = self.date + duration
        return end_date

    class Meta:
        ordering = ("id",)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_recorded = models.DateField("Record Date")
    description = models.CharField("Description", max_length=500, blank=True)
    attachment = models.FileField(
        "Attachment", upload_to="File/Patient/MedicalRecords/", blank=True
    )
    date_added = models.DateTimeField("Added Date", auto_now_add=True)

    def __str__(self):
        return "{}".format(self.description)

    class Meta:
        ordering = ("id",)


class FavouriteDoctor(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    fav_date = models.DateTimeField("Date Added", auto_now_add=True)

    class Meta:
        ordering = ("id",)


class Appointment(models.Model):
    STATUS = (
        ("WAITING", "Waiting"),
        ("CONFIRMED", "Confirmed"),
        ("RESCHEDULED", "Rescheduled"),
        ("CANCELED", "Canceled"),
        ("PAID", "Paid"),
        ("COMPLETED", "Completed"),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    purpose = models.CharField("Purpose", max_length=50)
    amount = models.FloatField("Amount", default=0.00, editable=False)
    status = models.CharField("Status", max_length=20, choices=STATUS)
    date_created = models.DateTimeField("Appointment Date", auto_now_add=True)
    date_of_appointment = models.DateTimeField("Date Of Appointment")
    follow_up_appointment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return self.purpose

    @property
    def is_patient_new(self):
        appointments = Appointment.objects.filter(
            doctor=self.doctor.id, patient=self.patient.id
        )
        return appointments.count() <= 1

    class Meta:
        ordering = ("id",)


class Bill(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=50)
    quantity = models.FloatField("Quantity", default=1.0)
    vat = models.FloatField("V.A.T", default=0.0)
    amount = models.FloatField("Amount", default=0.00)
    paid = models.BooleanField("Paid", default=False)

    class Meta:
        ordering = ("id",)


class Invoice(models.Model):
    bills = models.ManyToManyField(Bill)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    # total_amount = models.FloatField('Total Amount', default=0.00)
    invoice_date = models.DateTimeField("Paid On", auto_now_add=True)

    @property
    def total_amount(self):
        bills = self.bills
        total_amount = 0.0
        for bill in bills:
            total_amount += bill.amount
        return total_amount

    @property
    def unpaid_balance(self):
        bills = self.bills
        total_amount = 0.0
        for bill in bills:
            if not bill.paid:
                total_amount += bill.amount
        return total_amount

    @property
    def amount_paid(self):
        bills = self.bills
        total_amount = 0.0
        for bill in bills:
            if bill.paid:
                total_amount += bill.amount
        return total_amount

    class Meta:
        ordering = ("id",)


class AppoinmentReview(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True)
    date = models.DateTimeField("Review Date", auto_now_add=True)
    rate = models.IntegerField("Rate")
    recommend = models.BooleanField("Recommend", default=False)
    text = models.CharField("Review Title", max_length=150, blank=True)

    def total_reviews(self):
        query = AppoinmentReview.objects.filter(doctor=self.appointment.doctor.id)
        return len(query)

    class Meta:
        ordering = ("id",)


class Reply(models.Model):
    review = models.ForeignKey(AppoinmentReview, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    date = models.DateTimeField("Review Date", auto_now_add=True)
    text = models.CharField("Review Title", max_length=150)

    class Meta:
        ordering = ("id",)


class LikedReview(models.Model):
    review = models.ForeignKey(AppoinmentReview, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    recommend = models.BooleanField("Recommend", default=False)

    class Meta:
        ordering = ("id",)


class LikedReply(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    recommend = models.BooleanField("Recommend", default=False)

    class Meta:
        ordering = ("id",)
