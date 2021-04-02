
# stage 1
FROM python:3.9-alpine as builder

# install dependencies to /root/.local/
COPY script/requirements.txt .
RUN pip install --user -r requirements.txt

# stage 2
FROM python:3.9-alpine
WORKDIR /app

# copy dependencies from the stage 1 image
COPY --from=builder /root/.local /root/.local

# copy the python application
COPY script/r53-ddns.py .

# launch a shell and run the application w/arguments (shell required for variable expansion)
CMD [ "sh", "-c", "python r53-ddns.py --hosted-zone-id $HOSTED_ZONE_ID --name $DNS_NAME -v"]