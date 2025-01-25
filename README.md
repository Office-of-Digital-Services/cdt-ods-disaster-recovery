# California Digital Disaster Recovery Center (DDRC)

This is open-source software that is developed and maintained by [Compiler LLC](https://compiler.la) in partnership with the [State of California Department of Technology](https://cdt.ca.gov).

## Development

This project is configured to use [VS Code devcontainers](https://code.visualstudio.com/docs/devcontainers/containers) to
provide a platform-agnostic, standardized development environment.

### Prerequisites

<details>

<summary>Expand for prerequisites</summary>

This section describes the tooling you need to have installed and configured on your development machine before continuing.

#### Git

Git is an open source version control system that we use in `pems` to track changes to the codebase over time. Many operating
systems come with Git already installed. Check if you have Git installed in a terminal with the following command:

```shell
git --version
```

If git is installed, the output should look similar to:

```console
$ git --version
git version 2.39.5
```

If Git is not installed, head to the [Git downloads page](https://git-scm.com/downloads) to get an installer for your operating
system.

#### Docker and Docker Compose

Docker and Docker Compose (or just Compose) are key tools that allow for running the various services required for `pems`.

Confirm if you already have Docker installed, in a terminal:

```shell
docker --version
```

If Docker is installed, the output should look similar to:

```console
$ docker --version
Docker version 27.4.0, build bde2b89
```

And similarly to check if Compose is installed:

```shell
docker compose version
```

When Compose is installed, output will look similar to:

```console
$ docker compose version
Docker Compose version v2.31.0
```

There are different ways to acquire this software depending on your operating system. The simplest approach for Windows and
MacOS users is to install [Docker Desktop](https://docs.docker.com/desktop/).

##### Windows

It is possible to run Docker and Compose on Windows without installing Docker Desktop. This involves using the [Windows Subsystem
for Linux v2 (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install#step-2-update-to-wsl-2), where Docker is configured
to run.

This article walks through this procedure in more detail:
[_How to run docker on Windows without Docker Desktop_](https://dev.to/_nicolas_louis_/how-to-run-docker-on-windows-without-docker-desktop-hik).

##### MacOS

With MacOS and [Homebrew](https://brew.sh/), installing Docker and Compose are as simple as:

```shell
brew install docker docker-compose colima
```

Once the install completes, start `colima` (an [open source container runtime](https://github.com/abiosoft/colima)):

```shell
brew services start colima
```

##### Linux

Docker CE (also known as Docker Engine) is how to run Docker and Compose on Linux. Docker provides an
[installation guide for Docker CE](https://docs.docker.com/engine/install/).

#### VS Code and Dev Containers extension

VS Code is an open source Integrated Development Environment (IDE) from Microsoft. Check if you already have it installed:

```shell
code -v
```

If installed, output should look similar to:

```console
$ code -v
1.95.3
f1a4fb101478ce6ec82fe9627c43efbf9e98c813
x64
```

Otherwise, [download VS Code](https://code.visualstudio.com/download) for your operating system.

Once installed, open VS Code and enter `Ctrl`/`Cmd` + `P` to open the VS Code Quick Open pane. Then enter:

```console
ext install ms-vscode-remote.remote-containers
```

`ms-vscode-remote.remote-containers` is the Extension ID of the
[Dev Containers extension from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

</details>

### Get the project code

Use Git to clone the repository to your local machine:

```shell
git clone https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery.git
```

Then change into the `cdt-ods-disaster-recovery` directory and create an environment file from the sample:

```shell
cd cdt-ods-disaster-recovery
cp .env.sample .env
```

Feel free to inspect the environment file, but leave the defaults for now.

### Open the project in a VS Code devcontainer

Still in your terminal, enter the following command to open the project in VS Code:

```shell
code .
```

Once the project is loaded in VS Code, you should see a notification pop-up asking to reopen the project in a devcontainer.

If you don't see this notification, or if it was dismissed, use the VS Code Quick Open pane with `Ctrl`/`Cmd` + `P` and enter:

```md
> Dev Containers: Rebuild and Reopen in Container
```

The VS Code window will reload into the devcontainer.

Once loaded, hit `F5` to start the application in debug mode. The application is now running on `http://localhost:8000`.
