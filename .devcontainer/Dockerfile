FROM cdt/disaster-recovery:web

# install Azure CLI
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt
USER root
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# install webp CLI
# https://developers.google.com/speed/webp/download
RUN apt install webp -y

USER $USER

COPY . .

# install devcontainer requirements
RUN pip install -e .[dev,test]
