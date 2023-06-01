FROM ubuntu:20.04

# Define non-root user.
ARG APP_USER=sembla
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user with sudo access.
RUN groupadd --gid $USER_GID $APP_USER \
 && useradd --uid $USER_UID --gid $USER_GID -m $APP_USER \
 && apt-get update \
 && apt-get install -y sudo python3 python3-pip curl \
 && echo $APP_USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$APP_USER \
 && chmod 0440 /etc/sudoers.d/$APP_USER \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Create usual aliases.
RUN ln -sf /usr/bin/python3 /usr/bin/python \
 && ln -sf /usr/bin/pip3 /usr/bin/pip

# Set the working directory inside the container
WORKDIR /app

# Change ownership of the working directory
RUN chown ${APP_USER}:${APP_USER} /app

# Switch to the user.
USER ${APP_USER}

# Install the project requirements.
COPY --chown=${APP_USER}:${APP_USER} requirements.txt .
RUN pip3 install -r requirements.txt

# Install the project.
COPY --chown=${APP_USER}:${APP_USER} . .
RUN pip3 install .

# Set default command.
ENTRYPOINT [ "/bin/bash" ]

# Set default arguments.
CMD [ "-c", "python -m sembla" ]
