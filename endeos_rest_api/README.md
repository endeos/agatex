# ENDEOS REST API

Módulo que permite acceder a Odoo a través de una API REST.

## Documentación de puntos de acceso

Todos los métodos funcionan con peticiones y respuestas en formato JSON. En las cabeceras de una petición, será necesario indicar un id de sesión en la clave _X-Openerp-Session-Id_. El id de sesión se puede obtener mediante el método de login en el apartado de autenticación.

### Autenticación

#### Mediante id sesión

Es necesario, en primer lugar, autenticarse para generar un id de sesión. Cada sesión creada tendrá una duración de 1 día. Este ID de sesión debe pasarse en subsecuentes peticiones.

Aunque las sesiones tendrán una validez de un día, es aconsejable lanzar la petición de logout una vez se hayan finalizado las operaciones.

#### Mediante API Key

Alternativamente, es posible autenticarse mediante una llave API en algunos puntos de acceso concretos. Si no se indica nada al respecto de esto en la documentación del punto de acceso, la autenticación se tiene que hacer mediante id de sesión.

#### Login (Generar id de sesión)

**Punto de acceso:** /api/auth

**Método:** POST

**Datos:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "login": "usuario",
    "password": "contraseña"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "session_id": {
        "sid": "bcd93b1369e9284a060819cfff662614534dd1ef",
        "expires_at": "2023-03-18 09:25:13"
      }
    },
    "errors": []
  }
}
```

El valor en la clave _sid_ es el que necesitaremos indicar en posteriores peticiones.

#### Logout

**Punto de acceso:** /api/logout

**Método:** GET

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos GET:**

```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": ["Logout complete"],
    "errors": []
  }
}
```

### Contactos

Para detalles de campos y tipos en contactos, consultar modelo res.partner.

#### Listado de contactos

Devuelve un listado de los contactos y sus campos.

**Punto de acceso:** /api/v1/contacts

**Método:** GET/POST (si se indica rec_ids)

**Parámetros:**

- rec_ids: opcional. Listado de enteros representando id's de contactos.

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos GET:**

```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rec_ids": [14, 26]
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": [
      {
        "id": 14,
        "ref": false,
        "vat": false,
        "name": "Azure Interior",
        "email": "azure.Interior24@example.com",
        "mobile": false,
        "phone": "(870)-931-0505",
        "street": "4557 De Silva St",
        "street2": false,
        "city": "Fremont",
        "zip": "94538",
        "state_id": [
          13,
          "California (US)"
        ],
        "country_id": [
          233,
          "United States"
        ],
        "comment": false,
        "company_id": false,
        "company_type": "company",
        "type": "contact",
        "child_ids": [
          26,
          33,
          27
        ],
        "parent_id": false
      },
      {
        "id": 26,
        "ref": false,
        "vat": false,
        "name": "Brandon Freeman",
        "email": "brandon.freeman55@example.com",
        "mobile": false,
        "phone": "(355)-687-3262",
        "street": "4557 De Silva St",
        "street2": false,
        "city": "Fremont",
        "zip": "94538",
        "state_id": [
          13,
          "California (US)"
        ],
        "country_id": [
          233,
          "United States"
        ],
        "comment": false,
        "company_id": false,
        "company_type": "person",
        "type": "contact",
        "child_ids": [],
        "parent_id": [
          14,
          "Azure Interior"
        ]
      },
      {...},
    ]
}
```

#### Obtener datos de un contacto

Devuelve datos de un contacto.

**Punto de acceso:** /api/v1/contact/[int:id]

**Método:** GET

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos GET:**

```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "jsonrpc": "2.0",
      "id": null,
      "result": {
        "data": {
          "id": 26,
          "ref": false,
          "vat": false,
          "name": "Brandon Freeman",
          "email": "brandon.freeman55@example.com",
          "mobile": false,
          "phone": "(355)-687-3262",
          "street": "4557 De Silva St",
          "street2": false,
          "city": "Fremont",
          "zip": "94538",
          "state_id": [
            13,
            "California (US)"
          ],
          "country_id": [
            233,
            "United States"
          ],
          "comment": false,
          "company_id": false,
          "company_type": "person",
          "type": "contact",
          "child_ids": [],
          "parent_id": [
            14,
            "Azure Interior"
          ]
        },
        "errors": []
      }
    }
}
```

#### Actualizar contacto

Actualiza una ficha de contacto con la información pasada.

**Punto de acceso:** /api/v1/contact/[int:id]

**Método:** PATCH

**Parámetros:**

- contact_data: diccionario con valores de creación. Algunos posibles valores: ["id","ref","vat","name","email","mobile","phone","street","street2","city","zip","state_id","country_id","comment","company_id","company_type","type","child_ids","parent_id"]

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "contact_data": {
      "phone": "666666666",
      "email": "email2@domain2.com"
    }
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "updated": true
    },
    "errors": []
  }
}
```

#### Crear contacto

Crea nuevo contacto y devuelve el nuevo id.

**Punto de acceso:** /api/v1/contact

**Método:** POST

**Parámetros:**

- contact_data: diccionario con valores de creación. Algunos posibles valores: ["id","ref","vat","name","email","mobile","phone","street","street2","city","zip","state_id","country_id","comment","company_id","company_type","type","child_ids","parent_id"]

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "contact_data":{
      "name": "TEST CONTACT",
      "ref": "abc",
      "vat": "12345678A",
      ...
    }
  }
}
```

Consultar modelo res.partner para detalle de tipos.

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "new_contact_id": 45
    },
    "errors": []
  }
}
```

#### Eliminar un contacto

Eliminar un contacto

**Punto de acceso:** /api/v1/contact/[int:id]

**Método:** DELETE

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

**Datos GET:**

```json
{
  "jsonrpc": "2.0",
  "params": {}
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "deleted": true
    },
    "errors": []
  }
}
```

### Mapeo de API XML RPC

Es posible acceder a una adaptación REST de las funcionalidades genéricas de la [API original XML RPC](https://www.odoo.com/documentation/15.0/es/developer/reference/external_api.html).
Si no hay puntos de acceso creados para un modelo en concreto, es posible usar este punto de acceso más genérico.

**Punto de acceso:** /api/v1/rpc_call

**Método:** POST

**Cabeceras:**

- X-Openerp-Session-Id: id sesión

Si se quiere autenticar mediante una llave API, se puede usar este punto de acceso:

**Punto de acceso:** /api/v1/public_rpc_call

**Método:** POST

**Valores extra en datos POST:**

Junto con los parámetros que necesarios, añadiremos el valor _api_key_ con el valor de la llave generada en el perfil de usuario de Odoo.

```json
{
  "jsonrpc": "2.0",
  "params": {
    "api_key": "xyzxyzxyz"
    ...
  }
}
```

#### Buscar registros

Devuelve un listado de identificadores de registros que cumplan una determinada condición de filtro llamada _dominio_.

Ejemplos de dominios: [https://odootricks.tips/about/building-blocks/domain-in-odoo/](https://odootricks.tips/about/building-blocks/domain-in-odoo/)

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "search",
    "model": "res.partner",
    "domain": "[('name', 'ilike', 'azure')]"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": [14],
    "errors": []
  }
}
```

#### Contar registros

Devuelve el total de registros contados en un modelo para un dominio establecido.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "search_count",
    "model": "res.partner",
    "domain": "[('name', 'ilike', 'azure')]"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": 1,
    "errors": []
  }
}
```

#### Obtener campos de un modelo

Devuelve un listado de los campos disponibles en un modelo.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "fields_get",
    "model": "res.partner"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "name": {
        "type": "char",
        "string": "Name"
      },
      "display_name": {
        "type": "char",
        "string": "Display Name"
      },
      "date": {
        "type": "date",
        "string": "Date"
      },
      "title": {
        "type": "many2one",
        "string": "Title"
      },
      "parent_id": {
        "type": "many2one",
        "string": "Related Company"
      },
      "parent_name": {
        "type": "char",
        "string": "Parent name"
      },
      "child_ids": {
        "type": "one2many",
        "string": "Contact"
      },
      "ref": {
        "type": "char",
        "string": "Reference"
      },
      "lang": {
        "type": "selection",
        "help": "All the emails and documents sent to this contact will be translated in this language.",
        "string": "Language"
      },
      {...},
    },
    "errors": []
  }
}
```

#### Leer campos de uno o varios registros

A partir de un modelo y de un listado de identificadores de registros del mismo, devuelve un listado de valores para unos campos también determinados.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "read",
    "model": "res.partner",
    "rec_ids": [14],
    "fields": ["id", "name", "email"],
    "lang": "es_ES"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": [
      {
        "id": 14,
        "name": "Azure Interior",
        "email": "azure.Interior24@example.com"
      }
    ],
    "errors": []
  }
}
```

#### Búsqueda + lectura

Combinación de una operación de búsqueda de registros con la de lectura de valores de sus campos.

Tendremos que indicar un dominio de búsqueda para un modelo concreto y los campos que queremos ver del mismo.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "search_read",
    "model": "res.partner",
    "domain": "[('name', 'ilike', 'azure')]",
    "fields": ["id", "name", "email"],
    "lang": "es_ES"
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": [
      {
        "id": 14,
        "name": "Azure Interior",
        "email": "azure.Interior24@example.com"
      }
    ],
    "errors": []
  }
}
```

#### Crear nuevo registro

Indicando un modelo y los valores para sus campos, se crea un nuevo registro. Devuelve el identificador del nuevo registro creado.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "create",
    "model": "res.partner",
    "record_data": {
      "name": "Test",
      "email": "apicontact@domain.com",
      "phone": "123456789"
    }
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "new_record_id": 49
    },
    "errors": []
  }
}
```

#### Actualizar registros

Permite actualizar uno o varios registros indicando un listado de los identificadores que nos interesen, su modelo y los campos a actualizar. Devuelve un booleano de confirmación.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "write",
    "model": "res.partner",
    "rec_ids": [48],
    "record_data": {
      "street": "Calle Falsa, 123"
    }
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "updated": true
    },
    "errors": []
  }
}
```

#### Eliminar registros

Permite eliminar uno o varios registros indicando un listado de los identificadores que nos interesen y su modelo. Devuelve un booleano de confirmación.

Puede ser que para mantener integridad referencial en la base de datos no sea posible eliminar algunos registros sin antes eliminar otros relacionados.

**Datos POST:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "rpc_method": "unlink",
    "model": "res.partner",
    "rec_ids": [48]
  }
}
```

**Respuesta:**

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "data": {
      "deleted": true
    },
    "errors": []
  }
}
```
