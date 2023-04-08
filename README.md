# Clinic_Appointment_App_API
Built with Django REST Framework

## Table of Contents
  - [Features](#features)
    - [Implemented](#implemented)
    - [Todo](#todo)
  - [Installation guide](#installation-guide)
    - [Dependacies Installation](#dependacies-installation)
  - [Testing and Running Guide](#testing-and-running-guide)
  - [API Documentation](#api-documentation)
  - [Key Python Modules Used](#key-python-modules-used)
  - [Reference Resources](#reference-resources)


## Features
### Implemented
0. Create User
  - Generate token (Login), Revoke token by User
  - Update, View User profile by User owner
  - Forgot, Reset User Password by User owner
  - Delete, View user by Admin
  
1. View User Activity Logs List by Admin
2. Export User Activity Logs as CSV/Excel by Admin
    - Create, List, Detail, Update and Delete of User Roles by Admin

3. Create, List, Detail, Update and Delete Doctor Speciality by Admin
4. Create and List Clinic by User. 
    - Detail, Update and Delete Clinic by Clinic Owner
5. Clinic Invite Doctor by Clinic Owner

6. Doctor Accept Invite by Invited Doctor
    - Doctor Reject Clinic Invite by Invited Doctor

7. Create, List and Detail Doctor
    - Update and Delete Doctor by Owner Doctor

8. Create, Update and Delete Doctor's Timeslot and Schedule by Owner Doctor
    - List and Detail view of Doctor's Timeslot and Schedule by any user

9. Create, Update and Delete Doctor's Education, Awards, Experience, Membership and Registration by Owner Doctor.
    - List and Detail view of Doctor's Education, Awards, Experience, Membership and Registration by any user

10. Create, List and Detail Patient
    - Update and Delete Patient by Owner Patient
11. Book, cancel and request reschedule Appointment with a doctor by Patient
    - Accept, cancel, request reschedule and follow-up appointment by Doctor 

11. Create, List, Detail, Update and Delete Patient's Medical Record by Doctor
    - View Medical Record by owner patient
12. Create, List, Detail, Update and Delete Patient's Presicription by DOCTOR
    - View Presicription by owner patient

13. Appointment Billing
14. Generate Invoices

15. Review Doctor by Patient
16. Doctor Reply to review
17. Users like reviews and reply

### Todo
- Document apis with Postman
- JWT Authentication
- Payment endpoints
- Create and Send appointment Notifications (Calery)
- Geo-locate clinic
- Doctor - Patient chat app


## Installation Guide

### Dependacies Installation

- Installing the application locally requires 
	1. [Python 3.7+](https://www.python.org/downloads/release/python-393/) - download and install it.
	2. [virtualenv](https://docs.python-guide.org/dev/virtualenvs/) - To create a virtual environment and activate it, run the following commands. 
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
- Install the project dependacies from requirements.txt by running the following command in shell: 
```bash
pip install -r requirements.txt 
```

## Testing and Running Guide
1. To activate the development server run:
```bash
python manage.py runserver
```
At this point, the development server should be accessible at _http://127.0.0.1:8000/_

2. Testing - To run all the tests:

```bash
python manage.py test
```


## API Documentation
- **OpenAPI Specification Docs:** [http://127.0.0.1:8000/?format=openapi-json](http://127.0.0.1:8000/?format=openapi-json)

## Key Python Modules Used
- **Django(3.2.18):** Django is a back-end server side web framework. Django is free, open source and written in Python. Django makes it easier to build web pages using Python.
- **Django Rest Framework:** Django Rest Framework (DRF) is a package built on the top of Django to create web APIs. DRF allows us to represent their functionality Django application in the form of REST APIs.
- **django-user-agents:**  A django package that allows easy identification of visitor’s browser, OS and device information, including whether the visitor uses a mobile phone, tablet or a touch capable device. 
- **django-cors-headers:** A Django App that adds Cross-Origin Resource Sharing (CORS) headers to responses. This allows in-browser requests to your Django application from other origins.
- **pilkit:** PILKit is a collection of utilities for working with PIL (the Python Imaging Library). One of its main features is a set of processors which expose a simple interface for performing manipulations on PIL images.
- **openpyxl:** The Openpyxl library is used to write or read the data in the excel file and many other tasks.
- **flake8** - static analysis tool

## Reference Resources
- [virtualenv](https://docs.python-guide.org/dev/virtualenvs/)
- [Django(3.2.18)](https://docs.djangoproject.com/en/3.2/intro/overview/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django User Agents](https://pypi.org/project/django-user-agents/)
- [Django CORS Headers](https://pypi.org/project/django-cors-headers/)
