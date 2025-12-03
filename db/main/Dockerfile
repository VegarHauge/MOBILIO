FROM mysql:8.0

# Set environment variables for database initialization
ENV MYSQL_ROOT_PASSWORD=rootpass
ENV MYSQL_DATABASE=DAT515
ENV MYSQL_USER=dat515user
ENV MYSQL_PASSWORD=admin123

# Copy init script to initialize database on first run
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

# Use native password authentication
CMD ["--default-authentication-plugin=mysql_native_password"]

# Expose MySQL port
EXPOSE 3306

# Data is stored in /var/lib/mysql (mount as volume for persistence)
VOLUME ["/var/lib/mysql"]
