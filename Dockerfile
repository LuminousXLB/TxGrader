FROM python:3.10-alpine

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

CMD flask --app TxGrader run --debug --host=0.0.0.0 --port=5000
