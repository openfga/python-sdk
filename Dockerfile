FROM python:3.10
WORKDIR /app/tests
COPY . /app
RUN pip install -r test-requirements.txt
CMD ["sh", "-c", "pytest"]