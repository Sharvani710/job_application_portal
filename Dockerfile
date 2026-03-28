FROM python:3.12.6

WORKDIR /app

COPY job_appication_portal/placement_portal/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY job_appication_portal/placement_portal/ .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
