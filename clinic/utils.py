from clinic.models import DoctorSchedule, Appointment

import datetime as dt


def validate_appointment_date(doctor, date_time):
    """
    A function to check if appointment date
    is inline with doctor schedule dates and
    the timeslot is not fully booked
    """

    schedules = DoctorSchedule.objects.filter(doctor=doctor)

    for schdl in schedules:
        if str(schdl.day).title() == str(f"{date_time:%A}").title():

            for time_slot in schdl.time_slot.all():
                start_hour = int(time_slot.start_time.hour)
                end_hour = int(time_slot.end_time.hour)

                if (
                    int(date_time.hour) >= start_hour
                    and int(date_time.hour) <= end_hour
                ):
                    if date_time.minute <= time_slot.end_time.minute:
                        start_date = dt.datetime(
                            year=date_time.year,
                            month=date_time.month,
                            day=date_time.day,
                            hour=time_slot.start_time.hour,
                            minute=time_slot.start_time.minute,
                        )
                        end_date = dt.datetime(
                            year=date_time.year,
                            month=date_time.month,
                            day=date_time.day,
                            hour=time_slot.end_time.hour,
                            minute=time_slot.end_time.minute,
                        )
                        appointments = (
                            Appointment.objects.filter(doctor=doctor)
                            .exclude(date_of_appointment__lt=start_date)
                            .exclude(date_of_appointment__gt=end_date)
                        )
                        if appointments.count() >= time_slot.number_of_appointments:
                            return {
                                "validated": False,
                                "message": "Timeslot is Fully Booked.",
                            }
                        else:
                            return {"validated": True, "message": None}

    if schedules.count() == 0:
        return {"validated": False, "message": "Doctor has not created a schedule."}

    return {
        "validated": False,
        "message": "Invalid Date: Check the Doctor Appointment Schedule before booking.",
    }
