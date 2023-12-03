# JSON graph querying with NetworkX

### Running the application

With Docker

```
docker build -t json-graph .
docker run -p 5000:5000 json-graph
```
or perform
```
pip install Flask numpy networkx
python3 app.py
```

### Purpose

The API is designed to provide valid responses and allows filtering tasks based on criteria like "which tickets need to be completed so feature X can be deployed."

### Implementation

To cover a wide range of search use cases and even more complex selections, the API supports querying using various operators. Queries are structured as JSON objects with the following keys:

`op` - Specifies the operator
`rules` - a list of nested rules, if operator is `or` or `and`
`prop` - A property to which a rule is applied.
`val` - the value to compare, using operators `eq` / `ne` / `in` / `nin` / `txt` / `ntxt`

The app validates the query payload and responds with `400` if the query payload is incomplete or contains properties not in the JSON.

### Suported operators

`eq` / `ne` - Used for strict equality or inequality checks
`in` / `nin` -  Used for inclusion or exclusion among a list of specified values
`txt` / `ntxt` - Simplified text search operators. Checks if the given string is a case-insensitive substring of the property value, while `ntxt` checks for the absence of the substring.

### Examples

To retreive all JSON properties available for querying
```
curl http://localhost:5000/props
```

Retuns all tickets of a `CoreDataUpgrade` project

```
curl --location 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data '{
    "op": "eq",
    "prop": "project",
    "val": "CoreDataUpgrade"
}'
```

Return all tickets where `status=CURRENT_SPRINT` and assigned to Eva or Beth:
```
curl --location 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data '{
    "rules": [
        {
            "op": "or",
            "rules": [
                {
                    "op": "eq",
                    "prop": "assignedTo",
                    "val": "Eva"
                },
                {
                    "op": "eq",
                    "prop": "assignedTo",
                    "val": "Beth"
                }
            ]
        },
        {
            "op": "eq",
            "prop": "status",
            "val": "CURRENT_SPRINT"
        }
    ]
}'
```

The request payload can be an Array of rules or just an object. In the case of an Array, it will be parsed as a set of rules with the operator `and` added by default unless `or` is specified. For example:

Return all tasks tagged `performance` but not tagged as `api`:
```
curl --location 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data '[
    {
        "op": "eq",
        "prop": "tags",
        "val": "performance"
    },
    {
        "op": "ne",
        "prop": "tags",
        "val": "api"
    }
]'
```

This request retrieves all tickets tagged `refactor` or `api`:

```
curl --location 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data '{
    "op": "or",
    "rules": [
        {
            "op": "eq",
            "prop": "tags",
            "val": "refactor"
        },
        {
            "op": "eq",
            "prop": "tags",
            "val": "api"
        }
    ]
}'
```

The operator `eq` can be omitted, as it is the default operator. The following request is equivalent to the previous one:

```
curl --location 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data '{
    "op": "or",
    "rules": [
        {
            "prop": "tags",
            "val": "refactor"
        },
        {
            "op": "eq",
            "prop": "tags",
            "val": "api"
        }
    ]
}'
```

And so on, there could be tons of possible criterias.

### Areas for improvement
- The app does not support nested objects but supports one-level nested arrays. Essentially, the app does not cover more advanced JSON structures beyond the current dataset.
- A few automated tests to cover the query language flow would be beneficial.
