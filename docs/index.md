# California Digital Disaster Recovery Center (DDRC)

This website provides technical documentation for the [DDRC][ddrc-repo] application from the
[California Department of Technology (CDT)][cdt].

[DDRC](https://recovery.cdt.ca.gov/vital-records/) is a web application that enables [free vital records replacement](https://www.ca.gov/lafires/help-for-you/replace-personal-documents/birth-death-marriage-certificates/) for survivors of the 2025 Los Angeles County fires and other recent natural disasters in California.
It is open-source software that is designed, developed, and maintained by <a href="https://compiler.la/" target="_blank">Compiler LLC</a> on behalf of [CDT][cdt].

## Supported vital records requests

The DDRC app supports the following vital records requests:

| Vital Record Type    | Status      | Launch                                                                                                    |
| -------------------- | ----------- | --------------------------------------------------------------------------------------------------------- |
| Birth Certificate    | Live        | [08/2025](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/releases/tag/2025.08.1) |
| Marriage Certificate | Live        | [09/2025](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/releases/tag/2025.09.1) |
| Death Certificate    | Live        | [10/2025](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/releases/tag/2025.10.1) |

## Technical and security details

DDRC is a [Django 5][django] web application. The application uses [Login.gov’s Identity Assurance Level 2 (IAL2)](https://developers.login.gov/attributes/) via the [California Identity Gateway](https://cdt.ca.gov/digitalid/) to verify a person has an address in a disaster-affected zip code.

Running the application locally is possible with [Docker and Docker Compose][docker].

The application communicates with the California Identity Gateway via redirects, over the public internet. See [all the system interconnections][interconnections].

### Infrastructure

The DDRC application is deployed to Microsoft Azure. Traffic is encrypted between the user and the application, as well as between the application and external systems.

The network is managed by [CDT](https://cdt.ca.gov/), who provide a firewall and [distributed denial-of-service (DDoS)](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/) protection.

You can find more technical details on [our infrastructure page](reference/infrastructure/).

### Data storage

The DDRC application minimizes the information exchanged between systems. The following information is temporarily stored in a secure database:

- The user's attestation and information required to submit a vital records request

Sensitive user information exists in the following places:

- To qualify for free vital records replacement, users need to [provide personal information to Login.gov](https://login.gov/create-an-account/)
- Users need to provide their attestation and vital record information to submit a vital records request

Learn more about the security/privacy practices of our integration partners:

- [Login.gov](https://www.login.gov/policy/)
- [CDT privacy policy](https://cdt.ca.gov/privacy-policy/)

DDRC collects analytics on usage, without any identifying information. You can find more details on [our analytics page](reference/analytics/).

### Practices

[Dependabot](https://github.com/features/security/software-supply-chain) immediately notifies the team of vulnerabilities in application dependencies.

Upon doing new major integrations, features, or architectural changes, the DDRC team has a penetration test performed by a third party to ensure the security of the system.

All code changes are reviewed by at least one other member of the engineering team, which is enforced through [branch protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches).

[ddrc-repo]: https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery
[cdt]: https://cdt.ca.gov/
[django]: https://docs.djangoproject.com/en/
[docker]: https://www.docker.com
[interconnections]: reference/infrastructure/#system-interconnections
