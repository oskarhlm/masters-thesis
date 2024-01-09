ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

RUN echo ${OPENAI_API_KEY}

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 8000

CMD ["uvicorn", "server:app", "--port", "8000", "--host", "0.0.0.0"]