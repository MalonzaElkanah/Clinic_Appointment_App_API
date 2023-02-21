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
1. User Activity Logs List (**ADMIN**)
2. User Activity Logs Export (**ADMIN**)
3. Create, List, Detail, Update and Delete Doctor Speciality (**ADMIN**)
4. Create, List, Detail, Update and Delete Clinic
5. Clinic Invite Doctor
6. Doctor Accept Invite
    - Doctor Reject Clinic Invite
7. Create, List, Detail, Update and Delete Doctor 
8. Create, List, Detail, Update and Delete Doctor's Timeslot and Schedule 
9. Create, List, Detail, Update and Delete Doctor's 
    - Education, 
    - Awards,
    - Experience,
    - Membership and
    - Registration
10. Create, List, Detail, Update and Delete Patient
11. Book Appointment by Patient
11. Create, List, Detail, Update and Delete Patient's Medical Record
12. Create, List, Detail, Update and Delete Patient's Presicription by DOCTOR
13. Billing
14. Invoices
15. Review Doctor by Patient
16. 

### Todo
- 


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
To activate the development server run:
```bash
python manage.py runserver
```
At this point, the development server should be accessible at _http://127.0.0.1:8000/_


## API Documentation
- **OpenAPI Specification Docs:** [http://127.0.0.1:8000/?format=openapi-json](http://127.0.0.1:8000/?format=openapi-json)

## Key Python Modules Used
- **Django(3.2.18):** Django is a back-end server side web framework. Django is free, open source and written in Python. Django makes it easier to build web pages using Python.
- **Django Rest Framework:** Django Rest Framework (DRF) is a package built on the top of Django to create web APIs. DRF allows us to represent their functionality Django application in the form of REST APIs.
- **django-user-agents:**  A django package that allows easy identification of visitor’s browser, OS and device information, including whether the visitor uses a mobile phone, tablet or a touch capable device. 
- **django-cors-headers:** A Django App that adds Cross-Origin Resource Sharing (CORS) headers to responses. This allows in-browser requests to your Django application from other origins.
- **pilkit:** PILKit is a collection of utilities for working with PIL (the Python Imaging Library). One of its main features is a set of processors which expose a simple interface for performing manipulations on PIL images.
- **openpyxl:** The Openpyxl library is used to write or read the data in the excel file and many other tasks.

## Reference Resources
- [virtualenv](https://docs.python-guide.org/dev/virtualenvs/)
- [Django(3.2.18)](https://docs.djangoproject.com/en/3.2/intro/overview/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django User Agents](https://pypi.org/project/django-user-agents/)
- [Django CORS Headers](https://pypi.org/project/django-cors-headers/)
