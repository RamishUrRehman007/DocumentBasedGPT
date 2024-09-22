# Dockerfile for the frontend
FROM nginx:alpine

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy your frontend files to the Nginx HTML directory
COPY . /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80
