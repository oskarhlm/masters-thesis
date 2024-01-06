ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 8001

CMD ["uvicorn", "server:app", "--port", "8001", "--host", "0.0.0.0"]