# Lax

An effort to provide a flexible, mostly-structured, data store for articles.

A publisher has one or many journals, each journal has many articles.

Each article is uniquely identified by it's DOI. The DOI doesn't have to be 
registered with Crossref.

Each article consists of a set of [known attributes](https://github.com/elifesciences/lax/blob/develop/src/publisher/models.py#L24) that are stored together in the database.

Each article also has zero or many attributes in a simple `key=val` table that 
supplements the normalised article data. This allows for collection of ad-hoc 
article data. These attributes and their values may be migrated into the 
`article` database table at a later point.

Both the `Article` and `ArticleAttribute` models keep a record of data that is
changed. If an article is updated, it's previous version is kept and can be 
queried if you want insight into it's history.

## The 'Publisher' app

The core application on which other apps may be dependant.

It models the basic relationships between entities and captures events occurring
against Articles.

## Installation

    $ git clone https://github.com/elifesciences/lax
    $ cd lax
    $ ./install.sh

## Updating

    $ ./install.sh

## Testing

    $ ./test.sh

## Running

    $ ./runserver.sh
    $ firefox http://127.0.0.1:8000/admin

## Running with Docker

With Docker running, do:

    $ ./build-docker.sh

to build the container tagged "elifesciences/lax-develop" and once built, use:

    $ ./run-docker.sh
    
to start the Django webserver accessible via port 8001.

The admin username and password for this instance are "admin" and "admin. 


# deprecated

## Loading Article JSON

    $ ./load-json.sh /path/to/json/dir/
    
or, via http:
    
    $ curl -vX POST http://127.0.0.1:8000/import-article/ \
      --data @article.json \
      --header "Content-Type: application/json"

## Adding Article Attributes

    $ curl -vX POST http://127.0.0.1:8000/add-attribute-to-article/<doi>/<version>/ \
      --data {"key": "Date Published", "val": "1997-08-29 06:14:00+UTC"} \
      --header "Content-Type: application/json"

## Testing

    $ ./test.sh
   
## Copyright & Licence

Copyright 2015 eLife Sciences. Licensed under the [GPLv3](LICENCE.txt)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

