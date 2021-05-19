# XBRL

## Terminology

| XBRL Term                 | Business Term                                         | Description                                                  |
| ------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| Taxonomy                  | Rule Book and Specifications                          | Collection of definitions of reporting concepts, relationships between them and various resources |
| Instance Document         | Submission Document (Filing / XBRL Report)            | Container of the reporting facts. Its content is based on metadata defined in the taxonomy |
| Reporting Fact / Fact     | Data Point (A Cell in a QRT)                          | A fact holds the value for a cell but also includes all information to describe the cell - concepts (eg GWP), data type (eg monetary), descriptive dimensions (eg Motor business), entity (eg Insurance Company A), period (eg 31st December 2021), unit (eg USD), rounding information (eg 2 decimal places) |
| Context                   | Grouped information that supports similar data points | Container of dimensional information related to a fact. Contexts can be shared between facts eg instead of repeating all datapoints relating to Motor business will refer to a context which specifies the line of business |
| Unit                      | Unit of a data point                                  | Describes how the fact is measured. For example: monetary value in **GBP**, monetary value in **USD**, non-monetary value (must be used in combination with Data type and Decimals attribute to ascertain the specific unit eg 2 d.p., 4 d.p. etc.) |
| Reporting Entity / Entity | Company ID (LEI / Local Registration Number)          | Provides identification of the reporting entity in the classification of a specific regulator eg can be LEI or in some cases the regulator requires a local registration number to be used to identify the insurer in the XBRL eg CBI in Ireland |
| Period                    | Reporting Period                                      | Either instant (year end date or quarter end date), or duration - start/end date. |
| Dimension                 | Line of business, Valuation method etc.               | Dimension is a property of a reporting fact eg line of business dimension or valuation method dimension. |
| Dimensional analysis      | Dimensional analysis                                  | The set of reporting facts can break down based on values of a specific dimension:<br/>Primary dimensions - entity, period, unit, Custom dimensions - specific concepts (**typed** and **explicit**) |

