# Dockerfile for custom Open-WebUI with EasyVista tool
FROM ghcr.io/open-webui/open-webui:main

# Switch to root user to install dependencies and set permissions
USER root

# Copy the entire tool directory into the container's tools folder
# This ensures both the tool and its requirements.txt are available
COPY ./openwebui_tool /app/backend/tools/easyvista_tool

# Install the tool's Python dependencies
# Open-WebUI's base image has pip available.
RUN pip install --no-cache-dir -r /app/backend/tools/easyvista_tool/requirements.txt

# It's good practice to change ownership of the copied files to the container's user
# The default user for Open-WebUI is 'abc' with UID/GID 1000
RUN chown -R 1000:1000 /app/backend/tools/easyvista_tool

# Switch back to the non-root user to run the application
USER 1000
