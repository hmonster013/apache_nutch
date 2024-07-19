FROM openjdk:11-jdk

# Cài đặt các gói cần thiết và supervisor
RUN apt-get update && \
    apt-get install nano && \
    apt-get install -y supervisor ant && \
    mkdir -p /var/log/supervisor

# Tải và cài đặt Apache Nutch
WORKDIR /opt
RUN wget https://archive.apache.org/dist/nutch/1.19/apache-nutch-1.19-bin.tar.gz && \
    tar -xzf apache-nutch-1.19-bin.tar.gz && \
    mv apache-nutch-1.19 nutch && \
    rm apache-nutch-1.19-bin.tar.gz

# Thiết lập biến môi trường cho Nutch
ENV NUTCH_HOME /opt/nutch
ENV PATH $NUTCH_HOME/bin:$PATH

# Cấu hình supervisor để quản lý các tiến trình
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Thiết lập lệnh mặc định khi khởi động container
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
