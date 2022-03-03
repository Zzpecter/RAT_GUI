FROM python:latest

ADD rat.py /

RUN pip install pyqt5
RUN pip install opencv-python
RUN pip install numpy
RUN pip install pandas
RUN pip install shapely

CMD [ "python", "./rat.py" ]
