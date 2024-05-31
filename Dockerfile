FROM arakurumi/mltb:latest

WORKDIR /usr/src/app

RUN chmod 777 /usr/src/app

COPY . .

RUN pip install --break-system-packages --no-cache-dir --requirement requirements.txt

CMD ["bash", "start.sh"]