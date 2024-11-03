# Start your image with a node base image
FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y python3.12 \
    && ln -s /usr/bin/python3.12 /usr/bin/python3 \
    && apt install python3-pip -y

COPY . .
# ENSURE python exists
RUN python3 -V
#RUN apt install -y python3.12-venv
#RUN python3 -m venv backendVenv
#RUN chmod 777 backendVenv/bin/activate
RUN rm /usr/lib/python3.12/EXTERNALLY-MANAGED
#RUN ./backendVenv/bin/activate && ls && 
RUN pip3 install -r requirements.txt

EXPOSE 6060

# Start the app using serve command
CMD ["python3", "manage.py", "runserver", "35.183.197.0:6060"]