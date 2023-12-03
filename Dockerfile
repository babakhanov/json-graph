FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install Flask numpy networkx
EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
CMD ["flask", "run"]
