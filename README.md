# turku-api

## About Turku
Turku is an agent-based backup system where the server doing the backups has no direct access to the machine being backed up.  Instead, the machine's agent coordinates with an API server and opens a reverse tunnel to the storage server when it is time to do a backup.

Turku is comprised of the following components:

* [turku-api](https://github.com/rfinnie/turku-api), a Django web application which acts as an API server and coordinator.
* [turku-storage](https://github.com/rfinnie/turku-storage), an agent installed on the servers which do the actual backups.
* [turku-agent](https://github.com/rfinnie/turku-agent), an agent installed on the machines to be backed up.

turku-api has the following models:

* Auth, registration secrets for Machines and Storages.
* Storage, registered agents for servers running turku-storage.
* Machine, registered agents for machines running turku-agent.
* Source, sources of data to be backed up on a Machine.
* FilterSet, rsync filter definitions of what to include and exclude (optional).
* BackupLog, records of Machine/Source backup runs.

## Installation

turku-api is a standard Django application; please see [Django's installation guide](https://docs.djangoproject.com/en/1.11/topics/install/) for setting up an application.  Django 1.6 (Ubuntu Trusty era) through Django 2.2 (Ubuntu Focal era) have been tested.

turku-api requires Python 3.  The following optional Python modules can also be installed:

* croniter, for cron-style scheduling definitions

It is highly recommended to serve turku-api over HTTPS, as registration and agent-specific secrets are passed from turku-storage and turku-agent agents to turku-api.  However, actual backups are done over SSH, not this application.

turku-api's default configuration will use a SQLite database.  This is fine for small installations, but it's recommended to use a PostgreSQL/MySQL database for larger installations.

Besides database configuration, turku-api's default Django settings are adequate.  The only recommended change is an installation-specific Django SECRET_KEY.  Create ```turku_api/local_settings.py``` with:

```
SECRET_KEY = 'long random key string'
```

Any other changes to ```turku_api/settings.py``` should be put in ```turku_api/local_settings.py``` as well.

Getting the admin web site working is recommended, but not required.

## Configuration

Once the installation is complete, you will need to add at least one Storage registration Auth, and at least one Machine registration Auth:

```
$ python manage.py turku_auth_create --name "Storage Registrations" storage_reg
New registration secret created: fDLICqVwO5wouqTAPKzI7WN7C1Zd0L (Storage Registrations)
$ python manage.py turku_auth_create --name "Machine Registrations" machine_reg
New registration secret created: IvBXnYmTTzzPlj2NP2xFY5yj5JLRkp (Machine Registrations)
```

Multiple of each type of Auth can be created.  For example, you may have multiple groups within an organization; creating a separate Machine registration Auth for each group may be desired.  turku-api tracks which Auth is used to register a Machine, but the Auth is not used for authentication beyond registration; a Machine-specific generated secret is used for check-ins.

## Deployments

Once you have the Storage and Machine registration secrets, move on to installing turku-storage and turku-agent agents and registering them with turku-api.  See the README.md files in their respective repositories for more details.

For small deployments, turku-api, turku-storage, and a turku-agent agent may all be on the same server.  For example, the server may have a main turku-api coordinator, a turku-storage agent configured to store backups on a removable USB drive, and a turku-agent agent configured to back up the turku-api SQLite database.

For larger deployments, Turku supports scale-out.  Load-balancing HTTPS frontends may point to multiple turku-api application servers, which themselves may use primary/secondary PostgreSQL databases.  Multiple turku-storage servers may register with turku-api, as storage needs increase.  All turku-agent machines will need access to the turku-api application servers (or their frontends) via HTTPS, and to their assigned turku-storage server over SSH.  No ingress access is needed to turku-agent machines.

## License

Turku backups - API server

Copyright (C) 2015-2020 Canonical Ltd., Ryan Finnie and other contributors

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
