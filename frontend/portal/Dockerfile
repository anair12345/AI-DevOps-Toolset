FROM python:3.12-slim
WORKDIR /app
COPY src/ /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
CMD ["streamlit", "run", "app.py"]
