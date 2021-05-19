# XBRL Objects

| **Taxonomy**                                                 | **Instance Document**                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Contains metadata**<br/>Knowledge about how to produce instance documents | **Contains data**                                            |
| **Web resource**<br/>Similar to a database with normative information<br/>Taxonomies can share objects</br>All objects within a taxonomy are **globally** identified | **Mainly used to transmit data between reporting entity and consumer**<br/>Facts within an XBRL instance are **not** globally addressable. XBRL instance documents cannot share facts. |
| **Multiple files**<br/>Files are discovered by following links between them. To start the discovery process we need an **entry point**. | **Single file**<br/>However, XBRL instances can be part of larger filings. |
|                                                              | **No structure** <br/>There is no information in the XBRL instance document about how to order facts. |
| **Includes concepts**                                        | **Includes facts**<br/>(instances of concepts)               |

