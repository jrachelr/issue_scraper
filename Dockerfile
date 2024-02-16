FROM python:3.10-bullseye
RUN python -m pip install --upgrade pip
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD app.py /
CMD [ "python", "./app.py" ]
