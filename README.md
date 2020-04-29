# Mobile First Indexing Tool


```
            ┌─────────────────────────────────────────────────────────────────────────────────────┐                 
            │                               Mobile First Indexing Request                         │                 
            └─────────────────────────────────────────────────────────────────────────────────────┘                 
                     |   ▲                       |   ▲                          |   ▲                               
                     │   |                       │   |                          │   |                               
                     |   |                       |   |                          |   |                               
            ┌────────▼───|───┐          ┌────────▼───|───┐             ┌────────▼───|───┐                           
            │                |          │                |             │                |                           
            │      API       │          │      API       |             │     API        |                           
            │    GATEWAY     │          │    GATEWAY     │             │    GATEWAY     │                           
            │                │          │                │             │                │                           
            │                │          │                │             │                │                           
            └────────────────┘          └────────────────┘             └────────────────┘                           
                     |   ▲                       |   ▲                          |   ▲                               
                     │   |                       │   |                          │   |                               
                     |   |                       |   |                          |   |                               
            ┌────────▼───|───┐          ┌────────▼───|───┐             ┌────────▼───|───┐                           
            │                |          │                |             │                |                           
            │      MFI       │          │      MFI       |             │     MFI        |                           
            │      BASE      │          │    CONTENT     │             │   LIGHTHOUSE   │                           
            │                │          │                │             │                │                           
            │                │          │                │             │                │                           
            └────────────────┘          └────────────────┘             └────────────────┘                           
                         ▲                       ▲                              ▲                                   
                         |                       |                              |                                   
                         |                       |                              |                                   
            ┌─────────────────────────────────────────────────────────────────────────────────────┐                 
            │                  MFI LAMBDA LAYERS (Selenium, request, etc)                         │                 
            └─────────────────────────────────────────────────────────────────────────────────────┘                 

```

## Installation

```shell script
git clone https://github.com/zeoagency/mobile-first-indexing-tool.git
```

## File Structure

```bash
── mfi-base/
    ├── handler.py
    └── serverless.yaml
── mfi-contents/
    ├── handler.py
    └── serverless.yaml
── mfi-layers/
    ├── bs4/
    ├── chromedriver/
    ├── extruct/
    ├── lxml/
    ├── requests/
    ├── selenium/
    ├── w3lib
    └── serverless.yaml
── mfi-lighthouse/
    ├── handler.py
    └── serverless.yaml  
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[APACHE](LICENSE)