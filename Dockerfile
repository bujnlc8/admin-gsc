FROM yy194131/gsc-admin-base:0.0.2
WORKDIR /opt/snow
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && apk update
RUN pip install --upgrade pip setuptools wheel
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY snow/ snow/
COPY entry.sh entry.sh
RUN chmod 755 entry.sh
RUN mkdir /log
CMD [ "/opt/snow/entry.sh" ]
