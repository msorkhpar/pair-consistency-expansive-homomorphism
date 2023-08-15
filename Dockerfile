FROM gurobi/optimizer:10.0.2

RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED 1
RUN pip install pipenv

WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy --ignore-pipfile

COPY . /app/

CMD ["pipenv", "run", "start"]